from dataclasses import dataclass

from rid_lib.types import KoiNetNode, KoiNetEdge
from koi_net.components.interfaces import KnowledgeHandler, HandlerType
from koi_net.components import NodeIdentity, Cache, EventQueue, KobjQueue
from koi_net.protocol import (
    KnowledgeObject,
    Event, 
    EventType, 
    EdgeType, 
    generate_edge_bundle
)


@dataclass
class HandshakeHandler(KnowledgeHandler):
    identity: NodeIdentity
    cache: Cache
    event_queue: EventQueue
    kobj_queue: KobjQueue
    
    # handler config
    handler_type = HandlerType.Network
    rid_types = (KoiNetNode,)
    
    def handle(self, kobj: KnowledgeObject):
        # only respond if a foreign node declares itself as NEW
        if not (kobj.event_type == EventType.NEW and kobj.source == kobj.rid):
            return
        
        self.log.info("Handling node handshake")
            
        self.log.info("Sharing this node's bundle with peer")
        identity_bundle = self.cache.read(self.identity.rid)
        self.event_queue.push(
            event=Event.from_bundle(
                event_type=EventType.NEW, 
                bundle=identity_bundle),
            target=kobj.rid
        )
        
        self.log.info("Proposing new edge")
        # defer handling of proposed edge
        
        edge_bundle = generate_edge_bundle(
            source=kobj.rid,
            target=self.identity.rid,
            edge_type=EdgeType.WEBHOOK,
            rid_types=[KoiNetNode, KoiNetEdge]
        )
        
        # force a refresh of cached edge so communication happens regardless
        # of state change
        self.kobj_queue.push(rid=edge_bundle.rid, event_type=EventType.FORGET)
        self.kobj_queue.push(bundle=edge_bundle)
