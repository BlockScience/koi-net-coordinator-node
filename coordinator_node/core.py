from rid_lib.ext import Cache
from rid_lib.types import KoiNetNode, KoiNetEdge
from koi_net import NodeInterface
from koi_net.protocol.node import NodeProfile, NodeType, NodeProvides
from .config import PORT


node = NodeInterface(
    name="coordinator",
    cache=Cache(".cache"),
    profile=NodeProfile(
        base_url=f"http://127.0.0.1:{PORT}/koi-net",
        node_type=NodeType.FULL,
        provides=NodeProvides(
            event=[KoiNetNode, KoiNetEdge],
            state=[KoiNetNode, KoiNetEdge]
        )
    )
)

from . import handlers