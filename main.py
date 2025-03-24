import os
import sys
from config.settings import AUDIO_CONFIG, CLOUD_CONFIG, STT_CONFIG, AI_CONFIG, RESULTS_DIR
from src.audio.recorder import AudioRecorder
from src.audio.processor import AudioProcessor
from src.services.stt_service import STTService
from src.services.ai_service import AIService
from src.cloud.storage import CloudStorage
from src.utils.logger import setup_logger

logger = setup_logger('main')

def check_environment():
    """환경 설정 확인"""
    missing_configs = []
    
    if not all([CLOUD_CONFIG['ACCESS_KEY'], CLOUD_CONFIG['SECRET_KEY'], CLOUD_CONFIG['BUCKET_NAME']]):
        missing_configs.append("클라우드 스토리지")
        
    if not all([STT_CONFIG['INVOKE_URL'], STT_CONFIG['SECRET_KEY']]):
        missing_configs.append("STT 서비스")
        
    if not AI_CONFIG['API_KEY']:
        missing_configs.append("AI 서비스")
    
    if missing_configs:
        logger.error(f"다음 설정이 완료되지 않았습니다: {', '.join(missing_configs)}")
        logger.error("프로그램을 실행하기 전에 .env 파일에 모든 필요한 환경 변수를 설정해주세요.")
        return False
        
    return True

def main():
    """메인 함수"""
    logger.info("음성 녹음 및 처리 프로그램을 시작합니다...")
    
    # 환경 설정 확인
    if not check_environment():
        return
    
    # 클라우드 스토리지 연결 확인
    cloud_storage = CloudStorage()
    if not cloud_storage.check_connection():
        logger.warning("클라우드 스토리지 연결에 실패했습니다. 로컬 저장만 진행합니다.")
    
    # 서비스 초기화
    stt_service = STTService()
    ai_service = AIService()
    
    try:
        with AudioRecorder() as recorder:
            audio_processor = AudioProcessor(recorder.audio)
            
            logger.info("녹음을 중지하려면 Ctrl+C를 누르세요.")
            
            while True:
                # 오디오 녹음
                frames = recorder.record()
                if not frames:
                    continue
                
                # 오디오 저장
                audio_info = audio_processor.save_audio(frames)
                if not audio_info:
                    continue
                
                # 클라우드 스토리지에 오디오 업로드
                object_key = f"audio/{audio_info['date']}/{audio_info['filename']}"
                cloud_upload_success = cloud_storage.upload_file(audio_info['filepath'], object_key)
                
                # STT 변환
                stt_text = stt_service.transcribe(audio_info['filepath'])
                if not stt_text or len(stt_text) <= 6:
                    logger.warning("STT 결과가 없거나 너무 짧아 처리를 건너뜁니다.")
                    continue
                
                # AI 요약
                ai_summary = ai_service.summarize(stt_text)
                
                # 결과 저장
                audio_processor.save_result(
                    audio_info, 
                    stt_text, 
                    ai_summary,
                    object_key if cloud_upload_success else None
                )
                
                # 클라우드 스토리지에 결과 업로드
                if cloud_upload_success:
                    result_file = os.path.join(RESULTS_DIR, f"{audio_info['date']}.json")
                    object_key_json = f"results/{audio_info['date']}.json"
                    cloud_storage.upload_file(result_file, object_key_json)
                
    except KeyboardInterrupt:
        logger.info("프로그램이 사용자에 의해 종료되었습니다.")
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {e}")
    
    logger.info("프로그램을 종료합니다.")

if __name__ == "__main__":
    main() 