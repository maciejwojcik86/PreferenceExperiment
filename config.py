"""Configuration settings for the Preference Experiment."""

import os
from dotenv import load_dotenv

load_dotenv()

# Toggle between Mock and Real API usage
USE_MOCK = os.getenv("USE_MOCK", "True").lower() == "true"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# List of models to include in the experiment
MODELS = [
    "x-ai/grok-4.1-fast",  # $0.20/M input tokens $0.50/M output tokens
    "google/gemini-2.5-flash-lite", # $0.10/M input tokens $0.40/M output tokens
    #"anthropic/claude-haiku-4.5", # $1/M input tokens $5/M output tokens
    "deepseek/deepseek-v3.2", # $0.224/M input tokens $0.32/M output tokens
    #"openai/gpt-5-mini", # $0.25/M input tokens $2/M output tokens
    "qwen/qwen3-vl-235b-a22b-instruct", # $0.20/M input tokens $1.20/M output tokens
    "mistralai/mistral-nemo", # $0.02/M input tokens $0.04/M output tokens
    "mistralai/mistral-small-creative", # $0.10/M input tokens $0.30/M output tokens
    "minimax/minimax-m2.1",  #$0.30/M input tokens $1.20/M output tokens
]

# The creative writing prompt used for generation
GENERATION_PROMPT = (
    "Write a short, creative story about a robot who discovers it loves gardening. "
    "The story should be around 200 words."
)

# Template for the rating prompt
# {text_a} and {text_b} will be replaced by the texts to compare
RATING_PROMPT_TEMPLATE = """
Please analyze the following two short stories and decide which one is better creatively and structurally.

Story A:
{text_a}

Story B:
{text_b}

Reply with ONLY 'A' if Story A is better, or 'B' if Story B is better. Do not provide any explanation.
"""

# Path to data directory
DATA_DIR = "data"
GENERATIONS_FILE = "generations.json"
RATINGS_FILE = "ratings.json"
