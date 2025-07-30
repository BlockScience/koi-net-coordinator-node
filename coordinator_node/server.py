import logging
from functools import wraps
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Depends
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
from koi_net.protocol.secure_models import SignedEnvelope
from koi_net.protocol.consts import (
    BROADCAST_EVENTS_PATH,
    POLL_EVENTS_PATH,
    FETCH_RIDS_PATH,
    FETCH_MANIFESTS_PATH,
    FETCH_BUNDLES_PATH
)
from .core import node


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    node.start()
    yield
    node.stop()

app = FastAPI(
    lifespan=lifespan, 
    title="KOI-net Protocol API",
    version="1.0.0"
)

koi_net_router = APIRouter(
    prefix="/koi-net"
)


def envelope_handler(func):
    @wraps(func)
    async def wrapper(req: SignedEnvelope, *args, **kwargs) -> SignedEnvelope | None:
        logger.info("Validating envelope")
        node.secure.validate_envelope(req)
        logger.info("Calling endpoint handler")
        result = await func(req, *args, **kwargs)
        if result is not None:
            logger.info("Creating response envelope")
            return node.secure.create_envelope(
                payload=result,
                target=req.source_node
            )
    return wrapper


@koi_net_router.post(BROADCAST_EVENTS_PATH)
@envelope_handler
async def broadcast_events(req: SignedEnvelope[EventsPayload]):    
    logger.info(f"Request to {BROADCAST_EVENTS_PATH}, received {len(req.payload.events)} event(s)")
    for event in req.payload.events:
        node.processor.handle(event=event, source=KnowledgeSource.External)
    
@koi_net_router.post(POLL_EVENTS_PATH)
@envelope_handler
async def poll_events(req: SignedEnvelope[PollEvents]) -> SignedEnvelope[EventsPayload]:
    logger.info(f"Request to {POLL_EVENTS_PATH}")
    events = node.network.flush_poll_queue(req.payload.rid)
    return EventsPayload(events=events)

@koi_net_router.post(FETCH_RIDS_PATH)
@envelope_handler
async def fetch_rids(req: SignedEnvelope[FetchRids]) -> SignedEnvelope[RidsPayload]:
    return node.response_handler.fetch_rids(req.payload)

@koi_net_router.post(FETCH_MANIFESTS_PATH)
@envelope_handler
async def fetch_manifests(req: SignedEnvelope[FetchManifests]) -> SignedEnvelope[ManifestsPayload]:
    return node.response_handler.fetch_manifests(req.payload)

@koi_net_router.post(FETCH_BUNDLES_PATH)
@envelope_handler
async def fetch_bundles(req: SignedEnvelope[FetchBundles]) -> SignedEnvelope[BundlesPayload]:
    return node.response_handler.fetch_bundles(req.payload)
    
app.include_router(koi_net_router)