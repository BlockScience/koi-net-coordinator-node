from rid_lib.types import KoiNetNode, KoiNetEdge
from koi_net.config import (
    FullNodeConfig, 
    KoiNetConfig, 
    ServerConfig, 
    FullNodeProfile, 
    NodeProvides
)


class CoordinatorConfig(FullNodeConfig):
    server: ServerConfig = ServerConfig(port=8080)
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="coordinator",
        node_profile=FullNodeProfile(
            provides=NodeProvides(
                event=[KoiNetNode, KoiNetEdge],
                state=[KoiNetNode, KoiNetEdge]
            )
        ),
        rid_types_of_interest=[KoiNetNode, KoiNetEdge]
    )
