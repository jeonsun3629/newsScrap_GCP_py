from notion_client import Client
from datetime import datetime
from utils.logger import logger
from config import Config

class NotionService:
    """Notion 데이터베이스 통합 클래스"""
    
    def __init__(self):
        """Notion API 초기화"""
        self.token = Config.Notion.TOKEN
        self.database_id = Config.Notion.DATABASE_ID
        self.property_fields = Config.Notion.PROPERTY_FIELDS
        
        # Notion 클라이언트 초기화
        self.client = Client(auth=self.token)
    
    def save_to_notion(self, article):
        """
        기사 정보를 Notion 데이터베이스에 저장
        
        Args:
            article (dict): 저장할 기사 정보
            
        Returns:
            dict: 생성된 Notion 페이지 정보
        """
        logger.info(f"Notion에 저장 시작: {article['title']}")
        
        try:
            # 현재 날짜 생성
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Notion 페이지 속성 구성
            properties = {
                # 제목 속성
                self.property_fields["title"]: {
                    "title": [{"text": {"content": article["title"]}}]
                },
                # 요약 속성
                self.property_fields["summary"]: {
                    "rich_text": [{"text": {"content": article["summary"]}}]
                },
                # 국가 속성 (select 유형)
                self.property_fields["country"]: {
                    "select": {"name": article["country"]}
                },
                # 출처 속성
                self.property_fields["site"]: {
                    "rich_text": [{"text": {"content": article["site"]}}]
                },
                # 날짜 속성
                self.property_fields["crawled_at"]: {
                    "date": {"start": today}
                },
                # URL 속성
                self.property_fields["url"]: {
                    "url": article["url"]
                }
            }
            
            # Notion 페이지 생성 요청
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            logger.info(f"Notion에 저장 완료: {article['title']} (페이지 ID: {response['id']})")
            return response
            
        except Exception as error:
            logger.error(f"Notion 저장 오류 ({article['title']}): {str(error)}")
            return None


# 싱글톤 인스턴스
notion_service = NotionService() 