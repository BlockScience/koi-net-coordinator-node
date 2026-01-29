import structlog
from koi_net.core import FullNode
from .config import CoordinatorConfig
from . import handlers

log = structlog.stdlib.get_logger()


class CoordinatorNode(FullNode):
    config_schema = CoordinatorConfig
    knowledge_handlers = FullNode.knowledge_handlers + handlers.knowledge_handlers


if __name__ == "__main__":
    CoordinatorNode().run()
