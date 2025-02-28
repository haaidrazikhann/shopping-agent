from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

google_api_key = os.environ.get("GOOGLE_API_KEY")

llama = ChatGoogleGenerativeAI(api_key=google_api_key,model="gemini-2.0-flash",temperature=0)