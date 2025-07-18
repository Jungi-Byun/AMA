#---------------------------------------------------------
# LLM(Exaone) 관련 함수 (OCR merge, 요약, 단원 선택 등)
#---------------------------------------------------------

import re
import json
import torch
import time
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer
from .ocr_utils import EasyOCR_from_file, PaddleOCR_from_file

def run_vlm_analysis(image_path: str, vlm_processor, vlm_model):
    vlm_start = time.time()
    image = Image.open(image_path)

    vlm_chat = [
        {
            "role": "system",
            "content": [{"text": "당신은 초등학교 교안 이미지를 분석해 전반적 설명을 하고, 해당 교안이 수학 교육과 관련이 있는지 판단하는 AI입니다.", "type": "text"}]
        },
        {
            "role": "user",
            "content": [
                {
                    "text": (
                        "이미지를 보고 아래 JSON 형식으로 출력하세요.\n\n"
                        "출력 형식:\n"
                        "```json\n"
                        "{\n"
                        '  "overall_description": "이미지의 전반적인 내용을 2~4문장으로 간결하고 사실적으로 설명하세요.",\n'
                        '  "is_math_related": "yes" 또는 "no"\n'
                        "}\n"
                        "```\n\n"
                        "유의사항:\n"
                        "- 'overall_description'은 핵심만 담아 간결하게 작성하세요.\n"
                        "- 'is_math_related'는 다음 기준에 따라 판단하세요:\n"
                        "  * **수학적 개념(도형, 숫자, 측정, 비교, 계산, 도표 등)이 일부라도 포함되면 'yes'를 선택하세요.**\n"
                        "  * **명확한 수학 교안이 아니더라도, 수학적 사고가 필요한 활동이면 'yes'를 선택해도 됩니다.**\n"
                        "  * 그 외에는 'no'를 선택하세요.\n"
                        "- 창의력, 흥미 유도, 교육적 가치 같은 **추측이나 해석은 하지 마세요.**\n"
                        "- 단순히 **보이는 사실**만 묘사하세요.\n"
                        "- 예: '여러 개의 삼각형 그림이 보입니다.'\n"
                        "- JSON 외의 다른 텍스트를 출력하지 마세요.\n"
                    ),
                    "type": "text"
                },
                {"filename": image_path.split("/")[-1], "image": image, "type": "image"}
            ]
        }
    ]

    model_inputs = vlm_processor.apply_chat_template(
        vlm_chat,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        add_generation_prompt=True
    ).to("cuda")

    output_ids = vlm_model.generate(
        **model_inputs,
        max_new_tokens=1024,
        do_sample=False,
    )

    result_text = vlm_processor.batch_decode(output_ids, skip_special_tokens=True)[0]

    overall_description = ""
    is_math_related = False

    match = re.search(r'```json\s*(\{.*?\})\s*```', result_text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            parsed_json = json.loads(json_str)
            overall_description = parsed_json.get("overall_description", "")
            is_math_related_str = parsed_json.get("is_math_related", "no")
            is_math_related = is_math_related_str.lower() == "yes"
        except Exception as e:
            print(f"JSON 파싱 실패: {e}")
    else:
        print("JSON 블록을 결과에서 찾을 수 없습니다.")

    output = {
        "overall_description": overall_description,
        "is_math_related": is_math_related
    }

    if not is_math_related:
        output["warning"] = "수학 관련 내용이 아닙니다. 그래프를 종료합니다."

    del model_inputs
    del output_ids
    torch.cuda.empty_cache()
    image.close()

    vlm_time = time.time() - vlm_start
    print(f"vlm 소요시간: {vlm_time:.2f}")
    return output

def run_ocr_all(file_path, paddleocr_instance, easyocr_reader):
    # PaddleOCR 실행
    paddleocr_start = time.time()
    paddleocr_result = PaddleOCR_from_file(file_path, None, ocr=paddleocr_instance)
    print("\n PaddleOCR 결과:\n", paddleocr_result)

    torch.cuda.empty_cache()
    paddleocr_time = time.time() - paddleocr_start
    print(f"paddleOCR 소요시간: {paddleocr_time:.2f}")
    
    # EasyOCR 실행
    easyocr_start = time.time()
    results, _ = EasyOCR_from_file(file_path, None, reader=easyocr_reader)
    easyocr_result = " ".join([text for _, text, _ in results])
    print("\n EasyOCR 결과:\n", easyocr_result)

    torch.cuda.empty_cache()
    easyocr_time = time.time() - easyocr_start
    print(f"easyOCR 소요시간: {easyocr_time:.2f}")

    return {
        "easyocr_result": easyocr_result,
        "paddleocr_result": paddleocr_result
    }

def run_ocr_merge(easy, paddle, llm_tokenizer, llm_model):
    merge_start = time.time()
    prompt = f"""다음은 동일한 교안 이미지에 대해 두 가지 OCR 엔진(EasyOCR, PaddleOCR)이 추출한 텍스트 결과입니다.
두 결과를 비교하여 잘못된 문장을 보완하고, 가능한 한 정확하고 자연스러운 하나의 최종 결과로 합쳐주세요.
문맥상 맞지 않거나 인식이 잘못된 단어는 유추하여 수정해 주세요.

### EasyOCR 결과:
{easy}

### PaddleOCR 결과:
{paddle}
"""

    messages = [
        {"role": "system",
         "content":"당신은 두 개의 OCR 결과(EasyOCR와 PaddleOCR)를 비교하여, "
                   "최대한 정확하고 자연스러운 하나의 통합된 텍스트를 생성하는 전문 AI입니다."},
        {"role": "user", "content": prompt}
    ]

    input_ids = llm_tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    )

    output_ids = llm_model.generate(
        input_ids.to("cuda"),
        eos_token_id=llm_tokenizer.eos_token_id,
        max_new_tokens=1024,
        do_sample=False,
    )

    output_text = llm_tokenizer.decode(output_ids[0], skip_special_tokens=True)
    result = output_text.split("[|assistant|]")[-1].strip()

    # JSON 블록 제거하고 merged_text만 추출
    merged_text = re.sub(r'```json\s*\{.*?\}\s*```', '', result, flags=re.DOTALL).strip()
    merged_text = re.sub(r'### JSON 결과:?\s*', '', merged_text).strip()
    # print("\n 통합 텍스트:\n", merged_text)

    del input_ids
    del output_ids
    torch.cuda.empty_cache()

    merge_time = time.time() - merge_start
    print(f"reconstruction llm 소요시간: {merge_time:.2f}")
    return merged_text

