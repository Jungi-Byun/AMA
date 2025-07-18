#---------------------------------------------------------
# LLM(Exaone) 관련 함수 (OCR merge, 요약, 단원 선택 등)
#---------------------------------------------------------

import re
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# 수정사항
# 1. OCR 병합 Prompt (run_ocr_merge)
#     명확한 역할 정의: "두 개의 OCR 결과를 비교하여 최적의 통합 텍스트를 생성하는 전문가"
#     구체적인 작업 지침: 4단계로 명확히 구분된 작업 과정
#     분석 기준 제시: 숫자/기호, 한글 텍스트, 문장 구조, 교육적 맥락 등 구체적 기준
#     출력 형식 명시: 단계별 출력 요구사항 명확화
# 2. 교안 요약 Prompt (run_exaone_summary)
#     분석 목표 명시: 체계적 분석과 핵심 요약, 단원 매칭
#     3단계 프로세스: 요약 → 1차 후보 선정 → 최종 선택
#     중요 규칙 강조: 단원명 정확성, 형식 준수 등
#     구체적 예시: 출력 형식에 명확한 예시 제공
# 3. 단원 선택 Prompt (run_exaone_select)
#     선택 기준 명확화: 개념 중심, 내용 일치도, 교육적 적합성
#     중요 규칙 강조: 정확한 단원명만 사용, 부가 설명 금지
#     구조화된 정보: 분석 정보와 후보 목록을 명확히 구분
# 4. 공통 개선사항
#     이모지 활용: 시각적 구분과 가독성 향상
#     구조화된 형식: 섹션별로 명확히 구분된 정보 제공
#     명확한 지침: 모호함을 줄이고 구체적인 요구사항 제시
#     출력 형식 표준화: JSON 형식과 예시를 명확히 제시

def run_ocr_merge(easy, paddle, tokenizer, llm_model):
    # PaddleOCR 결과가 비어있을 때 안내 문구로 대체
    if not paddle or paddle.strip() == "":
        paddle = "(PaddleOCR에서 텍스트를 인식하지 못했습니다.)"
    
    prompt = f"""당신은 두 개의 OCR 결과를 비교하여 최적의 통합 텍스트를 생성하는 전문가입니다.

## 작업 지침:
1. **정확성 우선**: 두 결과 중 더 정확하게 인식된 부분을 우선적으로 선택
2. **문맥 보완**: 한쪽에서 잘못 인식된 부분을 다른 쪽의 정확한 부분으로 보완
3. **자연스러운 수정**: 문맥에 맞지 않는 단어는 교육적 맥락에 맞게 수정
4  **최소한의 수정**: 원본 텍스트의 의미를 유지하면서 최소한의 수정만 적용
5. **과도한 확장 금지**: 원본에 없는 내용을 추가하거나 확장하지 않음
6. **수학 교육 내용 확인**: 최종 결과가 초등 수학 교육과 관련된 내용인지 판단

## 특별 지침 (한쪽 OCR 결과가 없는 경우):
- EasyOCR 또는 PaddleOCR 중 한쪽에서 텍스트를 인식하지 못한 경우, 인식된 결과만을 기반으로 분석
- 해당 OCR 결과가 수학 교육과 관련된 내용이라면 적절히 정리하여 통합 텍스트 생성
- 수학 관련 키워드나 내용이 있으면 수학 교육 관련으로 판단

## 분석 기준:
- **숫자와 기호**: 수학 문제의 숫자, 연산자, 기호의 정확성
- **한글 텍스트**: 수학 용어와 설명 텍스트의 정확성
- **문장 구조**: 교육 자료로서의 자연스러운 문장 구성
- **교육적 맥락**: 초등 수학 교과서나 학습 자료의 특성 반영

## 출력 형식:
1. **통합 텍스트**: 두 OCR 결과를 비교하여 최적화된 하나의 텍스트로 통합
2. **수학 관련성 판단**: 최종 결과가 초등 수학 교육과 관련된 내용인지 판단
   - `"yes"`: 수학 교육 관련 내용
   - `"no"`: 수학 교육과 무관한 내용
3. **JSON 출력**: 반드시 마지막에 JSON 형식으로 결과 출력

### EasyOCR 결과:
{easy}

### PaddleOCR 결과:
{paddle}

### 최종 통합 결과:
[여기에 통합된 텍스트를 작성하세요]

### 수학 관련성 판단:
```json
{{"is_math_related": "yes"}}
```

**중요**: 반드시 마지막에 JSON 블록을 포함해야 합니다!
"""
    messages = [
        {"role": "system", "content":"당신은 두 개의 OCR 결과(EasyOCR와 PaddleOCR)를 비교하여, 최대한 정확하고 자연스러운 하나의 통합된 텍스트를 생성하는 전문 AI입니다."},
        {"role": "user", "content": prompt}
    ]
    input_ids = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    )
    output_ids = llm_model.generate(
        input_ids.to("cuda"),
        eos_token_id=tokenizer.eos_token_id,
        max_new_tokens=1024,
        do_sample=False,
    )
    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    result = output_text.split("[|assistant|]")[-1].strip() # assistant 이후 실제 답변
    
    # JSON 블록 찾기 시도
    match = re.search(r'```json\s*(\{.*?\})\s*```', result, re.DOTALL)
    is_math_related = True  # 기본값을 True로 설정
    
    if match:
        try:
            json_data = json.loads(match.group(1))
            is_math_related_str = json_data.get("is_math_related", "yes")
            is_math_related = is_math_related_str.lower() == "yes"
        except Exception as e:
            print(f"JSON 파싱 오류: {e}, 기본값 사용")
            is_math_related = True
    else:
        # JSON 블록이 없으면 키워드 기반으로 수학 관련성 판단
        math_keywords = ['수학', '사각형', '직사각형', '정사각형', '평행사변형', '마름모', '사다리꼴', 
                        '각', '변', '평행', '직각', '도형', '기하', '측정', '계산', '문제', '활동']
        # curriculum_units.json에서 키워드 추가
        try:
            from config import load_curriculum_units
            curriculum_units = load_curriculum_units()
            for unit in curriculum_units:
                for kw in unit.get('keywords', []):
                    if kw not in math_keywords:
                        math_keywords.append(kw)
        except Exception as e:
            print(f"curriculum_units.json에서 키워드 추가 중 오류: {e}")
        text_lower = result.lower()
        is_math_related = any(keyword in text_lower for keyword in math_keywords)
        print(f"JSON 블록을 찾을 수 없어 키워드 기반+curriculum_units로 수학 관련성 판단: {is_math_related}")
    
    # JSON 블록 제거
    merged_text = re.sub(r'```json\s*\{.*?\}\s*```', '', result, flags=re.DOTALL).strip()
    merged_text = re.sub(r'### JSON 결과:?', '', merged_text).strip()
    if not is_math_related:
        return {
            "merged_text": merged_text,
            "is_math_related": False,
            "warning": "수학 관련 내용이 아닙니다. 그래프를 종료합니다."
        }
    else:
        return {
            "merged_text": merged_text,
            "is_math_related": True
        }

