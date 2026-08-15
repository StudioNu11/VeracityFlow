from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client2 = genai.Client(api_key=os.environ.get("GEMINI_API_KEY_2"))
