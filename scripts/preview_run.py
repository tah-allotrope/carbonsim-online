"""Preview launcher for the Claude Code preview server.

Runs the FastAPI app via uvicorn. Honors the PORT env var (the preview harness
sets it when autoPort picks a free port); defaults to 8000.
"""

import os
import sys
from pathlib import Path

# Ensure the project root is importable regardless of the launcher's cwd.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("server.main:create_app", factory=True, host="127.0.0.1", port=port)
