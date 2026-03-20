from pathlib import Path
import yaml

def load_prompts() -> dict:
    base_dir = Path(__file__).resolve().parent
    prompt_path = base_dir / "prompts.yaml"
    with open(prompt_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)