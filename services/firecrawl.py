import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils.logger import logger
from config import Config

class FireCrawl:
    """FireCrawl API 관련 기능 클래스"""
    
    def __init__(self):
        """FireCrawl API 초기화"""
        self.api_key = Config.FireCrawl.API_KEY
        self.api_url = "https://api.firecrawl.dev/scrape"
    
    def scrape(self, options):
        """
        FireCrawl API로 웹 페이지 스크래핑
        
        Args:
            options (dict): 스크래핑 옵션 (url, formats, extract 등)
            
        Returns:
            dict: 스크래핑 결과
        """
        try:
            logger.info(f"FireCrawl API 스크래핑 시작: {options['url']}")
            
            # API 헤더 설정
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # API 요청
            response = requests.post(
                self.api_url,
                headers=headers,
                json=options,
                timeout=60
            )
            
            # 응답 확인
            response.raise_for_status()
            
            logger.info(f"FireCrawl API 스크래핑 완료: {options['url']}")
            return response.json()
            
        except Exception as error:
            logger.error(f"FireCrawl API 오류: {str(error)}")
            
            # 대체 방법: 직접 크롤링 시도
            logger.info(f"대체 방법으로 직접 크롤링 시도: {options['url']}")
            return self._fallback_scrape(options)
    
    def _fallback_scrape(self, options):
        """
        API 실패시 직접 크롤링 시도
        
        Args:
            options (dict): 스크래핑 옵션
            
        Returns:
            dict: 스크래핑 결과
        """
        try:
            # 웹페이지 요청
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            }
            
            response = requests.get(
                options["url"],
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 결과 객체
            result = {}
            
            # 요청에 formats가 있고 extract가 포함되어 있는 경우
            if "formats" in options and "extract" in options.get("formats", []):
                extract_prompt = options.get("extract", {}).get("prompt", "")
                
                # 헤드라인 추출하는 경우
                if "헤드라인" in extract_prompt:
                    headlines = self._extract_headlines(soup, options["url"])
                    result["result"] = {"extract": headlines}
                    logger.info(f"대체 방법으로 {len(headlines)}개 헤드라인 추출 완료: {options['url']}")
                
                # 기사 본문 추출하는 경우
                elif "본문" in extract_prompt:
                    content = self._extract_content(soup, options["url"])
                    result["result"] = {"extract": {"content": content}}
                    logger.info(f"대체 방법으로 기사 본문 추출 완료 ({len(content)} 글자): {options['url']}")
            
            return result
            
        except Exception as fallback_error:
            logger.error(f"대체 크롤링 방법도 실패: {str(fallback_error)}")
            raise
    
    def _extract_headlines(self, soup, url):
        """
        BeautifulSoup으로 헤드라인 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML
            url (str): 웹페이지 URL
            
        Returns:
            list: 헤드라인 목록
        """
        headlines = []
        base_url = url
        
        # 일반적인 뉴스 사이트 패턴의 CSS 선택자
        selectors = [
            "h1 a", "h2 a", "h3 a", ".headline a", ".title a",
            ".card a", ".news-item a", ".article-title a"
        ]
        
        # 각 선택자에 대해 요소 찾기
        for selector in selectors:
            elements = soup.select(selector)
            
            for element in elements:
                if len(headlines) >= 5:
                    break
                    
                title = element.get_text().strip()
                link = element.get("href", "")
                
                # 상대 경로를 절대 경로로 변환
                if link and not link.startswith(("http://", "https://")):
                    link = urljoin(base_url, link)
                
                # 중복 방지 및 유효성 검사
                if title and link and not any(h["title"] == title for h in headlines):
                    headlines.append({"title": title, "url": link})
        
        return headlines[:5]  # 최대 5개
    
    def _extract_content(self, soup, url):
        """
        BeautifulSoup으로 기사 본문 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML
            url (str): 웹페이지 URL
            
        Returns:
            str: 추출된 기사 본문
        """
        # 일반적인 뉴스 본문 컨테이너 CSS 선택자
        content_selectors = [
            "article", ".article", ".article-content", ".story-content",
            ".news-content", ".entry-content", ".post-content",
            "#article-body", ".article-body", ".article__body"
        ]
        
        # 각 선택자 시도
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # 불필요한 요소 제거 (광고, 관련기사 등)
                for unwanted in content_element.select(".ad, .advertisement, .related, .share, .social, .comments"):
                    unwanted.decompose()
                
                # 텍스트 추출 및 정리
                content = content_element.get_text().strip()
                content = " ".join(line.strip() for line in content.splitlines() if line.strip())
                
                if content:
                    return content
        
        # 선택자로 찾지 못한 경우 단락 텍스트 수집
        paragraphs = soup.select("p")
        content = " ".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
        
        return content


# 싱글톤 인스턴스
firecrawl = FireCrawl() 