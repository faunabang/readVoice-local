from openai import OpenAI
from config.settings import AI_CONFIG
from src.utils.logger import setup_logger

logger = setup_logger('ai_service')

class AIService:
    """OpenAI API를 이용한 AI 요약 서비스"""
    
    def __init__(self):
        self.api_key = AI_CONFIG['API_KEY']
        self.model = AI_CONFIG['MODEL']
        self.client = self._get_client()
    
    def _get_client(self):
        """OpenAI 클라이언트 생성"""
        if not self.api_key:
            logger.error("OpenAI API 키가 설정되지 않았습니다.")
            return None
            
        try:
            return OpenAI(api_key=self.api_key)
        except Exception as e:
            logger.error(f"OpenAI 클라이언트 생성 실패: {e}")
            return None
    
    def summarize(self, text):
        """텍스트 요약"""
        if not self.client:
            logger.error("OpenAI 클라이언트가 초기화되지 않았습니다.")
            return None
            
        if not text or len(text) <= 6:
            logger.warning("요약할 텍스트가 너무 짧습니다.")
            return None
            
        try:
            prompt = [
                {"role": "developer", "content": """
주어진 교내 방송 음성을 요약하세요.  

### 요구사항  
- 방송에서 실제로 말한 내용만 요약하세요.  
- 불필요한 단어를 줄이고, 핵심 키워드만 남기세요.  
- 문장보다는 간략한 정보 전달 방식으로 정리하세요.
- 입력이 짧다면 요약도 짧게 유지하세요. 내용을 추가하지 마세요.  

출력 예시: (요약의 "" 안에 있는 내용만 출력)
방송: "오늘 급식은 김치찌개와 불고기입니다. 맛있게 드세요!"  
요약: "급식: 김치찌개, 불고기"  

방송: "오전 10시에 체육관에서 학생회 모임이 있습니다."  
요약: "학생회 모임 - 10시, 체육관"
                """},
                {"role": "user", "content": text}
            ]
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=prompt
            )
            
            summary = completion.choices[0].message.content
            logger.info(f"AI 요약 성공: {len(summary)} 글자")
            return summary
            
        except Exception as e:
            logger.error(f"AI 요약 중 오류 발생: {e}")
            return None 