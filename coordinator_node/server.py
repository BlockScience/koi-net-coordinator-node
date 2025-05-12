import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
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
    root_path="/koi-net",
    title="KOI-net Protocol API",
    version="1.0.0"
)

@app.get("/health", tags=["System"])
async def health_check():
    """Basic health check for the service."""
    return {"status": "healthy", "node_id": str(node.identity.rid) if node.identity else "uninitialized"}


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
