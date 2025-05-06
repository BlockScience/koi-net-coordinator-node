from pydantic import Field
from rid_lib.types import KoiNetNode, KoiNetEdge
from koi_net.config import Config, KoiNetConfig
from koi_net.protocol.node import NodeProfile, NodeProvides, NodeType

class CoordinatorConfig(Config):
    koi_net: KoiNetConfig | None = Field(default_factory = lambda:
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