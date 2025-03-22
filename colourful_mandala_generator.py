import streamlit as st
import openai
import requests
from PIL import Image
from io import BytesIO
import base64
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Colorful Mandala Generator",
    page_icon="🌈",
    layout="centered"
)

# App title and styling
st.markdown("""
# 🌈 Colorful Mandala Art Generator
Generate vibrant and colorful mandala art from a single word inspiration.
""")

# Sidebar for API key and color settings
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    
    st.subheader("Color Preferences")
    color_style = st.radio(
        "Choose color style:",
        ["Vibrant", "Pastel", "Jewel Tone", "Rainbow", "Custom"]
    )
    
    if color_style == "Custom":
        primary_color = st.color_picker("Primary Color", "#FF5733")
        secondary_color = st.color_picker("Secondary Color", "#33A1FF")
        accent_color = st.color_picker("Accent Color", "#FFCC33")
    
    st.markdown("---")
    st.markdown("## About")
    st.markdown("""
    This app uses OpenAI's DALL-E 3 to generate unique colorful mandala art based on your inspiration.
    
    Provide a single word, select your color preferences, and the AI will create a beautiful mandala design for you.
    """)

# Function to generate the mandala image
def generate_mandala(prompt, api_key, color_style, custom_colors=None):
    if not api_key:
        return None, "Please enter an OpenAI API key in the sidebar."
    
    openai.api_key = api_key
    
    # Define color guidance based on selected style
    color_guidance = ""
    if color_style == "Vibrant":
        color_guidance = "Use vibrant, bold, and saturated colors like bright blues, intense reds, deep purples, and golden yellows."
    elif color_style == "Pastel":
        color_guidance = "Use soft, light pastel colors like baby blue, light pink, mint green, and lavender."
    elif color_style == "Jewel Tone":
        color_guidance = "Use rich jewel tones like emerald green, sapphire blue, ruby red, and amethyst purple."
    elif color_style == "Rainbow":
        color_guidance = "Use a full spectrum of rainbow colors in a harmonious progression."
    elif color_style == "Custom" and custom_colors:
        primary = custom_colors.get("primary", "#FF5733")
        secondary = custom_colors.get("secondary", "#33A1FF")
        accent = custom_colors.get("accent", "#FFCC33")
        color_guidance = f"Use primarily these colors: {primary} as the dominant color, {secondary} as the secondary color, and {accent} as an accent color."
    
    # Enhance the prompt to create a colorful mandala
    enhanced_prompt = f"Create a detailed colorful symmetric mandala design inspired by the concept of '{prompt}'. The mandala should be intricate, perfectly symmetrical, and feature detailed patterns. {color_guidance} The design should be centered and circular with radiating patterns. Make it high-resolution and suitable for printing. The background should complement the mandala."
    
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            style="vivid"
        )
        
        image_url = response.data[0].url
        
        # Download the image
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        
        return image, None
    except Exception as e:
        return None, f"Error: {str(e)}"

# Function to create a download link for the image
def get_image_download_link(img, filename, text):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}">Download {text}</a>'
    return href

# Main app layout
word_inspiration = st.text_input("Enter a word for inspiration:", placeholder="e.g., ocean, serenity, forest, cosmos")

generate_button = st.button("Generate Colorful Mandala")

# Store generated image in session state
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
    st.session_state.error_message = None
    st.session_state.last_prompt = None
    st.session_state.last_color_style = None

# Generate image when button is clicked
if generate_button and word_inspiration:
    # Prepare custom colors if needed
    custom_colors = None
    if color_style == "Custom":
        custom_colors = {
            "primary": primary_color,
            "secondary": secondary_color,
            "accent": accent_color
        }
    
    with st.spinner("Creating your colorful mandala art..."):
        image, error = generate_mandala(word_inspiration, api_key, color_style, custom_colors)
        st.session_state.generated_image = image
        st.session_state.error_message = error
        st.session_state.last_prompt = word_inspiration
        st.session_state.last_color_style = color_style

# Display image or error
if st.session_state.generated_image:
    st.markdown(f"### Colorful Mandala inspired by: '{st.session_state.last_prompt}'")
    st.markdown(f"**Color Style:** {st.session_state.last_color_style}")
    
    # Display the image
    st.image(st.session_state.generated_image, use_container_width=True)
    
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"mandala_{st.session_state.last_prompt}_{timestamp}.png"
    
    # Create download button
    st.markdown(get_image_download_link(st.session_state.generated_image, filename, "Image"), unsafe_allow_html=True)
    
    # Additional download options
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save as High Resolution"):
            # Save high resolution version
            high_res_filename = f"mandala_{st.session_state.last_prompt}_{timestamp}_high_res.png"
            st.session_state.generated_image.save(high_res_filename, "PNG")
            st.success(f"High resolution image saved as {high_res_filename}")
    
    with col2:
        if st.button("Generate Another"):
            st.session_state.generated_image = None
            st.session_state.last_prompt = None
            st.session_state.last_color_style = None
            st.experimental_rerun()

elif st.session_state.error_message:
    st.error(st.session_state.error_message)

# Display examples and tips at the bottom
with st.expander("Tips for better mandalas"):
    st.markdown("""
    - Try using abstract concepts like "tranquility", "harmony", or "infinity"
    - Nature-related words often create beautiful patterns
    - Emotional words can lead to interesting designs
    - Try combining words with colors like "ocean-blue" or "forest-emerald"
    - Different color styles work better for different concepts:
        - Vibrant: Great for energetic concepts like "celebration" or "vitality"
        - Pastel: Works well with gentle concepts like "serenity" or "dream"
        - Jewel Tone: Perfect for rich concepts like "royalty" or "abundance"
        - Rainbow: Ideal for diverse concepts like "diversity" or "spectrum"
        - Custom: Best when you have specific colors in mind for your concept
    """)