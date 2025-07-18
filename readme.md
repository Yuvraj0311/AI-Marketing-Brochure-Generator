# 🚀 AI Marketing Brochure Generator

An intelligent web application that transforms company websites into professional, customizable marketing brochures using **AI** and **automated web scraping**. Built with **Streamlit** and **OpenAI GPT models**, this tool supports multiple languages, flexible tones, and brochure downloads in **PDF** and **Markdown** formats.

---

## ✨ Features

- **🔍 Web Scraping Engine**: Automatically extracts key content and visuals from any public website
- **🤖 AI-Powered Copywriting**: Uses OpenAI GPT to generate structured, compelling marketing brochures
- **🗣️ Multi-Language Support**: Generate content in 8 different languages
- **🎭 Custom Writing Tones**: Choose from 7 professional tones (e.g., confident, witty, informative)
- **📄 PDF Export**: Download a fully formatted brochure in PDF format
- **📝 Markdown Export**: Export content in clean Markdown format for reuse
- **⚡ Real-Time Streaming**: Watch brochure content generate live in the interface
- **🔐 Secure & Stateless**: All data is processed in-session, with no storage

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/ai-marketing-brochure.git
cd ai-marketing-brochure
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
# Create a .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

4. **Run the application**:
```bash
streamlit run app.py
```

## 🚀 Usage

1. **Configure settings**:
   - Select your preferred language
   - Choose the tone for your brochure
2. **Input company details**:
   - Enter the company name
   - Provide the website URL
3. **Generate brochure** and watch it stream in real-time
4. **Download** in Markdown or PDF format

## 📁 Project Structure

```
ai-marketing-brochure/
├── app.py                 # Main Streamlit application
├── main.py               # Core business logic
├── requirements.txt      # Python