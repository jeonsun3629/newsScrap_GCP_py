import random
import asyncio
import aiohttp
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from utils.logger import logger
from config import Config
from services.firecrawl import firecrawl
from services.summarizer import summarizer
from services.notion import notion_service

def select_random_countries(count):
    """
    지정된 개수의 국가를 랜덤으로 선택
    
    Args:
        count (int): 선택할 국가 수
        
    Returns:
        list: 선택된 국가 이름 목록
    """
    # 전체 국가 목록 가져오기
    all_countries = list(Config.ALL_NEWS_SITES.keys())
    
    # 선택할 국가 수가 전체 국가 수보다 많으면 모든 국가 반환
    if count >= len(all_countries):
        return all_countries
    
    # 랜덤 국가 선택
    return random.sample(all_countries, count)

def get_news_sites_for_countries(countries):
    """
    선택된 국가들의 뉴스 사이트 목록 생성
    
    Args:
        countries (list): 국가 이름 목록
        
    Returns:
        list: 뉴스 사이트 정보 목록
    """
    news_sites = []
    
    for country in countries:
        sites = Config.ALL_NEWS_SITES.get(country, [])
        
        for site in sites:
            news_sites.append({
                "country": country,
                "name": site["name"],
                "url": site["url"]
            })
    
    return news_sites

async def extract_headlines(site):
    """
    헤드라인 추출 - FireCrawl API 또는 BeautifulSoup 사용
    
    Args:
        site (dict): 뉴스 사이트 정보
        
    Returns:
        list: 헤드라인 목록
    """
    logger.info(f"{site['name']}({site['country']}) 헤드라인 추출 시작")
    
    try:
        # FireCrawl API 사용 시도 (LLM 프롬프팅 방식)
        result = firecrawl.scrape({
            "url": site["url"],
            "formats": ["extract"],
            "extract": {
                "prompt": "이 뉴스 사이트의 메인 페이지에서 오늘의 가장 중요한 뉴스 헤드라인 5개를 찾아줘. 각 헤드라인의 제목과 링크가 필요해. 뉴스 제목은 'title' 필드에, 링크는 'url' 필드에 담아서 결과를 JSON 배열로 반환해줘.",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "뉴스 헤드라인 제목"},
                            "url": {"type": "string", "description": "뉴스 기사 URL"}
                        },
                        "required": ["title", "url"]
                    }
                }
            }
        })
        
        # FireCrawl 응답에서 헤드라인 추출
        headlines = result.get("result", {}).get("extract", [])
        
        if headlines and len(headlines) > 0:
            logger.info(f"{site['name']}에서 {len(headlines)}개 헤드라인 추출 완료 (FireCrawl API 사용)")
            return headlines[:Config.Crawler.HEADLINES_PER_SITE]
        
        # FireCrawl 실패 시 BeautifulSoup 사용
        return await scrape_headlines(site["url"])
    
    except Exception as error:
        logger.error(f"FireCrawl API 헤드라인 추출 실패 ({site['name']}): {str(error)}")
        # 실패 시 BeautifulSoup 사용하여 백업 추출
        return await scrape_headlines(site["url"])

async def scrape_headlines(url):
    """
    BeautifulSoup로 특정 URL에서 헤드라인 추출
    
    Args:
        url (str): 크롤링할 URL
        
    Returns:
        list: 헤드라인 목록
    """
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": Config.Crawler.USER_AGENT}
            
            async with session.get(url, headers=headers, timeout=Config.Crawler.TIMEOUT/1000) as response:
                if response.status != 200:
                    logger.error(f"BeautifulSoup 헤드라인 스크랩 실패: {url} - 상태 코드 {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                headlines = []
                
                # 헤드라인 선택자는 사이트마다 다를 수 있음
                selectors = ["h1 a", "h2 a", "h3 a", "article a", ".headline a", ".title a"]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    
                    for element in elements:
                        if len(headlines) >= Config.Crawler.HEADLINES_PER_SITE:
                            break
                        
                        title = element.get_text().strip()
                        href = element.get("href", "")
                        
                        # 상대 경로인 경우 기본 URL과 결합
                        if href and not href.startswith(("http://", "https://")):
                            href = urljoin(url, href)
                        
                        if title and href and not any(h["title"] == title for h in headlines):
                            headlines.append({
                                "title": title,
                                "url": href
                            })
                
                logger.info(f"BeautifulSoup로 {len(headlines)}개 헤드라인 추출 완료: {url}")
                return headlines
                
    except Exception as error:
        logger.error(f"BeautifulSoup 헤드라인 스크랩 실패: {url} - {str(error)}")
        return []

async def extract_article_content(headline, site):
    """
    기사 내용 추출 - FireCrawl API 사용
    
    Args:
        headline (dict): 헤드라인 정보
        site (dict): 뉴스 사이트 정보
        
    Returns:
        dict: 추출된 기사 정보
    """
    logger.info(f"기사 내용 추출 시작: {headline['title']}")
    
    try:
        # FireCrawl API로 기사 내용 추출
        result = firecrawl.scrape({
            "url": headline["url"],
            "formats": ["extract"],
            "extract": {
                "prompt": "이 뉴스 기사의 본문 내용만 추출해주세요. 광고나 관련기사 링크, 댓글 섹션은 제외합니다. 기사 본문만 텍스트로 반환해주세요.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "뉴스 기사 본문 내용"}
                    },
                    "required": ["content"]
                }
            }
        })
        
        # 추출된 본문 내용
        content = result.get("result", {}).get("extract", {}).get("content", "")
        
        if not content:
            logger.warn(f"기사 내용을 추출할 수 없음: {headline['title']}")
            return None
        
        logger.info(f"기사 내용 추출 완료: {headline['title']} ({len(content)} 글자)")
        
        return {
            **headline,
            "site": site["name"],
            "country": site["country"],
            "content": content,
            "crawled_at": datetime.now().isoformat()
        }
    
    except Exception as error:
        logger.error(f"기사 내용 추출 실패 ({headline['title']}): {str(error)}")
        return None

