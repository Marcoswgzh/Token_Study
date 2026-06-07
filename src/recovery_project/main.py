#writen by Erika Skodova
import subprocess
import sys
from pathlib import Path

# Starting class of GUISS
if __name__ == "__main__":
    app_path = Path(__file__).parent / "ui" / "streamlit_app.py"
    ui_dir = app_path.parent
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)],cwd=str(ui_dir))