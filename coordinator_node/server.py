import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from starlette.responses import Response, StreamingResponse
from rid_lib.core import RID
from rid_lib.types import KoiNetNode
from koi_net.processor.knowledge_object import KnowledgeSource
from koi_net.protocol.api_models import (
    PollEvents,
    FetchRids,
    FetchManifests,
    FetchBundles,
    EventsPayload,
    RidsPayload,
    ManifestsPayload,
    BundlesPayload
)
from koi_net.protocol.consts import (
    BROADCAST_EVENTS_PATH,
    POLL_EVENTS_PATH,
    FETCH_RIDS_PATH,
    FETCH_MANIFESTS_PATH,
    FETCH_BUNDLES_PATH,
    KOI_NET_MESSAGE_SIGNATURE,
    KOI_NET_SOURCE_NODE_RID,
    KOI_NET_TARGET_NODE_RID
)
from koi_net.protocol.event import EventType
from koi_net.protocol.node import NodeProfile
from koi_net.protocol.secure import PublicKey
from koi_net.utils import sha256_hash
from .core import node


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    node.start()
    yield
    node.stop()

app = FastAPI(
    lifespan=lifespan, 
    root_path="/koi-net",
    title="KOI-net Protocol API",
    version="1.0.0"
)

@app.middleware("http")
async def secure_koi_validator(request: Request, call_next):
    req_body = await request.body()
    
    source_node_rid: KoiNetNode = RID.from_string(
            request.headers.get(KOI_NET_SOURCE_NODE_RID))
    
    try:
        node.network.response_handler.validate_request(
            request.headers, req_body
        )
    except Exception:
        # TEMPORARY, should only be called if source node is unknown
        if not request.url.path.endswith(BROADCAST_EVENTS_PATH):
            raise Exception("Unknown Node RID")
        
        # if type is broadcast, for initiating handshake
        req = EventsPayload.model_validate_json(req_body)
        for event in req.events:
            if event.rid != source_node_rid:
                continue
            if event.event_type != EventType.NEW:
                continue
            
            print("EVENT ABOUT THE SOURCE NODE")
            
            node_profile = event.bundle.validate_contents(NodeProfile)
            
            hashed_pub_key = sha256_hash(node_profile.public_key)
            print(node_profile.public_key)
            print(hashed_pub_key)
            print(source_node_rid)
            
            if source_node_rid.uuid != hashed_pub_key:
                raise Exception("Invalid public key on new node!")
                

        response: StreamingResponse = await call_next(request)
        
        if request.url.path.endswith(BROADCAST_EVENTS_PATH):
            logger.debug("Broadcast doesn't require secure response")
            return response
        
    
        resp_body = b"".join(
            chunk async for chunk in response.body_iterator)
                        
        print("RESP BODY:", resp_body)
        
        resp_headers = node.network.response_handler.generate_response_headers(
            resp_body, source_node_rid)
        
        logger.debug(f"resp body hash: {sha256_hash(resp_body.decode())}")
        
        logger.debug(f"Secure resp headers {resp_headers}")
            
        signed_response = Response(
            content=resp_body,
            status_code=response.status_code,
            headers=resp_headers | dict(response.headers),
            media_type=response.media_type
        )
            
        return signed_response
    
    else:
        return await call_next(request)

@app.post(BROADCAST_EVENTS_PATH)
def broadcast_events(req: EventsPayload):
    logger.info(f"Request to {BROADCAST_EVENTS_PATH}, received {len(req.events)} event(s)")
    for event in req.events:
        node.processor.handle(event=event, source=KnowledgeSource.External)
    
@app.post(POLL_EVENTS_PATH)
def poll_events(req: PollEvents) -> EventsPayload:
    logger.info(f"Request to {POLL_EVENTS_PATH}")
    events = node.network.flush_poll_queue(req.rid)
    return EventsPayload(events=events)

@app.post(FETCH_RIDS_PATH)
def fetch_rids(req: FetchRids) -> RidsPayload:
    return node.network.response_handler.fetch_rids(req)

@app.post(FETCH_MANIFESTS_PATH)
def fetch_manifests(req: FetchManifests) -> ManifestsPayload:
    return node.network.response_handler.fetch_manifests(req)

@app.post(FETCH_BUNDLES_PATH)
def fetch_bundles(req: FetchBundles) -> BundlesPayload:
    return node.network.response_handler.fetch_bundles(req)
    