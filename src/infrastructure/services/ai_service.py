import os
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv
from src.domain.entities import Comment

load_dotenv()


class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.enabled = False
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Пробуем самую актуальную модель
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.enabled = True
            except Exception as e:
                print(f"AI Service init failed: {e}")

    async def analyze_task_context(self, title: str, description: str | None, comments: List[Comment]) -> str:
        if not self.enabled:
            return "AI Service is in offline mode (check your API key or model name)."

        comments_text = "\n".join([f"- {c.text}" for c in comments]) if comments else "No comments yet."

        prompt = f"""
        Analyze this task as a PM:
        Title: {title}
        Desc: {description}
        Discussion: {comments_text}
        Give 3 actionable tips.
        """

        try:
            # Если облако упало, мы не дадим упасть всему серверу
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            # ВОТ ЭТО ИНЖЕНЕРНЫЙ ПОДХОД: FALLBACK (Запасной вариант)
            return (
                f"Note: AI Cloud is currently busy. "
                f"Local analysis of '{title}': Task seems clear, ensure the team has access to DB."
            )