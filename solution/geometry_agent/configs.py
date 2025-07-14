# model name for the geometry agent
# This should match the model used in the agent.py file
MODEL_NAME = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct"

# sections information for the geometry agent
# This dictionary contains the section names, their descriptions, math concepts, and hint types
# Each section corresponds to a specific geometry topic
# The hint_type can be 'svg', 'formula', 'both', or 'none'
# 'svg' indicates that the hint is a visual representation, 'formula' indicates a mathematical formula,
# 'both' indicates that both types of hints are provided, and 'none' indicates no hints are provided
SECTIONS_INFO = {
    "직선 알아보기": {
        "description": "직선을 보고 이름을 붙이며, 직선의 개념을 이해한다.",
        "math_concept": "직선",
        "hint_type": "svg",
    },
    "각 알아보기": {
        "description": "각의 구성 요소(꼭짓점, 변)를 알고 각을 인식할 수 있다.",
        "math_concept": "각",
        "hint_type": "svg",
    },
    "직각 알아보기": {
        "description": "직각을 판단하고, 직각과 다른 각을 구별할 수 있다.",
        "math_concept": "직각",
        "parameters": {"size": 90},
        "hint_type": "svg",
    },
    "직각삼각형 알아보기": {
        "description": "직각삼각형을 식별하고, 구성 요소(변, 각)를 이해한다.",
        "math_concept": "직각삼각형",
        "hint_type": "svg",
    },
    "직사각형의 특징 알아보기": {
        "description": "직사각형을 다른 사각형과 구별하고 그 특징을 설명할 수 있다.",
        "math_concept": "직사각형",
        "hint_type": "svg",
    },
    "정사각형의 특징 알아보기": {
        "description": "정사각형을 다른 사각형과 구별하고 그 특징을 설명할 수 있다.",
        "math_concept": "정사각형",
        "hint_type": "svg",
    },
    "원의 반지름과 지름 알아보기": {
        "description": "원의 반지름과 지름의 관계를 알고, 직접 측정하거나 구할 수 있다.",
        "math_concept": "원",
        "hint_type": "both",
    },
    "지름의 성질 알아보기": {
        "description": "지름과 반지름의 관계를 바탕으로 길이를 비교하거나 구한다.",
        "math_concept": "원",
        "hint_type": "both",
    },
    "원 그리기": {
        "description": "컴퍼스를 이용하여 정확한 원을 그리고 반지름/지름을 표시할 수 있다.",
        "math_concept": "원",
        "hint_type": "svg",
    },
    "원을 이용하여 여러 가지 모양 그리기": {
        "description": "원의 특성을 이용해 창의적인 도형이나 패턴을 구성한다.",
        "math_concept": "여러 가지 모양(원)",
        "hint_type": "svg",
    },
    "각의 크기 비교하기": {
        "description": "직각, 예각, 둔각 등을 비교하여 각의 크기를 판단한다.",
        "math_concept": "각",
        "hint_type": "svg"
    },
    "각도기를 이용하여 각도 재기": {
        "description": "각도기를 바르게 사용하여 각의 크기를 정확히 잴 수 있다.",
        "math_concept": "각도",
        "hint_type": "svg",
    },
    "각도를 나타내는 단위 알아보기": {
        "description": "각의 크기를 도(°) 단위로 표현하고, 단위 개념을 이해한다.",
        "math_concept": "각도",
        "hint_type": "svg",
    },
    "각도기와 자를 이용하여 각 그리기": {
        "description": "각도기와 자를 이용해 주어진 각도를 정확히 그릴 수 있다.",
        "math_concept": "각",
        "hint_type": "svg",
    },
    "예각과 둔각 알아보기": {
        "description": "주어진 각을 예각, 직각, 둔각으로 분류할 수 있다.",
        "math_concept": "예각과 둔각",
        "hint_type": "svg",
    },
    "각도를 어림하고 각도기로 재어 확인하기": {
        "description": "주어진 각도를 어림하고 각도기로 재어 확인한다.",
        "math_concept": "각도",
        "hint_type": "svg",
    },
    "각도의 합 또는 차의 활용": {
        "description": "주어진 상황에서 두 각의 크기를 더하거나 빼는 문제를 해결한다.",
        "math_concept": "각도의 합/차",
        "hint_type": "formula",
    },
    "두 각도의 차 구하기": {
        "description": "두 각도를 큰 각에서 작은 각을 빼서 더 작은 각을 만들 수 있다.",
        "math_concept": "각도의 합/차",
        "hint_type": "formula",
    },
    "두 각도의 합 구하기": {
        "description": "두 각도를 더하여 더 큰 각을 만들 수 있다.",
        "math_concept": "각도의 합/차",
        "hint_type": "formula",
    },
    "삼각형에서 나머지 한 각의 크기 구하기": {
        "description": "삼각형의 세 각의 합이 180°인 사실을 이용하여 두 각의 크기가 주어졌을 때 나머지 한 각의 크기를 구할 수 있다.",
        "math_concept": "삼각형의 내각의 합",
        "hint_type": "formula",
    },
    "삼각형의 세 각의 크기의 합 구하기": {
        "description": "삼각형의 세 각의 크기의 합을 구하여 삼각형의 내각의 합이 180°인 사실을 확인한다.",
        "math_concept": "삼각형의 내각의 합",
        "hint_type": "formula",
    },
    "사각형의 나머지 한 각의 크기 구하기": {
        "description": "사각형의 네 각의 합이 360°인 사실을 이용하여 세 각의 크기가 주어졌을 때 나머지 한 각의 크기를 구할 수 있다.",
        "math_concept": "사각형의 내각의 합",
        "hint_type": "formula",
    },
    "사각형의 네 각의 크기의 합 구하기": {
        "description": "사각형의 네 각의 크기의 합을 구하여 사각형의 내각의 합이 360°인 사실을 확인한다.",
        "math_concept": "사각형의 내각의 합",
        "hint_type": "formula",
    },
    "삼각형의 변의 길이에 따라 분류하기": {
        "description": "삼각형의 변의 길이에 따라 일반삼각형, 이등변삼각형과 정삼각형으로 분류할 수 있다.",
        "math_concept": "삼각형 분류(변)",
        "hint_type": "svg",
    },
    "이등변삼각형 알아보기": {
        "description": "삼각형에서 두 변의 길이가 같은 이등변삼각형을 이해한다.",
        "math_concept": "이등변삼각형",
        "hint_type": "svg",
    },
    "이등변삼각형의 성질 알아보기": {
        "description": "삼각형에서 두 변의 길이가 같은 이등변삼각형의 성질을 이해한다.",
        "math_concept": "이등변삼각형",
        "hint_type": "svg",
    },
    "각을 이용하여 이등변삼각형 그리기": {
        "description": "한 선분의 양 끝에서 각각 마주보는 방향으로 같은 각도로 선분을 그어 이등변삼각형을 그릴 수 있다.",
        "math_concept": "이등변삼각형",
        "hint_type": "svg",
    },
    "정삼각형 알아보기": {
        "description": "삼각형에서 세 변의 길이가 같은 정삼각형을 이해한다.",
        "math_concept": "정삼각형",
        "hint_type": "svg",
    },
    "정삼각형의 성질 알아보기": {
        "description": "정삼각형의 각과 변의 성질을 설명하고 활용할 수 있다.",
        "math_concept": "정삼각형",
        "hint_type": "svg",
    },
    "각을 이용하여 정삼각형 그리기": {
        "description": "한 선분의 양 끝에서 각각 마주보는 방향으로 60°로 선분을 그어 정삼각형을 그릴 수 있다.",
        "math_concept": "정삼각형",
        "hint_type": "svg",
    },
    "삼각형을 각의 크기에 따라 분류하기": {
        "description": "삼각형을 각의 크기에 따라 예각삼각형, 직각삼각형, 둔각삼각형으로 올바르게 분류할 수 있다.",
        "math_concept": "삼각형 분류(각)",
        "hint_type": "svg",
    },
    "예각삼각형 알아보기": {
        "description": "세 각이 모두 예각인 예각삼각형을 식별하고 특징을 이해한다.",
        "math_concept": "예각삼각형",
        "hint_type": "svg",
    },
    "둔각삼각형 알아보기": {
        "description": "삼각형의 세 각 중 하나가 둔각인 둔각삼각형을 구별하고 특징을 설명할 수 있다.",
        "math_concept": "둔각삼각형",
        "hint_type": "svg",
    },
    "삼각자와 각도기를 이용한 수선 긋기": {
        "description": "도구를 이용해 주어진 점에서 직선에 수선을 정확히 그릴 수 있다.",
        "math_concept": "수선",
        "hint_type": "svg",
    },
    "수직": {
        "description": "수직의 개념을 이해하고 도형에서 수직선을 찾거나 그릴 수 있다.",
        "math_concept": "수직",
        "hint_type": "svg",
    },
    "평행 알아보기": {
        "description": "평행선의 정의를 이해하고 구별할 수 있다.",
        "math_concept": "평행선",
        "hint_type": "svg",
    },
    "삼각자를 사용하여 평행선 긋기": {
        "description": "삼각자를 사용해 정확하게 평행선을 그릴 수 있다.",
        "math_concept": "평행선",
        "hint_type": "svg",
    },
    "주어진 거리의 평행선 긋기": {
        "description": "자와 삼각자를 활용해 주어진 거리만큼 떨어진 평행선을 그린다.",
        "math_concept": "평행선",
        "hint_type": "svg",
    },
    "평행선 사이의 거리 알아보기": {
        "description": "평행선 사이의 거리를 측정하고 설명할 수 있다.",
        "math_concept": "평행선 사이의 거리",
        "hint_type": "svg",
    },
    "직사각형의 성질 알아보기": {
        "description": "직사각형의 정의와 성질을 알고 도형을 분류한다.",
        "math_concept": "직사각형의 성질",
        "hint_type": "svg",
        
    },
    "정사각형의 성질 알아보기": {
        "description": "정사각형의 정의와 변, 각, 대각선의 성질을 이해하고 다른 사각형과 구별할 수 있다.",
        "math_concept": "정사각형의 성질",
        "hint_type": "svg",
        
    },
    "직사각형과 정사각형의 성질 활용": {
        "description": "두 도형의 성질을 바탕으로 실생활 문제를 해결한다.",
        "math_concept": "직사각형/정사각형의 성질 활용",
        "hint_type": "svg",
    },
    "사다리꼴 알아보기": {
        "description": "사다리꼴의 정의와 기본 성질을 이해한다.",
        "math_concept": "사다리꼴",
        "hint_type": "svg",
    },
    "평행사변형 알아보기": {
        "description": "평행사변형을 정의하고 특징을 파악한다.",
        "math_concept": "평행사변형",
        "hint_type": "svg",
    },
    "평행사변형의 성질 알아보기": {
        "description": "평행사변형의 성질을 이해하고 구분할 수 있다.",
        "math_concept": "평행사변형",
        "hint_type": "svg",
    },
    "마름모 알아보기": {
        "description": "마름모의 정의와 성질을 알고 구별할 수 있다.",
        "math_concept": "마름모",
        "hint_type": "svg",
    },
    "마름모의 성질 알아보기": {
        "description": "마름모의 대각선 성질을 이해하고 활용한다.",
        "math_concept": "마름모",
        "hint_type": "svg",
    },
}
