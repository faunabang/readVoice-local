import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 오디오 설정
AUDIO_CONFIG = {
    'THRESHOLD': 2000,
    'CHUNK': 1024,
    'FORMAT': 'paInt16',  # PyAudio 객체 생성 시 실제 값으로 변환
    'CHANNELS': 1,
    'RATE': 44100,
    'SILENCE_DURATION': 3,
    'FILE_EXTENSION': '.mp3'
}

# 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
AUDIO_DIR = os.path.join(DATA_DIR, 'audio')
RESULTS_DIR = os.path.join(DATA_DIR, 'results')

# 클라우드 스토리지 설정
CLOUD_CONFIG = {
    'ACCESS_KEY': os.getenv('NCP_ACCESS_KEY'),
    'SECRET_KEY': os.getenv('NCP_SECRET_KEY'),
    'ENDPOINT_URL': os.getenv('NCP_ENDPOINT_URL', 'https://kr.object.ncloudstorage.com'),
    'REGION_NAME': os.getenv('NCP_REGION_NAME', 'kr-standard'),
    'BUCKET_NAME': os.getenv('NCP_BUCKET_NAME')
}

# STT 서비스 설정
STT_CONFIG = {
    'INVOKE_URL': os.getenv('invoke_url'),
    'SECRET_KEY': os.getenv('secret')
}

# AI 서비스 설정
AI_CONFIG = {
    'API_KEY': os.getenv('OPENAI_API_KEY'),
    'MODEL': 'gpt-4o'
}

# 필요한 디렉토리 생성
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True) 