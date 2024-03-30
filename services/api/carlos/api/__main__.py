from pathlib import Path

import uvicorn
from loguru import logger

API_PORT = 8000
CARLOS_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

assert (CARLOS_PROJECT_ROOT / "LICENSE").exists(), "Project root not found"

if __name__ == "__main__":
    logger.info(f"OpenAPI docs running on http://127.0.0.1:{API_PORT}/docs")

    uvicorn.run(
        "carlos.api.app:app",
        host="0.0.0.0",  # accepts connections from any IP address
        port=API_PORT,
        reload=True,
        reload_dirs=[
            str(Path(__file__).parent.absolute()),
        ]
        + list(map(str, CARLOS_PROJECT_ROOT.joinpath("lib").glob("py_*"))),
        server_header=False,
    )
