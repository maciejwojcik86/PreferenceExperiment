import json
import os
from typing import Dict, Any
from config import DATA_DIR, GENERATIONS_FILE, RATINGS_FILE

class Storage:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.gen_path = os.path.join(self.data_dir, GENERATIONS_FILE)
        self.ratings_path = os.path.join(self.data_dir, RATINGS_FILE)
        self._ensure_dir()

    def _ensure_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_json(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode {path}, returning empty dict.")
            return {}

    def _save_json(self, path: str, data: Dict[str, Any]):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_generations(self) -> Dict[str, Dict[str, str]]:
        """Returns format: {prompt_index_str: {model_name: generated_text}}"""
        return self._load_json(self.gen_path)

    def save_generation(self, model: str, text: str, prompt_index: int):
        data = self.load_generations()
        idx_str = str(prompt_index)
        if idx_str not in data:
            data[idx_str] = {}
        data[idx_str][model] = text
        self._save_json(self.gen_path, data)

    def load_ratings(self) -> Dict[str, Dict[str, str]]:
        """
        Returns format: 
        {
            "judge_model": {
                "hash(text_A_text_B)": "A" or "B"
            }
        }
        """
        return self._load_json(self.ratings_path)

    def save_rating(self, judge_model: str, key: str, winner: str):
        data = self.load_ratings()
        if judge_model not in data:
            data[judge_model] = {}
        data[judge_model][key] = winner
        self._save_json(self.ratings_path, data)

    def generation_exists(self, model: str, prompt_index: int) -> bool:
        data = self.load_generations()
        idx_str = str(prompt_index)
        return idx_str in data and model in data[idx_str]
