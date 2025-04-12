import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class Config:
    """뉴스 크롤링 애플리케이션 설정"""
    
    # 국가별 뉴스 사이트 목록
    ALL_NEWS_SITES = {
        "한국": [
            {"name": "연합뉴스", "url": "https://www.yna.co.kr/"},
            {"name": "조선일보", "url": "https://www.chosun.com/"},
            {"name": "중앙일보", "url": "https://joongang.joins.com/"},
            {"name": "KBS", "url": "https://news.kbs.co.kr/"},
            {"name": "MBC", "url": "https://imnews.imbc.com/"}
        ],
        "일본": [
            {"name": "아사히 신문", "url": "https://www.asahi.com/"},
            {"name": "요미우리 신문", "url": "https://www.yomiuri.co.jp/"},
            {"name": "NHK", "url": "https://www3.nhk.or.jp/news/"},
            {"name": "마이니치 신문", "url": "https://mainichi.jp/"}
        ],
        "중국": [
            {"name": "신화통신", "url": "http://www.xinhuanet.com/"},
            {"name": "환구시보", "url": "https://www.globaltimes.cn/"},
            {"name": "CGTN", "url": "https://www.cgtn.com/"}
        ],
        "미국": [
            {"name": "CNN", "url": "https://www.cnn.com/"},
            {"name": "New York Times", "url": "https://www.nytimes.com/"},
            {"name": "Washington Post", "url": "https://www.washingtonpost.com/"},
            {"name": "Fox News", "url": "https://www.foxnews.com/"},
            {"name": "CNBC", "url": "https://www.cnbc.com/"}
        ],
        "영국": [
            {"name": "BBC", "url": "https://www.bbc.com/news"},
            {"name": "The Guardian", "url": "https://www.theguardian.com/"},
            {"name": "The Times", "url": "https://www.thetimes.co.uk/"},
            {"name": "Financial Times", "url": "https://www.ft.com/"}
        ],
        "프랑스": [
            {"name": "Le Monde", "url": "https://www.lemonde.fr/"},
            {"name": "Le Figaro", "url": "https://www.lefigaro.fr/"},
            {"name": "France 24", "url": "https://www.france24.com/"}
        ],
        "독일": [
            {"name": "Der Spiegel", "url": "https://www.spiegel.de/"},
            {"name": "Die Welt", "url": "https://www.welt.de/"},
            {"name": "Deutsche Welle", "url": "https://www.dw.com/"}
        ],
        "러시아": [
            {"name": "Russia Today", "url": "https://www.rt.com/"},
            {"name": "Tass", "url": "https://tass.com/"},
            {"name": "Pravda", "url": "https://www.pravda.ru/"}
        ],
        "인도": [
            {"name": "The Times of India", "url": "https://timesofindia.indiatimes.com/"},
            {"name": "Hindustan Times", "url": "https://www.hindustantimes.com/"},
            {"name": "The Hindu", "url": "https://www.thehindu.com/"}
        ],
        "브라질": [
            {"name": "O Globo", "url": "https://oglobo.globo.com/"},
            {"name": "Folha de S.Paulo", "url": "https://www.folha.uol.com.br/"}
        ],
        "호주": [
            {"name": "The Sydney Morning Herald", "url": "https://www.smh.com.au/"},
            {"name": "The Australian", "url": "https://www.theaustralian.com.au/"},
            {"name": "ABC News", "url": "https://www.abc.net.au/news/"}
        ],
        "캐나다": [
            {"name": "CBC", "url": "https://www.cbc.ca/news"},
            {"name": "The Globe and Mail", "url": "https://www.theglobeandmail.com/"}
        ],
        "남아프리카공화국": [
            {"name": "News24", "url": "https://www.news24.com/"},
            {"name": "Mail & Guardian", "url": "https://mg.co.za/"}
        ]
    }
    
    # 크롤러 설정
    class Crawler:
        # 랜덤으로 선택할 국가 수 (1개 국가만 선택)
        RANDOM_COUNTRIES = 5
        
        # 사이트당 추출할 헤드라인 수 (1개 뉴스만 선택)
        HEADLINES_PER_SITE = 1
        
        # 동시 요청 수 제한
        CONCURRENCY = 1
        
        # 타임아웃 설정 (ms)
        TIMEOUT = 30000
        
        # 재시도 횟수
        RETRIES = 2
        
        # 브라우저 사용자 에이전트
        USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    # FireCrawl 설정
    class FireCrawl:
        # API 키
        API_KEY = os.getenv('FIRECRAWL_API_KEY')
        
        # 헤드라인 추출 프롬프트 (5개 뉴스만 요청)
        HEADLINE_PROMPT = """이 페이지에서 광고를 제외하고 가장 중요한 뉴스 헤드라인 1개와 링크를 찾아서 반환해주세요. 헤드라인의 제목(title)과 링크(url)를 정확하게 추출하세요. title은 한국어로 반환해주세요. URL은 상대 경로인 경우 완전한 URL로 변환해주세요."""
        
        # 콘텐츠 추출 프롬프트
        CONTENT_PROMPT = """이 뉴스 기사의 본문 내용만 추출해주세요. 광고나 관련기사 링크, 댓글 섹션은 제외합니다. 기사 본문만 텍스트로 반환해주세요."""
    
    # 요약 설정 (GPT-3.5-turbo 사용)
    class Summarization:
        # API 키
        API_KEY = os.getenv('OPENAI_API_KEY')
        
        # 모델 설정
        MODEL = 'gpt-3.5-turbo'
        MAX_TOKENS = 1024
        
        # 요약 프롬프트
        PROMPT = """다음 뉴스 기사를 한국어로 간결하게 3-4문장으로 요약해주세요. 가장 중요한 사실과 정보를 포함시키세요."""
        
        TEMPERATURE = 0.5
    
    # Notion 통합 설정
    class Notion:
        # Notion API 토큰
        TOKEN = os.getenv('NOTION_TOKEN')
        
        # Notion 데이터베이스 ID
        DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
        
        # 프로퍼티 필드 이름
        PROPERTY_FIELDS = {
            'title': 'Title',
            'country': 'Country',
            'site': 'Source',
            'url': 'URL',
            'summary': 'Summary',
            'content': 'Content',
            'crawled_at': 'Date'
        } 