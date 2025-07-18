import streamlit as st
import os
import tempfile
import time
from main import BrochureGenerator, PDFExporter, validate_url, validate_api_key
import requests
import base64

st.set_page_config(
    page_title="AI Marketing Brochure Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .css-1d391kg {
        display: none;
    }
    
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 2rem;
        max-width: none;
        background-color: transparent;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .input-container {
        background: transparent !important;
        padding: 0;
        border-radius: 0;
        box-shadow: none;
        margin-bottom: 2rem;
    }
    
    .stTextInput > div > div > input {
        background-color: #21262d !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #e6edf3 !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #7d8590 !important;
    }
    
    .stSelectbox > div > div {
        background-color: #21262d !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #e6edf3 !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #667eea !important;
    }
    
    .stSelectbox > div > div > div {
        color: #e6edf3 !important;
    }
    
    .stSelectbox > div > div > div[data-baseweb="select"] > div {
        color: #e6edf3 !important;
        background-color: #21262d !important;
    }
    
    .stSelectbox > div > div > div[data-baseweb="select"] > div > div {
        color: #e6edf3 !important;
    }
    
    [data-baseweb="menu"] {
        background-color: #21262d !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    
    [data-baseweb="menu"] > li {
        background-color: #21262d !important;
        color: #e6edf3 !important;
    }
    
    [data-baseweb="menu"] > li:hover {
        background-color: #30363d !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        height: 3rem !important;
        transition: all 0.3s ease !important;
        font-size: 1rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:disabled {
        background: #30363d !important;
        color: #7d8590 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    .stTextInput > label,
    .stSelectbox > label {
        color: #e6edf3 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .brochure-content {
        margin-top: 1rem;
    }
    
    .brochure-content h1,
    .brochure-content h2,
    .brochure-content h3 {
        color: #e6edf3;
    }
    
    .brochure-content p {
        color: #c9d1d9;
        line-height: 1.6;
    }
    
    .brochure-content hr {
        border-color: #30363d;
    }
    
    .success-message {
        background: #0d4a1a;
        color: #4ac26b;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #4a0d15;
        color: #ff6b6b;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .download-section {
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 1px solid #30363d;
    }
    
    .download-section h3 {
        color: #e6edf3;
        margin-bottom: 1rem;
    }
    
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .stInfo {
        background-color: #0d2f4a !important;
        color: #79c0ff !important;
        border: 1px solid #1f6feb !important;
    }
    
    .stSpinner {
        color: #667eea !important;
    }
    
    .stApp > div,
    .stApp > div > div,
    .stApp > div > div > div,
    .stApp > div > div > div > div {
        background-color: transparent !important;
    }
    
    .input-row {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr auto;
        gap: 1.5rem;
        align-items: end;
        margin-bottom: 2rem;
    }
    
    @media (max-width: 1200px) {
        .input-row {
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        
        .input-row > div:nth-child(3),
        .input-row > div:nth-child(4) {
            grid-column: 1 / -1;
        }
        
        .input-row > div:nth-child(5) {
            grid-column: 1 / -1;
            justify-self: center;
        }
    }
    
    @media (max-width: 768px) {
        .input-row {
            grid-template-columns: 1fr;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    
    .company-info {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        color: #e6edf3;
    }
    
    .download-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 1rem;
    }
    
    @media (max-width: 768px) {
        .download-buttons {
            flex-direction: column;
            align-items: center;
        }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'brochure_generated' not in st.session_state:
        st.session_state.brochure_generated = False
    if 'brochure_content' not in st.session_state:
        st.session_state.brochure_content = ""
    if 'company_name' not in st.session_state:
        st.session_state.company_name = ""
    if 'website_url' not in st.session_state:
        st.session_state.website_url = ""

def display_header():
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Marketing Brochure Generator</h1>
        <p>Transform any website into a professional marketing brochure using AI</p>
    </div>
    """, unsafe_allow_html=True)

def get_company_favicon(url: str) -> str:
    try:
        favicon_url = f"https://www.google.com/s2/favicons?domain={url}&sz=32"
        response = requests.get(favicon_url, timeout=5)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
    except:
        pass
    return None

def display_company_info(company_name: str, website_url: str):
    favicon = get_company_favicon(website_url)
    
    col1, col2 = st.columns([1, 20])
    
    with col1:
        if favicon:
            st.markdown(f'<img src="data:image/png;base64,{favicon}" width="32" style="margin-top: 8px;">', unsafe_allow_html=True)
        else:
            st.markdown("🏢")
    
    with col2:
        st.markdown(f"**{company_name}** • {website_url}")

def create_pdf_download_link(content: str, filename: str) -> str:
    try:
        pdf_exporter = PDFExporter()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
        
        pdf_exporter.markdown_to_pdf(content, pdf_path)
        
        with open(pdf_path, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
        
        os.unlink(pdf_path)
        
        return pdf_bytes
    except Exception as e:
        st.error(f"Error creating PDF: {e}")
        return None

def check_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        st.markdown("""
        <div class="error-message">
            <strong>🔑 OpenAI API Key Required</strong><br>
            Please set your OpenAI API key in your environment variables or .env file.<br>
            See the README for detailed setup instructions.
        </div>
        """, unsafe_allow_html=True)
        return None
    
    if not validate_api_key(api_key):
        st.markdown("""
        <div class="error-message">
            <strong>❌ Invalid API Key</strong><br>
            Invalid API key format detected. Please check your OpenAI API key.
        </div>
        """, unsafe_allow_html=True)
        return None
    
    return api_key

def main():
    initialize_session_state()
    display_header()
    
    api_key = check_api_key()
    if not api_key:
        return
    
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown("### 📝 Enter Details")
    
    col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 1.5])
    
    with col1:
        company_name = st.text_input(
            "Company Name",
            value=st.session_state.company_name,
            placeholder="e.g., Apple Inc."
        )
    
    with col2:
        website_url = st.text_input(
            "Website URL",
            value=st.session_state.website_url,
            placeholder="https://www.example.com"
        )
    
    with col3:
        languages = {
            "English": "English",
            "Spanish": "Spanish", 
            "French": "French",
            "German": "German",
            "Italian": "Italian",
            "Portuguese": "Portuguese",
            "Chinese": "Chinese",
            "Japanese": "Japanese"
        }
        
        selected_language = st.selectbox(
            "Language",
            options=list(languages.keys()),
            index=0
        )
    
    with col4:
        tones = {
            "Professional": "Professional",
            "Friendly": "Friendly",
            "Technical": "Technical", 
            "Creative": "Creative",
            "Minimalist": "Minimalist",
            "Enthusiastic": "Enthusiastic",
            "Humorous": "Humorous"
        }
        
        selected_tone = st.selectbox(
            "Tone",
            options=list(tones.keys()),
            index=0
        )
    
    with col5:
        st.markdown("<br>", unsafe_allow_html=True)
        
        url_valid = True
        if website_url and not validate_url(website_url):
            url_valid = False
        
        generate_button = st.button(
            "Generate",
            disabled=not (company_name and website_url and url_valid)
        )
    
    if website_url and not url_valid:
        st.markdown("""
        <div class="error-message">
            Please enter a valid URL (including https://)
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show brochure content when generating
    if generate_button:
        st.session_state.company_name = company_name
        st.session_state.website_url = website_url
        
        display_company_info(company_name, website_url)
        st.markdown("---")
        
        try:
            generator = BrochureGenerator(
                api_key=api_key,
                model="gpt-4o-mini"
            )
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 Analyzing website...")
            progress_bar.progress(25)
            
            status_text.text("📊 Extracting relevant content...")
            progress_bar.progress(50)
            
            status_text.text("✨ Generating brochure...")
            progress_bar.progress(75)
            
            brochure_placeholder = st.empty()
            content = ""
            
            try:
                for chunk in generator.stream_brochure(
                    company_name=company_name,
                    url=website_url,
                    language=selected_language,
                    tone=selected_tone
                ):
                    if chunk.startswith("Error"):
                        st.error(chunk)
                        break
                    content += chunk
                    brochure_placeholder.markdown(content)
                    time.sleep(0.05)
                
                if not content.startswith("Error"):
                    progress_bar.progress(100)
                    status_text.text("✅ Brochure generated successfully!")
                    
                    st.session_state.brochure_content = content
                    st.session_state.brochure_generated = True
                    
                    st.markdown('<div class="download-section">', unsafe_allow_html=True)
                    st.markdown("### 📥 Download Options")
                    
                    col_md, col_pdf = st.columns(2)
                    
                    with col_md:
                        st.download_button(
                            label="📝 Download Markdown",
                            data=st.session_state.brochure_content,
                            file_name=f"{st.session_state.company_name}_brochure.md",
                            mime="text/markdown"
                        )
                    
                    with col_pdf:
                        if st.button("📄 Generate PDF"):
                            with st.spinner("Generating PDF..."):
                                pdf_bytes = create_pdf_download_link(
                                    st.session_state.brochure_content,
                                    f"{st.session_state.company_name}_brochure.pdf"
                                )
                                
                                if pdf_bytes:
                                    st.download_button(
                                        label="📄 Download PDF",
                                        data=pdf_bytes,
                                        file_name=f"{st.session_state.company_name}_brochure.pdf",
                                        mime="application/pdf"
                                    )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.session_state.brochure_generated = False
                    
            except Exception as stream_error:
                st.error(f"Error during brochure generation: {stream_error}")
                st.session_state.brochure_generated = False
            
        except Exception as e:
            st.error(f"Error initializing brochure generator: {e}")
            st.session_state.brochure_generated = False
    
    elif st.session_state.brochure_generated and st.session_state.brochure_content:
        st.markdown("### 📄 Generated Brochure")
        
        if st.session_state.company_name and st.session_state.website_url:
            display_company_info(st.session_state.company_name, st.session_state.website_url)
            st.markdown("---")
        
        st.markdown('<div class="brochure-content">', unsafe_allow_html=True)
        st.markdown(st.session_state.brochure_content)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        st.markdown("### 📥 Download Options")
        
        col_md, col_pdf = st.columns(2)
        
        with col_md:
            st.download_button(
                label="📝 Download Markdown",
                data=st.session_state.brochure_content,
                file_name=f"{st.session_state.company_name}_brochure.md",
                mime="text/markdown"
            )
        
        with col_pdf:
            if st.button("📄 Generate PDF"):
                with st.spinner("Generating PDF..."):
                    pdf_bytes = create_pdf_download_link(
                        st.session_state.brochure_content,
                        f"{st.session_state.company_name}_brochure.pdf"
                    )
                    
                    if pdf_bytes:
                        st.download_button(
                            label="📄 Download PDF",
                            data=pdf_bytes,
                            file_name=f"{st.session_state.company_name}_brochure.pdf",
                            mime="application/pdf"
                        )
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()