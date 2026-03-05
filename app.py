import streamlit as st
import agents
import time

# Page Configuration
st.set_page_config(page_title="Nepal News Script AI", page_icon="📰", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    .agent-card {
        padding: 20px;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .headline-item {
        color: #00d4ff;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data
if 'script' not in st.session_state:
    st.session_state.script = ""
if 'nepal_news' not in st.session_state:
    st.session_state.nepal_news = []
if 'intl_news' not in st.session_state:
    st.session_state.intl_news = []

st.title("📰 SA News Nepal AI Assistant")
st.write("Generating premium Nepali news scripts using Gemini-powered summarization.")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.subheader("🕵️ Agent A: The Gatherer")
    st.info("Task: Scrape Nepal news (headlines + content) and International news.")
    
    start_btn = st.button("🚀 Fetch & Generate Summarized Script")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.subheader("📺 Brand: SA News Nepal")
    st.write("All scripts are automatically formatted for professional high-energy broadcasting.")
    st.markdown('</div>', unsafe_allow_html=True)

if start_btn:
    agent_a = agents.AgentA_Gatherer()
    
    with col2:
        with st.status("Executing Multi-Agent Workflow...", expanded=True) as status:
            st.write("🔍 Agent A is scraping Nepal news sites with content summaries...")
            time.sleep(1)
            
            # Fetching news and script
            nepal_news, intl_news, script = agent_a.gather_and_script()
            
            st.session_state.nepal_news = nepal_news
            st.session_state.intl_news = intl_news
            st.session_state.script = script
            
            st.write(f"✅ Found {len(nepal_news)} Nepal stories and {len(intl_news)} international updates.")
            st.write("✍️ Agent B for **SA News Nepal** is summarizing and writing the script...")
            time.sleep(1.5)
            status.update(label="Script Generated!", state="complete", expanded=False)
        
        st.success("🎉 News script is ready for your review!")

# Persistently show results if they exist in session state
if st.session_state.script:
    with col2:
        tabs = st.tabs(["📌 Nepal News Content", "🌍 International News", "📜 Final Script (Summarized)"])
        
        with tabs[0]:
            for item in st.session_state.nepal_news:
                with st.expander(f"Headline: {item['headline']}"):
                    st.write(f"**📍 Source:** {item['source']}")
                    st.write(f"**📝 Raw Content:** {item['content']}")
        
        with tabs[1]:
            for h in st.session_state.intl_news:
                st.markdown(f"- {h}")
        
        with tabs[2]:
            st.markdown("### SA News Nepal - Catchy Script")
            st.code(st.session_state.script, language="markdown")
            st.download_button("Download Script", st.session_state.script, file_name="SA_News_Nepal_Script.md")
else:
    if not start_btn:
        with col2:
            st.info("Click the button to begin.")
            # Use relative path for hosting or look in current directory
            import os
            img_path = "download.jpg"
            if os.path.exists(img_path):
                st.image(img_path, caption="SA News Nepal - Global Monitoring")
            else:
                st.image("https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=800&q=80", caption="SA News Nepal - Global Monitoring")

st.markdown("---")
st.markdown("Powered by **Streamlit** & **SA News Nepal AI**")
