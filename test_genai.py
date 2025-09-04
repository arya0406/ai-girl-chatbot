import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the API
api_key = os.environ.get("GOOGLE_API_KEY")
print(f"API key loaded: {api_key[:10]}..." if api_key else "No API key found")

genai.configure(api_key=api_key)

# List available models
print("\nListing available models:")
try:
    models = genai.list_models()
    for model in models:
        print(f"- {model.name}: {model.supported_generation_methods}")
except Exception as e:
    import traceback
    print(f"Error listing models: {str(e)}")
    print(traceback.format_exc())

# Try a test query with gemini-pro model
try:
    print("\nTesting direct query with Google Generative AI:")
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello! How are you?")
    print(f"Response: {response.text[:100]}...")
except Exception as e:
    import traceback
    print(f"Error with test query: {str(e)}")
    print(traceback.format_exc())
