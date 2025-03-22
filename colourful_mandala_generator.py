import streamlit as st
import requests
import io
import os
import json
import base64
from PIL import Image
from datetime import datetime
from openai import OpenAI
import google.generativeai as genai
import re

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
    .color-theme {
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        margin-right: 10px;
        cursor: pointer;
        border: 2px solid transparent;
    }
    .color-theme:hover {
        transform: scale(1.2);
        transition: transform 0.3s ease;
    }
    .download-btn {
        display: inline-block;
        background-color: #6c5ce7;
        color: white;
        padding: 8px 16px;
        text-decoration: none;
        border-radius: 8px;
        margin: 5px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .download-btn:hover {
        background-color: #4834d4;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<p class="title-text">✨ Colorful Mandala Generator ✨</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Enter a word and get a beautiful, unique mandala inspired by it</p>', unsafe_allow_html=True)

# Function to detect API key type
def detect_api_key_type(api_key):
    # Check for OpenAI key pattern (sk-...)
    if api_key.startswith("sk-"):
        return "openai"
    
    # Check for Google API key pattern (typically longer alphanumeric strings)
    if re.match(r'^AIza[0-9A-Za-z_-]{35}$', api_key):
        return "google"
    
    # Check for Anthropic/Claude API key pattern (sk-ant-...)
    if api_key.startswith("sk-ant-"):
        return "anthropic"
    
    # Default to OpenAI if we can't determine
    return "unknown"

# Generate mandala using OpenAI DALL-E
def generate_with_openai(prompt, api_key, color_theme=None):
    try:
        client = OpenAI(api_key=api_key)
        
        # Add color theme to prompt if specified
        if color_theme:
            detailed_prompt = f"""Create a vibrant, colorful symmetrical mandala inspired by the word '{prompt}' using primarily {color_theme} color palette. 
            The mandala should have intricate patterns, radial symmetry, and be highly detailed.
            Make it ornate with a harmonious {color_theme} color scheme. The background should complement the mandala.
            The style should be highly detailed and decorative, like traditional spiritual mandalas.
            Render in high resolution with clear details."""
        else:
            detailed_prompt = f"""Create a vibrant, colorful symmetrical mandala inspired by the word '{prompt}'. 
            The mandala should have intricate patterns, radial symmetry, and use colors that evoke the essence of '{prompt}'.
            Make it detailed and ornate with a harmonious color palette. The background should complement the mandala.
            The style should be highly detailed and decorative, like traditional spiritual mandalas but with contemporary colors.
            Render in high resolution with clear details."""
        
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
        st.error(f"Error with OpenAI: {str(e)}")
        return None

# Generate mandala using Google Gemini
def generate_with_gemini(prompt, api_key, color_theme=None):
    try:
        genai.configure(api_key=api_key)
        
        # Add color theme to prompt if specified
        if color_theme:
            detailed_prompt = f"""Create a vibrant, symmetrical mandala inspired by the word '{prompt}' using primarily {color_theme} color palette. 
            The mandala should have intricate patterns, radial symmetry, and be highly detailed.
            Make it ornate with a harmonious {color_theme} color scheme. The background should complement the mandala.
            The style should be highly detailed and decorative, like traditional spiritual mandalas.
            Generate as a high-resolution image."""
        else:
            detailed_prompt = f"""Create a vibrant, colorful symmetrical mandala inspired by the word '{prompt}'. 
            The mandala should have intricate patterns, radial symmetry, and use colors that evoke the essence of '{prompt}'.
            Make it detailed and ornate with a harmonious color palette. The background should complement the mandala.
            The style should be highly detailed and decorative, like traditional spiritual mandalas but with contemporary colors.
            Generate as a high-resolution image."""
        
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content(detailed_prompt)
        
        # Extract image from response
        image_data = response.parts[0].image_data
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
        return image
        
    except Exception as e:
        st.error(f"Error with Google Gemini: {str(e)}")
        return None

# Function for Anthropic/Claude API (placeholder - not fully implemented as Claude doesn't have direct image generation yet)
def generate_with_anthropic(prompt, api_key, color_theme=None):
    st.warning("Anthropic/Claude direct image generation is not fully supported yet. Redirecting to OpenAI...")
    return generate_with_openai(prompt, api_key, color_theme)

# Main mandala generation function that routes to the correct API
def generate_mandala(prompt_word, api_key, color_theme=None):
    # Detect API key type
    api_type = detect_api_key_type(api_key)
    
    st.info(f"🎨 Generating your beautiful mandala using {api_type.upper()} API... Please wait a moment.")
    
    # Route to the correct API based on the detected type
    if api_type == "openai":
        return generate_with_openai(prompt_word, api_key, color_theme)
    elif api_type == "google":
        return generate_with_gemini(prompt_word, api_key, color_theme)
    elif api_type == "anthropic":
        return generate_with_anthropic(prompt_word, api_key, color_theme)
    else:
        st.warning("Unknown API key type. Attempting with OpenAI...")
        return generate_with_openai(prompt_word, api_key, color_theme)

# Function to create a download link for the image
def get_image_download_link(img, filename, text, format="PNG"):
    buffered = io.BytesIO()
    if format.upper() == "JPG" or format.upper() == "JPEG":
        img.save(buffered, format="JPEG", quality=95)
        mime = "image/jpeg"
        ext = "jpg"
    else:
        img.save(buffered, format="PNG")
        mime = "image/png"
        ext = "png"
    
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:{mime};base64,{img_str}" download="{filename}.{ext}" class="download-btn">{text}</a>'
    return href

# Main app functionality
def main():
    # API Key input with password field
    api_key = st.text_input("Enter your API Key (OpenAI, Google Gemini, or Anthropic):", type="password", 
                           help="Your API key will be used only for this session and won't be stored.")
    
    # Check if API key is in Streamlit secrets if not provided
    if not api_key and "API_KEY" in st.secrets:
        api_key = st.secrets["API_KEY"]
    
    # Input for the inspiration word
    inspiration_word = st.text_input("Enter a word for inspiration:", placeholder="e.g., ocean, fire, forest, love...")
    
    # Color theme selection
    st.write("Choose a color theme (optional):")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        blue_theme = st.button("🔵 Blue")
    with col2:
        green_theme = st.button("🟢 Green")
    with col3:
        red_theme = st.button("🔴 Red")
    with col4:
        purple_theme = st.button("🟣 Purple")
    with col5:
        custom_theme = st.button("🎨 Random")
    
    # Set color theme based on button clicks
    color_theme = None
    if blue_theme:
        color_theme = "blue"
    elif green_theme:
        color_theme = "green"
    elif red_theme:
        color_theme = "red"
    elif purple_theme:
        color_theme = "purple"
    elif custom_theme:
        color_theme = "vibrant"
    
    # Store color theme in session state
    if 'color_theme' not in st.session_state or color_theme:
        st.session_state.color_theme = color_theme
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("🔮 Generate Mandala")
    
    # Storage for generated image in session state
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None
    
    # Generate mandala when button is clicked
    if generate_button and inspiration_word and api_key:
        with st.spinner("Creating your mandala... This might take up to 30 seconds"):
            mandala_image = generate_mandala(inspiration_word, api_key, st.session_state.color_theme)
            if mandala_image:
                st.session_state.generated_image = mandala_image
                st.session_state.inspiration_word = inspiration_word
    
    # Display generated mandala and download buttons
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
        base_filename = f"mandala_{st.session_state.inspiration_word}_{timestamp}"
        
        # Download options
        st.write("### Download Options")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                get_image_download_link(
                    st.session_state.generated_image, 
                    base_filename, 
                    "📥 Download as PNG",
                    "PNG"
                ),
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                get_image_download_link(
                    st.session_state.generated_image, 
                    base_filename, 
                    "📥 Download as JPG",
                    "JPG"
                ),
                unsafe_allow_html=True
            )
        
        # Add some space and a note
        st.write("")
        st.info("💡 Generate as many mandalas as you like! Each one will be unique.")
        
        # Option to try another color theme for the same word
        st.write("### Try another color theme?")
        if st.button("Generate with a different color theme"):
            st.session_state.color_theme = None
            st.experimental_rerun()

if __name__ == "__main__":
    main()
