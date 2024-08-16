import os
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import base64
from io import BytesIO

DEFAULT_FONT_PATH = "arial.ttf"

def calculate_font_size(draw, text, img_width, img_height, width_percentage, height_percentage):
    max_width = img_width * width_percentage
    max_height = img_height * height_percentage

    # Start with an initial guess for font size
    font_size = 1
    font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)

    # Increase font size until the text exceeds width or height constraints
    while True:
        text_width, text_height = draw.textsize(text, font=font)
        if text_width > max_width or text_height > max_height:
            break
        font_size += 1
        font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)

    # Return the last valid font size
    return font_size - 1

def merge_text_with_image(image, texts, width_percentages, height_percentages, text_colors, bg_colors, positions, position_mapping):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size

    for text, width_percentage, height_percentage, text_color, bg_color, position in zip(texts, width_percentages, height_percentages, text_colors, bg_colors, positions):
        # Calculate font size based on height and adjust for width
        font_size = calculate_font_size(draw, text, img_width, img_height, width_percentage, height_percentage)
        font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
        text_width, text_height = draw.textsize(text, font=font)

        if position == "top-left":
            x = 10
            y = 10
        elif position == "top-center":
            x = (img_width - text_width) // 2
            y = 10
        elif position == "top-right":
            x = img_width - text_width - 10
            y = 10
        elif position == "bottom-left":
            x = 10
            y = img_height - text_height - 10
        elif position == "bottom-center":
            x = (img_width - text_width) // 2
            y = img_height - text_height - 10
        elif position == "bottom-right":
            x = img_width - text_width - 10
            y = img_height - text_height - 10
        elif position == "center":
            x = (img_width - text_width) // 2
            y = (img_height - text_height) // 2

        # Draw background rectangle for the text
        draw.rectangle([x, y, x + text_width, y + text_height], fill=bg_color)
        # Draw the text
        draw.text((x, y), text, font=font, fill=text_color)

    return img

def overlay_logo(image, logo, logo_position, img_width, img_height, logo_width_percentage, logo_height_percentage):
    img = image.convert("RGBA")  # Ensure the image is in RGBA mode
    logo = logo.convert("RGBA")  # Ensure the logo is in RGBA mode

    logo_width = int(img_width * logo_width_percentage)
    logo_height = int(img_height * logo_height_percentage)

    logo = logo.resize((logo_width, logo_height), Image.ANTIALIAS)

    if logo_position == "top-left":
        x = 10
        y = 10
    elif logo_position == "top-center":
        x = (img_width - logo_width) // 2
        y = 10
    elif logo_position == "top-right":
        x = img_width - logo_width - 10
        y = 10
    elif logo_position == "middle-left":
        x = 10
        y = (img_height - logo_height) // 2
    elif logo_position == "middle-center":
        x = (img_width - logo_width) // 2
        y = (img_height - logo_height) // 2
    elif logo_position == "middle-right":
        x = img_width - logo_width - 10
        y = (img_height - logo_height) // 2
    elif logo_position == "bottom-left":
        x = 10
        y = img_height - logo_height - 10
    elif logo_position == "bottom-center":
        x = (img_width - logo_width) // 2
        y = img_height - logo_height - 10
    elif logo_position == "bottom-right":
        x = img_width - logo_width - 10
        y = img_height - logo_height - 10

    # Paste the logo onto the image
    img.paste(logo, (x, y), logo)

    return img.convert("RGB")

def download_images(images_with_text, text_idx, selected_sizes, image_sizes):
    for idx, image in enumerate(images_with_text):
        for selected_size_label in selected_sizes:
            image_size = image_sizes[selected_size_label]
            image = image.resize(image_size, Image.ANTIALIAS)
            st.image(image, caption=f"Image {idx + 1}", use_column_width=False)

            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            href = f'<a href="data:file/png;base64,{img_str}" download="image_{text_idx}_{selected_size_label}.png">Download Image {idx + 1}</a>'
            st.markdown(href, unsafe_allow_html=True)

def main():
    st.title("Image Text and Logo Overlay App")

    uploaded_images = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    uploaded_logo = st.file_uploader("Upload logo image", type=["jpg", "jpeg", "png"])

    if uploaded_images:
        st.write("Images uploaded successfully!")

    if uploaded_logo:
        st.write("Logo uploaded successfully!")

    call_to_action_text = st.text_input("Call to Action Text")
    call_to_action_width_percentage = st.slider("Call to Action Width (Percentage of Image Width)", 1, 100, 50, step=1) / 100.0
    call_to_action_height_percentage = st.slider("Call to Action Height (Percentage of Image Height)", 1, 100, 10, step=1) / 100.0
    call_to_action_position = st.selectbox("Call to Action Position", ["top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right", "center"])
    call_to_action_text_color = st.color_picker("Call to Action Text Color", "#FFFFFF")
    call_to_action_bg_color = st.color_picker("Call to Action Background Color", "#000000")

    description_text = st.text_input("Description Text")
    description_width_percentage = st.slider("Description Width (Percentage of Image Width)", 1, 100, 50, step=1) / 100.0
    description_height_percentage = st.slider("Description Height (Percentage of Image Height)", 1, 100, 10, step=1) / 100.0
    description_position = st.selectbox("Description Position", ["top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right", "center"])
    description_text_color = st.color_picker("Description Text Color", "#FFFFFF")
    description_bg_color = st.color_picker("Description Background Color", "#000000")

    logo_width_percentage = st.slider("Logo Width (Percentage of Image Width)", 1, 100, 20, step=1) / 100.0
    logo_height_percentage = st.slider("Logo Height (Percentage of Image Height)", 1, 100, 20, step=1) / 100.0
    logo_positions = ["top-left", "top-center", "top-right", "middle-left", "middle-center", "middle-right", "bottom-left", "bottom-center", "bottom-right"]
    selected_logo_position = st.selectbox("Select logo position", logo_positions)

    image_sizes = {
        "468 x 60": (468, 60),
        "728 x 90": (728, 90),
        "970 x 90": (970, 90),
        "320 x 50": (320, 50),
        "250 x 250": (250, 250),
        "200 x 200": (200, 200),
        "300 x 250": (300, 250),
        "336 x 280": (336, 280),
    }
    selected_image_sizes = [size for size, _ in image_sizes.items() if st.checkbox(size)]

    position_mapping = {
        "top-left": (10, 10),
        "top-center": ("center", 10),
        "top-right": (None, 10),
        "bottom-left": (10, None),
        "bottom-center": ("center", "bottom"),
        "bottom-right": (None, None),
        "center": ("center", "center"),
    }

    if st.button("Merge and Download"):
        if uploaded_images:
            st.write("Processing images...")
            for image in uploaded_images:
                img = Image.open(image)
                texts = [call_to_action_text, description_text]
                width_percentages = [call_to_action_width_percentage, description_width_percentage]
                height_percentages = [call_to_action_height_percentage, description_height_percentage]
                positions = [call_to_action_position, description_position]
                text_colors = [call_to_action_text_color, description_text_color]
                bg_colors = [call_to_action_bg_color, description_bg_color]
                merged_img = merge_text_with_image(img, texts, width_percentages, height_percentages, text_colors, bg_colors, positions, position_mapping)
                
                if uploaded_logo:
                    logo_img = Image.open(uploaded_logo)
                    merged_img = overlay_logo(merged_img, logo_img, selected_logo_position, img.width, img.height, logo_width_percentage, logo_height_percentage)
                
                download_images([merged_img], 0, selected_image_sizes, image_sizes)
            st.write("Images processed and available for download!")

if __name__ == "__main__":
    main()
