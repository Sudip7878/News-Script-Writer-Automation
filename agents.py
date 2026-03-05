import os
from groq import Groq
from dotenv import load_dotenv
import mcp_tools
from datetime import datetime

load_dotenv()

# Configure Groq
def get_groq_key():
    # Try Streamlit secrets first (for hosting)
    try:
        import streamlit as st
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    # Fallback to .env (for local)
    return os.getenv("GROQ_API_KEY")

api_key = get_groq_key()
client = Groq(api_key=api_key)

class AgentB_ScriptWriter:
    """
    Agent B: Specializes in writing catchy news scripts using Groq (GPT-OSS-120B).
    Summarizes news content and includes international segments.
    """
    def generate_script(self, nepal_news, intl_news):
        # Get current English date
        now = datetime.now()
        english_date = now.strftime("%Y-%m-%d") # e.g. 2026-03-05
        
        # Format nepal news for prompt
        nepal_context = ""
        for item in nepal_news:
            nepal_context += f"Headline: {item['headline']}\nContent: {item['content']}\nSource: {item['source']}\n\n"
        
        # Format intl news for prompt
        intl_context = "\n".join(intl_news)
        
        prompt = f"""
        You are the collective voice of "SA News Nepal". 
        Write a VIRAL, ENGAGING, and AUTHORITATIVE news script in NEPALI language.
        
        Starting Format:
        "SA News Nepal मा स्वागत छ। आजको मिति {english_date} (AD) र तदनुसार २०८२ फागुन २१ (BS) हो। आजको मुख्य समाचारबाट सुरु गरौं।"

        PART 1: NEPAL NEWS (Detailed Summarization):
        For each news item provided below, write a catchy headline and then summarize its RESPECTIVE content in 2-3 high-energy sentences.
        
        Input Data:
        {nepal_context}
        
        PART 2: INTERNATIONAL NEWS (Quick highlights):
        {intl_context}
        
        Requirements:
        1. Maintain the exact pair: Use the headline provided and summarize ONLY the content that came with that specific headline. DO NOT mix stories.
        2. The script MUST be entirely in NEPALI (Unicode) after the intro.
        3. Speak on behalf of the WHOLE "SA News Nepal" team - do NOT include any person names.
        4. Use a high-energy, dramatic tone.
        5. Transition smoothly between the Nepal stories and the International segment.
        6. Place the International News highlights in the LAST TWO sections of the script.
        7. End with a professional "SA News Nepal" sign-off.
        """
        
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are the official script writer for SA News Nepal. You write high-energy, anonymous news scripts in Nepali."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2048,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error generating script with Groq/GPT-OSS: {e}")
            return "त्रुटी: समाचार स्क्रिप्ट तयार गर्न सकिएन। मोडेल उपलब्ध नहुन सक्छ।"

class AgentA_Gatherer:
    """
    Agent A: Gathers multi-source news (Nepal & Intl) and orchestrates the script generation.
    """
    def __init__(self):
        self.writer = AgentB_ScriptWriter()

    def gather_and_script(self):
        # 1. Gather Nepal news with content
        print("Agent A: Gathering Nepal news content...")
        nepal_news = mcp_tools.fetch_nepal_news()
        
        # 2. Gather International news
        print("Agent A: Gathering International news...")
        intl_news = mcp_tools.fetch_international_news()
        
        # 3. Ask Agent B for a summarized catchy script
        print("Agent A: Requesting summarized script from Agent B (Groq)...")
        script = self.writer.generate_script(nepal_news, intl_news)
        
        return nepal_news, intl_news, script

if __name__ == "__main__":
    agent_a = AgentA_Gatherer()
    nepal, intl, script = agent_a.gather_and_script()
    print("\n--- GENERATED SCRIPT ---\n")
    print(script)
