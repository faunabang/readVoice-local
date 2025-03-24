import pyaudio
import numpy as np
import time
from config.settings import AUDIO_CONFIG
from src.utils.logger import setup_logger

logger = setup_logger('audio_recorder')

class AudioRecorder:
    """오디오 녹음 클래스"""
    
    def __init__(self):
        self.threshold = AUDIO_CONFIG['THRESHOLD']
        self.chunk = AUDIO_CONFIG['CHUNK']
        self.format = getattr(pyaudio, AUDIO_CONFIG['FORMAT'])
        self.channels = AUDIO_CONFIG['CHANNELS']
        self.rate = AUDIO_CONFIG['RATE']
        self.silence_duration = AUDIO_CONFIG['SILENCE_DURATION']
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def is_silent(self, data):
        """소리가 임계값보다 작은지 확인"""
        return max(np.frombuffer(data, dtype=np.int16)) < self.threshold
    
    def start_stream(self):
        """오디오 스트림 시작"""
        if self.stream is None:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            logger.info("오디오 스트림이 시작되었습니다.")
    
    def close(self):
        """리소스 정리"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        if self.audio:
            self.audio.terminate()
            self.audio = None
            
        logger.info("오디오 리소스가 정리되었습니다.")
    
    def record(self):
        """오디오 녹음"""
        self.start_stream()
        frames = []
        recording = False
        silent_start = None
        
        logger.info("소리를 감지하고 있습니다...")
        
        try:
            while True:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                
                if not self.is_silent(data):
                    if not recording:
                        logger.info("녹음 시작")
                        recording = True
                    frames.append(data)
                    silent_start = None
                elif recording:
                    if silent_start is None:
                        silent_start = time.time()
                    elif time.time() - silent_start >= self.silence_duration:
                        logger.info("녹음 종료")
                        return frames
                    else:
                        frames.append(data)
                        
        except KeyboardInterrupt:
            logger.info("사용자에 의해 녹음이 중단되었습니다.")
            if frames:
                return frames
            return None
        except Exception as e:
            logger.error(f"녹음 중 오류 발생: {e}")
            return None 