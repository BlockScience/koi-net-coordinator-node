from rid_lib.types import KoiNetNode, KoiNetEdge
from koi_net import NodeInterface
from koi_net.protocol.node import NodeProfile, NodeType, NodeProvides
from .config import PORT


node = NodeInterface(
    name="coordinator",
    profile=NodeProfile(
        base_url=f"http://127.0.0.1:{PORT}/koi-net",
        node_type=NodeType.FULL,
        provides=NodeProvides(
            event=[KoiNetNode, KoiNetEdge],
            state=[KoiNetNode, KoiNetEdge]
        )
    ),
    use_kobj_processor_thread=True
)

from . import handlers