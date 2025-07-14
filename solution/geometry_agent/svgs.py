import math
import random
from typing import Optional, Dict, Any, List

def gen_lines_prototype(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    곧은선(선분, 반직선, 직선)의 prototype을 그리는 코드 문자열을 생성합니다.

    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자
    
    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2
    
    x0, y0 = svg_frame // 4, svg_frame // 4
    x1, y1 = svg_frame // 4, svg_frame // 2
    x2, y2 = svg_frame // 4, (svg_frame * 3) // 4

    distance = svg_frame // 2

    svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
    <text x="{svg_frame // 2}" y="{svg_frame // 20}" font-size="{svg_frame // 20}" text-anchor="middle">곧은선</text>
    <text x="{svg_frame // 2}" y="{(svg_frame * 4) // 20}" font-size="{svg_frame // 20}" text-anchor="middle">선분</text>
    <!-- 선분 -->
    <circle cx="{x0}" cy="{y0}" r="1" stroke="{stroke}" stroke-width="{stroke_width}" fill="black" />
    <circle cx="{x0 + distance}" cy="{y0}" r="1" stroke="{stroke}" stroke-width="{stroke_width}" fill="black" />
    <line x1="{x0}" y1="{y0}" x2="{x0 + distance}" y2="{y0}" stroke="{stroke}" stroke-width="{stroke_width}" />
    <!-- 반직선 -->
    <text x="{svg_frame // 2}" y="{(svg_frame * 9) // 20}" font-size="{svg_frame // 20}" text-anchor="middle">반직선</text>
    <circle cx="{x1}" cy="{y1}" r="1" stroke="{stroke}" stroke-width="{stroke_width}" fill="black" />
    <circle cx="{x1 + distance}" cy="{y1}" r="1" stroke="{stroke}" stroke-width="{stroke_width}" fill="black" />
    <line x1="{x1}" y1="{y1}" x2="{svg_frame}" y2="{y1}" stroke="{stroke}" stroke-width="{stroke_width}" />
    <!-- 직선 -->
    <text x="{svg_frame // 2}" y="{(svg_frame * 14) // 20}" font-size="{svg_frame // 20}" text-anchor="middle">직선</text>
    <circle cx="{x2}" cy="{y2}" r="1" stroke="{stroke}" stroke-width="{stroke_width}" fill="black" />
    <circle cx="{x2 + distance}" cy="{y2}" r="1" stroke="{stroke}" stroke-width="{stroke_width}" fill="black" />
    <line x1="0" y1="{y2}" x2="{svg_frame}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}" />
    </svg>
    '''
    
    return svg_content

def gen_curves_prototype(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    굽은선(곡선)의 prototype을 그리는 코드 문자열을 생성합니다.

    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2
    
    svg_content = f'''
    <svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
    <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">굽은선</text>
    <!-- 복잡한 S자 곡선 (두 개의 Cubic Bézier) -->
    <path d="M {svg_frame // 5},{(svg_frame * 4) // 5}
    C {svg_frame // 5},{svg_frame // 5} {(svg_frame * 4) // 5},{svg_frame // 5} {(svg_frame * 4) // 5},{svg_frame // 2}
    C {(svg_frame * 4) // 5},{(svg_frame * 4) // 5} {svg_frame // 5},{(svg_frame * 4) // 5} {svg_frame // 5},{svg_frame // 5}"
    stroke="{stroke}" fill="none" stroke-width="{stroke_width}"/>
    </svg>
    '''
    return svg_content

def gen_angle_prototype(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    기준선과 기울어진 선 + 각도를 나타내는 보조선을 그리는 코드 문자열을 생성합니다.

    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2

    if concept == "각" or concept == "각도":
        degree = parameters.get("size") if (parameters is not None) and (parameters.get("size") is not None) else random.randint(1, 179)
    elif concept == "예각":
        degree = parameters.get("size") if (parameters is not None) and (parameters.get("size") is not None) else random.randint(1, 89)
    elif concept == "둔각":
        degree = parameters.get("size") if (parameters is not None) and (parameters.get("size") is not None) else random.randint(91, 179)
    else:
        degree = parameters.get("size") if (parameters is not None) and (parameters.get("size") is not None) else 90
    
    # 기준점
    x0, y0 = svg_frame // 4 if degree <= 90 else svg_frame // 2, (svg_frame * 2) // 3

    # 기준선 끝점 (수평)
    line_length = svg_frame // 2
    x1 = x0 + line_length
    y1 = y0

    # 기울어진 선 끝점
    rad = math.radians(degree)
    x2 = x0 + line_length * math.cos(-rad)
    y2 = y0 + line_length * math.sin(-rad)

    if degree != 90:
        # 호의 시작점 (반지름만큼 떨어진 점)
        arc_radius = svg_frame // 10
        arc_start_x = x0 + arc_radius * math.cos(-rad)
        arc_start_y = y0 + arc_radius * math.sin(-rad)

        # 호의 끝점 (반지름과 각도로 계산)
        arc_end_x = x0 + arc_radius
        arc_end_y = y0

        # SVG 내용
        svg_content = f'''<svg width="{svg_frame}" height="{(svg_frame * 3) // 4}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <!-- 기준선 -->
        <line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 기울어진 선 -->
        <line x1="{x0}" y1="{y0}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 각도 호 -->
        <path d="M {arc_start_x},{arc_start_y} A {arc_radius},{arc_radius} 0 0,1 {arc_end_x},{arc_end_y}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        <!-- 보조선 -->
        <text x="{x0 + arc_radius * 1.25 * math.cos(-rad / 2)}" y="{y0 + arc_radius * 1.25 * math.sin(-rad / 2)}" font-size="{svg_frame // 40}" text-anchor="middle">{degree}°</text>
        </svg>
        '''
    else:
        # 직각 보조선
        epsilon = svg_frame // 10

        h1 = x2 + epsilon
        h2 = y0 - epsilon

        # SVG 내용
        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <!-- 기준선 -->
        <line x1="{x0 - epsilon}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 기울어진 선 -->
        <line x1="{x2}" y1="{y0}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 직각 보조선 -->
        <polyline points="{h1}, {y0} {h1}, {h2} {x2} {h2}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        </svg>
        '''

    return svg_content

def gen_acute_obtuse_angles_prototype(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    예각과 둔각의 prototype을 그리는 코드 문자열을 생성합니다.

    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2

    acute_deg = random.randint(1, 89) # 예각
    obtuse_deg = random.randint(91, 179) # 둔각

    # 기준점
    x_acute_0, y_acute_0 = svg_frame // 3, (svg_frame * 2) // 5
    x_obtuse_0, y_obtuse_0 = svg_frame // 2, (svg_frame * 4) // 5

    # 기준선 끝점 (수평)
    line_length = svg_frame // 4
    x_acute_1, y_acute_1 = x_acute_0 + line_length, y_acute_0
    x_obtuse_1, y_obtuse_1 = x_obtuse_0 + line_length, y_obtuse_0

    # 기울어진 선 끝점
    acute_rad, obtuse_rad = math.radians(acute_deg), math.radians(obtuse_deg)
    x_acute_2, y_acute_2 = x_acute_0 + line_length * math.cos(-acute_rad), y_acute_0 + line_length * math.sin(-acute_rad)
    x_obtuse_2, y_obtuse_2 = x_obtuse_0 + line_length * math.cos(-obtuse_rad), y_obtuse_0 + line_length * math.sin(-obtuse_rad)
    
    # 호의 시작점 (반지름만큼 떨어진 점)
    arc_radius = svg_frame // 10
    arc_acute_start_x, arc_acute_start_y = x_acute_0 + arc_radius * math.cos(-acute_rad), y_acute_0 + arc_radius * math.sin(-acute_rad)
    arc_obtuse_start_x, arc_obtuse_start_y = x_obtuse_0 + arc_radius * math.cos(-obtuse_rad), y_obtuse_0 + arc_radius * math.sin(-obtuse_rad)

    # 호의 끝점 (반지름과 각도로 계산)
    arc_acute_end_x, arc_acute_end_y = x_acute_0 + arc_radius, y_acute_0
    arc_obtuse_end_x, arc_obtuse_end_y = x_obtuse_0 + arc_radius, y_obtuse_0

    # SVG 코드
    svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <!-- 예각 -->
        <text x="{svg_frame // 2}" y="{(svg_frame * 7) // 40}" font-size="{svg_frame // 25}" text-anchor="middle">예각</text>
        <!-- 기준선 -->
        <line x1="{x_acute_0}" y1="{y_acute_0}" x2="{x_acute_1}" y2="{y_acute_1}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 기울어진 선 -->
        <line x1="{x_acute_0}" y1="{y_acute_0}" x2="{x_acute_2}" y2="{y_acute_2}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 각도 호 -->
        <path d="M {arc_acute_start_x},{arc_acute_start_y} A {arc_radius},{arc_radius} 0 0,1 {arc_acute_end_x},{arc_acute_end_y}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        <!-- 보조선 -->
        <text x="{x_acute_0 + arc_radius * 1.25 * math.cos(-acute_rad / 2)}" y="{y_acute_0 + arc_radius * 1.25 * math.sin(-acute_rad / 2)}" font-size="{svg_frame // 40}" text-anchor="middle">{acute_deg}°</text>
        <!-- 둔각 -->
        <text x="{svg_frame // 2}" y="{(svg_frame * 21) // 40}" font-size="{svg_frame // 25}" text-anchor="middle">둔각</text>
        <!-- 기준선 -->
        <line x1="{x_obtuse_0}" y1="{y_obtuse_0}" x2="{x_obtuse_1}" y2="{y_obtuse_1}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 기울어진 선 -->
        <line x1="{x_obtuse_0}" y1="{y_obtuse_0}" x2="{x_obtuse_2}" y2="{y_obtuse_2}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 각도 호 -->
        <path d="M {arc_obtuse_start_x},{arc_obtuse_start_y} A {arc_radius},{arc_radius} 0 0,1 {arc_obtuse_end_x},{arc_obtuse_end_y}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        <!-- 보조선 -->
        <text x="{x_obtuse_0 + arc_radius * 1.25 * math.cos(-obtuse_rad / 2)}" y="{y_obtuse_0 + arc_radius * 1.25 * math.sin(-obtuse_rad / 2)}" font-size="{svg_frame // 40}" text-anchor="middle">{obtuse_deg}°</text>
        </svg>
    '''
    
    return svg_content

def gen_right_triangle_prototype(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    직각삼각형의 prototype을 그리는 코드 문자열을 생성합니다.

    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2

    # 기준점
    rt_base = (svg_frame * 2) // 3
    rt_height = svg_frame // 2
    x0, y0 = svg_frame // 6, (svg_frame * 5) // 6
    x1, y1 = min(x0 + rt_base, (svg_frame * 5) // 6), y0
    x2, y2 = x1, max(y1 - rt_height, svg_frame // 3)

    epsilon = min(rt_base, rt_height) // 10

    h1 = x1 - epsilon
    h2 = y1 - epsilon
    
    # SVG 내용
    svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
    <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
    <!-- 직각삼각형 -->
    <polygon points="{x0},{y0} {x1},{y1} {x2},{y2}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
    <!-- 직각 보조선 -->
    <polyline points="{h1}, {y1} {h1}, {h2} {x1} {h2}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
    <!-- 보조선들 -->
    <path d="M {x0}, {y0} Q {(x0 + x1) // 2}, {((y0 + y1) // 2) - epsilon} {x1}, {y1}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" stroke-dasharray="5,3" />
    <text x="{(x0 + x1) // 2}" y="{((y0 + y1) // 2) - epsilon}" font-size="{svg_frame // 40}" text-anchor="middle">밑변</text>
    <path d="M {x1}, {y1} Q {((x1 + x2) // 2) - epsilon}, {(y1 + y2) // 2} {x2}, {y2}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" stroke-dasharray="5,3" />
    <text x="{((x1 + x2) // 2) - 1.2 * epsilon}" y="{(y1 + y2) // 2}" font-size="{svg_frame // 40}" text-anchor="middle">높이</text>
    <path d="M {x0}, {y0} Q {((x0 + x2) // 2) - epsilon}, {(y0 + y2) // 2 - epsilon} {x2}, {y2}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" stroke-dasharray="5,3" />
    <text x="{((x0 + x2) // 2) - 1.2 * epsilon}" y="{(y0 + y2) // 2 - epsilon}" font-size="{svg_frame // 40}" text-anchor="middle">빗변</text>
    </svg>
    '''
    return svg_content

def gen_rectangle_prototype(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    직사각형/정사각형의 prototype을 그리는 코드 문자열을 생성합니다.

    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2
    fill="none"

    x = svg_frame // 5
    y = svg_frame // 5
    if concept == "정사각형":
        r_width = (svg_frame * 3) // 5
        r_height = r_width
        svg_height = svg_frame
    else:
        r_width = (svg_frame * 3) // 5
        r_height = r_width // 2
        svg_height = min(500, ((y + r_height) * 5) // 4)

    # 사각형이 가로로 중앙에 위치하도록
    x = (svg_frame - r_width) // 2

    # 직사각형, 정사각형에 따른 용어 변경
    if concept == "정사각형":
        base_term = "한변"
        height_term = "한변"
    else:
        base_term = "밑변"
        height_term = "높이"

    epsilon = min(r_width, r_height) // 5
    
    # svg_width = x + width + x, svg_height = y + height + y
    svg_content = f'''<svg width="{svg_frame}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
    <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
    <rect x="{x}" y="{y}" width="{r_width}" height="{r_height}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />
    <!-- 보조선들 -->
    <path d="M {x}, {y + r_height} Q {x + (r_width // 2)}, {y + r_height - epsilon} {x + r_width}, {y + r_height}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" stroke-dasharray="5,3" />
    <text x="{x + (r_width // 2)}" y="{y + r_height - epsilon}" font-size="{svg_frame // 40}" text-anchor="middle">{base_term}</text>
    <path d="M {x + r_width}, {y} Q {x + r_width - epsilon}, {y + (r_height // 2)} {x + r_width}, {y + r_height}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" stroke-dasharray="5,3" />
    <text x="{x + r_width - epsilon}" y="{y + (r_height // 2)}" font-size="{svg_frame // 40}" text-anchor="middle">{height_term}</text>
    <polyline points="{x + r_width}, {y + r_height - epsilon} {x + r_width - epsilon}, {y + r_height - epsilon} {x + r_width - epsilon} {y + r_height}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
    </svg>'''
    return svg_content

def gen_circle_prototype(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    원의 prototype을 그리는 코드 문자열을 생성합니다.
    
    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2
    fill="none"
    
    cx = svg_frame // 2
    cy = cx
    r = svg_frame // 3

    # SVG 코드
    svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
    <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">원</text>
    <circle cx="{cx}" cy="{cy}" r="{r}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />
    <circle cx="{cx}" cy="{cy}" r="{r // 50}" stroke="{stroke}" stroke-width="{stroke_width}" fill="black" />
    <line x1="{cx - r}" y1="{cy}" x2="{cx + r}" y2="{cy}" stroke="{stroke}" stroke-width="{stroke_width}" />
    <!-- 보조선 -->
    <path d="M {cx}, {cy} Q {cx + (r // 2)}, {cy - (r // 6)} {cx + r}, {cy}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" stroke-dasharray="5,3" />
    <text x="{cx + (r // 2)}" y="{cy - (r // 6)}" font-size="{svg_frame // 40}" text-anchor="middle">반지름</text>
    <path d="M {cx - r}, {cy} Q {cx}, {cy + (r // 6)} {cx + r}, {cy}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" stroke-dasharray="5,3" />
    <text x="{cx}" y="{cy + (r // 4)}" font-size="{svg_frame // 40}" text-anchor="middle">지름</text>
    </svg>
    '''

    return svg_content

def gen_flower_by_circles(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    원의 prototype을 그리는 코드 문자열을 생성합니다.
    
    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2
    fill="none"

    # 꽃 그리기
    cx, cy = svg_frame // 2, svg_frame // 2
    cr = svg_frame // 14

    radius = svg_frame // 7

    # SVG 코드
    svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
    <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
    <circle cx="{cx}" cy="{cy}" r="{cr}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />
    <circle cx="{cx + (cr + radius)}" cy="{cy}" r="{radius}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />
    <circle cx="{cx - (cr + radius)}" cy="{cy}" r="{radius}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />
    <circle cx="{cx}" cy="{cy - (cr + radius)}" r="{radius}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />
    <circle cx="{cx}" cy="{cy + (cr + radius)}" r="{radius}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />
    </svg>
    '''

    return svg_content

def gen_triangles_by_length(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    변의 길이에 따른 삼각형(이등변삼각형, 정삼각형)의 prototype을 그리는 코드 문자열을 생성합니다.
    
    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2
    fill="none"

    # 이등변삼각형
    isosceles_rad = math.pi / 6
    isosceles_lateral = svg_frame // 2
    isosceles_x0, isosceles_y0 = svg_frame // 4, svg_frame // 4
    isosceles_x1, isosceles_y1 = isosceles_x0 + isosceles_lateral * math.cos((math.pi - isosceles_rad) / 2), isosceles_y0 + isosceles_lateral * math.sin((math.pi - isosceles_rad) / 2)
    isosceles_x2, isosceles_y2 = isosceles_x0 + isosceles_lateral * math.cos((math.pi + isosceles_rad) / 2), isosceles_y0 + isosceles_lateral * math.sin((math.pi + isosceles_rad) / 2)

    isosceles_epsilon = isosceles_lateral // 10
    isosceles_same_tick = isosceles_lateral // 30

    # 정삼각형
    equilateral_rad = math.pi / 3
    equilateral_lateral = svg_frame // 2
    equilateral_x0, equilateral_y0 = (svg_frame * 3) // 4, svg_frame // 4
    equilateral_x1, equilateral_y1 = equilateral_x0 + equilateral_lateral * math.cos(equilateral_rad), equilateral_y0 + equilateral_lateral * math.sin(equilateral_rad)
    equilateral_x2, equilateral_y2 = equilateral_x0 + equilateral_lateral * math.cos(2 * equilateral_rad), equilateral_y0 + equilateral_lateral * math.sin(2 * equilateral_rad)

    equilateral_epsilon = equilateral_lateral // 10
    equilateral_same_tick = equilateral_lateral // 30
    
    # SVG 코드
    svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
    <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
    <!-- 아등변삼각형 -->
    <text x="{svg_frame // 4}" y="{svg_frame // 5}" font-size="{svg_frame // 25}" text-anchor="middle">이등변삼각형</text>
    <polygon points="{isosceles_x0},{isosceles_y0} {isosceles_x1},{isosceles_y1} {isosceles_x2},{isosceles_y2}" stroke="{stroke}"
    stroke-width="{stroke_width}" fill="none"/>
    <!-- 보조선들 -->
    <line x1="{(isosceles_x0 + isosceles_x1) / 2 - isosceles_same_tick * math.cos((math.pi - isosceles_rad) / 2 + math.pi / 2)}"
    y1="{(isosceles_y0 + isosceles_y1) / 2 - isosceles_same_tick * math.sin((math.pi - isosceles_rad) / 2 + math.pi / 2)}"
    x2="{(isosceles_x0 + isosceles_x1)/ 2 + isosceles_same_tick * math.cos((math.pi - isosceles_rad) / 2 + math.pi / 2)}"
    y2="{(isosceles_y0 + isosceles_y1) / 2 + isosceles_same_tick * math.sin((math.pi - isosceles_rad) / 2 + math.pi / 2)}"
    stroke="{stroke}" stroke-width="{stroke_width}" />
    <line x1="{(isosceles_x0 + isosceles_x2) / 2 - isosceles_same_tick * math.cos((math.pi + isosceles_rad) / 2 + math.pi / 2)}"
    y1="{(isosceles_y0 + isosceles_y2) / 2 - isosceles_same_tick * math.sin((math.pi + isosceles_rad) / 2 + math.pi / 2)}"
    x2="{(isosceles_x0 + isosceles_x2)/ 2 + isosceles_same_tick * math.cos((math.pi + isosceles_rad) / 2 + math.pi / 2)}"
    y2="{(isosceles_y0 + isosceles_y2) / 2 + isosceles_same_tick * math.sin((math.pi + isosceles_rad) / 2 + math.pi / 2)}"
    stroke="{stroke}" stroke-width="{stroke_width}" />
    
    <!-- 정삼각형 -->
    <text x="{(svg_frame * 3) // 4}" y="{svg_frame // 5}" font-size="{svg_frame // 25}" text-anchor="middle">정삼각형</text>
    <polygon points="{equilateral_x0},{equilateral_y0} {equilateral_x1},{equilateral_y1} {equilateral_x2},{equilateral_y2}" stroke="{stroke}"
    stroke-width="{stroke_width}" fill="none"/>
    <!-- 보조선들 -->
    <line x1="{(equilateral_x0 + equilateral_x1) / 2 - equilateral_same_tick * math.cos(equilateral_rad + math.pi / 2)}"
    y1="{(equilateral_y0 + equilateral_y1) / 2 - equilateral_same_tick * math.sin(equilateral_rad + math.pi / 2)}"
    x2="{(equilateral_x0 + equilateral_x1)/ 2 + equilateral_same_tick * math.cos(equilateral_rad + math.pi / 2)}"
    y2="{(equilateral_y0 + equilateral_y1) / 2 + equilateral_same_tick * math.sin(equilateral_rad + math.pi / 2)}"
    stroke="{stroke}" stroke-width="{stroke_width}" />
    <line x1="{(equilateral_x1 + equilateral_x2) / 2 - equilateral_same_tick * math.cos(math.pi / 2)}"
    y1="{(equilateral_y1 + equilateral_y2) / 2 - equilateral_same_tick * math.sin(math.pi / 2)}"
    x2="{(equilateral_x1 + equilateral_x2) / 2 + equilateral_same_tick * math.cos(math.pi / 2)}"
    y2="{(equilateral_y1 + equilateral_y2) / 2 + equilateral_same_tick * math.sin(math.pi / 2)}"
    stroke="{stroke}" stroke-width="{stroke_width}" />
    <line x1="{(equilateral_x0 + equilateral_x2) / 2 - equilateral_same_tick * math.cos(2 * equilateral_rad + math.pi / 2)}"
    y1="{(equilateral_y0 + equilateral_y2) / 2 - equilateral_same_tick * math.sin(2 * equilateral_rad + math.pi / 2)}"
    x2="{(equilateral_x0 + equilateral_x2) / 2 + equilateral_same_tick * math.cos(2 * equilateral_rad + math.pi / 2)}"
    y2="{(equilateral_y0 + equilateral_y2) / 2 + equilateral_same_tick * math.sin(2 * equilateral_rad + math.pi / 2)}"
    stroke="{stroke}" stroke-width="{stroke_width}" />
    </svg>
    '''

    return svg_content

def gen_isosceles_prototype(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    이등변삼각형과 정삼각형의 prototype을 그리는 코드 문자열을 생성합니다.
    
    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2
    fill="none"

    if concept == "정삼각형":
        # 정삼각형
        rad = math.pi / 3
        lateral = svg_frame // 2
        x0, y0 = svg_frame // 2, svg_frame // 4
        x1, y1 = x0 + lateral * math.cos(rad), y0 + lateral * math.sin(rad)
        x2, y2 = x0 + lateral * math.cos(2 * rad), y0 + lateral * math.sin(2 * rad)

        epsilon = lateral // 10
        same_tick = lateral // 30

        # SVG 내용
        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <!-- 정삼각형 -->
        <polygon points="{x0},{y0} {x1},{y1} {x2},{y2}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        <!-- 보조선들 -->
        <path d="M {x0}, {y0} Q {(x0 + x1) / 2 + epsilon}, {((y0 + y1) / 2) - epsilon} {x1}, {y1}" fill="none" stroke="{stroke}"
        stroke-width="{stroke_width}" stroke-dasharray="5,3" />
        <text x="{(x0 + x1) / 2 + 1.5 * epsilon}" y="{((y0 + y1) / 2) - epsilon}" font-size="{svg_frame // 40}" text-anchor="middle">한변</text>
        <line x1="{(x0 + x1) / 2 - same_tick * math.cos(rad + math.pi / 2)}" y1="{(y0 + y1) / 2 - same_tick * math.sin(rad + math.pi / 2)}"
        x2="{(x0 + x1)/ 2 + same_tick * math.cos(rad + math.pi / 2)}" y2="{(y0 + y1) / 2 + same_tick * math.sin(rad + math.pi / 2)}"
        stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{(x1 + x2) / 2 - same_tick * math.cos(math.pi / 2)}" y1="{(y1 + y2) / 2 - same_tick * math.sin(math.pi / 2)}"
        x2="{(x1 + x2) / 2 + same_tick * math.cos(math.pi / 2)}" y2="{(y1 + y2) / 2 + same_tick * math.sin(math.pi / 2)}"
        stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{(x0 + x2) / 2 - same_tick * math.cos(2 * rad + math.pi / 2)}" y1="{(y0 + y2) / 2 - same_tick * math.sin(2 * rad + math.pi / 2)}"
        x2="{(x0 + x2) / 2 + same_tick * math.cos(2 * rad + math.pi / 2)}" y2="{(y0 + y2) / 2 + same_tick * math.sin(2 * rad + math.pi / 2)}"
        stroke="{stroke}" stroke-width="{stroke_width}" />
        <path d="M {x0 + epsilon * math.cos(rad)},{y0 + epsilon * math.sin(rad)} A {epsilon},{epsilon} 0 0,1
        {x0 + epsilon * math.cos(2 * rad)},{y0 + epsilon * math.sin(2 * rad)}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        <path d="M {x1 - epsilon},{y2} A {epsilon},{epsilon} 0 0,1
        {x1 + epsilon * math.cos(-(math.pi + rad) / 2)},{y1 + epsilon * math.sin(-(math.pi + rad) / 2)}"
        stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        <path d="M {x2 + epsilon * math.cos(-math.pi/3)},{y2 + epsilon * math.sin(-math.pi/3)} A {epsilon},{epsilon} 0 0,1
        {x2 + epsilon},{y2}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        </svg>
        '''
    else:
        # 이등변삼각형
        rad = math.pi / 6
        lateral = svg_frame // 2
        x0, y0 = svg_frame // 2, svg_frame // 4
        x1, y1 = x0 + lateral * math.cos((math.pi - rad) / 2), y0 + lateral * math.sin((math.pi - rad) / 2)
        x2, y2 = x0 + lateral * math.cos((math.pi + rad) / 2), y0 + lateral * math.sin((math.pi + rad) / 2)

        epsilon = lateral // 10
        same_tick = lateral // 30

        # SVG 내용
        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">이등변삼각형</text>
        <!-- 아등변삼각형 -->
        <polygon points="{x0},{y0} {x1},{y1} {x2},{y2}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        <!-- 보조선들 -->
        <path d="M {x0}, {y0} Q {(x0 + x1) // 2 + epsilon}, {((y0 + y1) // 2) - epsilon} {x1}, {y1}" fill="none" stroke="{stroke}"
        stroke-width="{stroke_width}" stroke-dasharray="5,3" />
        <text x="{(x0 + x1) // 2 + epsilon}" y="{((y0 + y1) // 2) - epsilon}" font-size="{svg_frame // 40}" text-anchor="middle">등변</text>
        <line x1="{(x0 + x1) / 2 - same_tick * math.cos((math.pi - rad) / 2 + math.pi / 2)}"
        y1="{(y0 + y1) / 2 - same_tick * math.sin((math.pi - rad) / 2 + math.pi / 2)}"
        x2="{(x0 + x1)/ 2 + same_tick * math.cos((math.pi - rad) / 2 + math.pi / 2)}"
        y2="{(y0 + y1) / 2 + same_tick * math.sin((math.pi - rad) / 2 + math.pi / 2)}"
        stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{(x0 + x2) / 2 - same_tick * math.cos((math.pi + rad) / 2 + math.pi / 2)}"
        y1="{(y0 + y2) / 2 - same_tick * math.sin((math.pi + rad) / 2 + math.pi / 2)}"
        x2="{(x0 + x2)/ 2 + same_tick * math.cos((math.pi + rad) / 2 + math.pi / 2)}"
        y2="{(y0 + y2) / 2 + same_tick * math.sin((math.pi + rad) / 2 + math.pi / 2)}"
        stroke="{stroke}" stroke-width="{stroke_width}" />
        <path d="M {x1 - epsilon},{y2} A {epsilon},{epsilon} 0 0,1
        {x1 + epsilon * math.cos(-(math.pi + rad) / 2)},{y1 + epsilon * math.sin(-(math.pi + rad) / 2)}"
        stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        <path d="M {x2 + epsilon * math.cos(-(math.pi - rad) / 2)},{y2 + epsilon * math.sin(-(math.pi - rad) / 2)} A {epsilon},{epsilon} 0 0,1
        {x2 + epsilon},{y2}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        </svg>
        '''
        
    return svg_content

def gen_triangles_by_angle(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    각의 크기에 따른 삼각형(예각삼각형, 직각삼각형, 둔각삼각형)의 prototype을 그리는 코드 문자열을 생성합니다.
    
    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2
    fill="none"

    # 예각삼각형
    x_acute_0, y_acute_0 = svg_frame // 6, svg_frame // 4
    x_acute_1, y_acute_1 = svg_frame // 10, (svg_frame * 4) // 5
    x_acute_2, y_acute_2 = (svg_frame * 3) // 10, (svg_frame * 4) // 5

    epsilon = svg_frame // 30

    # 직각삼각형
    x_right_0, y_right_0 = (svg_frame * 2) // 5, svg_frame // 4
    x_right_1, y_right_1 = (svg_frame * 2) // 5, (svg_frame * 4) // 5
    x_right_2, y_right_2 = (svg_frame * 3) // 5, (svg_frame * 4) // 5

    # 둔각삼각형
    rad = math.radians(75)
    lateral = (svg_frame * 11) // 20
    x_obtuse_1, y_obtuse_1 = (svg_frame * 7) // 10, (svg_frame * 4) // 5
    x_obtuse_2, y_obtuse_2 = (svg_frame * 5) // 6, (svg_frame * 4) // 5
    x_obtuse_0, y_obtuse_0 = x_obtuse_2 + lateral * math.cos(-rad), y_obtuse_2 + lateral * math.sin(-rad)

    svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
    <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
    <!-- 예각삼각형 -->
    <text x="{svg_frame // 6}" y="{svg_frame // 5}" font-size="{svg_frame // 25}" text-anchor="middle">예각삼각형</text>
    <polygon points="{x_acute_0},{y_acute_0} {x_acute_1},{y_acute_1} {x_acute_2},{y_acute_2}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
    <!-- 직각삼각형 -->
    <text x="{svg_frame // 2}" y="{svg_frame // 5}" font-size="{svg_frame // 25}" text-anchor="middle">직각삼각형</text>
    <polygon points="{x_right_0},{y_right_0} {x_right_1},{y_right_1} {x_right_2},{y_right_2}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
    <polyline points="{x_right_1 + epsilon}, {y_right_1} {x_right_1 + epsilon}, {y_right_1 - epsilon} {x_right_1} {y_right_1 - epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
    <!-- 둔각삼각형 -->
    <text x="{(svg_frame * 5) // 6}" y="{svg_frame // 5}" font-size="{svg_frame // 25}" text-anchor="middle">둔각삼각형</text>
    <polygon points="{x_obtuse_0},{y_obtuse_0} {x_obtuse_1},{y_obtuse_1} {x_obtuse_2},{y_obtuse_2}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
    <path d="M {x_obtuse_2 - epsilon},{y_obtuse_2} A {epsilon},{epsilon} 0 0,1 {x_obtuse_2 + epsilon * math.cos(-rad)},{y_obtuse_2 + epsilon * math.sin(-rad)}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
    </svg>
    '''
        
    return svg_content

def gen_acute_obtuse_triangles(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    예각삼각형, 둔각삼각형의 prototype을 그리는 코드 문자열을 생성합니다.
    
    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2
    fill="none"

    if concept == "둔각삼각형":
        x_0, y_0 = svg_frame * 3 // 4, svg_frame // 4 
        x_1, y_1 = svg_frame // 5, (svg_frame * 4) // 5
        x_2, y_2 = (svg_frame * 3) // 5, (svg_frame * 4) // 5

        rad = math.atan((y_2 - y_0) / (x_2 - x_0))
        epsilon = svg_frame // 30
        
        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <polygon points="{x_0},{y_0} {x_1},{y_1} {x_2},{y_2}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        <path d="M {x_2 - epsilon},{y_2} A {epsilon},{epsilon} 0 0,1 {x_2 + epsilon * math.cos(rad)},{y_2 + epsilon * math.sin(rad)}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        </svg>
        '''
    else:
        # 예각 삼각형
        x_0, y_0 = svg_frame // 3, svg_frame // 4 
        x_1, y_1 = svg_frame // 5, (svg_frame * 4) // 5
        x_2, y_2 = (svg_frame * 4) // 5, (svg_frame * 4) // 5
        
        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <polygon points="{x_0},{y_0} {x_1},{y_1} {x_2},{y_2}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        </svg>
        '''

    return svg_content

def gen_parallel_lines_prototype(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    평행선의 prototype을 그리는 코드 문자열을 생성합니다.
    
    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2
    fill="none"

    if "거리" in concept:
        x0, y0 = svg_frame // 4, (svg_frame * 3) // 4
        x1, y1 = x0, svg_frame // 4
        distance = svg_frame // 2

        distance_x = x0 + (distance // 3)
        epsilon = svg_frame // 15

        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <!-- 기준선 -->
        <line x1="{x0}" y1="{y0}" x2="{x0 + distance}" y2="{y0}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 기준선과 평행선 -->
        <line x1="{x1}" y1="{y1}" x2="{x1 + distance}" y2="{y1}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 거리 -->
        <line x1="{distance_x}" y1="{y0}" x2="{distance_x}" y2="{y1}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <polyline points="{distance_x + epsilon}, {y0} {distance_x + epsilon}, {y0 - epsilon} {distance_x} {y0 - epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <path d="M {distance_x}, {y0} Q {distance_x - epsilon}, {((y0 + y1) // 2)} {distance_x}, {y1}" fill="none" stroke="{stroke}"
        stroke-width="{stroke_width}" stroke-dasharray="5,3" />
        <text x="{distance_x - epsilon}" y="{((y0 + y1) // 2)}" font-size="{svg_frame // 40}" text-anchor="middle">거리</text>
        </svg>
        '''
        pass
    else: # 평행선
        x0, y0 = svg_frame // 4, (svg_frame * 3) // 4
        y1 = svg_frame // 2
        y2 = svg_frame // 4
        distance = svg_frame // 2

        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <!-- 기준선 -->
        <line x1="{x0}" y1="{y0}" x2="{x0 + distance}" y2="{y0}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 기준선과 평행선들 -->
        <line x1="{x0}" y1="{y1}" x2="{x0 + distance}" y2="{y1}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x0}" y1="{y2}" x2="{x0 + distance}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}" />
        </svg>
        '''

        # Animation - Flutter에서 지원 안 해서 불가능함
        # svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        # <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        # <!-- 기준선 -->
        # <line x1="{x0}" y1="{y0}" x2="{x0 + distance}" y2="{y0}" stroke="{stroke}" stroke-width="{stroke_width}" />
        # <!-- 움직이는 선: 그룹에 애니메이션 -->
        # <g>
        # <line x1="{x0}" y1="{y0}" x2="{x0 + distance}" y2="{y0}" stroke="{stroke}" stroke-width="{stroke_width}" />
        # <animateTransform attributeName="transform" type="translate" from="0 0" to="0 {y1 - y0}" dur="4s" repeatCount="indefinite" />
        # </g>
        # <!-- 기준선과 평행선 -->
        # <line x1="{x0}" y1="{y1}" x2="{x0 + distance}" y2="{y1}" stroke="{stroke}" stroke-width="{stroke_width}" />
        # </svg>
        # '''

    return svg_content

def gen_rectangle_property(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    직사각형, 정사각형의 성질의 prototype을 그리는 코드 문자열을 생성합니다.
    
    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2
    fill="none"

    if "직사각형/정사각형" in concept:
        # 직사각형
        r_width = (svg_frame * 3) // 10
        r_height = r_width * 2

        # 직사각형의 위치하도록
        r_x, r_y = (svg_frame - r_width) // 5, svg_frame // 4

        # 정사각형
        s_width = (svg_frame * 3) // 10
        s_height = s_width

        # 정사각형의 위치
        s_x, s_y = (svg_frame + s_width) // 2, svg_frame // 4

        epsilon = min(r_width, r_height) // 8
        same_tick = epsilon // 3
        tick_interval = same_tick // 2
        
        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <!-- 직사각형 -->
        <text x="{svg_frame * 7 // 24}" y="{svg_frame // 5}" font-size="{svg_frame // 25}" text-anchor="middle">직사각형</text>
        <rect x="{r_x}" y="{r_y}" width="{r_width}" height="{r_height}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />
        <!-- 직각 보조선들 -->
        <polyline points="{r_x + epsilon}, {r_y} {r_x + epsilon}, {r_y + epsilon} {r_x} {r_y + epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <polyline points="{r_x + r_width - epsilon}, {r_y} {r_x + r_width - epsilon}, {r_y + epsilon} {r_x + r_width} {r_y + epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <polyline points="{r_x + epsilon}, {r_y + r_height} {r_x + epsilon}, {r_y + r_height - epsilon} {r_x} {r_y + r_height - epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <polyline points="{r_x + r_width - epsilon}, {r_y + r_height} {r_x + r_width - epsilon}, {r_y + r_height - epsilon} {r_x + r_width} {r_y + r_height - epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" />
        <!-- 등변 보조선들 -->
        <line x1="{r_x + (r_width / 2) - tick_interval}" y1="{r_y - same_tick}" x2="{r_x + (r_width / 2) - tick_interval}" y2="{r_y + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{r_x + (r_width / 2) - tick_interval}" y1="{r_y + r_height - same_tick}" x2="{r_x + (r_width / 2) - tick_interval}" y2="{r_y + r_height + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{r_x + (r_width / 2) + tick_interval}" y1="{r_y - same_tick}" x2="{r_x + (r_width / 2) + tick_interval}" y2="{r_y + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{r_x + (r_width / 2) + tick_interval}" y1="{r_y + r_height - same_tick}" x2="{r_x + (r_width / 2) + tick_interval}" y2="{r_y + r_height + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{r_x - same_tick}" y1="{r_y + (r_height / 2)}" x2="{r_x + same_tick}" y2="{r_y + (r_height / 2)}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{r_x + r_width - same_tick}" y1="{r_y + (r_height / 2)}" x2="{r_x + r_width + same_tick}" y2="{r_y + (r_height / 2)}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 정사각형 -->
        <text x="{svg_frame * 19 // 24}" y="{svg_frame // 5}" font-size="{svg_frame // 25}" text-anchor="middle">정사각형</text>
        <rect x="{s_x}" y="{s_y}" width="{s_width}" height="{s_height}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />
        <!-- 직각 보조선들 -->
        <polyline points="{s_x + epsilon}, {s_y} {s_x + epsilon}, {s_y + epsilon} {s_x} {s_y + epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <polyline points="{s_x + s_width - epsilon}, {s_y} {s_x + s_width - epsilon}, {s_y + epsilon} {s_x + s_width} {s_y + epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <polyline points="{s_x + epsilon}, {s_y + s_height} {s_x + epsilon}, {s_y + s_height - epsilon} {s_x} {s_y + s_height - epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <polyline points="{s_x + s_width - epsilon}, {s_y + s_height} {s_x + s_width - epsilon}, {s_y + s_height - epsilon} {s_x + s_width} {s_y + s_height - epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" />
        <!-- 등변 보조선들 -->
        <line x1="{s_x + (s_width / 2) - tick_interval}" y1="{s_y - same_tick}" x2="{s_x + (s_width / 2) - tick_interval}" y2="{s_y + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{s_x + (s_width / 2) - tick_interval}" y1="{s_y + s_height - same_tick}" x2="{s_x + (s_width / 2) - tick_interval}" y2="{s_y + s_height + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{s_x + (s_width / 2) + tick_interval}" y1="{s_y - same_tick}" x2="{s_x + (s_width / 2) + tick_interval}" y2="{s_y + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{s_x + (s_width / 2) + tick_interval}" y1="{s_y + s_height - same_tick}" x2="{s_x + (s_width / 2) + tick_interval}" y2="{s_y + s_height + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{s_x - same_tick}" y1="{s_y + (s_height / 2) - tick_interval}" x2="{s_x + same_tick}" y2="{s_y + (s_height / 2) - tick_interval}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{s_x - same_tick}" y1="{s_y + (s_height / 2) + tick_interval}" x2="{s_x + same_tick}" y2="{s_y + (s_height / 2) + tick_interval}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{s_x + s_width - same_tick}" y1="{s_y + (s_height / 2) - tick_interval}" x2="{s_x + s_width + same_tick}" y2="{s_y + (s_height / 2) - tick_interval}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{s_x + s_width - same_tick}" y1="{s_y + (s_height / 2) + tick_interval}" x2="{s_x + s_width + same_tick}" y2="{s_y + (s_height / 2) + tick_interval}" stroke="{stroke}" stroke-width="{stroke_width}" />
        </svg>
        '''
    elif "정사각형" in concept:
        r_width = (svg_frame * 3) // 5
        r_height = r_width

        # 사각형이 가로로 중앙에 위치하도록
        x, y = (svg_frame - r_width) // 2, svg_frame // 5

        epsilon = min(r_width, r_height) // 8
        same_tick = epsilon // 5
        tick_interval = same_tick // 2
        
        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <rect x="{x}" y="{y}" width="{r_width}" height="{r_height}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />
        <!-- 직각 보조선들 -->
        <polyline points="{x + epsilon}, {y} {x + epsilon}, {y + epsilon} {x} {y + epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <polyline points="{x + r_width - epsilon}, {y} {x + r_width - epsilon}, {y + epsilon} {x + r_width} {y + epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <polyline points="{x + epsilon}, {y + r_height} {x + epsilon}, {y + r_height - epsilon} {x} {y + r_height - epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <polyline points="{x + r_width - epsilon}, {y + r_height} {x + r_width - epsilon}, {y + r_height - epsilon} {x + r_width} {y + r_height - epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" />
        <!-- 등변 보조선들 -->
        <line x1="{x + (r_width / 2) - tick_interval}" y1="{y - same_tick}" x2="{x + (r_width / 2) - tick_interval}" y2="{y + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x + (r_width / 2) - tick_interval}" y1="{y + r_height - same_tick}" x2="{x + (r_width / 2) - tick_interval}" y2="{y + r_height + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x + (r_width / 2) + tick_interval}" y1="{y - same_tick}" x2="{x + (r_width / 2) + tick_interval}" y2="{y + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x + (r_width / 2) + tick_interval}" y1="{y + r_height - same_tick}" x2="{x + (r_width / 2) + tick_interval}" y2="{y + r_height + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x - same_tick}" y1="{y + (r_height / 2) - tick_interval}" x2="{x + same_tick}" y2="{y + (r_height / 2) - tick_interval}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x - same_tick}" y1="{y + (r_height / 2) + tick_interval}" x2="{x + same_tick}" y2="{y + (r_height / 2) + tick_interval}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x + r_width - same_tick}" y1="{y + (r_height / 2) - tick_interval}" x2="{x + r_width + same_tick}" y2="{y + (r_height / 2) - tick_interval}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x + r_width - same_tick}" y1="{y + (r_height / 2) + tick_interval}" x2="{x + r_width + same_tick}" y2="{y + (r_height / 2) + tick_interval}" stroke="{stroke}" stroke-width="{stroke_width}" />
        </svg>
        '''
    else: # 직사각형
        r_width = (svg_frame * 3) // 5
        r_height = r_width // 2

        # 사각형이 가로로 중앙에 위치하도록
        x, y = (svg_frame - r_width) // 2, svg_frame // 5

        epsilon = min(r_width, r_height) // 8
        same_tick = epsilon // 3
        tick_interval = same_tick // 2
        
        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <rect x="{x}" y="{y}" width="{r_width}" height="{r_height}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />
        <!-- 직각 보조선들 -->
        <polyline points="{x + epsilon}, {y} {x + epsilon}, {y + epsilon} {x} {y + epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <polyline points="{x + r_width - epsilon}, {y} {x + r_width - epsilon}, {y + epsilon} {x + r_width} {y + epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <polyline points="{x + epsilon}, {y + r_height} {x + epsilon}, {y + r_height - epsilon} {x} {y + r_height - epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        <polyline points="{x + r_width - epsilon}, {y + r_height} {x + r_width - epsilon}, {y + r_height - epsilon} {x + r_width} {y + r_height - epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" />
        <!-- 등변 보조선들 -->
        <line x1="{x + (r_width / 2) - tick_interval}" y1="{y - same_tick}" x2="{x + (r_width / 2) - tick_interval}" y2="{y + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x + (r_width / 2) - tick_interval}" y1="{y + r_height - same_tick}" x2="{x + (r_width / 2) - tick_interval}" y2="{y + r_height + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x + (r_width / 2) + tick_interval}" y1="{y - same_tick}" x2="{x + (r_width / 2) + tick_interval}" y2="{y + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x + (r_width / 2) + tick_interval}" y1="{y + r_height - same_tick}" x2="{x + (r_width / 2) + tick_interval}" y2="{y + r_height + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x - same_tick}" y1="{y + (r_height / 2)}" x2="{x + same_tick}" y2="{y + (r_height / 2)}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x + r_width - same_tick}" y1="{y + (r_height / 2)}" x2="{x + r_width + same_tick}" y2="{y + (r_height / 2)}" stroke="{stroke}" stroke-width="{stroke_width}" />
        </svg>
        '''

    return svg_content

def gen_various_quadrangles_prototype(concept:str, parameters:Optional[Dict[str,Any]]=None) -> str:
    """
    사다리꼴, 평행사변형, 마름모의 prototype을 그리는 코드 문자열을 생성합니다.
    
    Parameters:
        concept (str): 수학 개념
        parameters (Optional[Dict[str, Any]]): 수학 개념의 prototype을 위한 추가 인자

    Returns:
        svg_content (str): SVG 코드 문자열
    """

    # SVG config
    svg_frame=500
    stroke="black"
    stroke_width=2
    fill="none"

    if concept == "사다리꼴":
        # 좌상단 좌표
        x0, y0 = svg_frame // 3, svg_frame // 4
        
        upper_width = svg_frame // 3
        extend = svg_frame // 6
        height = svg_frame // 2

        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <polygon points="{x0},{y0} {x0 + upper_width},{y0} {x0 + upper_width + extend},{y0 + height} {x0 - extend},{y0 + height}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        </svg>
        '''
    elif concept == "평행사변형":
        # 좌상단 좌표
        x0, y0 = svg_frame // 3, svg_frame // 4
        
        width = svg_frame // 3
        extend = svg_frame // 6
        height = svg_frame // 2

        rad = math.atan(height / extend)

        same_tick = svg_frame // 50
        tick_interval = same_tick // 4

        epsilon = svg_frame // 20
        
        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <polygon points="{x0},{y0} {x0 + width},{y0} {x0 + width - extend},{y0 + height} {x0 - extend},{y0 + height}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        <!-- 등변 보조선 -->
        <line x1="{x0 + (width / 2) - tick_interval}" y1="{y0 - same_tick}" x2="{x0 + (width / 2) - tick_interval}" y2="{y0 + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x0 + (width / 2) + tick_interval}" y1="{y0 - same_tick}" x2="{x0 + (width / 2) + tick_interval}" y2="{y0 + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x0 + (width / 2) -extend - tick_interval}" y1="{y0 + height - same_tick}" x2="{x0 + (width / 2) -extend - tick_interval}" y2="{y0 + height + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x0 + (width / 2) -extend + tick_interval}" y1="{y0 + height - same_tick}" x2="{x0 + (width / 2) -extend + tick_interval}" y2="{y0 + height + same_tick}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x0 - (extend / 2) - same_tick}" y1="{y0 + (height / 2)}" x2="{x0 - (extend / 2) + same_tick}" y2="{y0 + (height / 2)}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{x0 + width - (extend / 2) - same_tick}" y1="{y0 + (height / 2)}" x2="{x0 + width - (extend / 2) + same_tick}" y2="{y0 + (height / 2)}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 등각 보조선 -->
        <path d="M {x0 + epsilon},{y0} A {epsilon},{epsilon} 0 0,1 {x0 + epsilon * math.cos(math.pi - rad)},{y0 + epsilon * math.sin(math.pi - rad)}" stroke="red" stroke-width="{stroke_width}" fill="none"/>
        <path d="M {x0 + width - extend - epsilon},{y0 + height} A {epsilon},{epsilon} 0 0,1 {x0 + width - extend + epsilon * math.cos(-rad)},{y0 + height+ epsilon * math.sin(-rad)}" stroke="red" stroke-width="{stroke_width}" fill="none"/>
        <path d="M {x0 + width + epsilon * math.cos(math.pi - rad)},{y0 + epsilon * math.sin(math.pi - rad)} A {epsilon},{epsilon} 0 0,1 {x0 + width - epsilon},{y0}" stroke="blue" stroke-width="{stroke_width}" fill="none"/>
        <path d="M {x0 - extend + epsilon * math.cos(-rad)},{y0 + height + epsilon * math.sin(-rad)} A {epsilon},{epsilon} 0 0,1 {x0 - extend + epsilon},{y0 + height}" stroke="blue" stroke-width="{stroke_width}" fill="none"/>
        </svg>
        '''
    elif concept == "마름모":
        # 상단 꼭짓점
        tx, ty = svg_frame // 2, svg_frame // 4
        # 좌측 꼭짓점
        lx, ly = svg_frame // 6, svg_frame // 2
        # 우측 꼭짓점
        rx, ry = (svg_frame * 5) // 6, svg_frame // 2
        # 하단 꼭짓점
        bx, by = svg_frame // 2, (svg_frame * 3) // 4

        same_tick = svg_frame // 50
        rad = math.atan((ly - ty) / (tx - lx))
        epsilon = svg_frame // 25

        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <polygon points="{tx},{ty} {rx},{ry} {bx},{by} {lx},{ly}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        <!-- 등변 보조선 -->
        <line x1="{(lx + tx) / 2 - same_tick * math.cos(math.pi / 2 - rad)}" y1="{(ly + ty) / 2 - same_tick * math.sin(math.pi / 2 - rad)}" x2="{(lx + tx) / 2 + same_tick * math.cos(math.pi / 2 - rad)}" y2="{(ly + ty) / 2 + same_tick * math.sin(math.pi / 2 - rad)}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{(rx + bx) / 2 - same_tick * math.cos(math.pi / 2 - rad)}" y1="{(ry + by) / 2 - same_tick * math.sin(math.pi / 2 - rad)}" x2="{(rx + bx) / 2 + same_tick * math.cos(math.pi / 2 - rad)}" y2="{(ry + by) / 2 + same_tick * math.sin(math.pi / 2 - rad)}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{(lx + bx) / 2 - same_tick * math.cos(-rad)}" y1="{(ly + by) / 2 - same_tick * math.sin(-rad)}" x2="{(lx + bx) / 2 + same_tick * math.cos(-rad)}" y2="{(ly + by) / 2 + same_tick * math.sin(-rad)}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <line x1="{(rx + tx) / 2 - same_tick * math.cos(-rad)}" y1="{(ry + ty) / 2 - same_tick * math.sin(-rad)}" x2="{(rx + tx) / 2 + same_tick * math.cos(-rad)}" y2="{(ry + ty) / 2 + same_tick * math.sin(-rad)}" stroke="{stroke}" stroke-width="{stroke_width}" />
        <!-- 등각 보조선 -->
        <path d="M {tx + epsilon * math.cos(rad)},{ty + epsilon * math.sin(rad)} A {epsilon},{epsilon} 0 0,1 {tx + epsilon * math.cos(math.pi - rad)},{ty + epsilon * math.sin(math.pi - rad)}" stroke="red" stroke-width="{stroke_width}" fill="none"/>
        <path d="M {bx - epsilon * math.cos(rad)},{by - epsilon * math.sin(rad)} A {epsilon},{epsilon} 0 0,1 {bx - epsilon * math.cos(math.pi - rad)},{by - epsilon * math.sin(math.pi - rad)}" stroke="red" stroke-width="{stroke_width}" fill="none"/>
        <path d="M {lx + epsilon * math.cos(-rad)},{ly + epsilon * math.sin(-rad)} A {epsilon},{epsilon} 0 0,1 {lx + epsilon * math.cos(rad)},{ly + epsilon * math.sin(rad)}" stroke="blue" stroke-width="{stroke_width}" fill="none"/>
        <path d="M {rx + epsilon * math.cos(math.pi - rad)},{ry + epsilon * math.sin(math.pi - rad)} A {epsilon},{epsilon} 0 0,1 {rx + epsilon * math.cos(-math.pi + rad)},{ry + epsilon * math.sin(-math.pi + rad)}" stroke="blue" stroke-width="{stroke_width}" fill="none"/>
        <!-- 대각 보조선 -->
        <line x1="{tx}" y1="{ty}" x2="{bx}" y2="{by}" stroke="{stroke}" stroke-width="{stroke_width}" stroke-dasharray="5,3" />
        <line x1="{lx}" y1="{ly}" x2="{rx}" y2="{ry}" stroke="{stroke}" stroke-width="{stroke_width}" stroke-dasharray="5,3" />
        <polyline points="{tx + epsilon}, {ly} {tx + epsilon}, {ly - epsilon} {tx} {ly - epsilon}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" /> 
        </svg>
        '''
    else: # 일반사각형
        # 좌상단 좌표
        x0, y0 = svg_frame // 3, svg_frame // 4
        upper_width = svg_frame // 3
        extend = svg_frame // 6
        height = svg_frame // 2

        svg_content = f'''<svg width="{svg_frame}" height="{svg_frame}" xmlns="http://www.w3.org/2000/svg">
        <text x="{svg_frame // 2}" y="{svg_frame // 10}" font-size="{svg_frame // 20}" text-anchor="middle">{concept}</text>
        <polygon points="{x0},{y0} {x0 + upper_width},{y0 + extend} {x0 + upper_width + extend},{y0 + height} {x0 - extend},{y0 + height}" stroke="{stroke}" stroke-width="{stroke_width}" fill="none"/>
        </svg>
        '''

    return svg_content