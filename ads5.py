import os
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import base64
from io import BytesIO

DEFAULT_FONT_PATH = "arial.ttf"

def merge_text_with_image(image, texts, font_sizes, text_colors, bg_colors, positions, position_mapping):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    for text, font_size, text_color, bg_color, position in zip(texts, font_sizes, text_colors, bg_colors, positions):
        font = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)
        text_width, text_height = draw.textsize(text, font=font)

        if position == "bottom-center":
            img_width, img_height = img.size
            x = (img_width - text_width) // 2
            y = img_height - text_height
        else:
            x, y = position_mapping[position]

            try:
                x = int(x)
            except (ValueError, TypeError):
                x = None

            try:
                y = int(y)
            except (ValueError, TypeError):
                y = None

        if x is None:
            img_width, _ = img.size
            x = (img_width - text_width) // 2

        if y is None:
            _, img_height = img.size
            y = (img_height - text_height) // 2

        draw.rectangle([x, y, x + text_width, y + text_height], fill=bg_color)
        draw.text((x, y), text, font=font, fill=text_color)

    return img

def overlay_logo(image, logo, logo_position, logo_mapping, max_logo_size_ratio=0.2):
    img = image.convert("RGBA")  # Ensure the image is in RGBA mode
    logo = logo.convert("RGBA")  # Ensure the logo is in RGBA mode

    img_width, img_height = img.size
    logo_max_width = int(img_width * max_logo_size_ratio)
    logo_max_height = int(img_height * max_logo_size_ratio)

    logo.thumbnail((logo_max_width, logo_max_height), Image.ANTIALIAS)
    logo_width, logo_height = logo.size

    x, y = logo_mapping[logo_position]

    if x == "center":
        x = (img_width - logo_width) // 2
    elif x == "right":
        x = img_width - logo_width
    else:  # "left"
        x = 0

    if y == "center":
        y = (img_height - logo_height) // 2
    elif y == "bottom":
        y = img_height - logo_height
    else:  # "top"
        y = 0

    # Create a mask from the alpha channel of the logo
    logo_mask = logo.split()[3]  # This extracts the alpha channel

    # Paste the logo onto the image using the alpha channel as the mask
    img.paste(logo, (x, y), logo_mask)
    
    return img.convert("RGB")  # Convert back to RGB if you don't need alpha

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
    call_to_action_font_size = st.slider("Call to Action Font Size", 10, 100, 40, step=1)
    call_to_action_position = st.selectbox("Call to Action Position", ["top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right", "center"])
    call_to_action_text_color = st.color_picker("Call to Action Text Color", "#FFFFFF")
    call_to_action_bg_color = st.color_picker("Call to Action Background Color", "#000000")

    description_text = st.text_input("Description Text")
    description_font_size = st.slider("Description Font Size", 10, 100, 40, step=1)
    description_position = st.selectbox("Description Position", ["top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right", "center"])
    description_text_color = st.color_picker("Description Text Color", "#FFFFFF")
    description_bg_color = st.color_picker("Description Background Color", "#000000")

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

    logo_mapping = {
        "top-left": ("left", "top"),
        "top-center": ("center", "top"),
        "top-right": ("right", "top"),
        "middle-left": ("left", "center"),
        "middle-center": ("center", "center"),
        "middle-right": ("right", "center"),
        "bottom-left": ("left", "bottom"),
        "bottom-center": ("center", "bottom"),
        "bottom-right": ("right", "bottom"),
    }

    if st.button("Merge and Download"):
        if uploaded_images:
            st.write("Processing images...")
            for image in uploaded_images:
                img = Image.open(image)
                texts = [call_to_action_text, description_text]
                font_sizes = [call_to_action_font_size, description_font_size]
                positions = [call_to_action_position, description_position]
                text_colors = [call_to_action_text_color, description_text_color]
                bg_colors = [call_to_action_bg_color, description_bg_color]
                merged_img = merge_text_with_image(img, texts, font_sizes, text_colors, bg_colors, positions, position_mapping)
                
                if uploaded_logo:
                    logo_img = Image.open(uploaded_logo)
                    merged_img = overlay_logo(merged_img, logo_img, selected_logo_position, logo_mapping)
                
                download_images([merged_img], 0, selected_image_sizes, image_sizes)
            st.write("Images processed and available for download!")

if __name__ == "__main__":
    main()