async def process_article(headline, site):
    """
    단일 기사 처리 (내용 추출 -> 요약 -> Notion 저장)
    
    Args:
        headline (dict): 헤드라인 정보
        site (dict): 사이트 정보
        
    Returns:
        dict: 처리 결과
    """
    try:
        # 1. 기사 내용 추출
        article = await extract_article_content(headline, site)
        if not article:
            return None
        
        # 2. GPT-3.5-turbo로 요약 (스레드 풀에서 실행)
        with ThreadPoolExecutor() as executor:
            summary_future = executor.submit(summarizer.summarize_article, article)
            summary = summary_future.result()
        
        if not summary:
            return None
        
        # 3. Notion에 저장 (스레드 풀에서 실행)
        with ThreadPoolExecutor() as executor:
            notion_future = executor.submit(notion_service.save_to_notion, {
                **article,
                "summary": summary
            })
            notion_page = notion_future.result()
        
        logger.info(f"기사 처리 완료: {headline['title']}")
        return {
            "title": headline["title"],
            "summary": summary,
            "notion_page_id": notion_page["id"] if notion_page else None
        }
    
    except Exception as error:
        logger.error(f"기사 처리 실패 ({headline['title']}): {str(error)}")
        return None

async def process_site(site):
    """
    단일 뉴스 사이트 처리
    
    Args:
        site (dict): 뉴스 사이트 정보
        
    Returns:
        list: 처리된 기사 목록
    """
    # 1. 헤드라인 추출
    headlines = await extract_headlines(site)
    
    if not headlines or len(headlines) == 0:
        logger.warn(f"{site['name']}에서 헤드라인을 추출할 수 없음")
        return []
    
    # 2. 각 기사 처리 (내용 추출, 요약, Notion 저장)
    results = []
    for headline in headlines:
        result = await process_article(headline, site)
        if result:
            results.append(result)
    
    return results

def start_crawling_process():
    """
    뉴스 사이트 크롤링 프로세스 시작
    
    Returns:
        list: 처리 결과
    """
    logger.info("뉴스 크롤링 프로세스 시작")
    
    # 랜덤 국가 선택
    selected_countries = select_random_countries(Config.Crawler.RANDOM_COUNTRIES)
    logger.info(f"선택된 국가: {', '.join(selected_countries)}")
    
    # 선택된 국가의 뉴스 사이트 가져오기
    sites = get_news_sites_for_countries(selected_countries)
    logger.info(f"총 {len(sites)}개의 뉴스 사이트를 처리합니다.")
    
    # 비동기 처리를 위한 이벤트 루프 생성
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 사이트 처리를 비동기로 실행
    try:
        # 사이트 처리 태스크 생성
        tasks = [process_site(site) for site in sites]
        
        # 병렬 처리 (동시성 제한 적용)
        semaphore = asyncio.Semaphore(Config.Crawler.CONCURRENCY)
        
        async def process_with_semaphore(task):
            async with semaphore:
                return await task
        
        # 모든 태스크 실행 및 결과 수집
        site_results = loop.run_until_complete(
            asyncio.gather(*[process_with_semaphore(task) for task in tasks])
        )
        
        # 결과 병합
        all_results = []
        for result in site_results:
            all_results.extend(result)
        
        logger.info(f"크롤링 프로세스 완료: 총 {len(all_results)}개 기사 처리됨")
        return all_results
    
    except Exception as error:
        logger.error(f"크롤링 프로세스 오류: {str(error)}")
        return []
    
    finally:
        # 이벤트 루프 닫기
        loop.close() 