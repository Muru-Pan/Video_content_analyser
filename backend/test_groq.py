import os
import traceback
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_core.prompts import PromptTemplate
    from langchain_groq import ChatGroq
    from langchain_core.output_parsers import StrOutputParser

    print("GROQ_API_KEY snippet:", os.getenv("GROQ_API_KEY")[:5] if os.getenv("GROQ_API_KEY") else "None")

    llm = ChatGroq(model="llama3-8b-8192", api_key=os.getenv("GROQ_API_KEY"))
    prompt = PromptTemplate.from_template("Summarize this: {transcript}")
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({"transcript": "This is a test transcript."})
    print("SUCCESS. Response:", response)
except Exception as e:
    print("EXCEPTION CAUGHT:")
    traceback.print_exc()
