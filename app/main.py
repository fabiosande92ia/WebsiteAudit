from fastapi import FastAPI
import logging
import sys

from .database import engine, Base
from .api import routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Website Audit API",
    description="A professional REST API for automatic website auditing using Lighthouse and basic security checks.",
    version="1.0.0"
)

app.include_router(routes.router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
