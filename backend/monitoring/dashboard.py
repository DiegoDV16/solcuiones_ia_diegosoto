import subprocess
import sys
from pathlib import Path


def run_dashboard():
    """Start the Streamlit monitoring dashboard."""
    dashboard_path = Path(__file__).resolve().parent.parent.parent / "dashboard_app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(dashboard_path), "--server.port", "8501"]
    subprocess.run(cmd)


if __name__ == "__main__":
    run_dashboard()
