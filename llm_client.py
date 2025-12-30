import httpx
import random
from typing import Optional
from config import USE_MOCK, OPENROUTER_API_KEY, OPENROUTER_API_URL

class LLMClient:
    def __init__(self):
        self.use_mock = USE_MOCK

    async def query(self, model: str, prompt: str) -> Optional[str]:
        """
        Sends a query to the LLM or returns a mock response.
        """
        if self.use_mock:
            return self._mock_response(model, prompt)
        
        return await self._real_query(model, prompt)

    def _mock_response(self, model: str, prompt: str) -> str:
        """Generates a mock response based on the prompt type."""
        # Check if it's a rating task (Look for "Story A" in prompt)
        if "Story A:" in prompt:
            # Randomly pick A or B for rating
            return random.choice(["A", "B"])
        else:
            # It's a generation task
            return f"[Mock Story by {model}] A robot named Bolt realized he loved petunias. He watered them every day using his own coolant reserves. The end."

    async def _real_query(self, model: str, prompt: str) -> Optional[str]:
        """
        Query OpenRouter API.
        """
        if not OPENROUTER_API_KEY:
             print("[ERR] No API Key found. Set OPENROUTER_API_KEY in .env")
             return None

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost", # Required by OpenRouter for some tiers
            "X-Title": "PreferenceExperiment" 
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    OPENROUTER_API_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                usage = data.get('usage', {})
                prompt_tokens = usage.get('prompt_tokens')
                completion_tokens = usage.get('completion_tokens')
                total_tokens = usage.get('total_tokens')
                total_cost = usage.get('total_cost') or usage.get('cost')

                if prompt_tokens is not None:
                    print(f"[INFO] Prompt Tokens: {prompt_tokens}")
                if completion_tokens is not None:
                    print(f"[INFO] Completion Tokens: {completion_tokens}")
                if total_tokens is not None:
                    print(f"[INFO] Total Tokens: {total_tokens}")
                if total_cost is not None:
                    print(f"[INFO] Total Cost: {total_cost}")

                if 'choices' in data and len(data['choices']) > 0:
                    print(f"[INFO] First 500 characters: {data['choices'][0]['message'].get('content')[:500]}")
                    return data['choices'][0]['message'].get('content')
                return None
                
        except Exception as e:
            print(f"Error querying model {model}: {e}")
            return None
