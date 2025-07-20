import os
import json
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

# 문제/힌트 생성 병렬 처리
import concurrent.futures

### Internal Modules
# Utilities for server
from utils import UPLOAD_FOLDER, DOWNLOAD_FOLDER, Response

# FileAgent to save uploaded image file to server
from file_agent import FileAgent

# OCRAgent to analyze materials and classify them according to math curriculum.
from ocr import OCRAgent

# Math Q Agent to generate exercises by types
from math_q_agent import QuestionAgent

# Geometry Agent to generate hints for students who are struggling to solve generated questions
from geometry_agent import GeometryAgent

# Flask app 생성 및 설정
app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Upload, Download 폴더 존재 여부 확인, 없는 경우 생성
for folder in [UPLOAD_FOLDER, DOWNLOAD_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# 파일 다운로드 API
@app.route('/image/<filename>', methods=['GET'])
def get_image(filename):
    if file_agent.file_exists(filename):
        return send_file(file_agent.get_file_path(filename), mimetype='image/jpeg')
    else:
        return jsonify({"error": "File not found"}), 404

# 파일 업로드 및 문제/힌트 생성 API
@app.route('/upload', methods=['POST'])
def upload_file():
    if not request.data:
        return jsonify({"error": "File data is null"}), 400

    try:
        # 요청 데이터 파싱 및 정보 추출
        data = request.data.decode('utf-8')
        data_dict = json.loads(data)

        filename = data_dict.get('filename')
        filedata = data_dict.get('file')
        question_type = data_dict.get('question_type')
        
        # 업로드된 이미지 파일 저장
        if not file_agent.save_image(filename, filedata):
            return jsonify({"error": "No filename or Not allowed format"}), 400

        # OCR 인식 및 소단원 예측
        file_path = file_agent.get_file_path(filename)
        if file_path is not None:
            topic = ocr_agent.run(file_path=file_path)
        else:
            return jsonify({"error": "Internal server error"}), 500

        # 문제와 힌트를 병렬로 생성
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_questions = executor.submit(QuestionAgent.generate_response, topic, question_type)
            future_hint = executor.submit(geometry_agent.run, topic)

            # 생성된 문제와 힌트 가져오기
            questions = future_questions.result()
            hint = future_hint.result()

        return jsonify(Response(question_type, questions, hint).to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500 

if __name__ == '__main__':
    # Tokenizer 병렬 처리 비활성화
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # Agent 인스턴스 생성
    file_agent = FileAgent()
    ocr_agent = OCRAgent()
    geometry_agent = GeometryAgent()
    
    # 서버 실행
    app.run(host='0.0.0.0', port=5111, debug=False)
