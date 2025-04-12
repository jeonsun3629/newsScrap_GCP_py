import os
import logging
from logging.handlers import RotatingFileHandler

# 로그 레벨 설정
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

# 로거 생성
logger = logging.getLogger('newsscrap')
logger.setLevel(getattr(logging, log_level))

# 포맷 정의
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 콘솔 핸들러
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# GCP Cloud Run에서는 콘솔 로그가 Cloud Logging으로 자동 전송됨

def get_logger():
    """로거 인스턴스 반환"""
    return logger

# 기본 로거 인스턴스 제공
logger = get_logger() 