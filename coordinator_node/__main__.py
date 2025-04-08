import uvicorn
from .config import PORT

uvicorn.run("coordinator_node.server:app", port=PORT)