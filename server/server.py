from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import json
import base64

app = Flask(__name__)

# 업로드된 파일을 저장할 디렉토리 설정
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 허용할 파일 확장자 설정
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

        filename = data_dict['filename']
        print('filename : ', filename)

        if filename == '':
            return jsonify({"error": "No selected filename"}), 400
        if allowed_file(filename):
            filename = secure_filename(filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # 파일 내용을 request.data에서 읽어서 저장
            # Base64 디코딩
            image_data = base64.b64decode(data_dict['file'])

            with open(file_path, 'wb') as f:
                f.write(image_data)
        
            return jsonify({"message": "File uploaded successfully", "filename": filename}), 201
        else:
            return jsonify({"error": "File type not allowed"}), 400
    else:
        return jsonify({"error": "File data is null"}), 400    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5111, debug=True)
