import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from services.crawler import start_crawling_process
from utils.logger import logger

# 환경 변수 로드 (파일이 없어도 오류 발생하지 않음)
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"환경 변수 파일(.env) 로드 실패: {str(e)}")
    logger.info("계속 진행: 환경 변수는 시스템 설정에서 불러옵니다.")

app = Flask(__name__)
PORT = int(os.getenv('PORT', 8080))

@app.route('/health')
def health():
    """헬스 체크 엔드포인트"""
    return jsonify({'status': 'OK'})

@app.route('/')
def index():
    """메인 크롤링 엔드포인트 - GCP Cloud Scheduler에서 호출됨"""
    logger.info('뉴스 크롤링 요약 작업 시작')
    
    try:
        # 크롤링 및 요약 프로세스 시작
        results = start_crawling_process()
        
        response = {
            'status': 'success',
            'message': '뉴스 크롤링 및 요약 작업이 완료되었습니다.',
            'processed': len(results) if results else 0
        }
        
        logger.info(f'뉴스 크롤링 요약 작업 완료: {len(results) if results else 0}개 기사 처리됨')
        return jsonify(response), 200
    
    except Exception as error:
        logger.error(f'크롤링 처리 중 오류 발생: {str(error)}')
        
        response = {
            'status': 'error',
            'message': '뉴스 크롤링 및 요약 작업 중 오류가 발생했습니다.',
            'error': str(error)
        }
        
        return jsonify(response), 500

# 기본 홈 엔드포인트 추가
@app.route('/home')
def home():
    return jsonify({
        "status": "success",
        "message": "안녕하세요! Google Cloud Run에서 실행 중인 서비스입니다."
    })

if __name__ == '__main__':
    logger.info(f'서버가 0.0.0.0의 포트 {PORT}에서 실행 중입니다.')
    app.run(host='0.0.0.0', port=PORT, debug=False) 