def run_exaone_summary(text, tokenizer, llm_model, curriculum_units):
    curriculum_titles = "\n".join(item["title"] for item in curriculum_units)
    prompt = f"""당신은 초등학교 수학 교육 자료를 분석하는 전문 AI입니다.

## 분석 목표:
교안 내용을 체계적으로 분석하여 핵심을 요약하고, 가장 관련성 높은 수학 단원을 찾아내는 것입니다.

## 분석 프로세스:

### 1단계: 교안 내용 요약
- **핵심 개념 추출**: 수학적 원리, 정의, 개념, 또는 주요 활동
- **학습 목표 파악**: 학생이 이 수업을 통해 달성해야 할 구체적인 목표
- **교육적 맥락 이해**: 초등 수학 교육의 특성과 난이도 고려

### 2단계: 단원 매칭 (1차 후보 선정)
- 제공된 단원 목록에서 **제목 기반 유사도**로 상위 5개 선정
- 키워드 매칭과 의미적 유사성을 종합적으로 고려
- **정확한 단원명만** 사용 (부가 설명 없이)

### 3단계: 최종 단원 선택
- 1차 후보 5개 중에서 **내용 기반 유사도**로 최종 1개 선택
- **개념 중심 단원**을 우선적으로 고려 (활동 중심보다 개념 설명이 더 적절)
- 교안의 핵심 내용과 가장 밀접한 단원 선택

## 중요 규칙:
- 단원명은 반드시 제공된 목록에서 정확히 일치하는 이름만 사용
- 부가 설명, 괄호, 줄바꿈 등은 포함하지 않음
- 출력 형식을 정확히 준수

### 교안 원문:
{text}

### 초등 수학 단원 목록:
{curriculum_titles}

### 출력 형식:
1. 요약 내용:
- 핵심 개념: [수학적 개념이나 원리]
- 학습 목표: [구체적인 학습 목표]

2. 1차 후보 단원 (상위 5개):
```json
{{
  "topic_1st": "단원명",
  "topic_2st": "단원명", 
  "topic_3st": "단원명",
  "topic_4st": "단원명",
  "topic_5st": "단원명"
}}
```

3. 최종 선택 단원:
```json
{{
  "most_relevant_topic": "단원명"
}}
```
"""
    messages = [
        {"role": "system", "content": "당신은 초등학교 교육자료를 잘 요약해 주는 유능한 AI입니다."},
        {"role": "user", "content": prompt}
    ]
    input_ids = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
            )
    output_ids = llm_model.generate(
        input_ids.to("cuda"),
        eos_token_id=tokenizer.eos_token_id,
        max_new_tokens=512,
        do_sample=False,
        )
    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    if "[|assistant|]" in output_text:
        result = output_text.split("[|assistant|]")[-1].strip()
        return result
    return output_text.strip()

