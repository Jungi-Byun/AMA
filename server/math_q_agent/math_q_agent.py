from .math_q_retrieval import (random_question_retrieval, retrieve_sample_question)
from .math_q_generation import generate_question
from .math_q_classification import extract_classification
from .math_q_state import State
from utils import (QUESTION_TYPE_RANDOM, QUESTION_TYPE_GENERATE)
from langgraph.graph import StateGraph, END

class MathQAgent:
    def __init__(self):
        self._setup_graph()

    def _setup_graph(self):
        """그래프 초기화 및 설정"""
        self.graph = StateGraph(State)
        # 노드 추가
        self.graph.add_node("init_route_question", self.route_question)
        self.graph.add_node("random_question", random_question_retrieval)
        self.graph.add_node("retrieve_sample_question", retrieve_sample_question)
        self.graph.add_node("generate_question", generate_question)
        self.graph.add_node("response_with_question_list", self.response_with_question_list)

        # 시작점 설정
        self.graph.set_entry_point("init_route_question")

        # 조건부 간선 추가
        self.graph.add_conditional_edges(
            "init_route_question",
            self.extract_route,
            {
                QUESTION_TYPE_RANDOM: "random_question",
                QUESTION_TYPE_GENERATE: "retrieve_sample_question",
            },
        )

        self.graph.add_conditional_edges(
            "retrieve_sample_question",
            extract_classification,
            {
                0: "retrieve_sample_question",
                1: "generate_question",
                99: "response_with_question_list"
            },
        )

        # 간선 추가
        self.graph.add_edge("random_question", 'response_with_question_list')
        self.graph.add_edge("generate_question", "response_with_question_list")
        self.graph.add_edge("response_with_question_list", END)

        # 그래프 컴파일
        self.graph = self.graph.compile()

    def route_question(self, state: State):
        """문제 타입 입력 확인"""
        print(f"[route_question] State: {state}")

    def extract_route(self, state: State) -> int:
        """문제 타입에 따른 라우팅 결과"""
        print(f"[extract_route] State: {state}")
        return state["request_question_type"]

    def response_with_question_list(self, state: State):
        """추출된 문제 또는 생성된 문제를 회신"""
        if state["request_question_type"] == QUESTION_TYPE_GENERATE and len(state["sample_question"]) <= 0:
            state["question_list"] = []

        return {"question_list": state["question_list"]}

    def invoke(self, topic, problem_type, count):
        """Agent invoke 함수"""
        answer = self.graph.invoke({
            'topic': topic,
            'request_question_type': problem_type,
            'count': count
        })
        
        return answer