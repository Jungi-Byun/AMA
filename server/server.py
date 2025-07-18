import os
import json
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from file_agent import FileAgent
from math_q_agent import QuestionAgent
from model import get_classifier_model, get_llm_model
from utils import UPLOAD_FOLDER, DOWNLOAD_FOLDER
from response import Response
# 힌트 생성 에이전트
from geometry_agent import GeometryAgent
# ocr
from ocr import OCRAgent

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# OCR agent
ocr_agent = None

for folder in [UPLOAD_FOLDER, DOWNLOAD_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

@app.route('/image/<filename>', methods=['GET'])
def get_image(filename):
    file_agent = FileAgent()
    if file_agent.file_exists(filename):
        return send_file(file_agent.get_file_path(filename), mimetype='image/jpeg')
    else:
        return jsonify({"error": "File not found"}), 404

@app.route('/upload', methods=['POST'])
def upload_fiile():
    if not request.data:
        return jsonify({"error": "File data is null"}), 400

    try:
        data = request.data.decode('utf-8')
        data_dict = json.loads(data)
        question_type = data_dict.get('question_type')
        filename = data_dict.get('filename')
        filedata = data_dict.get('file')
        
        file_agent = FileAgent()
        response = file_agent.save_image(filename, filedata)
        
        if response == False:
            return jsonify({"error": "No filename or Not allowed format"}), 400

        # OCR
        file_path = file_agent.get_file_path(filename)
        if file_path is not None:
            topic = ocr_agent.run(file_path=file_path)
        else:
            topic = "invaild"

        #힌트 생성
        hint_agent = GeometryAgent()
        # TODO: 힌트 생성에 필요한 파라미터를 OCR 인식 후 분류한 소단원으로 변경
        hint_data = hint_agent.run('지름의 성질 알아보기')
        
        question_topic = '지름의 성질 알아보기'
        questions = QuestionAgent.generate_response(question_topic, question_type)
        response = Response(question_type, questions, hint_data)
        print('response = ', response)
        
        return jsonify(response.to_dict())
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500 

if __name__ == '__main__':
    llm_model, llm_tokenizer, device = get_llm_model()
    classifier_model, classifier_tokenizer = get_classifier_model()
    ocr_agent = OCRAgent()
    
    app.run(host='0.0.0.0', port=5111, debug=True)
