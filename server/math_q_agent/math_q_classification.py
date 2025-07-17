import torch
from model import get_classifier_model
from .math_q_state import State

def predict_classification(model, tokenizer, text) -> int:
    """텍스트 분류 예측"""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    prediction = torch.argmax(outputs.logits, dim=1).item()
    return prediction

def extract_classification(state: State) -> int:
    """문제 분류 타입 따른 라우팅 결과"""
    state["question_list"] = []
    fn = 'extract_classification'
    
    if len(state["sample_question"]) <= 0:
        state["sample_question_type"] = 99
    else:
        model, tokenizer = get_classifier_model()
        class_predict = predict_classification(model, tokenizer, state["sample_question"])
        state["sample_question_type"] = class_predict
    
    print(f"[{fn}] class_predict : ", class_predict)
    print(f"[{fn}] state : ", state)
    return state["sample_question_type"]


