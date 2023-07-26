import os
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import base64
from io import BytesIO

def merge_text_with_image(image, text, font_size, text_color, bg_color, position, position_mapping):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", font_size)
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

    if bg_color is not None:
        draw.rectangle([x, y, x + text_width, y + text_height], fill=bg_color)
    draw.text((x, y), text, font=font, fill=text_color)

    return img


def download_images(images_with_text, text_idx, image_size, font_size):
    for idx, image in enumerate(images_with_text):
        # Resize the image to the desired image size
        image = image.resize(image_size, Image.ANTIALIAS)

        # Display the image with its actual dimensions in the app view
        st.image(image, caption=f"Text {text_idx + 1} - Image {idx + 1} - Font Size {font_size}", width=image.width)

        # Download link for the image
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        href = f'<a href="data:file/png;base64,{img_str}" download="text_image_{text_idx}_{image_size}_font_size_{font_size}.png">Download Image {idx + 1}</a>'
        st.markdown(href, unsafe_allow_html=True)

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
                    images_with_text = []
                    for image in uploaded_images:
                        img = Image.open(image)
                        for position in selected_positions:
                            for selected_size in selected_image_sizes:
                                image_size = image_sizes[selected_size]
                                resized_img = img.copy()
                                resized_img.thumbnail(image_size)
                                for text_color in text_colors:
                                    for bg_color in bg_colors:
                                        merged_img = merge_text_with_image(resized_img, text, font_size, text_color, bg_color, position, position_mapping)
                                        images_with_text.append(merged_img)

                    download_images(images_with_text, text_idx, selected_size, font_size)

if __name__ == "__main__":
    main()
