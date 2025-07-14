from typing import Optional, Dict, Any, List
from langgraph.graph import StateGraph, END

from configs import MODEL_NAME
from states import GeometryState
from nodes import (
    classify_sections,
    activate_nodes_by_state,
    generate_code_node,
    generate_comments_node,
    generate_formulas_node,
    merge_hints
)   

class GeometryAgent():
    def __init__(self):
        self.agent = self.build_graph()
        
    def build_graph(self):
        graph = StateGraph(GeometryState)

        # 노드 등록
        graph.add_node("extract_sections_info", classify_sections)
        graph.add_node("generate_code", generate_code_node)
        graph.add_node("generate_comments", generate_comments_node)
        graph.add_node("generate_formulas", generate_formulas_node)
        graph.add_node("aggregate_hints", merge_hints)

         # 엣지 연결
        graph.set_entry_point("extract_sections_info")
        graph.add_conditional_edges(
            "extract_sections_info",
            activate_nodes_by_state,
            {
                "generate_code": "generate_code",
                "generate_comments": "generate_comments",
                "generate_formulas": "generate_formulas",
            }
        )
        graph.add_edge("generate_code", "aggregate_hints")
        graph.add_edge("generate_comments", "aggregate_hints")
        graph.add_edge("generate_formulas", "aggregate_hints")
        graph.add_edge("aggregate_hints", END)

        # 그래프 완성
        agent = graph.compile()

        return agent

    def run(self, section: str):
        result = self.agent.invoke({"input_section": section})

        return result
