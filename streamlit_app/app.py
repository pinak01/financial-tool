import os
import sys


# Add the root directory (finance-tool) to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import asyncio
from dotenv import load_dotenv
from orchestrator.agent_coordinator import AgentCoordinator

class StreamlitApp:
    def __init__(self):
        """
        Initialize Streamlit application
        """
        # Load environment variables
        load_dotenv()
        
        # Get Gemini API key
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # Initialize agent coordinator
        try:
            self.agent_coordinator = AgentCoordinator(self.gemini_api_key)
            self.setup_page()
        except ValueError as e:
            st.error(str(e))
    
    def setup_page(self):
        """
        Set up the Streamlit page configuration
        """
        st.set_page_config(
            page_title="Financial Intelligence Assistant",
            page_icon=":chart_with_upwards_trend:",
            layout="wide"
        )
        st.title("🤖 Financial Intelligence Assistant")
        st.markdown("Get real-time market insights and analysis")
        
        # API Key input (if not already set)
        if not self.gemini_api_key:
            st.warning("Gemini API Key is required")
            gemini_api_key = st.text_input(
                "Enter your Gemini API Key", 
                type="password",
                help="You can get your API key from Google AI Studio"
            )
            
            if st.button("Save API Key"):
                if gemini_api_key:
                    # Save to .env file
                    with open('.env', 'w') as f:
                        f.write(f"GEMINI_API_KEY={gemini_api_key}")
                    st.success("API Key saved successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Please enter a valid API key")
    
    def run(self):
        """
        Main application run method
        """
        # Ensure API key is available
        if not self.gemini_api_key:
            return
        
        # Query input
        query = st.text_input(
            "Enter your financial query", 
            placeholder="What's happening with tech stocks today?"
        )
        
        # Voice input option
        st.markdown("### Or Upload Voice Query")
        uploaded_audio = st.file_uploader(
            "Upload an audio file", 
            type=['wav', 'mp3']
        )
        
        # Process button
        if st.button("Get Market Insights"):
            # Show loading spinner
            with st.spinner('Analyzing market data...'):
                try:
                    # Process query
                    if query:
                        results = asyncio.run(self.agent_coordinator.process_query(query))
                        self.display_results(results)
                    
                    # Process voice input
                    elif uploaded_audio:
                        # Save uploaded file
                        with open('temp_audio.wav', 'wb') as f:
                            f.write(uploaded_audio.getbuffer())
                        
                        # Convert speech to text
                        voice_agent = self.agent_coordinator.voice_agent
                        transcribed_query = voice_agent.speech_to_text('temp_audio.wav')
                        
                        # Process transcribed query
                        results = asyncio.run(self.agent_coordinator.process_query(transcribed_query))
                        self.display_results(results)
                    
                    else:
                        st.warning("Please enter a query or upload an audio file")
                
                except Exception as e:
                    st.error(f"An error occurred: {e}")
    
    def display_results(self, results: dict):
        """
        Display analysis results in Streamlit
        
        Args:
            results (dict): Processed query results
        """
        # Narrative Response
        st.subheader("Market Brief")
        st.write(results['narrative_response'])
        
        # Stock Data
        st.subheader("Stock Details")
        for ticker, data in results['stock_data'].items():
            if 'error' not in data:
                with st.expander(f"{ticker} Details"):
                    st.json(data)
        
        # News
        # st.subheader("Recent News")
        # for ticker, news in results['news_data'].items():
        #     with st.expander(f"{ticker} News"):
        #         for article in news:
        #             st.markdown(f"**{article.get('title', 'No Title')}**")
        #             st.write(f"Link: {article.get('link', 'No Link')}")
        
        # # Risk Analysis
        # st.subheader("Portfolio Risk Analysis")
        # st.json(results['risk_analysis'])
        
        # Voice Response (if available)
        if results['voice_response']:
            st.audio(results['voice_response'])

def main():
    """
    Main entry point for the Streamlit application
    """
    app = StreamlitApp()
    app.run()

if __name__ == "__main__":
    main()