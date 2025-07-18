import os
import requests
import json
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import markdown
import time
from urllib.parse import urljoin, urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-4.1-nano" 

def validate_api_key(api_key):
    """Validate OpenAI API key format"""
    return api_key and (api_key.startswith('sk-') or api_key.startswith('sk-proj-'))

# Validate API key before initializing OpenAI client
if not validate_api_key(api_key):
    logger.error("Invalid or missing OpenAI API key")
    raise ValueError("Please set a valid OPENAI_API_KEY in your environment variables")

openai = OpenAI()


class Website:
    """
    A utility class to represent a website that we have scraped with links.
    """
    
    def __init__(self, url: str, timeout: int = 10):
        self.url = url
        self.title = ""
        self.text = ""
        self.links = []
        self.images = []
        self.error = None
        
        try:
            self.scrape_website(timeout)
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error scraping {url}: {e}")
    
    def scrape_website(self, timeout: int):
        """Scrape website content with error handling"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(self.url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        self.title = soup.title.string.strip() if soup.title else "No title found"
        
        # Extract text content
        if soup.body:
            # Remove irrelevant elements
            for element in soup.body(['script', 'style', 'img', 'input', 'nav', 'footer']):
                element.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        
        # Extract links
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [self._normalize_url(link) for link in links if link]
    
    def _normalize_url(self, url: str):
        """Convert relative URLs to absolute URLs"""
        if url.startswith('http'):
            return url
        return urljoin(self.url, url)
    
    def get_contents(self):
        if self.error:
            return f"Error accessing {self.url}: {self.error}"
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"
    
    def is_valid(self):
        return self.error is None

class BrochureGenerator:
    """
    Main class for generating AI-powered marketing brochures
    """
    
    def __init__(self, api_key, model):
        # Validate API key
        if not validate_api_key(api_key):
            raise ValueError("Invalid OpenAI API key format")
        
        # Language and tone configurations
        self.languages = {
            "English": "en",
            "Spanish": "es", 
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Chinese": "zh",
            "Japanese": "ja"
        }
        
        self.tones = {
            "Professional": "professional and formal",
            "Friendly": "friendly and approachable", 
            "Technical": "technical and detailed",
            "Creative": "creative and engaging",
            "Minimalist": "concise and to-the-point",
            "Enthusiastic": "enthusiastic and energetic",
            "Humorous": "humorous and funny"
        }
    
    def link_system_prompt(self):
        return """You are provided with a list of links on a webpage. 
        You are able to decide which of the links would be most relevant to include in a brochure about the company 
        such as links to an About page, Company page, Services, Products, or Careers/Jobs pages.
        
        You should respond in JSON as in the example:
        {
            "links": [
                {"type": "about page", "url": "https://full.url/goes/here/about"},
                {"type": "careers page", "url": "https://another.full.url/careers"},
                {"type": "services page", "url": "https://example.com/services"}
            ]
        }
        """

    def links_user_prompt(self, website: Website):
        prompt = f"""Here is the list of links from the website {website.url} - 
        please decide which of these are relevant web links for a brochure about the company.
        Respond with the full https URL in JSON format. 
        Do not include Terms of Service, Privacy Policy, email links, or social media links.
        
        Links:
        """
        prompt += "\n".join(website.links[:50])
        return prompt
    
    def get_relevant_links(self, website: Website):
        """Get relevant links using AI"""
        try:
            response = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {'role': 'system', 'content': self.link_system_prompt()},
                    {'role': 'user', 'content': self.links_user_prompt(website)}
                ],
                response_format={'type': 'json_object'},
                timeout=30
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('links', [])
            
        except Exception as e:
            logger.error(f"Error getting relevant links: {e}")
            return []
    
    def get_all_details(self, url):
        """Scrape main website and relevant linked pages"""
        result = "Landing page:\n"
        
        # Get main website
        main_website = Website(url)
        if not main_website.is_valid():
            return f"Error: Could not access {url}. {main_website.error}"
        
        result += main_website.get_contents()
        
        # Get relevant links
        relevant_links = self.get_relevant_links(main_website)
        
        for link in relevant_links[:20]:
            try:
                link_website = Website(link['url'])
                if link_website.is_valid():
                    result += f"\n\n{link['type']}:\n"
                    result += link_website.get_contents()
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.warning(f"Could not scrape {link['url']}: {e}")
                continue
        
        return result[:25000]  # Truncate if too long
    
    def get_brochure_system_prompt(self, language, tone):
        """Generate system prompt for brochure creation"""
        lang_instruction = f" in {language}" if language != "English" else ""
        
        return f"""You are an expert marketing copywriter that analyzes company website content 
        and creates compelling brochures for prospective customers, investors, and recruits.
        
        Write the brochure{lang_instruction} with a {tone} tone.
        
        Structure the brochure with:
        1. Company name and tagline
        2. About/Overview section
        3. Products/Services
        4. Company culture and values
        5. Customer focus
        6. Career opportunities (if available)
        7. Contact information
        
        Use markdown formatting and make it visually appealing and professional.
        Include specific details from the website content provided.
        """
    
    def get_brochure_user_prompt(self, company_name, website_content):
        """Generate user prompt for brochure creation"""
        return f"""Company name: {company_name}
        
        Here is the website content to analyze:
        {website_content}
        
        Create a comprehensive marketing brochure based on this information.
        """
    
    def stream_brochure(self, company_name, url, language="English", 
                       tone="Professional"):
        """Generate brochure with streaming response"""
        try:
            website_content = self.get_all_details(url)
            
            if website_content.startswith("Error:"):
                yield website_content
                return
            
            # Fixed: Use chat.completions.create for streaming, not completions.create
            stream = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {'role': 'system', 'content': self.get_brochure_system_prompt(language, tone)},
                    {'role': 'user', 'content': self.get_brochure_user_prompt(company_name, website_content)}
                ],
                temperature=0.7,
                stream=True,
                timeout=60
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error streaming brochure: {e}")
            yield f"Error generating brochure: {str(e)}"

class PDFExporter:
    """
    Class for exporting brochures to PDF format
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor='#2c3e50'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor='#34495e'
        ))
    
    def markdown_to_pdf(self, markdown_content, filename):
        """Convert markdown content to PDF"""
        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(markdown_content)
            
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            
            # Parse HTML and convert to PDF elements
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol']):
                if element.name == 'h1':
                    story.append(Paragraph(element.get_text(), self.styles['CustomTitle']))
                elif element.name in ['h2', 'h3']:
                    story.append(Paragraph(element.get_text(), self.styles['CustomHeading']))
                elif element.name == 'p':
                    story.append(Paragraph(element.get_text(), self.styles['Normal']))
                elif element.name in ['ul', 'ol']:
                    for li in element.find_all('li'):
                        story.append(Paragraph(f"• {li.get_text()}", self.styles['Normal']))
                
                story.append(Spacer(1, 12))
            
            doc.build(story)
            return filename
            
        except Exception as e:
            logger.error(f"Error creating PDF: {e}")
            raise Exception(f"Failed to create PDF: {str(e)}")

def validate_url(url: str):
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