def run_exaone_summary(text: str, description: str, llm_tokenizer, llm_model, curriculum_units):
    summary_start = time.time()
    prompt = f"""당신은 초등학교 수학 교육 자료를 분석하고 분류하는 유능한 AI입니다.  
아래 지침에 따라 교안 내용을 **간결하게 요약**하고, **가장 관련성 높은 단원**을 순차적으로 판단해 주세요.

---

## 분석 대상:

1. **전반적 설명 (Overall Description)**
{description}

2. **교안의 세부 텍스트 (OCR 결과)**
{text}

---

## 분석 단계 1: 교안 요약
- 위 두 가지 내용을 종합하여 다음 정보를 추출하세요:
  - 핵심 개념: 수학적 원리, 개념, 또는 활동
  - 학습 목표: 학생이 이 수업을 통해 도달해야 할 목표

## 분석 단계 2: 1차 후보 단원 선정 (단원명 기반)
- 제공된 초등 수학 단원 목록을 참고하여, 교안의 주제와 단원명 간 유사도를 판단해
관련성이 높은 단원 5개를 **정확한 단원명**으로 추려냅니다.

## 분석 단계 3: 최종 관련 단원 선정 (내용 기반)
- 위에서 추린 5개 단원의 핵심 개념과 학습 목표를 확인하고, 요약된 교안 내용과 가장 밀접한 단원 1개를 최종 선택합니다.
- 단원의 명칭은 반드시 **초등 수학 단원 목록에서 일치하는 이름만 사용**하세요.

---

**주의사항:**
- 단원명 외에는 부가 설명, 해설, 괄호 등을 포함하지 마세요.
- 출력 형식을 반드시 지켜 주세요.

---

### 초등 수학 단원 목록:
{curriculum_units}

---

### Output 형식:

1. 요약 내용:
- 핵심 개념: ...
- 학습 목표: ...

2. 1차 후보 단원 (단원명 기반 유사도 상위 5개, JSON 형식):
```json
{{
  "topic_1st": "여기에 단원명",
  "topic_2st": "여기에 단원명",
  "topic_3st": "여기에 단원명",
  "topic_4st": "여기에 단원명",
  "topic_5st": "여기에 단원명"
}}
```

3. 최종 선택 단원 (내용 기반 유사도 최상위 1개, JSON 형식):
```json
{{
  "most_relevant_topic": "여기에 단원명"
}}
```
"""
    messages = [
        {"role": "system",
         "content": "당신은 초등학교 교육자료를 잘 요약해 주는 유능한 AI입니다."},
        {"role": "user", "content": prompt}
    ]

    input_ids = llm_tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
            )

    # print("\n 입력 토큰 수:", len(input_ids[0]))

    output_ids = llm_model.generate(
        input_ids.to("cuda"),
        eos_token_id=llm_tokenizer.eos_token_id,
        max_new_tokens=512,
        do_sample=False,
        )

    #  여기서 문자열로 디코딩
    output_text = llm_tokenizer.decode(output_ids[0], skip_special_tokens=True)

    matches = re.findall(r'"most_relevant_topic"\s*:\s*"([^"]+)"', output_text)

    selected_title = ""
    titles = [item['title'] for item in curriculum_units]
    if matches:
        if matches[-1].strip() in titles:
            selected_title = matches[-1].strip()
            # print("최종 추천 단원:", selected_title)
        else:
            print(f"추천된 단원이 후보군에 없음: {selected_title}")
    else:
        print("출력에서 valid_topic 추출 실패")

    #  1차 후보 단원 추출
    candidate_titles = []
    #  문자열에 대해 split 적용
    if "[|assistant|]" in output_text:
        result = output_text.split("[|assistant|]")[-1].strip()
        # print('\n\n ', result)

        # candidate_topics 파싱
        candidate_titles = []
        for k in range(1, 6):
            pattern = rf'"topic_{k}(st|nd|rd|th)"\s*:\s*"([^"]+)"'
            match = re.search(pattern, result)
            if match:
                candidate_titles.append(match.group(2).strip())

        del input_ids
        del output_ids
        torch.cuda.empty_cache()

        summary_time = time.time() - summary_start
        print(f"summary llm 소요시간: {summary_time:.2f}")
        return result, selected_title, candidate_titles

    del input_ids
    del output_ids
    torch.cuda.empty_cache()
    # print('\n\n', output_text.strip())

    summary_time = time.time() - summary_start
    print(f"summary llm 소요시간: {summary_time:.2f}")
    return output_text.strip(), selected_title, candidate_titles
