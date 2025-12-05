import structlog
from rid_lib.types import KoiNetNode, KoiNetEdge
from koi_net.protocol.event import Event, EventType
from koi_net.protocol.edge import EdgeType, generate_edge_bundle
from koi_net.processor.handler import (
    KnowledgeHandler, 
    HandlerType, 
    HandlerContext,
    KnowledgeObject
)

log = structlog.stdlib.get_logger()


@KnowledgeHandler.create(
    HandlerType.Network, 
    rid_types=[KoiNetNode])
def handshake_handler(ctx: HandlerContext, kobj: KnowledgeObject):
    # only respond if node declares itself as NEW
    if not (kobj.event_type == EventType.NEW and kobj.source == kobj.rid):
        return
    
    log.info("Handling node handshake")
        
    log.info("Sharing this node's bundle with peer")
    identity_bundle = ctx.cache.read(ctx.identity.rid)
    ctx.event_queue.push(
        event=Event.from_bundle(
            event_type=EventType.NEW, 
            bundle=identity_bundle),
        target=kobj.rid
    )
    
    log.info("Proposing new edge")    
    # defer handling of proposed edge
    
    edge_bundle = generate_edge_bundle(
        source=kobj.rid,
        target=ctx.identity.rid,
        edge_type=EdgeType.WEBHOOK,
        rid_types=[KoiNetNode, KoiNetEdge]
    )
        
    ctx.kobj_queue.push(rid=edge_bundle.rid, event_type=EventType.FORGET)
    ctx.kobj_queue.push(bundle=edge_bundle)
