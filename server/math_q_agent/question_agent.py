"""파일 처리 및 외부 서비스 연동"""
from model import get_classifier_model, get_llm_model
from .math_q_agent import MathQAgent
from utils import SUCCESS_CODE, SUCCESS_MESSAGE

class QuestionAgent:
    @staticmethod
    def generate_response(question_topic, question_type):    
        fn = 'generate_response'
        print(f"[{fn}]") 
        math_q_agent = MathQAgent()
        response = math_q_agent.invoke(question_topic, question_type, 4)
        # print('response = ', response['question_list'])
        question_list = response['question_list']
        
        return question_list



