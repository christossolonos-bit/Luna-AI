"""
Run the combined agent (Luna + HIM + JEPA) from this folder.
All tokens and config stay here: .env, discord_token.txt, discord_config.json, twitch_config.json.
"""
import sys
from pathlib import Path

# Ensure we run from this folder
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load .env from this folder
env_file = ROOT / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
    except ImportError:
        pass

from luna_clean import main

if __name__ == "__main__":
    main()
