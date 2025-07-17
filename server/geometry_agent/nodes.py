import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional, Dict, Any, List

from geometry_agent.states import GeometryState
from geometry_agent.configs import MODEL_NAME, SECTIONS_INFO, LEARNED_ORDER, LEARNED_CONCEPTS
from geometry_agent.svgs import *

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, trust_remote_code=True).to(DEVICE)

def classify_sections(state: GeometryState) -> GeometryState:
    """
    소단원(Section)을 보고 힌트를 제공하는데 필요한 수학 개념과 관련된 인자, 힌트 유형(none, svg, formula, both)을 분류한다
    """

    section = state["input_section"]
    section_info = SECTIONS_INFO[section]

    state["section_description"] = section_info["description"]
    state["math_concept"] = section_info["math_concept"]
    if "parameters" in section_info.keys():
        state["parameters"] = section_info["parameters"]
    state["hint_type"] = section_info["hint_type"]

    return state   

def activate_nodes_by_state(state: GeometryState) -> list[str]:
    """
    소단원(Section)을 보고 분류된 정보가 기입된 state를 확인하여 힌트 생성에 필요한 노드를 선택한다
    """

    # 기본적으로 generate_comments 노드를 활성화한다
    activated_nodes = ["generate_comments"]

    hint_type = state["hint_type"]
    if hint_type == "svg":
        activated_nodes.append("generate_code")
    elif hint_type == "formula":
        activated_nodes.append("generate_formulas")
    elif hint_type == "both":
        activated_nodes.extend(["generate_code", "generate_formulas"])
    else: # hint_type == "none"
        pass

    return activated_nodes

def generate_code_node(state: GeometryState) -> GeometryState:
    
    concept = state["math_concept"]
    parameters = state["parameters"] if "parameters" in state.keys() else None

    if concept == "직선":
        code = gen_lines_prototype(concept, parameters)
    elif concept == "각" or concept == "각도" or concept == "직각" or concept == "수직" or concept == "수선":
        code = gen_angle_prototype(concept, parameters)
    elif concept == "직각삼각형":
        code = gen_right_triangle_prototype(concept, parameters)
    elif concept == "직사각형" or concept == "정사각형":
        code = gen_rectangle_prototype(concept, parameters)
    elif concept == "원" or concept == "반지름" or concept == "지름":
        code = gen_circle_prototype(concept, parameters)
    elif concept == "여러 가지 모양(원)":
        code = gen_flower_by_circles(concept, parameters)
    elif concept == "예각과 둔각":
        code = gen_acute_obtuse_angles_prototype(concept, parameters)
    elif concept == "삼각형 분류(변)":
        code = gen_triangles_by_length(concept, parameters)
    elif concept == "이등변삼각형" or concept == "정삼각형":
        code = gen_isosceles_prototype(concept, parameters)
    elif concept == "삼각형 분류(각)":
        code = gen_triangles_by_angle(concept, parameters)
    elif concept == "예각삼각형" or concept == "둔각삼각형":
        code = gen_acute_obtuse_triangles(concept, parameters)
    elif concept == "평행선" or concept == "평행선 사이의 거리":
        code = gen_parallel_lines_prototype(concept, parameters)
    elif concept == "직사각형의 성질" or concept == "정사각형의 성질" or concept == "직사각형/정사각형의 성질 활용":
        code = gen_rectangle_property(concept, parameters)
    elif concept == "사다리꼴" or concept == "평행사변형" or concept == "마름모":
        code = gen_various_quadrangles_prototype(concept, parameters)
    else:
        code = f'''<svg width="{500}" height="{500}" xmlns="http://www.w3.org/2000/svg">
        <text x="{250}" y="{50}" font-size="{12}" text-anchor="middle"># {concept}을(를) 그리는 코드는 아직 구현되지 않았습니다.</text>
        </svg>
        '''

    return {"generated_code": code}

