import boto3
from botocore.client import Config
from config.settings import CLOUD_CONFIG
from src.utils.logger import setup_logger

logger = setup_logger('cloud_storage')

class CloudStorage:
    """네이버 Object Storage 관리 클래스"""
    
    def __init__(self):
        self.access_key = CLOUD_CONFIG['ACCESS_KEY']
        self.secret_key = CLOUD_CONFIG['SECRET_KEY']
        self.endpoint_url = CLOUD_CONFIG['ENDPOINT_URL']
        self.bucket_name = CLOUD_CONFIG['BUCKET_NAME']
        
        self.client = self._get_client()
    
    def _get_client(self):
        """S3 클라이언트 생성"""
        if not all([self.access_key, self.secret_key, self.endpoint_url, self.bucket_name]):
            logger.error("클라우드 스토리지 설정이 완료되지 않았습니다.")
            return None
            
        try:
            return boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=Config(
                    signature_version='s3v4',
                    retries={'max_attempts': 3}
                )
            )
        except Exception as e:
            logger.error(f"S3 클라이언트 생성 실패: {e}")
            return None
    
    def upload_file(self, local_path, object_key):
        """파일 업로드"""
        if not self.client:
            logger.error("S3 클라이언트가 초기화되지 않았습니다.")
            return False
            
        try:
            # 버킷 존재 여부 확인
            try:
                self.client.head_bucket(Bucket=self.bucket_name)
                logger.info(f"버킷 접근 가능: {self.bucket_name}")
            except Exception as e:
                logger.error(f"버킷 접근 실패: {str(e)}")
                return False

            # 업로드 시도
            self.client.upload_file(
                local_path, 
                self.bucket_name, 
                object_key,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': 'application/octet-stream'
                }
            )
            url = f"https://{self.bucket_name}.kr.object.ncloudstorage.com/{object_key}"
            logger.info(f"파일 업로드 성공: {url}")
            return True
        except Exception as e:
            logger.error(f"파일 업로드 실패 상세: {type(e).__name__}, {str(e)}")
            # 권한 정보 출력 시도
            try:
                bucket_policy = self.client.get_bucket_policy(Bucket=self.bucket_name)
                logger.info(f"현재 버킷 정책: {bucket_policy}")
            except Exception as policy_e:
                logger.error(f"버킷 정책 확인 실패: {str(policy_e)}")
            return False
    
    def check_connection(self):
        """연결 상태 확인"""
        if not self.client:
            return False
            
        try:
            self.client.list_buckets()
            return True
        except Exception as e:
            logger.error(f"클라우드 스토리지 연결 확인 실패: {e}")
            return False 