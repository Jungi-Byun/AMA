import os
import base64
import random
from math_q_agent.state import State
from math_q_agent.config import (DEFAULT_QUESTION_COUNT, PRACTICE_DATA, RANDOM_DATA, \
                            DIR_PATH_LABELS_DS1, DIR_PATH_IMAGES_DS1,\
                            DIR_PATH_LABELS_DS2, DIR_PATH_IMAGES_DS2, )

from math_q_agent.db_data import get_problem_df
from math_q_agent.utils import add_newline_before_string

# 파일에 저장할 경로와 파일명
practice_db = PRACTICE_DATA
random_db = RANDOM_DATA

dir_path_labels_ds1 = DIR_PATH_LABELS_DS1
dir_path_labels_ds2 = DIR_PATH_LABELS_DS2
dir_path_images_ds1 = DIR_PATH_IMAGES_DS1
dir_path_images_ds2 = DIR_PATH_IMAGES_DS2

#----------------------------------------------------
# get_math_question_list 함수
# @topic : 학습 목표(학습 단원)
# @type : 문제 유형(1 - Random, 2-유형 생성)
#----------------------------------------------------
def get_math_question_list(topic, type):
    fn = 'get_math_question_list'

    print(f"[{fn}] topic :", topic)
    print(f'[{fn}] type :' ,type)

    # 파일에서 dataset 데이터를 읽어옴
    df = get_problem_df()

    conditions = (df['question_topic_name'] == topic) & (df['question_type1'].astype(int) == type)
    data_list = df[conditions]

    return data_list

#----------------------------------------------------
# get_random_questions 함수
# @state : GraphState
#----------------------------------------------------       
def get_random_questions(state: State):
    """문제 은행에서 문제 추출"""
    fn = 'get_random_questions'

    total_df = get_math_question_list(state["topic"], state["request_question_type"])
    # print(total_df.index)
    print(f"[{fn}] total_df :", len(total_df))

    question_list = []
    question_index_list = set()
    
    if len(total_df) == 0:
        print(f'[{fn}] Error: 문제 출제를 위한 DataSet이 없습니다.')
        state["question_list"] = []
    else:
        if state["count"] == 0:
            state["count"] = DEFAULT_QUESTION_COUNT
        
        if state["count"] > len(total_df):
            state["count"] = len(total_df)
    
        while len(question_list) < state["count"]:
            index = random.choice(total_df.index)
            print(f'[{fn}] index  : ', index)
            
            if index not in question_index_list:
                question_index_list.add(index)
                file = total_df.loc[index]['question_filename']

                if file:
                    if total_df.loc[index]['question_dataset'] == 1:
                        image_path = os.path.join(DIR_PATH_IMAGES_DS1, file)
                    else:
                        image_path = os.path.join(DIR_PATH_IMAGES_DS2, file) 
                    
                    with open(image_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        question_list.append(encoded_string)
        
        state["question_list"] = question_list

    return {"question_list": state["question_list"]}
        

#----------------------------------------------------
# get_sample_question 함수
# @state : GraphState
#----------------------------------------------------      
def get_sample_question(state: State):
    """문제 생성을 위한 샘플 문제 추출"""
    fn = 'get_sample_question'
    
    total_df = get_math_question_list(state["topic"], state["request_question_type"])
    # print(total_df.index)
    print(f"[{fn}] total_df :", len(total_df))

    loop_count = 0
    sample_question = None
    if len(total_df) == 0:
        print(f'[{fn}] Error: 문제 생성을 위한 DataSet이 없습니다.')

        state["sample_question"] = ""
        state["sample_question_info"] = {}
    else:
        if state["count"] == 0:
            state["count"] = DEFAULT_QUESTION_COUNT
        
        while sample_question == None and loop_count < 10:
            index = random.choice(total_df.index)
            if total_df.loc[index]['question_type2'] == 1:
                sample_question = add_newline_before_string(total_df.loc[index]['question_text'])

                sample_question_info = {
                    "question_grade": total_df.loc[index]['question_grade'],
                    "question_term": total_df.loc[index]['question_term'],
                    "question_unit": total_df.loc[index]['question_unit'],
                }
            else:
                loop_count =+1
        
        state["sample_question"] = sample_question
        state["sample_question_info"] = sample_question_info

    return {
        "sample_question": state["sample_question"],
        "sample_question_info": state["sample_question_info"]
    }