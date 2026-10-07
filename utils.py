import logging
from datetime import datetime
from pathlib import Path
import config

def setup_logging():
    log_dir = Path(config.LOGS_DIR)
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_dir / "icrawler.log"), logging.StreamHandler()]
    )
    return logging.getLogger(__name__)

def save_output(brief: str, output: str, category: str):
    output_dir = Path(config.CACHE_DIR)
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"output_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"BRIEF:\n{brief}\n\nOUTPUT:\n{output}\n\nCATEGORY: {category}\nTIMESTAMP: {datetime.now().isoformat()}\n")
    return filename
