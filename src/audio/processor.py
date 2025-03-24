import wave
import os
import json
from datetime import datetime
import pyaudio
from config.settings import AUDIO_CONFIG, AUDIO_DIR, RESULTS_DIR
from src.utils.logger import setup_logger

logger = setup_logger('audio_processor')

class AudioProcessor:
    """오디오 처리 클래스"""
    
    def __init__(self, audio_instance):
        self.audio = audio_instance
        self.format = getattr(pyaudio, AUDIO_CONFIG['FORMAT'])
        self.channels = AUDIO_CONFIG['CHANNELS']
        self.rate = AUDIO_CONFIG['RATE']
        self.extension = AUDIO_CONFIG['FILE_EXTENSION']
    
    def save_audio(self, frames):
        """오디오 파일 저장"""
        if not frames:
            logger.warning("저장할 프레임이 없습니다.")
            return None
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date = datetime.now().strftime("%Y-%m-%d")
        
        # 날짜별 디렉토리 생성
        date_dir = os.path.join(AUDIO_DIR, date)
        os.makedirs(date_dir, exist_ok=True)
        
        # 파일명 생성
        filename = timestamp.replace(':', '_').replace(' ', '_') + self.extension
        filepath = os.path.join(date_dir, filename)
        
        try:
            # WAV 파일로 저장
            wf = wave.open(filepath, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            logger.info(f"오디오 파일이 저장되었습니다: {filepath}")
            
            return {
                'timestamp': timestamp,
                'date': date,
                'filepath': filepath,
                'filename': filename
            }
            
        except Exception as e:
            logger.error(f"오디오 파일 저장 중 오류 발생: {e}")
            return None
    
    def save_result(self, audio_info, stt_text, ai_summary, object_storage_path=None):
        """결과 JSON 파일 저장"""
        if not audio_info or not stt_text:
            logger.warning("저장할 결과 정보가 부족합니다.")
            return False
            
        date = audio_info['date']
        result_file = os.path.join(RESULTS_DIR, f"{date}.json")
        
        try:
            # 기존 파일이 있으면 로드
            if os.path.exists(result_file):
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
            
            # 새 결과 추가
            result = {
                "timestamp": audio_info['timestamp'],
                "audio_filepath": audio_info['filepath'],
                "stt_text": stt_text
            }
            
            if ai_summary:
                result["ai_summary"] = ai_summary
                
            if object_storage_path:
                result["object_storage_path"] = object_storage_path
                
            data.append(result)
            
            # 파일 저장
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            logger.info(f"결과가 저장되었습니다: {result_file}")
            return True
            
        except Exception as e:
            logger.error(f"결과 저장 중 오류 발생: {e}")
            return False 