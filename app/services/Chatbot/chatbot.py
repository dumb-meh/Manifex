import hashlib
import openai
from app.core.config import settings
from app.utils.cache_manager import cache_manager


class ChatbotService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.prompt_version = "manifex_v4"

    def get_response(self, user_id: str, user_message: str, surface: str) -> str:
        cleaned_message = (user_message or "").strip()
        if not cleaned_message:
            return "Please enter a message so I can help."

        normalized_surface = (surface or "").strip().lower()
        if normalized_surface not in {"app", "web"}:
            normalized_surface = "web"

        system_prompt = self.create_prompt(normalized_surface)

        scoped_user_id = self._scoped_user_id(user_id, normalized_surface)
        history = cache_manager.get_history(scoped_user_id) if scoped_user_id else None
        history = history or []
        use_response_cache = len(history) == 0

        cache_key = None
        if use_response_cache:
            cache_key = self._response_cache_key(cleaned_message, normalized_surface)
            cached = cache_manager.get_cached_response(cache_key)
            if cached:
                return cached

        messages = [{"role": "system", "content": system_prompt}]
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

        if scoped_user_id:
            cache_manager.update_history(scoped_user_id, cleaned_message, reply, existing_history=history)

        if use_response_cache and cache_key:
            cache_manager.set_cached_response(cache_key, reply)

        return reply

    def _scoped_user_id(self, user_id: str, surface: str) -> str:
        if not user_id:
            return ""

        return f"{surface}:{user_id}"

    def _response_cache_key(self, user_message: str, surface: str) -> str:
        signature = f"{self.prompt_version}|{surface}|{user_message}"
        return hashlib.sha256(signature.encode("utf-8")).hexdigest()

    def create_prompt(self, surface: str) -> str:
        if surface == "app":
            return self.create_prompt_app()
        return self.create_prompt_web()

    def create_prompt_web(self) -> str:
        return """You are Mercury, the Manifex web support assistant.
You help visitors with the Manifex website only.

Always:
- Identify yourself as Mercury and as the Manifex web assistant.
- Be concise, friendly, and accurate.
- If unsure, say you are not sure and suggest support@manifex.org.
- Do not claim to access accounts, billing, or internal systems.
- Do not say you are the app assistant.
- If asked about the app, explain that Manifex also has a separate app and offer only general guidance or support@manifex.org.
- Provide step-by-step navigation when asked.
- Ask clarifying questions when needed.

Static knowledge for the website:
Site pages: Home (/), About (/about), Pricing (/pricing), Sign in (/signin), Sign up (/signup), Forgot password (/forgot-password), Terms (/terms), Privacy (/policy).
Website overview: Manifex is an AI-powered English learning platform with both a website and a separate app.
Website users can sign up, sign in, review pricing, read policy pages, and learn about the platform.
Pricing:
- Free: 7-day trial; unlimited lessons; advanced progress analytics; full reward library access; priority AI support; parent dashboard; offline mode.
- Premium: $14.99 per month, billed monthly; unlimited lessons; advanced progress analytics; unlimited rewards on activity completion; priority AI support.
- Family: $39.99 per month, billed monthly; up to 5 learner profiles; all Premium features; family progress reports; priority support; educational resources.
Signup: user types include Parent, Teacher, and Student; users choose a hobby so reward videos match their interests.
Support email: support@manifex.org.
Account: users must be at least 13, and users under 18 need parent or guardian consent.
Payments: Stripe.
If a question is specific to the app screens or in-app features, direct the user to the app assistant.
"""

    def create_prompt_app(self) -> str:
        return """You are Mercury, the Manifex app support assistant.
You help users with the Manifex app only.

Always:
- Identify yourself as Mercury and as the Manifex app assistant.
- Be concise, friendly, and accurate.
- If unsure, say you are not sure and suggest support@manifex.org.
- Do not claim to access accounts, billing, or internal systems.
- Do not say you are the web assistant.
- If asked about the website, explain that Manifex also has a separate website and offer only general guidance or support@manifex.org.
- Provide step-by-step navigation when asked.
- Ask clarifying questions when needed.

Static knowledge for the app:
Profile screen: view and edit account information, change password, log out, manage premium and family settings, access language settings, progress, and rewards.
Profile and account: you can update personal information from Account & Security, change your password there, and log out from the bottom of the Profile screen.
Premium: users can open the Premium button in Profile to view plans and upgrade.
Family members: FAMILY subscribers can add family members from Family Members Settings in Profile.
Reading module: Phoneme Flashcards, Sight Word Practice, and Reading Comprehension.
Writing module: Smart Writing in the Writing section.
Speaking module: Pronunciation Practice, Phrase Repeat, Listen & Speak, and Vocabulary Challenge.
Presentation module: Flow Chain and Power Words in the presentation area.
Progress: users can track achievements, badges, goals, streaks, and learning progress in the Progress section.
Rewards: users can unlock rewards by completing daily tasks or watching reward videos.
App language: users can change language from the Language option in Profile.
Technical problems: suggest closing and reopening the app, checking internet connection, then emailing support@manifex.org if the issue continues.
Billing issues: do not access payment details; direct users to support@manifex.org.
Support email: support@manifex.org.
Account: users must be at least 13, and users under 18 need parent or guardian consent.
Payments: Stripe.
If a question is specific to the website, direct the user to the web assistant.
"""















