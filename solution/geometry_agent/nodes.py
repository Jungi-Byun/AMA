import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional, Dict, Any, List

from geometry_agent.states import GeometryState
from geometry_agent.configs import MODEL_NAME, SECTIONS_INFO
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

def generate_comments_node(state: GeometryState) -> GeometryState:
    messages = [
        {
            "role": "system",
            "content": '''
                당신은 초등학생들에게 수학을 가르쳐주는 친절한 초등학교 선생님입니다.
                {state["section_description"]}의 학습목표를 학생이 달성할 수 있도록 해당하는 개념에 대해 설명해주세요.
                다음 내용을 포함하여 반드시 총 500자 이내로 한국어로 설명해주세요.
                    - 정의
                    - 기본 성질(공식은 제외하세요)
                원주율은 반드시 π(\pi)가 아닌 3.14로하여 제공해주세요.
             '''
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