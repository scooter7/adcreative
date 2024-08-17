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

def overlay_logo(image, uploaded_logo, logo_position, img_width, img_height, logo_width_percentage, logo_height_percentage):
    img = image.convert("RGBA")
    logo = Image.open(uploaded_logo).convert("RGBA")

    logo_width = int(img_width * logo_width_percentage)
    logo_height = int(img_height * logo_height_percentage)

    logo = logo.resize((logo_width, logo_height), Image.ANTIALIAS)

    x, y = get_position_coordinates(logo_position, img_width, img_height, logo_width, logo_height)

    img.paste(logo, (x, y), logo)

    return img.convert("RGB")

def merge_text_with_image(image, call_to_action_text, description_text, width_percentages, height_percentages, text_colors, bg_colors, cta_position, desc_position, logo_position, logo_width_percentage, logo_height_percentage, uploaded_logo):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size

    font_size_cta = calculate_font_size(draw, call_to_action_text, img_width, img_height, width_percentages[0], height_percentages[0])
    font_size_desc = calculate_font_size(draw, description_text, img_width, img_height, width_percentages[1], height_percentages[1])
    font_cta = ImageFont.truetype(DEFAULT_FONT_PATH, font_size_cta)
    font_desc = ImageFont.truetype(DEFAULT_FONT_PATH, font_size_desc)

    text_width_cta, text_height_cta = draw.textsize(call_to_action_text, font=font_cta)
    x_cta, y_cta = get_position_coordinates(cta_position, img_width, img_height, text_width_cta, text_height_cta)

    text_width_desc, text_height_desc = draw.textsize(description_text, font=font_desc)
    x_desc, y_desc = get_position_coordinates(desc_position, img_width, img_height, text_width_desc, text_height_desc)

    draw.rectangle([x_cta, y_cta, x_cta + text_width_cta, y_cta + text_height_cta], fill=bg_colors[0])
    draw.text((x_cta, y_cta), call_to_action_text, font=font_cta, fill=text_colors[0])

    draw.rectangle([x_desc, y_desc, x_desc + text_width_desc, y_desc + text_height_desc], fill=bg_colors[1])
    draw.text((x_desc, y_desc), description_text, font=font_desc, fill=text_colors[1])

    if logo_position != cta_position and logo_position != desc_position:
        img = overlay_logo(img, uploaded_logo, logo_position, img_width, img_height, logo_width_percentage, logo_height_percentage)

    return img

def download_images(images_with_text, selected_image_sizes):
    for idx, image in enumerate(images_with_text):
        for channel, label, dimensions in selected_image_sizes:
            image_resized = image.resize(dimensions, Image.ANTIALIAS)
            st.image(image_resized, caption=f"Image {idx + 1} - Channel: {channel}, Size: {label}", use_column_width=False)

            buffered = BytesIO()
            image_resized.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            href = f'<a href="data:file/png;base64,{img_str}" download="image_{idx + 1}_{channel}_{label}.png">Download Image</a>'
            st.markdown(href, unsafe_allow_html=True)

def add_draggable_functionality(img_base64, call_to_action_text, description_text, logo_base64, img_width, img_height):
    # HTML and JS for draggable elements
    st.components.v1.html(f"""
        <style>
            .draggable {{
                position: absolute;
                cursor: move;
            }}
            #logoImage img {{
                width: 100px; height: auto;
            }}
        </style>
        <div style="position: relative; width: {img_width}px; height: {img_height}px; background-image: url('data:image/png;base64,{img_base64}'); background-size: contain; background-repeat: no-repeat;">
            <div id="ctaText" class="draggable" style="top: 50px; left: 50px; font-size: 24px; color: white;">
                {call_to_action_text}
            </div>
            <div id="descText" class="draggable" style="top: 150px; left: 50px; font-size: 18px; color: yellow;">
                {description_text}
            </div>
            <div id="logoImage" class="draggable" style="top: 250px; left: 50px;">
                <img src="data:image/png;base64,{logo_base64}">
            </div>
        </div>

        <script>
            document.querySelectorAll('.draggable').forEach(elmnt => {{
                elmnt.onmousedown = function(event) {{
                    event.preventDefault();
                    let shiftX = event.clientX - elmnt.getBoundingClientRect().left;
                    let shiftY = event.clientY - elmnt.getBoundingClientRect().top;
                    
                    function moveAt(pageX, pageY) {{
                        elmnt.style.left = pageX - shiftX + 'px';
                        elmnt.style.top = pageY - shiftY + 'px';
                    }}

                    function onMouseMove(event) {{
                        moveAt(event.pageX, event.pageY);
                    }}

                    document.addEventListener('mousemove', onMouseMove);

                    elmnt.onmouseup = function() {{
                        document.removeEventListener('mousemove', onMouseMove);
                        elmnt.onmouseup = null;
                    }};
                }};
                
                // Disable drag and drop on mobile devices
                elmnt.ontouchstart = function() {{
                    return false;
                }};
            }});
        </script>
    """, height=img_height + 50)

def main():
    st.title("Image Text and Logo Overlay App")

    uploaded_images = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    uploaded_logo = st.file_uploader("Upload logo image", type=["jpg", "jpeg", "png"])

    if uploaded_images:
        st.write("Images uploaded successfully!")
        for uploaded_image in uploaded_images:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    if uploaded_logo:
        st.write("Logo uploaded successfully!")
        st.image(uploaded_logo, caption="Uploaded Logo", use_column_width=True)

    if st.button("Merge and Download"):
        if uploaded_images and uploaded_logo:
            st.write("Starting image processing...")
            try:
                # Call your image processing functions here
                process_images(uploaded_images, uploaded_logo)
                st.write("Images processed and available for download!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please upload both images and a logo before merging.")

def process_images(images, logo):
    # Dummy function for image processing logic
    st.write("Processing images...")  # Add real processing logic here

if __name__ == "__main__":
    main()
