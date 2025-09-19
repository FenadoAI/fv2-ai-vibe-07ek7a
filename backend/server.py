from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import random

# AI agents
from ai_agents.agents import AgentConfig, SearchAgent, ChatAgent


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# AI agents init
agent_config = AgentConfig()
search_agent: Optional[SearchAgent] = None
chat_agent: Optional[ChatAgent] = None

# Main app
app = FastAPI(title="AI Agents API", description="Minimal AI Agents API with LangGraph and MCP support")

# API router
api_router = APIRouter(prefix="/api")


# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


# AI agent models
class ChatRequest(BaseModel):
    message: str
    agent_type: str = "chat"  # "chat" or "search"
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    agent_type: str
    capabilities: List[str]
    metadata: dict = Field(default_factory=dict)
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class SearchResponse(BaseModel):
    success: bool
    query: str
    summary: str
    search_results: Optional[dict] = None
    sources_count: int
    error: Optional[str] = None


# LLM Models for Hot-or-Not
class LLMModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    provider: str
    description: str
    capabilities: List[str]
    performance_score: float = 0.0
    total_votes: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    image_url: Optional[str] = None

    def calculate_win_rate(self):
        if self.total_votes == 0:
            return 0.0
        return round(self.wins / self.total_votes * 100, 1)


class Vote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    winner_id: str
    loser_id: str
    voter_ip: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Battle(BaseModel):
    model1: LLMModel
    model2: LLMModel


class VoteRequest(BaseModel):
    winner_id: str
    loser_id: str

# Routes
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]


# AI agent routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    # Chat with AI agent
    global search_agent, chat_agent
    
    try:
        # Init agents if needed
        if request.agent_type == "search" and search_agent is None:
            search_agent = SearchAgent(agent_config)
            
        elif request.agent_type == "chat" and chat_agent is None:
            chat_agent = ChatAgent(agent_config)
        
        # Select agent
        agent = search_agent if request.agent_type == "search" else chat_agent
        
        if agent is None:
            raise HTTPException(status_code=500, detail="Failed to initialize agent")
        
        # Execute agent
        response = await agent.execute(request.message)
        
        return ChatResponse(
            success=response.success,
            response=response.content,
            agent_type=request.agent_type,
            capabilities=agent.get_capabilities(),
            metadata=response.metadata,
            error=response.error
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            success=False,
            response="",
            agent_type=request.agent_type,
            capabilities=[],
            error=str(e)
        )


@api_router.post("/search", response_model=SearchResponse)
async def search_and_summarize(request: SearchRequest):
    # Web search with AI summary
    global search_agent
    
    try:
        # Init search agent if needed
        if search_agent is None:
            search_agent = SearchAgent(agent_config)
        
        # Search with agent
        search_prompt = f"Search for information about: {request.query}. Provide a comprehensive summary with key findings."
        result = await search_agent.execute(search_prompt, use_tools=True)
        
        if result.success:
            return SearchResponse(
                success=True,
                query=request.query,
                summary=result.content,
                search_results=result.metadata,
                sources_count=result.metadata.get("tools_used", 0)
            )
        else:
            return SearchResponse(
                success=False,
                query=request.query,
                summary="",
                sources_count=0,
                error=result.error
            )
            
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return SearchResponse(
            success=False,
            query=request.query,
            summary="",
            sources_count=0,
            error=str(e)
        )


