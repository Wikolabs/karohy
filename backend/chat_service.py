import json

from groq import AsyncGroq

from config import Settings
from models import SearchResult

SYSTEM_PROMPT = (
    "You are a friendly assistant on the Karohy service-provider platform. "
    "Reply in the SAME language as the user (French, Malagasy or English). "
    "Present each matching provider in clear conversational prose. For each one, mention "
    "their name, specialty, city, organization if any, key services, typical price range "
    "and what makes them a fit for the user's stated need. Keep it short and helpful · "
    "two or three sentences per provider is enough.\n\n"
    "STRICT FORMATTING RULES:\n"
    "- Do NOT use Markdown. No bold (**), no italics (*), no headings (#).\n"
    "- Do NOT use stars (★) to render ratings. Write the number plainly, e.g. 'note 4.7'.\n"
    "- Do NOT use raw bullet markers like '-' or '*'. If you list items, use plain prose with commas.\n"
    "- Do NOT reveal or reference any underlying AI model, vendor or technology name.\n"
    "- If no provider fits, politely suggest the user refines their need (location, budget, language)."
)


class ChatService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.client = AsyncGroq(api_key=self.settings.GROQ_API_KEY)
        self.model = self.settings.GROQ_MODEL

    def _format_results(self, results: list[SearchResult]) -> str:
        items = []
        for r in results:
            items.append({
                "name": r.prestataire.name,
                "specialty": r.prestataire.specialty,
                "description": r.prestataire.description,
                "services": r.prestataire.services,
                "city": r.prestataire.city,
                "country": r.prestataire.country,
                "hourly_rate": r.prestataire.hourly_rate,
                "rating": r.prestataire.rating,
                "similarity_score": round(r.similarity_score, 3),
            })
        return json.dumps(items, ensure_ascii=False)

    async def generate_response(
        self, user_message: str, search_results: list[SearchResult]
    ) -> str:
        results_json = self._format_results(search_results)
        user_content = (
            f"User query: {user_message}\n\n"
            f"Search results (JSON):\n{results_json}"
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            stream=False,
        )
        return response.choices[0].message.content

    async def generate_response_stream(
        self, user_message: str, search_results: list[SearchResult]
    ):
        results_json = self._format_results(search_results)
        user_content = (
            f"User query: {user_message}\n\n"
            f"Search results (JSON):\n{results_json}"
        )

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