def run_exaone_select(summary_text, tokenizer, llm_model, curriculum_units):
    core_concept_match = re.search(
        r"-\s*\*?\*?핵심 개념\*?\*?\s*:\s*(.+?)(?=\n\s*-\s*\*?\*?학습 목표\*?\*?\s*:)",
        summary_text,
        re.DOTALL,
    )
    objective_match = re.search(
        r"-\s*\*?\*?학습 목표\*?\*?\s*:\s*(.+?)(?=\n\s*\d+\.|\n\s*```|\Z)",
        summary_text,
        re.DOTALL,
    )
    if not core_concept_match or not objective_match:
        return ""
    core_concept = core_concept_match.group(1).strip()
    objective = objective_match.group(1).strip()
    candidate_titles = []
    for i in range(1, 6):
        pattern = rf'"topic_{i}st"\s*:\s*"([^"]+)"'
        match = re.search(pattern, summary_text)
        if match:
            candidate_titles.append(match.group(1))
    title2item = {item["title"]: item for item in curriculum_units}
    valid_candidates = []
    candidate_descriptions = []
    for title in candidate_titles:
        item = title2item.get(title)
        if item:
            keywords = ", ".join(item.get("keywords", []))
            examples = ", ".join(item.get("examples", []))
            description = (
                f"{item['title']}\n"
                f"핵심 개념: {item['core_concept']}\n"
                f"학습 목표: {item['objective']}\n"
                f"키워드: {keywords}\n"
                f"예시: {examples}\n"
            )
            valid_candidates.append(item["title"])
            candidate_descriptions.append(description)
    if not valid_candidates:
        return ""
    curriculum_titles_text = "\n".join(f"- {desc}" for desc in candidate_descriptions)
    prompt = f"""당신은 초등 수학 교육 내용을 분석하여 가장 적합한 단원을 선택하는 전문가입니다.

## 선택 기준:
1. **개념 중심 우선**: 단순한 활동보다는 수학적 개념이나 정의를 설명하는 단원 선택
2. **내용 일치도**: 핵심 개념과 학습 목표, 키워드, 예시가 가장 잘 일치하는 단원 선택
3. **교육적 적합성**: 초등 수학 교육의 특성과 난이도에 적합한 단원 선택
4. **성질 우선 선택**: 만약 분석 정보(핵심 개념, 학습 목표, 키워드, 예시)에 '성질'이라는 단어가 포함되어 있으면 , 성질이 포함된 단원명을 우선적으로 선택

## 분석 정보:
- **핵심 개념**: {core_concept}
- **학습 목표**: {objective}
- **키워드**: {keywords}
- **예시**: {examples}

## 중요 규칙:
- 반드시 제공된 목록에서 **정확히 일치하는 단원명 하나만** 선택
- 부연 설명, 괄호, 줄바꿈 등은 절대 포함하지 않음
- 단원명만 정확히 작성
- 분석 정보에 '성질', '특징', '규칙' 등 성질 관련 키워드가 포함되어 있으면, 성질이 포함된 단원명을 우선적으로 선택

## 후보 단원 목록:
{curriculum_titles_text}

## 출력 형식:
```json
{{
  "valid_topic": "선택된 단원명"
}}
"""
    messages = [
        {"role": "system", "content": "당신은 초등학교 수학 교육 내용을 분석해 가장 관련 있는 단원을 추천하는 전문가 AI입니다."},
        {"role": "user", "content": prompt}
    ]
    input_ids = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    )
    output_ids = llm_model.generate(
        input_ids.to("cuda"),
        eos_token_id=tokenizer.eos_token_id,
        max_new_tokens=256,
        do_sample=False,
    )
    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    matches = re.findall(r'"valid_topic"\s*:\s*"([^"]+)"', output_text)
    if matches:
        selected_title = matches[-1].strip()
        if selected_title in [v.strip() for v in valid_candidates]:
            return selected_title
    return "" 