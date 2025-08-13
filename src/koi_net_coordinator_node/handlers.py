import logging
from rid_lib.types import KoiNetNode, KoiNetEdge
from koi_net.context import HandlerContext
from koi_net.processor.handler import HandlerType
from koi_net.processor.knowledge_object import KnowledgeObject
from koi_net.protocol.event import Event, EventType
from koi_net.protocol.edge import EdgeType, generate_edge_bundle
from .core import node

logger = logging.getLogger(__name__)


@node.processor.pipeline.register_handler(
    HandlerType.Network, 
    rid_types=[KoiNetNode])
def handshake_handler(ctx: HandlerContext, kobj: KnowledgeObject):

    # only respond if node declares itself as NEW
    if kobj.event_type != EventType.NEW:
        return
    
    logger.info("Handling node handshake")
        
    logger.info("Sharing this node's bundle with peer")
    identity_bundle = ctx.effector.deref(ctx.identity.rid)
    ctx.event_queue.push_event_to(
        event=Event.from_bundle(
            event_type=EventType.NEW, 
            bundle=identity_bundle),
        node=kobj.rid,
        flush=True
    )
    
    logger.info("Proposing new edge")    
    # defer handling of proposed edge
    
    edge_bundle = generate_edge_bundle(
        source=kobj.rid,
        target=ctx.identity.rid,
        edge_type=EdgeType.WEBHOOK,
        rid_types=[KoiNetNode, KoiNetEdge]
    )
        
    ctx.handle(rid=edge_bundle.rid, event_type=EventType.FORGET)
    ctx.handle(bundle=edge_bundle)
