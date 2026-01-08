from fastapi import APIRouter, HTTPException
from backend.models.chat import ChatRequest, ChatResponse, ChatMessage, ChatHistory
from backend.services.chat_service import chat_service
from backend.services.rag_service import rag_service
from backend.services.gemini_llm import gemini_llm
from pymongo import MongoClient
from backend.config import Config
from datetime import datetime
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

# MongoDB connection
client = MongoClient(Config.MONGODB_URI)
db = client[Config.DATABASE_NAME]
chat_collection = db["chats"]

@router.post("/start/{user_id}")
async def start_chat(user_id: str):
    """Start a new chat session"""
    
    # Check if there's an existing incomplete chat
    existing_chat = chat_collection.find_one({
        "user_id": user_id,
        "is_completed": False
    })
    
    if existing_chat:
        return {
            "message": "Resuming existing chat",
            "greeting": "Welcome back! Let's continue where we left off."
        }
    
    # Create new chat
    greeting = chat_service.get_greeting_message()
    
    chat_data = {
        "user_id": user_id,
        "messages": [
            {
                "role": "assistant",
                "content": greeting,
                "timestamp": datetime.now()
            }
        ],
        "is_completed": False,
        "summary": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    chat_collection.insert_one(chat_data)
    
    return {
        "message": "Chat started",
        "greeting": greeting
    }

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message and get response"""
    
    # Get chat history
    chat = chat_collection.find_one({
        "user_id": request.user_id,
        "is_completed": False
    })
    
    if not chat:
        raise HTTPException(status_code=404, detail="No active chat found. Please start a chat first.")
    
    # Convert stored messages to ChatMessage objects
    messages = [ChatMessage.model_validate(msg) for msg in chat["messages"]]
    
    # Add user message
    user_message = ChatMessage(role="user", content=request.message, timestamp=datetime.now())
    messages.append(user_message)
    
    # Get response from chat service
    result = chat_service.process_message(request.message, messages)
    
    # Add assistant response
    assistant_message = ChatMessage(
        role="assistant", 
        content=result["response"],
        timestamp=datetime.now()
    )
    messages.append(assistant_message)
    
    # Update database
    update_data = {
        "messages": [msg.model_dump() for msg in messages],
        "updated_at": datetime.now()
    }
    
    if result["is_summary"]:
        update_data["is_completed"] = True
        update_data["summary"] = result["response"]
    
    chat_collection.update_one(
        {"user_id": request.user_id, "is_completed": False},
        {"$set": update_data}
    )
    
    return ChatResponse(
        response=result["response"],
        is_summary=result["is_summary"]
    )

@router.get("/history/{user_id}")
async def get_chat_history(user_id: str):
    """Get chat history for a user"""
    
    chats = list(chat_collection.find({"user_id": user_id}).sort("created_at", -1))
    
    # Convert ObjectId to string
    for chat in chats:
        chat["_id"] = str(chat["_id"])
    
    return {"chats": chats}


@router.get("/active/{user_id}")
async def get_active_chat(user_id: str):
    """Get active (incomplete) chat for a user"""
    
    chat = chat_collection.find_one({
        "user_id": user_id,
        "is_completed": False
    })
    
    if not chat:
        return {"active_chat": None}
    
    chat["_id"] = str(chat["_id"])
    return {"active_chat": chat}

class DirectQuestionRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_direct_question(request: DirectQuestionRequest):
    """Direct RAG-based question answering"""
    try:
        # Create mock chat history with the question
        chat_history = [{"role": "user", "content": request.question}]

        # Get RAG context
        context = rag_service.get_rag_context(chat_history) or ""

        # Create a prompt that uses the context
        prompt = f"""You are Hazzy, an AI Health Assistant specialized in physiotherapy and general health awareness. 
When a user asks a question, provide a clear, short, and structured answer that includes:
1. 2–3 common reasons or causes for the issue.
2. 2–3 basic solutions or management tips that are physiotherapy-safe.
3. End the answer by recommending consulting a qualified doctor or physiotherapist.

Keep the explanation simple, human-like, and medically accurate — avoid saying you lack data or context.
Do NOT mention the words 'knowledge base' or 'context'.
Always sound confident and empathetic.

Example Format:
**Possible Reasons:** ...
**Basic Solutions:** ...
**Consultation Advice:** ...

User Question: {request.question}
"""
        prompt += f"""Context from physiotherapy knowledge base: {context}""" if context else ""  # Add context if available
        # Generate response
        response = gemini_llm.generate(prompt)

        return {
            "question": request.question,
            "answer": response,
            "context_found": len(context.strip()) > 0,
            "context_length": len(context)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")
























