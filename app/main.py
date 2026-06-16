from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router
from app.routes.business import router as business_router
from app.services.langgraph_checkpointer import get_checkpointer_context_manager
from app.agents.orchestrator import build_orchestrator_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
	"""
	FastAPI lifespan context manager (startup/shutdown).
	
	Runs on application startup (before first request).
	Runs on application shutdown (when server stops).
	
	Enables async resource initialization and cleanup.
	
	Phase 2: Initialize AsyncPostgresSaver and compile LangGraph.
	
	CRITICAL: yield must be INSIDE the async with block so the checkpointer
	context remains active for the entire app lifetime. If yield is outside,
	the context exits and closes the connection before requests arrive.
	"""
	# === STARTUP ===
	print("[STARTUP] Initializing FastAPI application...")
	
	# Initialize AsyncPostgresSaver with context manager
	# IMPORTANT: Keep the context open for the entire app lifetime
	print("[STARTUP] Initializing AsyncPostgresSaver...")
	async with get_checkpointer_context_manager() as checkpointer:
		# Setup database tables and connection
		await checkpointer.setup()
		app.state.checkpointer = checkpointer
		
		# Build and compile LangGraph with checkpointer
		print("[STARTUP] Compiling LangGraph orchestrator...")
		app.state.orchestrator_graph = build_orchestrator_graph(checkpointer)
		
		print("[STARTUP] Application initialization complete.")
		
		# Yield control to FastAPI; app is now running (with context still active)
		yield
		
		# === SHUTDOWN ===
		print("[SHUTDOWN] Cleaning up resources...")
		
		# Clear app.state references
		app.state.checkpointer = None
		app.state.orchestrator_graph = None
		
		print("[SHUTDOWN] Cleanup complete.")
		# Async context manager automatically closes on exit


app = FastAPI(
	title="Project Beta API",
	version="0.1.0",
	lifespan=lifespan,  # Connect lifespan context manager to app
)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.include_router(chat_router)
app.include_router(business_router)