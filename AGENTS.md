# AI Context for Preference Experiment

## Project Overview
This project is a standalone Python application located in `PreferenceExperiment/`. It is designed to run experiments to detect self-preference bias in LLMs.

## Key Components
- **Mocking**: The system is designed to run without real API keys initially. `USE_MOCK` in `config.py` controls this.
- **Resumability**: `storage.py` ensures that if the process is interrupted, it can resume from the last saved state.
- **Data Structure**:
    - `results/generations.json`: Stores generated texts. structure: `{model_name: text}`
    - `results/ratings.json`: Stores pairwise comparison results.

## Workflow
1. `generate`: Iterate through all configured PROMPTS. For each prompt, call all models. Save outputs grouped by prompt index.
2. `rate`: For each model (Judge), iterate through all pairs of (Self-Text, Other-Text). Ask Judge to pick the better one.
3. `analyze`: Calculate Win Rates and Self-Preference ratios.
4. `combined_analysis`: (Optional) Aggregate multiple run folders in `results/` to gain statistical significance.

## Development Notes
- Do not rely on external dependencies that are not installed.
- Maintain clean separation between logic (experiment.py) and data access (storage.py).
