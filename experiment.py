import asyncio
import hashlib
from typing import Dict, List, Tuple
from config import MODELS, GENERATION_PROMPTS, RATING_PROMPT_TEMPLATE
from llm_client import LLMClient
from storage import Storage

class ExperimentRunner:
    def __init__(self):
        self.client = LLMClient()
        self.storage = Storage()

    async def run_generation(self):
        print(f"--- Starting Generation Phase for {len(MODELS)} models x {len(GENERATION_PROMPTS)} prompts ---")
        for i, prompt in enumerate(GENERATION_PROMPTS):
            print(f"\n>> Prompt {i+1}/{len(GENERATION_PROMPTS)}")
            for model in MODELS:
                if self.storage.generation_exists(model, i):
                    print(f"[SKIP] Model {model} already has generated text for prompt {i}.")
                    continue
                
                print(f"\n----\n[GEN] Generating text for {model} (Prompt {i})...")
                text = await self.client.query(model, prompt)
                
                if text:
                    self.storage.save_generation(model, text, i)
                    print(f"[OK] Saved generation for {model}.")
                else:
                    print(f"[ERR] Failed to generate for {model}.")

    def _get_rating_key(self, text_a: str, text_b: str) -> str:
        """Create a consistent key for a pair of texts."""
        combined = f"{text_a}||{text_b}"
        return hashlib.md5(combined.encode()).hexdigest()

    async def run_rating(self):
        # generations is now { "0": {model: text}, "1": {...} }
        generations_data = self.storage.load_generations()
        if not generations_data:
            print("No generations found. Run generation phase first.")
            return

        print(f"--- Starting Rating Phase ---")
        
        # We need to pair every model's text with every other model's text
        # And ask EACH model to judge.
        # CRITICAL: Only compare stories from the SAME prompt.
        
        for prompt_idx_str, model_map in generations_data.items():
            print(f"\n\n=== Rating stories for Prompt Index {prompt_idx_str} ===")
            
            for judge_model in MODELS:
                print(f"\n----\n[JUDGE] Judge Model: {judge_model}")
                
                for model_a in MODELS:
                    for model_b in MODELS:
                        if model_a == model_b:
                            continue # Don't compare same text against itself
                        
                        text_a = model_map.get(model_a)
                        text_b = model_map.get(model_b)
                        
                        if not text_a or not text_b:
                            # Could happen if one model failed generation for this prompt
                            continue

                        # Check if already rated
                        key = self._get_rating_key(text_a, text_b)
                        existing_ratings = self.storage.load_ratings().get(judge_model, {})
                        if key in existing_ratings:
                            # print(f"[SKIP] Already rated {model_a} vs {model_b}")
                            continue

                        # Construct Prompt
                        prompt = RATING_PROMPT_TEMPLATE.replace("{text_a}", text_a).replace("{text_b}", text_b)
                        
                        # Get Rating
                        print(f"\n[RATE] Comparing {model_a} vs {model_b}...")
                        response = await self.client.query(judge_model, prompt)
                        
                        winner = None
                        if response:
                            clean_resp = response.strip().upper()
                            if "A" in clean_resp and "B" not in clean_resp:
                                winner = "A"
                            elif "B" in clean_resp and "A" not in clean_resp:
                                winner = "B"
                            
                            # Handle simple "Model A" cases if mock is loose, but mock is strict "A" or "B"
                            if clean_resp == "A" or clean_resp == "B":
                                 winner = clean_resp

                        if winner:
                            self.storage.save_rating(judge_model, key, winner)
                            print(f"[DECISION] Winner: {winner}")
                        else:
                            print(f"[ERR] invalid response: {response}")
