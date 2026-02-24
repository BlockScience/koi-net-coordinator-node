from koi_net.core import FullNode
from .config import CoordinatorConfig
from .handshake_handler import HandshakeHandler


class CoordinatorNode(FullNode):
    config_schema = CoordinatorConfig
    handshake_handler = HandshakeHandler