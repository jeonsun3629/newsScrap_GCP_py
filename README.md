# NewsScrap - 뉴스 크롤링 및 요약 서비스

FireCrawl과 OpenAI API를 활용하여 다양한 국가의 뉴스 사이트를 크롤링하고, 내용을 요약한 뒤 Notion 데이터베이스에 저장하는 Google Cloud Run 서비스입니다.

## 프로젝트 개요

NewsScrap은 다음과 같은 작업을 자동화하는 서비스입니다:
1. 전 세계 다양한 국가의 주요 뉴스 사이트에서 최신 뉴스 기사를 크롤링
2. AI 기반 웹 크롤링 기술을 사용하여 정확한 콘텐츠 추출
3. GPT 모델을 활용한 기사 내용의 간결한 요약
4. 추출한 정보와 요약을 Notion 데이터베이스에 구조화하여 저장
5. 자동 실행 스케줄링을 통한 최신 뉴스 모니터링

현재 버전은 랜덤으로 1개 국가, 1개 뉴스만 선택하여 처리하도록 설정되어 있습니다.

## 동작 순서

1. **국가 및 뉴스 사이트 선택**:
   - 설정된 국가 목록에서 랜덤으로 1개 국가를 선택
   - 선택된 국가의 뉴스 사이트 목록을 가져옴

2. **헤드라인 추출**:
   - FireCrawl API 또는 직접 크롤링을 통해 뉴스 사이트의 주요 헤드라인 1개를 추출
   - 추출에 실패할 경우 백업 방법으로 BeautifulSoup을 사용한 직접 크롤링 시도

3. **기사 내용 추출**:
   - 추출된 헤드라인의 링크를 통해 전체 기사 내용을 크롤링
   - 광고, 관련 기사 링크, 댓글 등을 제외한 순수 기사 내용만 추출

4. **내용 요약**:
   - OpenAI GPT-3.5-turbo 모델을 사용하여 기사 내용을 3-4문장으로 요약
   - 핵심 정보와 주요 사실을 중심으로 요약 생성

5. **Notion 저장**:
   - 추출한 헤드라인, 기사 URL, 내용, 요약 등을 Notion 데이터베이스에 저장
   - 국가, 뉴스 출처, 수집 시간 등의 메타데이터도 함께 저장

## 주요 기능

1. **다국어 뉴스 크롤링**: 13개 이상의 국가에서 50개 이상의 주요 뉴스 사이트 지원
2. **LLM 기반 추출**: FireCrawl API를 활용한 지능형 웹 크롤링으로 정확한 데이터 추출
3. **비동기 처리**: 비동기 요청 처리를 통한 효율적인 크롤링 수행
4. **대체 크롤링 방식**: API 장애 시 직접 크롤링으로 자동 전환되는 내결함성 설계
5. **내용 요약**: OpenAI GPT-3.5-turbo를 사용한 정확하고 간결한 요약 제공
6. **Notion 통합**: 구조화된 데이터베이스에 정보 저장 및 관리
7. **Cloud Run 배포**: 서버리스 환경에서 안정적으로 실행되는 확장 가능한 구조

## 시스템 구조

```
NewsScrap
│
├── app.py                  # Flask 웹 서버 및 메인 애플리케이션
├── config.py               # 설정 파일 (뉴스 사이트, API 설정 등)
├── requirements.txt        # 의존성 패키지 목록
│
├── services/               # 주요 서비스 모듈
│   ├── crawler.py          # 크롤링 프로세스 관리
│   ├── firecrawl.py        # FireCrawl API 연동
│   ├── summarizer.py       # OpenAI 요약 서비스
│   └── notion.py           # Notion API 연동
│
└── utils/                  # 유틸리티
    └── logger.py           # 로깅 유틸리티
```

- **Flask 웹 서버**: 요청을 처리하고 크롤링 프로세스를 시작합니다.
- **FireCrawl 모듈**: LLM 기반 웹 크롤링을 수행합니다.
- **OpenAI 요약 모듈**: GPT-3.5-turbo로 기사 내용을 요약합니다.
- **Notion API 연동**: 처리된 정보를 Notion 데이터베이스에 저장합니다.
- **Cloud Run**: 서버리스 환경에서 애플리케이션을 실행합니다.

## 실행 방법

### 로컬에서 실행

1. 가상 환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 패키지 설치
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정
`.env` 파일에 다음 내용을 설정합니다:
```
OPENAI_API_KEY=your_openai_api_key
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_notion_database_id
FIRECRAWL_API_KEY=your_firecrawl_api_key
LOG_LEVEL=INFO
PORT=8080
```

4. 애플리케이션 실행
```bash
python app.py
```

### Google Cloud Run에 배포

1. Google Cloud SDK 설치
   [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)

2. 프로젝트 설정 및 인증
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

3. 필요한 API 활성화
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
```

4. 이미지 빌드 및 배포
```bash
gcloud builds submit --config cloudbuild.yaml
gcloud run services update newsscrap-service \
    --set-env-vars="OPENAI_API_KEY=your_openai_api_key,NOTION_TOKEN=your_notion_token,NOTION_DATABASE_ID=your_database_id,FIRECRAWL_API_KEY=your_firecrawl_api_key" \
    --region=asia-northeast3
```

5. 스케줄러 설정 (선택 사항)
```bash
gcloud scheduler jobs create http newsscrap-daily \
    --schedule="0 7 * * * " \
    --uri="https://newsscrap-service-639453608377.asia-northeast3.run.app" \
    --http-method=GET \
    --time-zone="Asia/Seoul" \
    --project=newsscrap-456607 \
    --location=asia-northeast3
```

## 환경 변수

- `OPENAI_API_KEY`: OpenAI API 키
- `NOTION_TOKEN`: Notion API 통합 토큰
- `NOTION_DATABASE_ID`: Notion 데이터베이스 ID
- `FIRECRAWL_API_KEY`: FireCrawl API 키
- `LOG_LEVEL`: 로깅 레벨 (INFO, DEBUG, ERROR 등)
- `PORT`: 애플리케이션 포트 (기본값: 8080)

## 주의사항

- Notion 데이터베이스는 미리 생성되어 있어야 하며, 필요한 프로퍼티가 설정되어 있어야 합니다.
- 민감한 API 키와 토큰은 반드시 Cloud Run의 환경 변수로 설정해야 합니다. .env 파일은 자동으로 업로드되지 않습니다.
- 크롤링 대상 사이트의 이용 약관 및 저작권을 존중해야 합니다.
- 배포 시 클라우드 비용이 발생할 수 있으므로 사용량을 모니터링하세요. 