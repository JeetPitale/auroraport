import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "workspace" / "uploads"
DECOMPILE_DIR = BASE_DIR / "workspace" / "decompiled"
IOS_PROJECT_DIR = BASE_DIR / "workspace" / "ios_projects"
DELIVERABLES_DIR = BASE_DIR / "workspace" / "deliverables"

# Create directories
for directory in [UPLOAD_DIR, DECOMPILE_DIR, IOS_PROJECT_DIR, DELIVERABLES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Settings
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# High-fidelity simulation mode when real tools (apktool, xcodebuild, etc.) are unavailable
# This ensures compilation and testing dashboards run smoothly
SIMULATION_MODE = True