def get_concepts_by_custom_order(concept_dict, order_list, target_key):
    # order_list: 네가 지정한 순서
    if target_key not in order_list:
        raise ValueError(f"키 '{target_key}'는 order_list에 없습니다.")
    
    # target_key까지 포함하는 인덱스
    target_index = order_list.index(target_key)
    
    # 슬라이싱 후 역순
    selected_keys = order_list[:target_index + 1][::-1]
    
    # 각 개념의 값 리스트도 역순으로 바꿔서 합치기
    merged_values = []
    for key in selected_keys:
        reversed_values = concept_dict[key][::-1]
        merged_values.extend(reversed_values)

    return merged_values

def generate_comments_node(state: GeometryState) -> GeometryState:
    basic_prompt = '''
        당신은 초등학생들에게 수학을 가르쳐주는 친절한 초등학교 선생님입니다.
        사용자가 제공하는 {state["section_description"]}의 학습목표와 관련된 문제를 학생이 해결할 수 있도록 다음의 조건을 반드시 지키며 해당하는 개념에 대해 설명해주세요.
        1. 총 300자 이내로 학생들이 이해하기 쉽게 한국어로만 간결하고 정확하게 설명해주세요.
        2. 음수, 다양한 도형들의 대각선, 빗변, 밑변, 밑각, 등변, 높이, 길이, 둘레, 넓이, 면적, 정리(예: 피타고라스의 정리 등)에 대한 개념은 절대 언급하지 마세요.
        3. 영어, 그리스 문자, 수학 기호(∠(각), π(원주율))를 절대 사용하지 마세요.
        4. 학생이 아직 배우지 않은 개념을 포함하지 않기 위해 반드시 아래 개념들만 활용하세요. 아래 목록에 없는 개념은 절대 사용하지 마세요.
    '''

    preliminary = get_concepts_by_custom_order(LEARNED_CONCEPTS, LEARNED_ORDER, state["input_section"])

    system_prompt = basic_prompt
    for concept in preliminary:
        system_prompt += f'\t - {concept}\n'

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": state["section_description"]
        }
    ]
    
    input_ids = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    )

    output = model.generate(
        input_ids.to("cuda"),
        eos_token_id=tokenizer.eos_token_id,
        max_new_tokens=512,
        do_sample=False,
    )

    decoded = tokenizer.decode(output[0], skip_special_tokens=True)

    # 답변 추출 로직
    decoded = decoded[decoded.find("[|assistant|]") + len("[|assistant|]"):]

    return {"comments": decoded.strip()}

def generate_formulas_node(state: GeometryState) -> GeometryState:
    """
    소단원(Section)을 보고 힌트를 제공하는데 필요한 수학 공식을 제공한다
    """

    section = state["input_section"]
    formulas = {}

    if section in ["원의 반지름과 지름 알아보기", "지름의 성질 알아보기"]:
        formulas["반지름과 지름의 관계"] = "$\\mathrm{지름} = \\mathrm{반지름} \\times 2$"
    elif section in ["두 각도의 합 구하기", "두 각도의 차 구하기", "각도의 합 또는 차의 활용"]:
        formulas["두 각도의 합"] = "$\\mathrm{두 \\;각도의 \\;합}: \\mathrm{한 \\;각의 \\;크기(°)} + \\mathrm{다른 \\;각의 \\;크기(°)}$"
        formulas["두 각도의 차"] = "$\\mathrm{두 \\;각도의 \\;차}: \\mathrm{큰 \\;각의 \\;크기(°)} - \\mathrm{작은 \\;각의 \\;크기(°)}$"
    elif section in ["삼각형의 세 각의 크기의 합 구하기", "삼각형에서 나머지 한 각의 크기 구하기"]:
        formulas["삼각형의 내각의 합"] = "$\\mathrm{삼각형의 \\;내각의 \\;합} = 180°$"
    elif section in ["사각형의 네 각의 크기의 합 구하기", "사각형의 나머지 한 각의 크기 구하기"]:
        formulas["사각형의 내각의 합"] = "$\\mathrm{사각형의 \\;내각의 \\;합} = 360°$"

    return {"formulas": formulas}

def merge_hints(state: GeometryState) -> GeometryState:
    return state