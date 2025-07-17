from typing import TypedDict, Optional, Dict, Any, List

class GeometryState(TypedDict):
    input_section: str
    section_description: str
    math_concept: str = ""
    parameters: Optional[Dict[str, Any]]
    hint_type: str = "" # none, svg, formula, both
    generated_code: Optional[str]
    comments: str = ""
    formulas: Optional[Dict[str, str]]