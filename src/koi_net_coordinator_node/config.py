from pydantic import Field
from rid_lib.types import KoiNetNode, KoiNetEdge
from koi_net.config.full_node import (
    NodeConfig, 
    KoiNetConfig, 
    ServerConfig, 
    NodeProfile, 
    NodeType, 
    NodeProvides
)


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