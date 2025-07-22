import json
import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from math_q_agent.state import State
from math_q_agent.config import MODEL_NAME

_q_llm_model = None
_q_llm_tokenizer = None
_q_device = None

ADDITIONAL_INFO = {
	"직사각형의 특징 알아보기": "네 변의 길이의 합은 항상 짝수여야 하며, 네 변의 길이의 합은 가로 혹은 세로의 값 2배보다 항상 커야 한다.",
	"정사각형의 특징 알아보기": "직사각형이 문제에 주어지는 경우, 짧은 변의 길이의 배수가 정사각형의 한 변의 길이와 일치해야 한다.",
	"삼각형의 변의 길이에 따라 분류하기": "정삼각형의 총 길이는 3의 배수여야 합니다.",
	"이등변삼각형 알아보기": "이등변삼각형의 나머지 변을 찾아보는 문제라면 보기 변의 값이 서로 다른 값을 사용해야 합니다.",
	"예각삼각형 알아보기": "한 각이 90도이거나 두 각의 합이 90도인 값은 사용하지 않습니다. 세 각의 합은 반드시 180도여야 합니다.",
	"삼각형을 각의 크기에 따라 분류하기": "한 각이 90도이거나 두 각의 합이 90도인 값은 사용하지 않습니다. 세 각의 합은 반드시 180도여야 합니다.",
	"둔각삼각형 알아보기": "한 각이 90도이거나 두 각의 합이 90도인 값은 사용하지 않습니다. 세 각의 합은 반드시 180도여야 합니다.",
	"직사각형의 성질 알아보기": "문제에서 물체를 다루는 경우, 각 문제는 길이가 다른 두 종류의 물체(예: 수수깡, 막대, 판자 등)가 각각 2개씩 사용되는 경우를 다룹니다.",
	"정다각형과 정다각형의 이름 알아보기": "2개 이상의 정다각형이 나오는 경우, 각 정다각형의 변의 길이의 합이 모두 같아야 한다."
}


def get_llm_model():
    fn = 'get_llm_model'
    global _q_llm_model, _q_llm_tokenizer, _q_device
   
    if _q_llm_model is None:
        model_name = MODEL_NAME
        _q_llm_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True
        )
        _q_llm_tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        _q_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        _q_llm_model.to(_q_device)
        print(f"[{fn}] create new instance")
    else :
        print(f"[{fn}] exist instance")
    return _q_llm_model, _q_llm_tokenizer, _q_device



def get_prompt(ex_question, topic, additional_info=""):
    """프롬프트 생성"""
    prompt = f"""위 예시 문제의 문장 구조를 그대로 유지하면서 숫자 값만 변경하여 4개의 새로운 문제를 생성해 주세요.
            예시 문제: {ex_question}
            """

    messages = [
        {
            "role": "system",
            "content": f"""당신은 초등학교 수학 선생님입니다. 주어진 지시사항에 따라 수학 문제를 생성해야 합니다.
            지시사항:
                예시 문제의 문장 구조를 절대 변경하지 말고, 숫자 값만 변경하여 새로운 문제를 생성합니다.
                생성되는 모든 문제는 주제인 "{topic}"를 유지해야 합니다.
                문제의 구조와 형식은 예시 문제와 동일해야 합니다.
                필요한 경우 계산기를 사용하여 적절한 숫자를 선택할 수 있습니다.
                문제 출제 중 오류가 발견되면 다시 출제합니다.
                숫자 값은 자연수여야 합니다.
                {additional_info}
            출력 포맷은 다음과 같아야 합니다:
            {{
                "questions": [문제1, 문제2, 문제3, 문제4]
            }}"""
        },
        {"role": "user", "content": prompt}
    ]

    return messages

def generate_question(state: State):
    """분류 모델을 사용하여 결과 예측"""
    fn = 'generate_question'

    print(f"[generate_question] State: {state}")
    try:
        question_list = []
        if len(state["sample_question"]) > 0:
            key = state["topic"]
            if key in ADDITIONAL_INFO:
                add_info = ADDITIONAL_INFO[key]
                print(f"[{fn}] add_info: {add_info}")
            else: 
                add_info = ""
            
            messages = get_prompt(state["sample_question"], state["topic"], add_info)
            # print(f"[{fn}] messages: {messages}")

            model, tokenizer, device = get_llm_model()
            
            input_ids = tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt"
            )
            output = model.generate(
                input_ids.to(device),
                eos_token_id=tokenizer.eos_token_id,
                max_new_tokens=1024,
                do_sample=False,
            )
            print(f"[{fn}] output: {tokenizer.decode(output[0])}")
            
            json_pattern = re.compile(r'\[\|assistant\|\]\s*```json(.*?)```', re.DOTALL)
            match = json_pattern.search(tokenizer.decode(output[0]))
            print(f"[{fn}] match: {match}")
            
            if match:
                json_data = match.group(1).strip()
                escaped_json = json_data.replace("\\", "\\\\")
                
                escaped_data = json.loads(escaped_json)
                for value in escaped_data['questions']:
                    question_list.append(value)
            else:
                print("No JSON data found.")
        
        state["question_list"] = question_list        
        return {"question_list": state["question_list"]}
    except Exception as e:
        print(f"[{fn}] Internal server error : ", e)
        return {"question_list": []}