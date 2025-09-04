import os
from dotenv import load_dotenv
import google.generativeai as genai
import sys
import time

# Load API key from environment variable
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment variables")
    sys.exit(1)

# Configure the generative AI library
genai.configure(api_key=api_key)

# Function to list all available models
def list_models():
    print("Fetching available models...")
    try:
        models = genai.list_models()
        print("\nAvailable Models:")
        for model in models:
            print(f"- {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}")
            print(f"  Generation Methods: {', '.join(model.supported_generation_methods)}")
            print(f"  Input Token Limit: {model.input_token_limit}")
            print(f"  Output Token Limit: {model.output_token_limit}")
            print(f"  Temperature Range: {model.temperature_range}")
            print()
    except Exception as e:
        print(f"Error listing models: {str(e)}")

# Function to test a specific model
def test_model(model_name="gemini-1.5-flash"):
    print(f"\nTesting model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, what are your capabilities?")
        print("\nResponse:")
        print(response.text)
        print("\nTest successful!")
    except Exception as e:
        print(f"Error testing model: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            print("\nAPI RATE LIMIT OR QUOTA EXCEEDED")
            print("You've hit your API quota or rate limit. Here are some suggestions:")
            print("1. Check your Google AI Studio quota at: https://ai.google.dev/pricing")
            print("2. Try a different model with potentially lower resource requirements")
            print("3. Wait a while before making more requests")
            print("4. Consider upgrading your API tier if needed")

if __name__ == "__main__":
    # Open a file for writing the output
    with open("api_limits_report.txt", "w") as f:
        f.write("Google Generative AI API Limit Checker\n")
        f.write("=====================================\n")
        f.write(f"Using API key: {api_key[:8]}...{api_key[-4:]}\n")
        f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Also print to console
        print("Google Generative AI API Limit Checker")
        print("=====================================")
        print(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
        
        try:
            # List available models
            f.write("Fetching available models...\n")
            try:
                models = genai.list_models()
                f.write("\nAvailable Models:\n")
                for model in models:
                    f.write(f"- {model.name}\n")
                    f.write(f"  Display Name: {model.display_name}\n")
                    f.write(f"  Description: {model.description}\n")
                    f.write(f"  Generation Methods: {', '.join(model.supported_generation_methods)}\n")
                    f.write(f"  Input Token Limit: {model.input_token_limit}\n")
                    f.write(f"  Output Token Limit: {model.output_token_limit}\n")
                    f.write(f"  Temperature Range: {model.temperature_range}\n\n")
            except Exception as e:
                f.write(f"Error listing models: {str(e)}\n")
            
            # Test a model (default: gemini-1.5-flash)
            f.write("\nTesting model: gemini-1.5-flash\n")
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content("Hello, what are your capabilities?")
                f.write("\nResponse:\n")
                f.write(response.text + "\n")
                f.write("\nTest successful!\n")
            except Exception as e:
                f.write(f"Error testing model: {str(e)}\n")
                f.write(f"Error type: {type(e).__name__}\n")
                if "quota" in str(e).lower() or "rate" in str(e).lower():
                    f.write("\nAPI RATE LIMIT OR QUOTA EXCEEDED\n")
                    f.write("You've hit your API quota or rate limit. Here are some suggestions:\n")
                    f.write("1. Check your Google AI Studio quota at: https://ai.google.dev/pricing\n")
                    f.write("2. Try a different model with potentially lower resource requirements\n")
                    f.write("3. Wait a while before making more requests\n")
                    f.write("4. Consider upgrading your API tier if needed\n")
            
            # Try a different model if needed
            f.write("\nTesting model: gemini-1.5-pro\n")
            try:
                model = genai.GenerativeModel("gemini-1.5-pro")
                response = model.generate_content("Hello, what are your capabilities?")
                f.write("\nResponse:\n")
                f.write(response.text + "\n")
                f.write("\nTest successful!\n")
            except Exception as e:
                f.write(f"Error testing model: {str(e)}\n")
                f.write(f"Error type: {type(e).__name__}\n")
                if "quota" in str(e).lower() or "rate" in str(e).lower():
                    f.write("\nAPI RATE LIMIT OR QUOTA EXCEEDED\n")
                    f.write("You've hit your API quota or rate limit. Here are some suggestions:\n")
                    f.write("1. Check your Google AI Studio quota at: https://ai.google.dev/pricing\n")
                    f.write("2. Try a different model with potentially lower resource requirements\n")
                    f.write("3. Wait a while before making more requests\n")
                    f.write("4. Consider upgrading your API tier if needed\n")
                    
        except Exception as e:
            f.write(f"Unexpected error: {str(e)}\n")
        
        f.write("\nCheck completed at: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
    
    print("API limit check complete. Results written to api_limits_report.txt")
