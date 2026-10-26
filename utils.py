
import logging
from datetime import datetime
from pathlib import Path
import config

def setup_logging():
    log_dir = Path(config.LOGS_DIR)
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(log_dir / "icrawler.log"), logging.StreamHandler()])
    return logging.getLogger(__name__)

def save_output(brief: str, output: str, category: str, sandbox: str = "cosper"):
    output_dir = Path(config.BASE_DIR) / "workspaces" / sandbox
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"output_plan_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"<!-- BRIEF_START\n{brief}\nBRIEF_END -->\n\n")
        f.write(output)
    return filename
