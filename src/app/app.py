"""
FastAPI Application

Main application that includes all API routes and middleware.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import time
import uuid
import os

from src.api.chat_router import chat_router
from src.api.cost_router import cost_router
from src.api.agent_router import agent_router  # NEW MULTI-AGENT FEATURE
from src.api.document_router import document_router  # STUDENT ASSISTANT FEATURE
from src.api.podcast_router import router as podcast_router  # STUDENT ASSISTANT FEATURE - PHASE 5
from src.api.learning_router import router as learning_router  # STUDENT ASSISTANT FEATURE - PHASE 8
from src.infra.middleware import CostTrackingMiddleware
from src.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    logging.info("AI Chatbot application starting up")
    
    # Store middleware instance in app state for cost router access
    cost_middleware = CostTrackingMiddleware(app, buffer_size=1000)
    app.state.cost_middleware = cost_middleware
    
    yield
    # Shutdown
    logging.info("AI Chatbot application shutting down")


# Create FastAPI application
app = FastAPI(
    title="AI Chatbot",
    description="Enterprise AI Chatbot with web search capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add cost tracking middleware
app.add_middleware(CostTrackingMiddleware, buffer_size=1000)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log all HTTP requests with timing and trace ID."""
    trace_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Add trace ID to request state
    request.state.trace_id = trace_id
    
    # Log request
    logger = logging.getLogger(__name__)
    logger.info(
        f"Request started - {request.method} {request.url.path} "
        f"(trace_id: {trace_id})"
    )
    
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed - {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.3f}s "
            f"(trace_id: {trace_id})"
        )
        
        # Add headers
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log error
        logger.error(
            f"Request failed - {request.method} {request.url.path} "
            f"Error: {str(e)} "
            f"Time: {process_time:.3f}s "
            f"(trace_id: {trace_id})",
            exc_info=True
        )
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "trace_id": trace_id
            },
            headers={
                "X-Trace-ID": trace_id,
                "X-Process-Time": str(process_time)
            }
        )


# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(chat_router)
app.include_router(cost_router)
app.include_router(agent_router)  # NEW MULTI-AGENT FEATURE
app.include_router(document_router)  # STUDENT ASSISTANT FEATURE
app.include_router(podcast_router)  # STUDENT ASSISTANT FEATURE - PHASE 5
app.include_router(learning_router)  # STUDENT ASSISTANT FEATURE - PHASE 8


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-chatbot"}


@app.get("/")
async def root():
    """Serve the chatbot UI."""
    static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "index.html")
    if os.path.exists(static_path):
        return FileResponse(static_path)
    else:
        return {
            "service": "AI Chatbot",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
            "note": "UI not found - check static files"
        }


@app.get("/student")
async def student_ui():
    """Serve the Student Assistant UI."""
    static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "student.html")
    if os.path.exists(static_path):
        return FileResponse(static_path)
    else:
        return {
            "error": "Student UI not found",
            "note": "Check static/student.html file"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app.app:app", host="0.0.0.0", port=8000, reload=True)