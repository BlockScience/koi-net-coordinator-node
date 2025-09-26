from koi_net.core import NodeAssembler
from .config import CoordinatorConfig
from .handlers import handshake_handler


class CoordinatorAssembler(NodeAssembler):
    config = CoordinatorConfig
    knowledge_handlers = [
        *NodeAssembler.knowledge_handlers,
        handshake_handler
    ]