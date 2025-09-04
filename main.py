# main.py

import os
from fastapi import FastAPI
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
import time

# --- SETUP ---

# Load environment variables from the .env file
load_dotenv()

# Check if the Google API key is set
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("Google API Key not found in .env file")

# Initialize our FastAPI app
app = FastAPI(title="AI Girl Bot API")

# Import for better HTTP responses
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Add custom exception handlers for better debugging
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    error_details = traceback.format_exc()
    print(f"GLOBAL ERROR: {str(exc)}")
    print(f"Error details: {error_details}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__}
    )

# Initialize the Gemini LLM
# This is where we configure our connection to Google's model
try:
    print("Initializing Gemini LLM...")
    print(f"API Key present: {'GOOGLE_API_KEY' in os.environ}")
    # Use gemini-1.5-flash which has less resource requirements and available quota
    # Based on quota testing, gemini-1.5-flash is available but gemini-1.5-pro has exceeded quota
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    print("LLM initialization successful")
except Exception as e:
    print(f"ERROR initializing LLM: {str(e)}")
    import traceback
    print(f"Traceback: {traceback.format_exc()}")
    raise

# --- API DATA MODELS ---

# We use Pydantic to define the structure of our API requests and responses
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    """A simple endpoint to test if the server is running."""
    return {"status": "Server is running"}

@app.get("/api-status")
def api_status():
    """Endpoint to check the API status and quota information."""
    try:
        # Test a simple request to the model
        start_time = time.time()
        result = llm.invoke("Hello", timeout=10)
        response_time = time.time() - start_time
        
        return {
            "status": "operational",
            "model": llm.model,
            "response_time_seconds": round(response_time, 2),
            "message": "API is working correctly",
            "api_tier": "Free Tier (limited daily and per-minute quota)",
            "quota_info": "Check https://ai.google.dev/pricing for quota details"
        }
    except Exception as e:
        error_message = str(e)
        status_code = 500
        
        if "quota" in error_message.lower() or "rate" in error_message.lower():
            status_message = "quota_exceeded"
            status_code = 429
        else:
            status_message = "error"
        
        return {
            "status": status_message,
            "error": error_message,
            "model": llm.model,
            "api_tier": "Free Tier (limited daily and per-minute quota)",
            "quota_info": "Check https://ai.google.dev/pricing for quota details"
        }

from fastapi import HTTPException
from google.api_core.exceptions import ResourceExhausted

@app.post("/chat", response_model=ChatResponse)
def chat_with_ai(request: ChatRequest):
    """
    The main endpoint to chat with our AI bot.
    It receives a message and returns the AI's reply.
    """
    try:
        print(f"Received message: {request.message}")
        
        # Verify Google API key is still available
        if not os.environ.get("GOOGLE_API_KEY"):
            print("ERROR: Google API Key is missing")
            raise HTTPException(status_code=500, detail="API key configuration error")
        
        # Send the user's message to the LLM and get the result
        try:
            # Add a timeout to avoid hanging requests
            result = llm.invoke(request.message, timeout=30)
            ai_reply = result.content
            
            print(f"AI reply: {ai_reply}")
            
            # Return the AI's reply in the specified response format
            return ChatResponse(reply=ai_reply)
        except ResourceExhausted as quota_error:
            # Handle quota/rate limit errors specifically
            print(f"Quota exceeded: {str(quota_error)}")
            error_message = str(quota_error)
            
            # Check if it's specifically a rate limit issue
            if "rate limit" in error_message.lower():
                raise HTTPException(
                    status_code=429, 
                    detail="Rate limit exceeded. Please try again in a few seconds."
                )
            else:
                raise HTTPException(
                    status_code=429, 
                    detail="Google API quota exceeded. Your daily limit may have been reached. Please try again later or consider upgrading your API tier."
                )
        except TimeoutError:
            print("Request timed out")
            raise HTTPException(
                status_code=504,
                detail="Request to Google API timed out. The service might be experiencing high load."
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in chat endpoint: {str(e)}")
        print(f"Traceback: {error_details}")
        # Return a more user-friendly error
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")