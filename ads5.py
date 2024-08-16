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

def merge_text_with_image(image, call_to_action_text, description_text, width_percentages, height_percentages, text_colors, bg_colors, cta_positions, desc_positions):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size

    for (cta_text, desc_text, cta_position, desc_position) in zip(call_to_action_text, description_text, cta_positions, desc_positions):
        # Calculate font size based on height and adjust for width
        font_size_cta = calculate_font_size(draw, cta_text, img_width, img_height, width_percentages[0], height_percentages[0])
        font_size_desc = calculate_font_size(draw, desc_text, img_width, img_height, width_percentages[1], height_percentages[1])
        font_cta = ImageFont.truetype(DEFAULT_FONT_PATH, font_size_cta)
        font_desc = ImageFont.truetype(DEFAULT_FONT_PATH, font_size_desc)

        # Position for call to action text
        text_width_cta, text_height_cta = draw.textsize(cta_text, font=font_cta)
        x_cta, y_cta = get_position_coordinates(cta_position, img_width, img_height, text_width_cta, text_height_cta)

        # Position for description text
        text_width_desc, text_height_desc = draw.textsize(desc_text, font=font_desc)
        x_desc, y_desc = get_position_coordinates(desc_position, img_width, img_height, text_width_desc, text_height_desc)

        # Draw the background rectangles and texts
        draw.rectangle([x_cta, y_cta, x_cta + text_width_cta, y_cta + text_height_cta], fill=bg_colors[0])
        draw.text((x_cta, y_cta), cta_text, font=font_cta, fill=text_colors[0])

        draw.rectangle([x_desc, y_desc, x_desc + text_width_desc, y_desc + text_height_desc], fill=bg_colors[1])
        draw.text((x_desc, y_desc), desc_text, font=font_desc, fill=text_colors[1])

    return img

def get_position_coordinates(position, img_width, img_height, text_width, text_height, y_offset=0):
    if position == "top-left":
        x = 10
        y = 10 + y_offset
    elif position == "top-center":
        x = (img_width - text_width) // 2
        y = 10 + y_offset
    elif position == "top-right":
        x = img_width - text_width - 10
        y = 10 + y_offset
    elif position == "middle-left":
        x = 10
        y = (img_height - text_height) // 2 + y_offset
    elif position == "middle-center":
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2 + y_offset
    elif position == "middle-right":
        x = img_width - text_width - 10
        y = (img_height - text_height) // 2 + y_offset
    elif position == "bottom-left":
        x = 10
        y = img_height - text_height - 10 + y_offset
    elif position == "bottom-center":
        x = (img_width - text_width) // 2
        y = img_height - text_height - 10 + y_offset
    elif position == "bottom-right":
        x = img_width - text_width - 10
        y = img_height - text_height - 10 + y_offset
    return x, y

def overlay_logo(image, logo, logo_position, img_width, img_height, logo_width_percentage, logo_height_percentage):
    img = image.convert("RGBA")  # Ensure the image is in RGBA mode
    logo = logo.convert("RGBA")  # Ensure the logo is in RGBA mode

    logo_width = int(img_width * logo_width_percentage)
    logo_height = int(img_height * logo_height_percentage)

    logo = logo.resize((logo_width, logo_height), Image.ANTIALIAS)

    x, y = get_position_coordinates(logo_position, img_width, img_height, logo_width, logo_height)

    # Paste the logo onto the image
    img.paste(logo, (x, y), logo)

    return img.convert("RGB")

def download_images(images_with_text, selected_sizes, image_sizes):
    for idx, image in enumerate(images_with_text):
        for selected_size_label in selected_sizes:
            image_size = image_sizes[selected_size_label]
            image_resized = image.resize(image_size, Image.ANTIALIAS)
            st.image(image_resized, caption=f"Image {idx + 1} - Size: {selected_size_label}", use_column_width=False)

            buffered = BytesIO()
            image_resized.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            href = f'<a href="data:file/png;base64,{img_str}" download="image_{idx + 1}_{selected_size_label}.png">Download Image</a>'
            st.markdown(href, unsafe_allow_html=True)

