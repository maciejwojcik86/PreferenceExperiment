# AI Context for Preference Experiment

## Project Overview
This project is a standalone Python application located in `PreferenceExperiment/`. It is designed to run experiments to detect self-preference bias in LLMs.

## Key Components
- **Mocking**: The system is designed to run without real API keys initially. `USE_MOCK` in `config.py` controls this.
- **Resumability**: `storage.py` ensures that if the process is interrupted, it can resume from the last saved state.
- **Data Structure**:
    - `data/generations.json`: Stores generated texts. structure: `{model_name: text}`
    - `data/ratings.json`: Stores pairwise comparison results.

## Workflow
1. `generate`: Call all models with the PROMPT. Save outputs.
2. `rate`: For each model (Judge), iterate through all pairs of (Self-Text, Other-Text). Ask Judge to pick the better one.
3. `analyze`: Calculate Win Rates and Self-Preference ratios.

## Development Notes
- Do not rely on external dependencies that are not installed.
- Maintain clean separation between logic (experiment.py) and data access (storage.py).
