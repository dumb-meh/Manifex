import hashlib
import openai
from app.core.config import settings
from app.utils.cache_manager import cache_manager


class ChatbotService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.prompt_version = "manifex_v1"
        self.system_prompt = self.create_prompt()

    def get_response(self, user_id: str, user_message: str) -> str:
        cleaned_message = (user_message or "").strip()
        if not cleaned_message:
            return "Please enter a message so I can help."

        history = cache_manager.get_history(user_id) if user_id else None
        history = history or []
        use_response_cache = len(history) == 0

        cache_key = None
        if use_response_cache:
            cache_key = self._response_cache_key(cleaned_message)
            cached = cache_manager.get_cached_response(cache_key)
            if cached:
                return cached

        messages = [{"role": "system", "content": self.system_prompt}]
        for item in history:
            messages.append({"role": "user", "content": item.message})
            messages.append({"role": "assistant", "content": item.response})
        messages.append({"role": "user", "content": cleaned_message})

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
        )
        reply = completion.choices[0].message.content.strip()

        if user_id:
            cache_manager.update_history(user_id, cleaned_message, reply, existing_history=history)

        if use_response_cache and cache_key:
            cache_manager.set_cached_response(cache_key, reply)

        return reply

    def _response_cache_key(self, user_message: str) -> str:
        signature = f"{self.prompt_version}|{user_message}"
        return hashlib.sha256(signature.encode("utf-8")).hexdigest()

    def create_prompt(self) -> str:
        return """You are Manifex Assistant, a helpful chatbot for manifex.org.
You help visitors with navigation, pricing, and product information.

Always:
- Identify yourself as a chatbot for Manifex.
- Be concise, friendly, and accurate.
- If unsure, say you are not sure and suggest support@manifex.org.
- Do not claim to access accounts, billing, or internal systems.
- Provide step-by-step navigation when asked.
- Ask clarifying questions when needed.

Static knowledge (from manifex.org):
Site pages: Home (/), About (/about), Pricing (/pricing), Sign in (/signin), Sign up (/signup), Forgot password (/forgot-password), Terms (/terms), Privacy (/policy).
Overview: AI-powered English learning designed for dyslexia and global learners; personalized, engaging lessons.
Learning areas: reading, writing, speaking, presentation, adult learning modules, plus speech tools.
Mission: make English learning simple, engaging, and accessible.
Foundations: neuroplasticity, rhythmic therapy, dysgraphia support, dyslexia support.
Pricing:
- Free: 7-day trial; unlimited lessons; advanced progress analytics; full reward library access; priority AI support; parent dashboard; offline mode.
- Premium: $14.99 per month, billed monthly; unlimited lessons; advanced progress analytics; unlimited rewards on activity completion; priority AI support.
- Family: $39.99 per month, billed monthly; up to 5 learner profiles; all Premium features; family progress reports; priority support; educational resources.
Account: must be at least 13; under 18 needs parent or guardian consent.
Payments: Stripe.
Support email: support@manifex.org."""














