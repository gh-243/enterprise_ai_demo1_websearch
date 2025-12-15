# NEW MULTI-AGENT FEATURE
"""
Agent API Router

REST API endpoints for the multi-agent system.
Does NOT modify existing chat router.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.agents import (
    AgentType,
    AgentOrchestrator,
    run_agent,
    list_available_agents
)


# Request/Response Models
class AgentRequest(BaseModel):
    """Request to run a single agent."""
    agent_type: str = Field(..., description="Agent type (research/fact_check/business_analyst/writing)")
    query: str = Field(..., description="Query or instruction for the agent", min_length=1)
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context from previous agents")


class PipelineStep(BaseModel):
    """Single step in an agent pipeline."""
    agent_type: str = Field(..., description="Agent type")
    query: Optional[str] = Field(None, description="Optional custom query (defaults to initial query)")


class PipelineRequest(BaseModel):
    """Request to run an agent pipeline."""
    query: str = Field(..., description="Initial query", min_length=1)
    pipeline: Optional[List[PipelineStep]] = Field(None, description="Custom pipeline steps")
    output_format: str = Field("report", description="Final document format (report/email/summary)")


class AgentInfo(BaseModel):
    """Agent information for UI."""
    type: str
    name: str
    description: str
    personality: str
    avatar: str
    color: str


class AgentResponseModel(BaseModel):
    """Agent response."""
    agent_name: str
    agent_type: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = None
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    tokens_used: int
    cost_usd: float = 0.0


class PipelineResponseModel(BaseModel):
    """Pipeline response with all agent outputs."""
    query: str
    agents_run: List[str]
    responses: List[AgentResponseModel]
    total_tokens: int
    total_cost_usd: float


# Router
agent_router = APIRouter(prefix="/v1/agents", tags=["agents"])


@agent_router.get("/list", response_model=List[AgentInfo])
async def list_agents():
    """
    List all available agents.
    
    Returns:
        List of agent information for UI display
    """
    agents = list_available_agents()
    return agents


@agent_router.post("/run", response_model=AgentResponseModel)
async def run_single_agent(request: AgentRequest):
    """
    Run a single agent.
    
    Args:
        request: Agent request with type, query, and optional context
        
    Returns:
        Agent response with content and metadata
        
    Raises:
        HTTPException: If agent fails or invalid agent type
    """
    try:
        response = run_agent(
            agent_name=request.agent_type,
            query=request.query,
            context=request.context
        )
        
        return AgentResponseModel(
            agent_name=response.agent_name,
            agent_type=response.agent_type.value,
            content=response.content,
            sources=response.sources,
            confidence_score=response.confidence_score,
            metadata=response.metadata,
            tokens_used=response.tokens_used,
            cost_usd=response.cost_usd
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


@agent_router.post("/pipeline", response_model=PipelineResponseModel)
async def run_agent_pipeline(request: PipelineRequest):
    """
    Run a pipeline of agents in sequence.
    
    Args:
        request: Pipeline request with query and optional custom pipeline
        
    Returns:
        Pipeline response with all agent outputs
        
    Raises:
        HTTPException: If pipeline fails
    """
    try:
        orchestrator = AgentOrchestrator()
        
        # Use custom pipeline or standard pipeline
        if request.pipeline:
            # Convert Pydantic models to dicts
            pipeline = [
                {
                    "agent": AgentType[step.agent_type.upper()],
                    "query": step.query or request.query
                }
                for step in request.pipeline
            ]
            responses = orchestrator.run_pipeline(pipeline, request.query)
        else:
            # Run standard pipeline
            responses = orchestrator.run_standard_pipeline(
                request.query,
                request.output_format
            )
        
        # Calculate totals
        total_tokens = sum(r.tokens_used for r in responses)
        total_cost = sum(r.cost_usd for r in responses)
        
        return PipelineResponseModel(
            query=request.query,
            agents_run=[r.agent_name for r in responses],
            responses=[
                AgentResponseModel(
                    agent_name=r.agent_name,
                    agent_type=r.agent_type.value,
                    content=r.content,
                    sources=r.sources,
                    confidence_score=r.confidence_score,
                    metadata=r.metadata,
                    tokens_used=r.tokens_used,
                    cost_usd=r.cost_usd
                )
                for r in responses
            ],
            total_tokens=total_tokens,
            total_cost_usd=total_cost
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline execution failed: {str(e)}"
        )


class StandardPipelineRequest(BaseModel):
    """Request for standard pipeline."""
    query: str = Field(..., description="Query to process", min_length=1)
    output_format: str = Field("report", description="Final document format (report/email/summary)")


@agent_router.post("/pipeline/standard", response_model=PipelineResponseModel)
async def run_standard_pipeline(request: StandardPipelineRequest):
    """
    Run the standard Research → Fact-Check → Business Analyst → Writer pipeline.
    
    This is a convenience endpoint for the most common workflow.
    
    Args:
        request: Standard pipeline request with query and output format
        
    Returns:
        Pipeline response with all agent outputs
    """
    pipeline_request = PipelineRequest(
        query=request.query, 
        output_format=request.output_format
    )
    return await run_agent_pipeline(pipeline_request)
