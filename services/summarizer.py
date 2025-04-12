from openai import OpenAI
from utils.logger import logger
from config import Config

class Summarizer:
    """뉴스 기사 요약 기능 클래스"""
    
    def __init__(self):
        """요약 기능 초기화"""
        self.api_key = Config.Summarization.API_KEY
        self.model = Config.Summarization.MODEL
        self.max_tokens = Config.Summarization.MAX_TOKENS
        self.temperature = Config.Summarization.TEMPERATURE
        self.prompt = Config.Summarization.PROMPT
        
        # OpenAI 클라이언트 초기화 - 최신 버전(1.0.0) 사용
        self.client = OpenAI(api_key=self.api_key)
    
    def summarize_article(self, article):
        """
        기사 내용을 요약
        
        Args:
            article (dict): 기사 정보 (title, content 등 포함)
            
        Returns:
            str: 요약된 내용
        """
        logger.info(f"기사 요약 시작: {article['title']}")
        
        try:
            # 프롬프트 생성
            prompt = f"{self.prompt}\n\n{article['content']}"
            
            # GPT-3.5-turbo를 이용하여 기사 요약 (최신 API 형식)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 뉴스 요약 전문가입니다. 핵심 내용을 2~3줄로 간결하게 요약해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # 최신 API 응답 형식에서 요약 텍스트 추출
            summary = response.choices[0].message.content.strip()
            
            if not summary:
                logger.warn(f"기사 요약 실패: 응답이 비어있음 ({article['title']})")
                return None
            
            logger.info(f"기사 요약 완료: {article['title']} ({len(summary)} 글자)")
            return summary
            
        except Exception as error:
            logger.error(f"기사 요약 오류 ({article['title']}): {str(error)}")
            return None


# 싱글톤 인스턴스
summarizer = Summarizer() 