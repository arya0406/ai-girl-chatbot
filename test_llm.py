import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Print diagnostic information
print("=== DIAGNOSTICS ===")
print(f"API Key present: {'GOOGLE_API_KEY' in os.environ}")
print(f"API Key value: {os.environ.get('GOOGLE_API_KEY')[:10]}..." if os.environ.get('GOOGLE_API_KEY') else "None")

# Try to initialize the LLM
try:
    print("\nInitializing LLM...")
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    print("LLM initialized successfully!")
    
    # Try a simple query
    print("\nTesting LLM with a simple query...")
    result = llm.invoke("Hello, can you hear me?")
    print(f"Response received: {result.content[:100]}...")
    
except Exception as e:
    import traceback
    print(f"\nERROR: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    print(f"Traceback: {traceback.format_exc()}")
