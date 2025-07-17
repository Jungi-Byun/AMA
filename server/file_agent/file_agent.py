import os
import base64
from werkzeug.utils import secure_filename
from utils import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

class FileAgent:
    def __init__(self, upload_folder=UPLOAD_FOLDER):
        self.upload_folder = upload_folder
        self.allowed_extensions = ALLOWED_EXTENSIONS
        self._ensure_upload_folder()
    
    def _ensure_upload_folder(self):
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def is_allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_image(self, filename, filedata):
        if not filename:
            return False
        if not self.is_allowed_file(filename):
            return False
        
        filename = secure_filename(filename)
        file_path = os.path.join(self.upload_folder, filename)
        image_data = base64.b64decode(filedata)
        
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        return True
    
    def file_exists(self, filename):
        file_path = os.path.join(self.upload_folder, filename)
        return os.path.exists(file_path)
    
    def get_file_path(self, filename):
        return os.path.join(self.upload_folder, filename)
