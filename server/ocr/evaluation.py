#---------------------------------------------------------
# 평가 프롬프트 및 OpenAI 평가 함수
#---------------------------------------------------------

from openai import OpenAI

def get_evaluation_prompt(easyocr_result, paddleocr_result, merged_text):
    return f"""
다음은 두 개의 OCR 결과(EasyOCR, PaddleOCR)를 통합하여 LLM이 생성한 텍스트입니다.  
이 통합 결과가 원문에 기반하여 얼마나 정확하고 자연스러운지를 아래 기준에 따라 평가해 주세요.

## 평가 항목:
1. **정확성 (0~10점)**: 두 OCR 결과에 있는 정보를 충실히 반영했는가? 누락, 왜곡 없이 잘 통합했는가?
2. **오류 수정 (0~10점)**: 인식 오류(오탈자, 잘못된 단어 등)를 문맥에 맞게 자연스럽게 수정했는가?
3. **문장의 자연스러움 (0~10점)**: 결과 문장이 문법적으로 매끄럽고 읽기 쉬운가?

각 항목을 0~10점으로 평가한 후, 전체 평균 점수(소수점 첫째 자리까지)를 **"total_score"**로 계산해 주세요.  

## 출력 형식 (JSON):
```json
{
  "evaluation": {
    "accuracy": 8.5,
    "error_correction": 9.0,
    "fluency": 9.5,
    "total_score": 9.0
  },
  "comments": "대부분의 정보를 잘 통합했으며, 오탈자 수정도 훌륭합니다. 다만 일부 숫자 인식 오류가 그대로 유지되어 감점되었습니다."
}

## OCR 결과:
### EasyOCR:
{easyocr_result}

### PaddleOCR:
{paddleocr_result}

## LLM 통합 결과:
{merged_text}
"""

def evaluate_ocr_merge(easyocr_result, paddleocr_result, merged_text, api_key):
    client = OpenAI(api_key=api_key)
    prompt = get_evaluation_prompt(easyocr_result, paddleocr_result, merged_text)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """당신은 OCR 결과 통합을 전문으로 평가하는 전문가입니다. 두 가지 OCR 결과를 하나의 자연스럽고 정확한 문장으로 통합한 AI의 결과물을 평가하는 역할입니다. 평가 기준은 정확성, 오류 수정 능력, 문장의 자연스러움입니다. 이 기준에 따라 세심하게 평가하고 근거를 들어 설명해 주세요."""
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=256
    )
    return response.choices[0].message.content 