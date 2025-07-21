from langgraph.graph import StateGraph, END

from math_q_agent.retrieval_node import (get_random_questions, get_sample_question)
from math_q_agent.generation_node import generate_question, get_llm_model
from math_q_agent.state import State
from math_q_agent.config import (QUESTION_TYPE_RANDOM, QUESTION_TYPE_GENERATE)
from math_q_agent.db_data import merge_csv_to_dataframe

class QuestionAgent:
    def __init__(self):
        self.load_db()
        self.setup_graph()
        self.load_llm()

    def load_db(self):
        df = merge_csv_to_dataframe()
        print('load_db :', len(df))

    def load_llm(self):
        get_llm_model()
        print('load_llm')

    def setup_graph(self):
        """그래프 초기화 및 설정"""
        self.graph = StateGraph(State)

        # 노드 추가
        self.graph.add_node("init_route_question", self.route_question)
        self.graph.add_node("random_question", get_random_questions)
        self.graph.add_node("sample_question", get_sample_question)
        self.graph.add_node("generate_question", generate_question)

        # 시작점 설정
        self.graph.set_entry_point("init_route_question")

        # 조건부 간선 추가
        self.graph.add_conditional_edges(
            "init_route_question",
            self.extract_route,
            {
                QUESTION_TYPE_RANDOM: "random_question",
                QUESTION_TYPE_GENERATE: "sample_question",
            },
        )

        # 간선 추가
        self.graph.add_edge("random_question", END)
        self.graph.add_edge("sample_question", "generate_question")
        self.graph.add_edge("generate_question", END)

        # 그래프 컴파일
        self.graph = self.graph.compile()

    def route_question(self, state: State):
        """문제 타입 입력 확인"""
        print(f"[route_question] State: {state}")

    def extract_route(self, state: State) -> int:
        """문제 타입에 따른 라우팅 결과"""
        return state["request_question_type"]
    
    def run(self, question_topic, question_type):    
        answer = self.graph.invoke({
            'topic': question_topic,
            'request_question_type': question_type,
            'count': 4
        })
        print('answer = ', answer)
        question_list = answer['question_list']

        return question_list