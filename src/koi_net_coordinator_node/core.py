from koi_net.core import FullNode
from .config import CoordinatorConfig
from .handlers import handshake_handler


class CoordinatorNode(FullNode):
    config_cls = CoordinatorConfig
    knowledge_handlers = FullNode.knowledge_handlers + [
        handshake_handler
    ]