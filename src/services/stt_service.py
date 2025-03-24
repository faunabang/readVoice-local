import requests
import json
import os
from config.settings import STT_CONFIG
from src.utils.logger import setup_logger

logger = setup_logger('stt_service')

class STTService:
    """CLOVA Speech API를 이용한 STT 서비스"""
    
    def __init__(self):
        self.invoke_url = STT_CONFIG['INVOKE_URL']
        self.secret = STT_CONFIG['SECRET_KEY']
        self.keywords = self._load_keywords()
    
    def _load_keywords(self):
        try:
            keywords_path = os.path.join('config', 'keywords.json')
            with open(keywords_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"키워드 파일 로드 실패: {e}")
            return {"boostings": [], "forbiddens": []}
    
    def transcribe(self, audio_file):
        """음성 파일을 텍스트로 변환"""
        if not all([self.invoke_url, self.secret]):
            logger.error("STT 서비스 설정이 완료되지 않았습니다.")
            return None
            
        try:
            request_body = self._create_request_body()
            headers = {
                'Accept': 'application/json;UTF-8',
                'X-CLOVASPEECH-API-KEY': self.secret
            }
            
            files = {
                'media': open(audio_file, 'rb'),
                'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
            }
            
            response = requests.post(
                headers=headers, 
                url=self.invoke_url + '/recognizer/upload', 
                files=files
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '').strip()
                logger.info(f"STT 변환 성공: {len(text)} 글자")
                return text
            else:
                logger.error(f"STT 요청 실패: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"STT 처리 중 오류 발생: {e}")
            return None
    
    def _create_request_body(self):
        """STT 요청 본문 생성"""
        return {
            'language': 'ko-KR',
            'completion': 'sync',
            'wordAlignment': True,
            'fullText': True,
            'speaker': {
                'enable': True,
                'min': 1,
                'max': 10
            },
            'keywordBoosting': {
                'boostings': self.keywords['boostings']
            },
            'forbidden': {
                'forbiddens': self.keywords['forbiddens']
            }
        } 