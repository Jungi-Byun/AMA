from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import base64
import total_topic_meta as meta

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
            #힌트 더미
            hint_data = {
                        'input_section': '원의 반지름과 지름 알아보기', 
                        'section_description': '원의 반지름과 지름의 관계를 알고, 직접 측정하거나 구할 수 있다.', 
                        'math_concept': '원', 
                        'hint_type': 'both', 
                        'generated_code': '<svg width="500" height="500" xmlns="http://www.w3.org/2000/svg">\n    <text x="250" y="50" font-size="25" text-anchor="middle">원</text>\n    <circle cx="250" cy="250" r="166" stroke="black" stroke-width="2" fill="none" />\n    <circle cx="250" cy="250" r="3" stroke="black" stroke-width="2" fill="black" />\n    <line x1="84" y1="250" x2="416" y2="250" stroke="black" stroke-width="2" />\n    <!-- 보조선 -->\n    <path d="M 250, 250 Q 333, 223 416, 250" fill="none" stroke="black" stroke-width="2" stroke-dasharray="5,3" />\n    <text x="333" y="223" font-size="12" text-anchor="middle">반지름</text>\n    <path d="M 84, 250 Q 250, 277 416, 250" fill="none" stroke="black" stroke-width="2" stroke-dasharray="5,3" />\n    <text x="250" y="291" font-size="12" text-anchor="middle">지름</text>\n    </svg>\n    ', 
                        'comments': '안녕하세요! 오늘은 원에 대해 알아볼게요. 특히 원의 **반지름**과 **지름**에 대해 쉽게 이해해볼게요.\n\n### 반지름 (Radius)\n- **정의**: 원의 중심에서 원 위의 어떤 점까지의 거리를 말해요. 쉽게 말해, 원의 중심을 지나는 선분이 원 위의 한 점까지 얼마나 멀리 있는지를 나타내는 거예요.\n- **기본 성질**: 반지름은 항상 양수이며, 원의 크기에 따라 길이가 달라집니다. 예를 들어, 반지름이 3cm인 원은 중심에서 가장 먼 점까지 3cm 떨어져 있어요.\n\n### 지름 (Diameter)\n- **정의**: 원의 한 점에서 반대쪽 점까지의 거리를 말해요. 즉, 원을 완전히 가로지르는 직선의 길이를 의미합니다. 이 직선은 원의 중심을 지나요.\n- **기본 성질**: 지름은 반지름의 두 배입니다. 그래서 만약 반지름이 2cm라면, 지름은 4cm가 되는 거예요. 또한, 지름은 원의 크기를 나타내는 중요한 측정값이기도 해요.\n\n### 직접 측정하기\n- **반지름 측정**: 원의 중심에서 원 위의 임의의 점까지 자를 이용해 거리를 재면 됩니다.\n- **지름 측정**: 원의 중심을 지나는 직선을 그려, 원의 가장 먼 두 점 사이의 거리를 재면 됩니다.\n\n이렇게 반지름과 지름을 이해하면 원의 모양과 크기를 더 잘 파악할 수 있어요. 재미있게 연습해보세요!', 
                        'formulas': {'반지름과 지름의 관계': '$\\mathrm{지름} = \\mathrm{반지름} \\times 2$'}   
                }

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