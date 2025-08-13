from pydantic import Field
from rid_lib.types import KoiNetNode, KoiNetEdge
from koi_net.config import NodeConfig, KoiNetConfig, ServerConfig
from koi_net.protocol.node import NodeProfile, NodeProvides, NodeType

class CoordinatorConfig(NodeConfig):
    server: ServerConfig = Field(default_factory=lambda: 
        ServerConfig(
            port=8080
        )
    )
    koi_net: KoiNetConfig = Field(default_factory=lambda:
        KoiNetConfig(
            node_name="coordinator",
            node_profile=NodeProfile(
                node_type=NodeType.FULL,
                provides=NodeProvides(
                    event=[KoiNetNode, KoiNetEdge],
                    state=[KoiNetNode, KoiNetEdge]
                )
            )
        )
    )