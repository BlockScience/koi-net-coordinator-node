import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from koi_net.protocol.api_models import (
    PollEvents,
    FetchRids,
    FetchManifests,
    FetchBundles,
    EventsPayload,
    RidsPayload,
    ManifestsPayload,
    BundlesPayload,
    ErrorResponse
)
from koi_net.protocol.errors import ProtocolError
from koi_net.protocol.envelope import SignedEnvelope
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

@app.exception_handler(ProtocolError)
def koi_net_protocol_error_handler(request, exc: ProtocolError):
    logger.info(f"caught protocol error: {exc}")
    resp = ErrorResponse(error=exc.error_type)
    logger.info(f"returning error response: {resp}")
    return JSONResponse(
        status_code=400,
        content=resp.model_dump(mode="json")
    )

@koi_net_router.post(BROADCAST_EVENTS_PATH)
@node.secure.envelope_handler
async def broadcast_events(req: SignedEnvelope[EventsPayload]):
    logger.info(f"Request to {BROADCAST_EVENTS_PATH}, received {len(req.payload.events)} event(s)")
    for event in req.payload.events:
        node.processor.handle(event=event, source=req.source_node)
    
@koi_net_router.post(POLL_EVENTS_PATH)
@node.secure.envelope_handler
async def poll_events(
    req: SignedEnvelope[PollEvents]
) -> SignedEnvelope[EventsPayload] | ErrorResponse:
    logger.info(f"Request to {POLL_EVENTS_PATH}")
    events = node.event_queue.flush_poll_queue(req.payload.rid)
    return EventsPayload(events=events)

@koi_net_router.post(FETCH_RIDS_PATH)
@node.secure.envelope_handler
async def fetch_rids(
    req: SignedEnvelope[FetchRids]
) -> SignedEnvelope[RidsPayload] | ErrorResponse:
    return node.response_handler.fetch_rids(req.payload)

@koi_net_router.post(FETCH_MANIFESTS_PATH)
@node.secure.envelope_handler
async def fetch_manifests(
    req: SignedEnvelope[FetchManifests]
) -> SignedEnvelope[ManifestsPayload] | ErrorResponse:
    return node.response_handler.fetch_manifests(req.payload)

@koi_net_router.post(FETCH_BUNDLES_PATH)
@node.secure.envelope_handler
async def fetch_bundles(
    req: SignedEnvelope[FetchBundles]
) -> SignedEnvelope[BundlesPayload] | ErrorResponse:
    return node.response_handler.fetch_bundles(req.payload)
    
app.include_router(koi_net_router)