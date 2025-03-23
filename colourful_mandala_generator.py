import streamlit as st
import requests
import io
import base64
from PIL import Image
from openai import OpenAI
import os

# Set page config
st.set_page_config(
    page_title="Mandala Art Generator",
    page_icon="🔮",
    layout="centered"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stApp {
        max-width: 900px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #3a0ca3;
    }
    .stButton button {
        background-color: #7209b7;
        color: white;
        border-radius: 10px;
    }
    .download-btn {
        background-color: #4cc9f0;
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        text-decoration: none;
        display: inline-block;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

def generate_mandala(api_key, inspiration, color_theme):
    """Generate mandala using OpenAI's DALL-E 3"""
    client = OpenAI(api_key=api_key)
    
    # Map color theme selections to detailed prompts
    color_theme_prompts = {
        "Warm Sunset": "warm sunset colors of orange, red, and golden yellow",
        "Ocean Blues": "ocean-inspired blues, teals, and aquamarine",
        "Forest Greens": "forest greens, earthy browns, and moss colors",
        "Purple Dream": "dreamy purples, lavenders, and soft pinks",
        "Rainbow": "vibrant rainbow colors across the entire spectrum"
    }
    
    theme_description = color_theme_prompts.get(color_theme, "vibrant colorful")
    
    prompt = f"""Create a detailed, symmetrical mandala inspired by the word '{inspiration}'. 
    Use {theme_description} colors to create a harmonious design.
    The mandala should be perfectly centered with intricate, balanced patterns.
    Create in the style of high-quality digital art with clear details and smooth lines.
    The background should be solid white to make the mandala stand out."""
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Get image URL
        image_url = response.data[0].url
        
        # Download the image
        image_response = requests.get(image_url)
        image = Image.open(io.BytesIO(image_response.content))
        return image, None
    
    except Exception as e:
        return None, str(e)

def get_image_download_link(img, filename="mandala.png", text="Download Mandala"):
    """Generate a download link for the image"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}" class="download-btn">{text}</a>'
    return href

# App title and description
st.title("✨ Magical Mandala Generator ✨")
st.markdown("Create beautiful, unique mandala art inspired by your ideas")

# API key input
api_key = st.text_input("Enter your OpenAI API Key", type="password", help="Your API key will not be stored")

# Sidebar for options
with st.sidebar:
    st.header("Mandala Options")
    
    # Inspiration word
    inspiration_word = st.text_input("Inspiration Word", 
                                     placeholder="Enter a word or concept...",
                                     help="This word will inspire your mandala's design")
    
    # Color theme selection
    color_themes = ["Warm Sunset", "Ocean Blues", "Forest Greens", "Purple Dream", "Rainbow"]
    selected_theme = st.selectbox("Color Theme", color_themes, 
                                 help="Choose the color palette for your mandala")
    
    # Generation button
    generate_button = st.button("Generate Mandala", 
                               help="Click to create your personalized mandala",
                               use_container_width=True)

# Main content area
if generate_button:
    if not api_key:
        st.error("Please enter your OpenAI API key")
    elif not inspiration_word:
        st.error("Please enter an inspiration word")
    else:
        with st.spinner('Creating your magical mandala...'):
            image, error = generate_mandala(api_key, inspiration_word, selected_theme)
            
            if error:
                st.error(f"Error generating image: {error}")
            elif image:
                # Display the generated image
                st.subheader(f"Your '{inspiration_word}' Mandala in {selected_theme}")
                st.image(image, use_column_width=True)
                
                # Download link
                st.markdown(get_image_download_link(image, 
                                                  filename=f"{inspiration_word}_mandala.png", 
                                                  text="⬇️ Download Your Mandala"), 
                          unsafe_allow_html=True)
                
                # Display related information
                st.info(f"This mandala was inspired by '{inspiration_word}' and uses the '{selected_theme}' color theme.")

# App information section
with st.expander("About this App"):
    st.markdown("""
    ### How to Use This App
    1. Enter your OpenAI API key (requires a paid account with access to DALL-E 3)
    2. Type a word or concept to inspire your mandala
    3. Select a color theme from the dropdown
    4. Click 'Generate Mandala' to create your art
    5. Use the download button to save your mandala
    
    ### About Mandalas
    Mandalas are geometric configurations of symbols with origins in religious practices. Today, they are also appreciated as art forms and tools for meditation and mindfulness.
    
    ### Technical Details
    This app uses OpenAI's DALL-E 3 model to generate unique mandala artwork based on your inputs. The images are created in 1024x1024 resolution.
    """)

# Footer
st.markdown("---")
st.markdown("Created with ❤️ | Powered by Streamlit and OpenAI")
