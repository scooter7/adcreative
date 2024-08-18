import os
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import base64
from io import BytesIO

DEFAULT_FONT_PATH = "arial.ttf"

def calculate_font_size(draw, text, img_width, img_height, width_percentage, height_percentage):
    max_width = img_width * width_percentage
    max_height = img_height * height_percentage

    font_size = 1
    font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)

    while True:
        text_width, text_height = draw.textsize(text, font=font)
        if text_width > max_width or text_height > max_height:
            break
        font_size += 1
        font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)

    return font_size - 1

def merge_text_with_image(image, call_to_action_text, description_text, width_percentages, height_percentages, text_colors, bg_colors, cta_position, desc_position, logo_position, logo_width_percentage, logo_height_percentage, uploaded_logo):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size

    # Calculating font sizes
    font_size_cta = calculate_font_size(draw, call_to_action_text, img_width, img_height, width_percentages[0], height_percentages[0])
    font_size_desc = calculate_font_size(draw, description_text, img_width, img_height, width_percentages[1], height_percentages[1])
    font_cta = ImageFont.truetype(DEFAULT_FONT_PATH, font_size_cta)
    font_desc = ImageFont.truetype(DEFAULT_FONT_PATH, font_size_desc)

    text_width_cta, text_height_cta = draw.textsize(call_to_action_text, font=font_cta)
    x_cta, y_cta = get_position_coordinates(cta_position, img_width, img_height, text_width_cta, text_height_cta)

    text_width_desc, text_height_desc = draw.textsize(description_text, font=font_desc)
    x_desc, y_desc = get_position_coordinates(desc_position, img_width, img_height, text_width_desc, text_height_desc)

    # Draw text background and text
    draw.rectangle([x_cta, y_cta, x_cta + text_width_cta, y_cta + text_height_cta], fill=bg_colors[0])
    draw.text((x_cta, y_cta), call_to_action_text, font=font_cta, fill=text_colors[0])

    draw.rectangle([x_desc, y_desc, x_desc + text_width_desc, y_desc + text_height_desc], fill=bg_colors[1])
    draw.text((x_desc, y_desc), description_text, font=font_desc, fill=text_colors[1])

    # Overlay logo
    if uploaded_logo:
        img = overlay_logo(img, uploaded_logo, logo_position, img_width, img_height, logo_width_percentage, logo_height_percentage)

    return img

def get_position_coordinates(position, img_width, img_height, text_width, text_height):
    if position == "top-left":
        x = 10
        y = 10
    elif position == "top-center":
        x = (img_width - text_width) // 2
        y = 10
    elif position == "top-right":
        x = img_width - text_width - 10
        y = 10
    elif position == "middle-left":
        x = 10
        y = (img_height - text_height) // 2
    elif position == "middle-center":
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
    elif position == "middle-right":
        x = img_width - text_width - 10
        y = (img_height - text_height) // 2
    elif position == "bottom-left":
        x = 10
        y = img_height - text_height - 10
    elif position == "bottom-center":
        x = (img_width - text_width) // 2
        y = img_height - text_height - 10
    elif position == "bottom-right":
        x = img_width - text_width - 10
        y = img_height - text_height - 10
    return x, y

def overlay_logo(image, uploaded_logo, logo_position, img_width, img_height, logo_width_percentage, logo_height_percentage):
    img = image.convert("RGBA")
    logo = Image.open(uploaded_logo).convert("RGBA")

    logo_width = int(img_width * logo_width_percentage)
    logo_height = int(img_height * logo_height_percentage)

    logo = logo.resize((logo_width, logo_height), Image.ANTIALIAS)

    x, y = get_position_coordinates(logo_position, img_width, img_height, logo_width, logo_height)

    img.paste(logo, (x, y), logo)

    return img.convert("RGB")

def add_draggable_functionality(img_base64, img_width, img_height):
    # Function to enable draggable elements on the image
    st.components.v1.html(f"""
        <div id="image-container" style="position: relative; width: {img_width}px; height: {img_height}px; background-image: url('data:image/png;base64,{img_base64}'); background-size: cover;">
        </div>

        <script>
            var container = document.getElementById('image-container');
            var isDragging = false;
            var currentElement;

            container.addEventListener('mousedown', function(e) {{
                if (e.target !== container) {{
                    isDragging = true;
                    currentElement = e.target;
                    offsetX = e.clientX - currentElement.getBoundingClientRect().left;
                    offsetY = e.clientY - currentElement.getBoundingClientRect().top;
                }}
            }});

            document.addEventListener('mousemove', function(e) {{
                if (isDragging) {{
                    currentElement.style.left = (e.clientX - offsetX) + 'px';
                    currentElement.style.top = (e.clientY - offsetY) + 'px';
                }}
            }});

            document.addEventListener('mouseup', function() {{
                isDragging = false;
            }});
        </script>
    """, height=img_height + 50)

def main():
    st.title("Image Text and Logo Overlay App")

    uploaded_images = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    uploaded_logo = st.file_uploader("Upload logo image", type=["jpg", "jpeg", "png"])

    if uploaded_logo:
        logo = Image.open(uploaded_logo)
        buffered_logo = BytesIO()
        logo.save(buffered_logo, format="PNG")
        logo_base64 = base64.b64encode(buffered_logo.getvalue()).decode()

    if uploaded_images and uploaded_logo:
        for uploaded_image in uploaded_images:
            img = Image.open(uploaded_image)

            # User inputs for text and layout
            call_to_action_text = st.text_input("Call to Action Text")
            description_text = st.text_input("Description Text")

            width_percentage_cta = st.slider("Call to Action Width (Percentage of Image Width)", 1, 100, 50, step=1) / 100.0
            height_percentage_cta = st.slider("Call to Action Height (Percentage of Image Height)", 1, 100, 10, step=1) / 100.0
            width_percentage_desc = st.slider("Description Width (Percentage of Image Width)", 1, 100, 50, step=1) / 100.0
            height_percentage_desc = st.slider("Description Height (Percentage of Image Height)", 1, 100, 10, step=1) / 100.0

            call_to_action_text_color = st.color_picker("Call to Action Text Color", "#FFFFFF")
            call_to_action_bg_color = st.color_picker("Call to Action Background Color", "#000000")
            description_text_color = st.color_picker("Description Text Color", "#FFFFFF")
            description_bg_color = st.color_picker("Description Background Color", "#000000")

            logo_width_percentage = st.slider("Logo Width (Percentage of Image Width)", 1, 100, 20, step=1) / 100.0
            logo_height_percentage = st.slider("Logo Height (Percentage of Image Height)", 1, 100, 20, step=1) / 100.0

            img_with_overlays = merge_text_with_image(
                img,
                call_to_action_text,
                description_text,
                [width_percentage_cta, width_percentage_desc],
                [height_percentage_cta, height_percentage_desc],
                [call_to_action_text_color, description_text_color],
                [call_to_action_bg_color, description_bg_color],
                "top-left",  # You can customize this with user input as well
                "bottom-right",  # You can customize this with user input as well
                "middle-center",  # You can customize this with user input as well
                logo_width_percentage,
                logo_height_percentage,
                uploaded_logo
            )

            buffered = BytesIO()
            img_with_overlays.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # Adding draggable functionality
            add_draggable_functionality(img_str, img_with_overlays.width, img_with_overlays.height)

            st.markdown(f'<a href="data:file/png;base64,{img_str}" download="image_with_overlays.png">Download Image</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
