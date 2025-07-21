from typing import TypedDict, List, Dict

class State(TypedDict):
    """
    그래프의 상태를 나타냅니다.

    Attributes:
        request_question_type : 요청된 문제 타입 (1 = Random / 2 - Create )
        topic: 소단원 주제
        count: 문제 요청 개수
        sample_question : topic을 이용하여 추출된 샘플 문제
        sample_question_info : 샘플 문제의 메타 정보(학년/학기/단원 정보 등)
        sample_question_type : 추출된 대표 문제의 타입 (0 = 생성 불가 문제 유형 / 2 - 생성 가능 문제 유형)
    """
    request_question_type: int
    topic: str
    count: int
    question_list: List[str]
    sample_question: str
    sample_question_info: Dict[str, str]
    sample_question_type: int