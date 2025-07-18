#---------------------------------------------------------
# LangGraph State, 노드 함수, 그래프 빌더
#---------------------------------------------------------

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from typing import TypedDict
from .llm_utils import run_ocr_merge, run_exaone_summary, run_exaone_select

class AgentState(TypedDict):
    easyocr_result: str
    paddleocr_result: str
    merged_text: str
    summary: str
    is_math_related: bool
    warning: str
    valid_topic: str

def ocr_merge_node(state: dict, tokenizer=None, llm_model=None):
    easy = state["easyocr_result"]
    paddle = state["paddleocr_result"]
    result = run_ocr_merge(easy, paddle, tokenizer, llm_model)
    output = {
        "merged_text": result["merged_text"],
        "is_math_related": result["is_math_related"]
    }
    if "warning" in result:
        output["warning"] = result["warning"]
    return output

def summarize_node(state: dict, tokenizer=None, llm_model=None, curriculum_units=None):
    input_text = state["merged_text"]
    summary = run_exaone_summary(input_text, tokenizer, llm_model, curriculum_units)
    return {"summary": summary}

def select_topic_node(state: dict, tokenizer=None, llm_model=None, curriculum_units=None):
    summary = state["summary"]
    valid_topic = run_exaone_select(summary, tokenizer, llm_model, curriculum_units)
    return {"valid_topic": valid_topic}

def end_with_warning_node(state: dict):
    print(state.get("warning", "비정상 종료"))
    return {"valid_topic": "INVALID"}

def build_graph(tokenizer, llm_model, curriculum_units):
    builder = StateGraph(AgentState)
    builder.add_node("ocr_merge", RunnableLambda(lambda state: ocr_merge_node(state, tokenizer, llm_model)))
    builder.add_node("summarize", RunnableLambda(lambda state: summarize_node(state, tokenizer, llm_model, curriculum_units)))
    builder.add_node("select_topic", RunnableLambda(lambda state: select_topic_node(state, tokenizer, llm_model, curriculum_units)))
    builder.add_node("end_with_warning", RunnableLambda(end_with_warning_node))
    builder.set_entry_point("ocr_merge")
    builder.add_conditional_edges(
        "ocr_merge",
        lambda state: "end_with_warning" if not state.get("is_math_related", False) else "summarize"
    )
    builder.add_edge("summarize", "select_topic")
    builder.add_edge("select_topic", END)
    builder.add_edge("end_with_warning", END)
    return builder.compile() 