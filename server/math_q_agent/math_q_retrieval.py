import os
import base64
import json
from .math_q_state import State
from utils import (DEFAULT_QUESTION_COUNT, META_DB, TOPIC_DB, LABELS_DIRECTORY_PATH, \
                    IMAGES_DIRECTORY_PATH, QUESTION_TYPE_RANDOM, )

from utils import add_newline_before_string, read_datasets_from_file, safe_get_random_index

# 파일에 저장할 경로와 파일명
meta_db = META_DB
topic_db = TOPIC_DB

labels_directory_path = LABELS_DIRECTORY_PATH
images_directory_path = IMAGES_DIRECTORY_PATH

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
    loaded_datasets = read_datasets_from_file(meta_db)
    
    extracted_values = []
    for data in loaded_datasets:
        data_dict = dict(data)
        if type == QUESTION_TYPE_RANDOM: 
            if data_dict['question_topic_name'] == topic: 
                extracted_values.append(data_dict)
        else:
            if data_dict['question_topic_name'] == topic and \
                data_dict['question_type1'] == "단답형" and \
                data_dict['question_type2'] == type:
                extracted_values.append(data_dict)
    
    return extracted_values

#----------------------------------------------------
# random_question_retrieval 함수
# @state : GraphState
#----------------------------------------------------       
def random_question_retrieval(state: State):
    """문제 은행에서 문제 추출"""
    total_list = get_math_question_list(state["topic"], state["request_question_type"])
    question_list = []
    question_index_list = set()
    
    if len(total_list) == 0:
        print('[random_question_retrieval] Error: 문제 출제를 위한 DataSet이 없습니다.')
        state["question_list"] = question_list
    else:
        if state["count"] == 0:
            state["count"] = DEFAULT_QUESTION_COUNT
        
        if state["count"] > len(total_list):
            state["count"] = len(total_list)
    
        while len(question_list) < state["count"]:
            index = safe_get_random_index(len(total_list)-1)
            
            if index not in question_index_list:
                question_index_list.add(index)
                file = total_list[index]['question_filename']
                if file:
                    image_path = os.path.join(IMAGES_DIRECTORY_PATH, file)
                    
                    with open(image_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        question_list.append(encoded_string)
        
        state["question_list"] = question_list

    return {"question_list": state["question_list"]}
        

#----------------------------------------------------
# retrieve_sample_question 함수
# @state : GraphState
#----------------------------------------------------      
def retrieve_sample_question(state: State):
    """문제 생성을 위한 샘플 문제 추출"""
    fn = 'retrieve_sample_question'
    total_list = get_math_question_list(state["topic"], state["request_question_type"])
    
    print(f"[{fn}] total_list :", len(total_list))

    question_list = []
    if len(total_list) == 0:
        print('[retrieve_sample_question] Error: 문제 생성을 위한 DataSet이 없습니다.')
        state["sample_question"] = ""
        state["sample_question_info"] = {}
    else:
        if state["count"] == 0:
            state["count"] = DEFAULT_QUESTION_COUNT
    
        
        while len(question_list) < 1:
            print(f"[{fn}] len(question_list) : ", len(question_list))
            index = safe_get_random_index(len(total_list)-1)
            file = total_list[index]['question_filename'].replace('.png', '.json')

            if file:
                json_path = os.path.join(LABELS_DIRECTORY_PATH, file)
                with open(json_path, "rb") as json_file:
                    json_data = json.load(json_file)
                    question_info = json_data['question_info'][0]
                    ocr_info = json_data['OCR_info'][0]
                    
                    image_exist = any(bbox['type'] == 'image' for bbox in ocr_info.get('question_bbox', []))
                    if not image_exist:
                        question = add_newline_before_string(ocr_info['question_text'])
                        question_list.append(question)

                        sample_question_info = {
                            "question_grade": question_info['question_grade'],
                            "question_term": question_info['question_term'],
                            "question_unit": question_info['question_unit'],
                        }
                        break
                    else:
                        print("image bbox found in OCR_info")
        
        state["sample_question"] = question_list[0]
        state["sample_question_info"] = sample_question_info
        # print(f"[{fn}] state : ", state)

    return {
        "sample_question": state["sample_question"],
        "sample_question_info": state["sample_question_info"]
    }