def main():
    st.title("Image Text and Logo Overlay App")

    uploaded_images = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    uploaded_logo = st.file_uploader("Upload logo image", type=["jpg", "jpeg", "png"])

    if uploaded_images:
        st.write("Images uploaded successfully!")

    if uploaded_logo:
        st.write("Logo uploaded successfully!")

    num_pairs = st.number_input("Number of Call to Action + Description Pairs", min_value=1, step=1)
    call_to_action_texts = [st.text_input(f"Call to Action Text {i + 1}") for i in range(num_pairs)]
    description_texts = [st.text_input(f"Description Text {i + 1}") for i in range(num_pairs)]
    
    width_percentage_cta = st.slider("Call to Action Width (Percentage of Image Width)", 1, 100, 50, step=1) / 100.0
    height_percentage_cta = st.slider("Call to Action Height (Percentage of Image Height)", 1, 100, 10, step=1) / 100.0
    width_percentage_desc = st.slider("Description Width (Percentage of Image Width)", 1, 100, 50, step=1) / 100.0
    height_percentage_desc = st.slider("Description Height (Percentage of Image Height)", 1, 100, 10, step=1) / 100.0

    selected_cta_positions = st.multiselect("Select Call to Action Text Positions", ["top-left", "top-center", "top-right", "middle-left", "middle-center", "middle-right", "bottom-left", "bottom-center", "bottom-right"])
    selected_desc_positions = st.multiselect("Select Description Text Positions", ["top-left", "top-center", "top-right", "middle-left", "middle-center", "middle-right", "bottom-left", "bottom-center", "bottom-right"])

    call_to_action_text_color = st.color_picker("Call to Action Text Color", "#FFFFFF")
    call_to_action_bg_color = st.color_picker("Call to Action Background Color", "#000000")
    description_text_color = st.color_picker("Description Text Color", "#FFFFFF")
    description_bg_color = st.color_picker("Description Background Color", "#000000")

    logo_width_percentage = st.slider("Logo Width (Percentage of Image Width)", 1, 100, 20, step=1) / 100.0
    logo_height_percentage = st.slider("Logo Height (Percentage of Image Height)", 1, 100, 20, step=1) / 100.0
    selected_logo_positions = st.multiselect("Select Logo Positions", ["top-left", "top-center", "top-right", "middle-left", "middle-center", "middle-right", "bottom-left", "bottom-center", "bottom-right"])

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

    if st.button("Merge and Download"):
        if uploaded_images and selected_cta_positions and selected_desc_positions and selected_logo_positions:
            st.write("Processing images...")
            images_with_text = []
            for image in uploaded_images:
                img = Image.open(image)
                for cta_position in selected_cta_positions:
                    for desc_position in selected_desc_positions:
                        for call_to_action_text, description_text in zip(call_to_action_texts, description_texts):
                            merged_img = merge_text_with_image(
                                img,
                                [call_to_action_text],
                                [description_text],
                                [width_percentage_cta, width_percentage_desc],
                                [height_percentage_cta, height_percentage_desc],
                                [call_to_action_text_color, description_text_color],
                                [call_to_action_bg_color, description_bg_color],
                                [cta_position],
                                [desc_position]
                            )
                            for logo_position in selected_logo_positions:
                                if uploaded_logo:
                                    logo_img = Image.open(uploaded_logo)
                                    final_img = overlay_logo(
                                        merged_img,
                                        logo_img,
                                        logo_position,
                                        img.width,
                                        img.height,
                                        logo_width_percentage,
                                        logo_height_percentage
                                    )
                                else:
                                    final_img = merged_img
                                images_with_text.append(final_img)
            download_images(images_with_text, selected_image_sizes, image_sizes)
            st.write("Images processed and available for download!")

if __name__ == "__main__":
    main()
