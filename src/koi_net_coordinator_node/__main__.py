import uvicorn
from .core import node
from .server import app

uvicorn.run(
    app=app,
    host=node.config.server.host, 
    port=node.config.server.port
)