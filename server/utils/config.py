"""설정 상수들"""

# 파일 관련 설정
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 데이터베이스 파일 경로
META_DB = "data/big_math_meta.txt"
TOPIC_DB = "data/big_math_topic_list.txt"

# META_DB = "/home/seungjwa.nam/AMA/AMA/server/data/big_math_meta.txt"
# TOPIC_DB = "/home/seungjwa.nam/AMA/AMA/server/data/big_math_topic_list.txt"

# 수학 문제 은행 경로
LABELS_DIRECTORY_PATH = 'big_math_bank/labels'
IMAGES_DIRECTORY_PATH = 'big_math_bank/origins'

# LABELS_DIRECTORY_PATH  = '/home/seungjwa.nam/AMA/AMA/server/big_math_bank/labels'
# IMAGES_DIRECTORY_PATH  = '/home/seungjwa.nam/AMA/AMA/server/big_math_bank/origins'

# 응답 상태 코드
SUCCESS_CODE = "2000"
SUCCESS_MESSAGE = "COMMON_SUCCESS"

# 문제 타입
QUESTION_TYPE_RANDOM = 1
QUESTION_TYPE_GENERATE = 2

# 기본 문제 개수
DEFAULT_QUESTION_COUNT = 4