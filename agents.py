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
        english_date = now.strftime("%Y-%m-%d")
        
        # Get dynamic Nepali date
        nepali_date = mcp_tools.fetch_nepali_date_google()
        
        # Format nepal news for prompt
        nepal_context = ""
        for item in nepal_news:
            nepal_context += f"Headline: {item['headline']}\nContent: {item['content']}\n\n"
        
        # Format intl news for prompt (headline + content)
        intl_context = ""
        for item in intl_news:
            intl_context += f"Headline: {item['headline']}\nContent: {item['content']}\n\n"
        
        # Handle empty international news
        intl_section = ""
        if intl_news:
            intl_section = f"""
        अन्तर्राष्ट्रिय समाचार (INTERNATIONAL NEWS):
        तलका अन्तर्राष्ट्रिय समाचारहरूका लागि, अंग्रेजी शीर्षकलाई नेपालीमा अनुवाद गर्नुहोस् र सामग्री सारांश 1-2 वाक्यमा लेख्नुहोस्।
        
        Input Data:
        {intl_context}
            """
        else:
            intl_section = "\n(अन्तर्राष्ट्रिय समाचार उपलब्ध नभएकाले यो खण्ड छोड्नुहोस्।)\n"

        prompt = f"""
        You are the collective voice of "SA News Nepal". 
        Write a VIRAL, ENGAGING, and AUTHORITATIVE news script ENTIRELY in the NEPALI language.
        
        Starting Format:
        "SA News Nepal मा स्वागत छ। आजको मिति {english_date} (AD) र तदनुसार {nepali_date} (BS) हो। आजको मुख्य समाचारबाट सुरु गरौं।"

        
        For each Nepal news item, write a catchy Nepali headline and summarize its RESPECTIVE content in 2-3 high-energy sentences.
        
        Input Data:
        {nepal_context}
        
        {intl_section}
        
        Instructions:
        1. Summarize EVERY single Nepal news item provided below. Write the headline in Nepali, then 2 sentences of summary in Nepali.
        2. Summarize EVERY single International news item provided below. TRANSLATE the English headline to Nepali first, then write 1-2 sentences of summary in Nepali.
        3. Write the ENTIRE script in NEPALI only. Do NOT leave any headline or sentence in English.
        4. Speak as the "SA News Nepal" team.
        5. CRITICAL: You MUST end the script with this exact professional closing statement: "हवस् त, आजको लागि SA News Nepal बाट यति नै, नमस्कार!"
        """
        
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are the official script writer for SA News Nepal. You write high-energy, anonymous news scripts in Nepali."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=8000,
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
