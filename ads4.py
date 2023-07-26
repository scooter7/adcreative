import os
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import base64
from io import BytesIO

DEFAULT_FONT_PATH = "arial.ttf"

# The merge_text_with_image function here

# The download_images function here

def main():
    st.title("Image Text Overlay App")

    uploaded_images = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    num_texts = st.number_input("Enter the number of text fields", min_value=1, step=1)
    texts = [st.text_input(f"Enter text {i + 1}") for i in range(num_texts)]

    text_colors = []
    text_color_black = st.checkbox("Text Color (Black)")
    if text_color_black:
        text_colors.append((0, 0, 0))
    text_color_white = st.checkbox("Text Color (White)")
    if text_color_white:
        text_colors.append((255, 255, 255))

    bg_colors = [None]  # Add None for the "No Background" option
    bg_color_black = st.checkbox("Text Background Area (Black)")
    if bg_color_black:
        bg_colors.append((0, 0, 0))
    bg_color_white = st.checkbox("Text Background Area (White)")
    if bg_color_white:
        bg_colors.append((255, 255, 255))

    font_sizes = []
    num_font_sizes = st.number_input("Enter the number of font sizes", min_value=1, step=1)
    for i in range(num_font_sizes):
        font_sizes.append(st.slider(f"Text Font Size {i + 1}", 10, 100, 40, step=1))

    positions = ["top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right", "center"]
    selected_positions = [position for position in positions if st.checkbox(position.title())]

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
    selected_image_sizes = [size for size, selected in image_sizes.items() if st.checkbox(size)]

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
            for text_idx, text in enumerate(texts):
                for font_size in font_sizes:
                    for text_color in text_colors:
                        for bg_color in bg_colors:
                            for position in selected_positions:
                                images_with_text = []
                                for image in uploaded_images:
                                    img = Image.open(image)
                                    for selected_size_label, selected_size in image_sizes.items():
                                        resized_img = img.copy()
                                        resized_img.thumbnail(selected_size)
                                        merged_img = merge_text_with_image(resized_img, text, font_size, text_color, bg_color, position, position_mapping)
                                        images_with_text.append(merged_img)

                                        # Move this function call here and pass the correct selected_size_label
                                        download_images(images_with_text, text_idx, selected_size_label, font_size, image_sizes)

if __name__ == "__main__":
    main()