@api_router.get("/agents/capabilities")
async def get_agent_capabilities():
    # Get agent capabilities
    try:
        capabilities = {
            "search_agent": SearchAgent(agent_config).get_capabilities(),
            "chat_agent": ChatAgent(agent_config).get_capabilities()
        }
        return {
            "success": True,
            "capabilities": capabilities
        }
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# LLM Models Battle Routes
@api_router.post("/models/seed")
async def seed_models():
    """Seed the database with popular LLM models"""
    models = [
        {
            "name": "GPT-4",
            "provider": "OpenAI",
            "description": "OpenAI's most advanced GPT model with superior reasoning capabilities",
            "capabilities": ["Text Generation", "Code", "Math", "Analysis", "Creative Writing"],
            "performance_score": 95.0,
            "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400"
        },
        {
            "name": "Claude 4 Sonnet",
            "provider": "Anthropic",
            "description": "Anthropic's flagship model balancing intelligence, speed, and cost",
            "capabilities": ["Text Analysis", "Code", "Math", "Creative Tasks", "Safety"],
            "performance_score": 94.0,
            "image_url": "https://images.unsplash.com/photo-1655635949348-953b0e3c140a?w=400"
        },
        {
            "name": "Gemini 2.5 Pro",
            "provider": "Google",
            "description": "Google's most advanced multimodal AI with exceptional capabilities",
            "capabilities": ["Multimodal", "Long Context", "Code", "Math", "Analysis"],
            "performance_score": 93.0,
            "image_url": "https://images.unsplash.com/photo-1639322537228-f710d846310a?w=400"
        },
        {
            "name": "Claude 4 Haiku",
            "provider": "Anthropic",
            "description": "Fast and efficient model for quick responses",
            "capabilities": ["Speed", "Text Generation", "Basic Analysis", "Code"],
            "performance_score": 87.0,
            "image_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=400"
        },
        {
            "name": "Llama 3.3",
            "provider": "Meta",
            "description": "Open-source powerhouse with strong performance",
            "capabilities": ["Open Source", "Text Generation", "Code", "Multilingual"],
            "performance_score": 89.0,
            "image_url": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=400"
        },
        {
            "name": "Mistral Large",
            "provider": "Mistral AI",
            "description": "European AI model with strong multilingual capabilities",
            "capabilities": ["Multilingual", "Code", "Text Generation", "Analysis"],
            "performance_score": 86.0,
            "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400"
        },
        {
            "name": "PaLM 2",
            "provider": "Google",
            "description": "Google's language model with strong reasoning abilities",
            "capabilities": ["Reasoning", "Code", "Math", "Multilingual"],
            "performance_score": 85.0,
            "image_url": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400"
        },
        {
            "name": "GPT-3.5 Turbo",
            "provider": "OpenAI",
            "description": "Fast and cost-effective model for general tasks",
            "capabilities": ["Speed", "Cost-effective", "Text Generation", "Code"],
            "performance_score": 82.0,
            "image_url": "https://images.unsplash.com/photo-1676277791608-ac54325e36e1?w=400"
        }
    ]

    try:
        # Clear existing models
        await db.llm_models.drop()

        # Insert new models
        for model_data in models:
            model = LLMModel(**model_data)
            await db.llm_models.insert_one(model.dict())

        return {"success": True, "message": f"Seeded {len(models)} LLM models"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/models", response_model=List[LLMModel])
async def get_all_models():
    """Get all LLM models"""
    try:
        models = await db.llm_models.find().to_list(1000)
        return [LLMModel(**model) for model in models]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/battle", response_model=Battle)
async def get_battle():
    """Get a random battle between two LLM models"""
    try:
        models = await db.llm_models.find().to_list(1000)
        if len(models) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 models to battle")

        # Select 2 random models
        selected_models = random.sample(models, 2)

        return Battle(
            model1=LLMModel(**selected_models[0]),
            model2=LLMModel(**selected_models[1])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/vote")
async def submit_vote(vote_request: VoteRequest):
    """Submit a vote for a battle"""
    try:
        # Create vote record
        vote = Vote(
            winner_id=vote_request.winner_id,
            loser_id=vote_request.loser_id
        )
        await db.votes.insert_one(vote.dict())

        # Update winner stats
        winner_update = {
            "$inc": {"total_votes": 1, "wins": 1}
        }
        await db.llm_models.update_one(
            {"id": vote_request.winner_id},
            winner_update
        )

        # Update loser stats
        loser_update = {
            "$inc": {"total_votes": 1, "losses": 1}
        }
        await db.llm_models.update_one(
            {"id": vote_request.loser_id},
            loser_update
        )

        # Recalculate win rates
        for model_id in [vote_request.winner_id, vote_request.loser_id]:
            model = await db.llm_models.find_one({"id": model_id})
            if model:
                model_obj = LLMModel(**model)
                win_rate = model_obj.calculate_win_rate()
                await db.llm_models.update_one(
                    {"id": model_id},
                    {"$set": {"win_rate": win_rate}}
                )

        return {"success": True, "message": "Vote recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/leaderboard", response_model=List[LLMModel])
async def get_leaderboard():
    """Get leaderboard sorted by win rate"""
    try:
        models = await db.llm_models.find().sort([("wins", -1), ("win_rate", -1)]).to_list(1000)
        return [LLMModel(**model) for model in models]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/stats")
async def get_battle_stats():
    """Get overall battle statistics"""
    try:
        total_votes = await db.votes.count_documents({})
        total_models = await db.llm_models.count_documents({})

        # Get top model
        top_models = await db.llm_models.find().sort([("wins", -1)]).limit(1).to_list(1)
        top_model = LLMModel(**top_models[0]) if top_models else None

        return {
            "total_votes": total_votes,
            "total_models": total_models,
            "top_model": top_model.name if top_model else None,
            "battles_completed": total_votes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    # Initialize agents on startup
    global search_agent, chat_agent
    logger.info("Starting AI Agents API...")
    
    # Lazy agent init for faster startup
    logger.info("AI Agents API ready!")


@app.on_event("shutdown")
async def shutdown_db_client():
    # Cleanup on shutdown
    global search_agent, chat_agent
    
    # Close MCP
    if search_agent and search_agent.mcp_client:
        # MCP cleanup automatic
        pass
    
    client.close()
    logger.info("AI Agents API shutdown complete.")
