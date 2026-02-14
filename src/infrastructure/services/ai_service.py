import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List
from src.domain.entities import Comment

load_dotenv()


class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.enabled = False

        if not api_key:
            print("⚠️ WARNING: GEMINI_API_KEY not found in env!")
        else:
            # --- DEBUG BLOCK ---
            # Показываем первые 5 символов и длину, чтобы понять, не попал ли мусор
            print(f"DEBUG: Key loaded. Starts with: '{api_key[:5]}...', Length: {len(api_key)}")
            # -------------------

            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.enabled = True
                print("✅ AI Service Initialized Successfully")
            except Exception as e:
                print(f"❌ AI Init Error: {e}")

    async def analyze_task_context(self, title: str, description: str | None, comments: List[Comment]) -> str:
        if not self.enabled:
            return "AI Service is disabled (Check API Key)."

        # Собираем контекст
        comments_text = "\n".join([f"- {c.text}" for c in comments]) if comments else "No comments yet."

        prompt = f"""
        Act as a Senior Project Manager. Analyze this task:
        Title: {title}
        Description: {description or 'No description'}

        Team Discussion:
        {comments_text}

        Provide 3 short, actionable tips to move forward.
        """

        try:
            # Асинхронный вызов
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            # ВОТ ЗДЕСЬ МЫ УВИДИМ РЕАЛЬНУЮ ПРИЧИНУ В КОНСОЛИ
            print(f"\n🔥 CRITICAL AI ERROR: {e}\n")
            return (
                f"Note: AI Cloud connection failed. Error details logged in server console. "
                f"Local tip: Check task clarity and assignee availability."
            )