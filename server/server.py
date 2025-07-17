from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import base64
import total_topic_meta as meta

# 힌트 생성 에이전트
from geometry_agent import GeometryAgent

app = Flask(__name__)
CORS(app)  # CORS 허용

# 업로드된 파일을 저장할 디렉토리 설정
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 허용할 파일 확장자 설정
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_request_image(filename, filedata):
    filename = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # 파일 내용을 request.data에서 읽어서 저장
    # Base64 디코딩
    image_data = base64.b64decode(filedata)

    with open(file_path, 'wb') as f:
        f.write(image_data)

# 이미지 출력 엔드포인트
@app.route('/image/<filename>', methods=['GET'])
def get_image(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='image/jpeg')
    else:
        return jsonify({"error": "File not found"}), 404

# 이미지 업로드 엔드포인트
@app.route('/upload', methods=['POST'])
def upload_file():
    if request.data:
        data = request.data.decode('utf-8')
        data_dict = json.loads(data)

        print('mine type :', request.mimetype)

        question_type = data_dict['question_type']
        print('question_type : ', question_type)

        filename = data_dict['filename']
        print('filename : ', filename)
        
        filedata = data_dict['file']

        if filename == '':
            return jsonify({"error": "No selected filename"}), 400
        if allowed_file(filename):
            # 요약 필요한 이미지 저장
            save_request_image(filename, filedata)
            
            # Dummy Data 전송
            # 문제 더미
            question_list = meta.get_math_questions('지름의 성질 알아보기', question_type)
            # string_question_list = [
            #     """다음을 계산하시오. (1) $ 3 \\frac{1}{2} \\times 1 \\frac{3}{4} $ (2) $ 1 \\frac{5}{8} \\times 3 \\frac{7}{13} $""",
            #     """$\\bigcirc$ 안에 $>, =, <$를 알맞게 써넣으시오. $ 13 \\div 9 \\bigcirc 5 \\frac{1}{7} \\div 4 $""",
            #     """$ 4 \\frac{2}{3} \\div 9 $를 어떻게 계산하는지 알아보려고 합니다. $\\square$ 안에 알맞은 수를 써넣으시오.(1) $ 4 \\frac{2}{3} \\div 9 $에서 $ 4 \\frac{2}{3} \\div 9 $를 가분수로 나타내시오. $ 4 \\frac{2}{3} \\div 9 $= $ \\frac{\\square}{\\square} \\div 9 $ (2) $ 4 \\frac{2}{3} \\div 9 $를 계산하시오 $ 4 \\frac{2}{3} \\div 9 $= $ \\frac{\\square}{\\square} \\div 9 $ =$ \\frac{\\square}{\\square} \\times \\frac{1}{9} $ = $ \\frac{\\square}{\\square} $""",
            #     """반지름이 $14cm$인 원의 넓이를 구하시오. (원주율 : $3.14$)"""
            #     ]

            #힌트 생성
            hint_agent = GeometryAgent()
            # TODO: 힌트 생성에 필요한 파라미터를 OCR 인식 후 분류한 소단원으로 변경
            hint_data = hint_agent.run('지름의 성질 알아보기')

            # questions = image_question_list if question_type == 1 else string_question_list
            response = {
                    "status": {
                        "code": "2000",
                        "message": "COMMON_SUCCESS"
                    },
                    "payload": {
                        "question_type" : question_type,
                        "questions": question_list,
                        "hint" : hint_data
                    }
                }

            # print(response)

            # 인코딩된 이미지 파일을 클라이언트에게 전송합니다
            return jsonify(response)
        else:
            return jsonify({"error": "File type not allowed"}), 400
    else:
        return jsonify({"error": "File data is null"}), 400   

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5111, debug=True)