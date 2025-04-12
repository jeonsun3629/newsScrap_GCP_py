FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# 필요한 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사 (단, .env 파일은 제외)
COPY . .

# 포트 노출
EXPOSE 8080

# 애플리케이션 실행
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app 