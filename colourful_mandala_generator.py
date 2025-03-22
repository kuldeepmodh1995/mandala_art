import streamlit as st
import requests
import io
from PIL import Image
from datetime import datetime
from openai import OpenAI

# Set page configuration
st.set_page_config(
    page_title="Colorful Mandala Generator",
    page_icon="🎨",
    layout="centered"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f5f7ff;
    }
    .title-text {
        font-size: 42px;
        font-weight: bold;
        color: #6c5ce7;
        text-align: center;
        margin-bottom: 20px;
    }
    .subtitle-text {
        font-size: 20px;
        color: #4834d4;
        text-align: center;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #6c5ce7;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #4834d4;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<p class="title-text">✨ Colorful Mandala Generator ✨</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Enter a word and get a beautiful, unique mandala inspired by it</p>', unsafe_allow_html=True)

# Function to generate mandala using DALL-E 3
def generate_mandala(prompt_word, api_key):
    # Check if API key was provided
    if not api_key:
        st.error("Please enter your OpenAI API key to generate mandalas.")
        return None
    
    # Initialize OpenAI client with the provided API key
    client = OpenAI(api_key=api_key)
    
    # Create detailed prompt for the mandala
    detailed_prompt = f"""Create a vibrant, colorful symmetrical mandala inspired by the word '{prompt_word}'. 
    The mandala should have intricate patterns, radial symmetry, and use colors that evoke the essence of '{prompt_word}'.
    Make it detailed and ornate with a harmonious color palette. The background should complement the mandala.
    The style should be highly detailed and decorative, like traditional spiritual mandalas but with contemporary colors.
    Render in high resolution with clear details."""
    
    try:
        st.info("🎨 Generating your beautiful mandala... Please wait a moment.")
        
        # Generate image using DALL-E 3
        response = client.images.generate(
            model="dall-e-3",
            prompt=detailed_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Get image URL
        image_url = response.data[0].url
        
        # Download image
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            return Image.open(io.BytesIO(image_response.content))
        else:
            st.error(f"Failed to download image: {image_response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Error generating mandala: {str(e)}")
        st.info("Make sure your API key is valid and has access to DALL-E 3.")
        return None

# Function to create a download link for the image
def get_image_download_link(img, filename, text):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = buffered.getvalue()
    
    # Create download link using HTML
    href = f'<a href="data:image/png;base64,{img_str.hex()}" download="{filename}">💾 {text}</a>'
    return href

# Main app functionality
def main():
    # Create a sidebar for API key input
    with st.sidebar:
        st.header("OpenAI API Key")
        st.markdown("⚠️ Your API key is required to generate mandalas")
        api_key = st.text_input("Enter your OpenAI API key:", type="password", help="Get an API key from https://platform.openai.com/api-keys")
        st.markdown("Your API key is not stored anywhere and is only used for this session")
        
        # Add API key instructions
        st.markdown("### How to get an API key")
        st.markdown("""
        1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
        2. Sign in or create an account
        3. Click "Create new secret key"
        4. Copy the key and paste it above
        """)
    
    # Input for the inspiration word
    inspiration_word = st.text_input("Enter a word for inspiration:", placeholder="e.g., ocean, fire, forest, love...")
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("Generate Mandala")
    
    # Storage for generated image in session state
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None
    
    # Generate mandala when button is clicked
    if generate_button and inspiration_word:
        with st.spinner("Creating your mandala... This might take up to 30 seconds"):
            mandala_image = generate_mandala(inspiration_word, api_key)
            if mandala_image:
                st.session_state.generated_image = mandala_image
                st.session_state.inspiration_word = inspiration_word
    
    # Display generated mandala and download button
    if st.session_state.generated_image:
        st.success(f"✨ Your mandala inspired by '{st.session_state.inspiration_word}' is ready!")
        
        # Display image with a caption
        st.image(
            st.session_state.generated_image, 
            caption=f"Mandala inspired by '{st.session_state.inspiration_word}'",
            use_column_width=True
        )
        
        # Create filename based on inspiration word and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mandala_{st.session_state.inspiration_word}_{timestamp}.png"
        
        # Download button
        st.markdown(
            get_image_download_link(
                st.session_state.generated_image, 
                filename, 
                "Download Your Mandala"
            ),
            unsafe_allow_html=True
        )
        
        # Add some space and a note
        st.write("")
        st.info("💡 Generate as many mandalas as you like! Each one will be unique.")

if __name__ == "__main__":
    main()
