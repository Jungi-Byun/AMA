#---------------------------------------------------------
# LangGraph State, 노드 함수, 그래프 빌더
#---------------------------------------------------------

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from typing import TypedDict, List
from functools import partial
from .llm_utils import run_vlm_analysis, run_ocr_all, run_ocr_merge, run_exaone_summary

class AgentState(TypedDict):
    image_path: str
    overall_description: str
    easyocr_result: str
    paddleocr_result: str
    merged_text: str # OCR result들을 reconstruction한 결과
    summary: str # LLM 요약문
    is_math_related: bool # 수학 관련 여부
    warning: str
    valid_topic: str # 최종 선택 단원
    candidate_topics: List[str]

def overview_analysis_node(state: dict, vlm_processor, vlm_model):
    image_path = state["image_path"]
    result = run_vlm_analysis(image_path, vlm_processor, vlm_model)

    output = {
        "overall_description": result["overall_description"],
        "is_math_related": result["is_math_related"]
    }

    if not output["is_math_related"]:
        output["warning"] = "수학 관련 내용이 아닙니다. 그래프를 종료합니다."

    return output

def ocr_extract_node(state: dict, paddleocr_instance, easyocr_reader):
    image_path = state["image_path"]
    result = run_ocr_all(image_path, paddleocr_instance, easyocr_reader)
    return {"easyocr_result": result["easyocr_result"], "paddleocr_result": result["paddleocr_result"]}

def ocr_merge_node(state: dict, llm_tokenizer, llm_model):
    easy = state["easyocr_result"]
    paddle = state["paddleocr_result"]
    result = run_ocr_merge(easy, paddle, llm_tokenizer, llm_model)
    return {"merged_text": result}

def summarize_node(state: dict, llm_tokenizer, llm_model, curriculum_units):
    input_text = state["merged_text"]
    overall_description = state["overall_description"]
    summary, valid_topic, candidate_topics = run_exaone_summary(input_text,
                                                                overall_description,
                                                                llm_tokenizer,
                                                                llm_model,
                                                                curriculum_units)
    return {"summary": summary, "valid_topic": valid_topic, "candidate_topics": candidate_topics}

def end_with_warning_node(state: dict):
    print(state.get("warning", "비정상 종료"))
    return {"valid_topic": "INVALID"}

def build_graph(llm_tokenizer, llm_model, vlm_processor, vlm_model,
                paddleocr_instance, easyocr_reader, curriculum_units):
    builder = StateGraph(AgentState)
    builder.add_node("overview_analysis", RunnableLambda(lambda state: overview_analysis_node(state,
                                                                                              vlm_processor,
                                                                                              vlm_model)))
    builder.add_node(
        "ocr_extract",
        RunnableLambda(partial(ocr_extract_node,
                            paddleocr_instance=paddleocr_instance,
                            easyocr_reader=easyocr_reader)))

    builder.add_node("ocr_merge", RunnableLambda(lambda state: ocr_merge_node(state,
                                                                              llm_tokenizer,
                                                                              llm_model)))
    builder.add_node("summarize", RunnableLambda(lambda state: summarize_node(state,
                                                                              llm_tokenizer,
                                                                              llm_model,
                                                                              curriculum_units)))
    builder.add_node("end_with_warning", RunnableLambda(end_with_warning_node))

    builder.set_entry_point("overview_analysis")

    # 수학 관련 여부에 따라 흐름 결정
    builder.add_conditional_edges(
        "overview_analysis",
        lambda state: "end_with_warning" if not state.get("is_math_related", False) else "ocr_extract"
    )

    builder.add_edge("ocr_extract", "ocr_merge")
    builder.add_edge("ocr_merge", "summarize")
    builder.add_edge("summarize", END)
    builder.add_edge("end_with_warning", END)
    return builder.compile() 