import os
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import base64
from io import BytesIO

DEFAULT_FONT_PATH = "arial.ttf"

def merge_text_with_image(image, text, font_size, text_color, bg_color, position, position_mapping):
    img = image.copy()
    draw = ImageDraw.Draw(img)
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

def download_images(images_with_text, text_idx, selected_sizes, font_size, image_sizes):
    for idx, image in enumerate(images_with_text):
        for selected_size_label in selected_sizes:
            image_size = image_sizes[selected_size_label]
            image = image.resize(image_size, Image.ANTIALIAS)
            st.image(image, caption=f"Text {text_idx + 1} - Image {idx + 1} - Font Size {font_size}", use_column_width=False)

            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            href = f'<a href="data:file/png;base64,{img_str}" download="text_image_{text_idx}_{selected_size_label}_font_size_{font_size}.png">Download Image {idx + 1}</a>'
            st.markdown(href, unsafe_allow_html=True)

def main():
    st.title("Image Text Overlay App")

    uploaded_images = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    num_texts = st.number_input("Enter the number of text fields", min_value=1, step=1)
    texts = [st.text_input(f"Enter text {i + 1}") for i in range(num_texts)]
    
    text_color_bg_combinations = {
        "White Text with Black Background": ((255, 255, 255), (0, 0, 0)),
        "Black Text with White Background": ((0, 0, 0), (255, 255, 255))
    }
    
    selected_combinations = [combo for combo, _ in text_color_bg_combinations.items() if st.checkbox(combo)]
    
    font_sizes = [st.slider(f"Text Font Size {i + 1}", 10, 100, 40, step=1) for i in range(st.number_input("Enter the number of font sizes", min_value=1, step=1))]

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
            for text_idx, text in enumerate(texts):
                for font_size in font_sizes:
                    for combo in selected_combinations:
                        text_color, bg_color = text_color_bg_combinations[combo]
                        for position in selected_positions:
                            images_with_text = []
                            for image in uploaded_images:
                                img = Image.open(image)
                                for selected_size_label in selected_image_sizes:
                                    resized_img = img.copy()
                                    resized_img.thumbnail(image_sizes[selected_size_label])
                                    merged_img = merge_text_with_image(resized_img, text, font_size, text_color, bg_color, position, position_mapping)
                                    images_with_text.append(merged_img)
                            download_images(images_with_text, text_idx, selected_image_sizes, font_size, image_sizes)

if __name__ == "__main__":
    main()
