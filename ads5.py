import os
from PIL import Image
import streamlit as st
import base64
from io import BytesIO

DEFAULT_FONT_PATH = "arial.ttf"

# Function to get the base64 string of an image
def get_base64_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Function to overlay logo on the image
def overlay_logo(image, uploaded_logo, logo_position, img_width, img_height, logo_width_percentage, logo_height_percentage):
    img = image.convert("RGBA")
    logo = Image.open(uploaded_logo).convert("RGBA")

    logo_width = int(img_width * logo_width_percentage)
    logo_height = int(img_height * logo_height_percentage)

    logo = logo.resize((logo_width, logo_height), Image.ANTIALIAS)

    x, y = get_position_coordinates(logo_position, img_width, img_height, logo_width, logo_height)

    img.paste(logo, (x, y), logo)

    return img.convert("RGB")

# Function to get the coordinates for positioning elements
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

# Function to generate the HTML content with draggable and resizable elements
def generate_html(img_base64, call_to_action_text, description_text, logo_base64, img_width, img_height):
    logo_html = f"""
        <div id="logoImage" style="position: absolute; top: 250px; left: 50px; cursor: move; resize: both; overflow: auto;">
            <img src="data:image/png;base64,{logo_base64}" style="width: 100px; height: auto;">
        </div>
    """ if logo_base64 else ""

    html_content = f"""
        <div id="imageContainer" style="position: relative; width: {img_width}px; height: {img_height}px; background-image: url('data:image/png;base64,{img_base64}'); background-size: contain; background-repeat: no-repeat;">
            <div id="ctaText" contenteditable="true" style="position: absolute; top: 50px; left: 50px; cursor: move; padding: 5px; resize: both; overflow: auto; background-color: rgba(0,0,0,0.5); color: white; font-size: 20px;">
                {call_to_action_text}
            </div>
            <div id="descText" contenteditable="true" style="position: absolute; top: 150px; left: 50px; cursor: move; padding: 5px; resize: both; overflow: auto; background-color: rgba(0,0,0,0.5); color: white; font-size: 16px;">
                {description_text}
            </div>
            {logo_html}
        </div>

        <button onclick="saveImage()">Save Image</button>

        <script>
            function dragElement(elmnt) {{
                var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
                elmnt.onmousedown = function(e) {{
                    e = e || window.event;
                    e.preventDefault();
                    pos3 = e.clientX;
                    pos4 = e.clientY;
                    document.onmouseup = closeDragElement;
                    document.onmousemove = function(e) {{
                        e.preventDefault();
                        pos1 = pos3 - e.clientX;
                        pos2 = pos4 - e.clientY;
                        pos3 = e.clientX;
                        pos4 = e.clientY;
                        elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
                        elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
                    }};
                }};

                function closeDragElement() {{
                    document.onmouseup = null;
                    document.onmousemove = null;
                }}
            }}

            function saveImage() {{
                var container = document.getElementById("imageContainer");
                html2canvas(container).then(function(canvas) {{
                    var link = document.createElement("a");
                    link.href = canvas.toDataURL("image/png");
                    link.download = "final_image.png";
                    link.click();
                }});
            }}

            dragElement(document.getElementById("ctaText"));
            dragElement(document.getElementById("descText"));
            { "dragElement(document.getElementById('logoImage'));" if logo_base64 else "" }
        </script>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/0.4.1/html2canvas.min.js"></script>
    """
    return html_content

def main():
    st.title("Interactive Image Editor with Draggable and Resizable Overlays")

    # Image Upload
    uploaded_images = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    if uploaded_images:
        for uploaded_image in uploaded_images:
            image = Image.open(uploaded_image)
            img_width, img_height = image.size
            img_base64 = get_base64_image(image)

            # Text Inputs
            call_to_action_text = st.text_input("Enter Call to Action Text", "Sample CTA")
            description_text = st.text_input("Enter Description Text", "Sample Description")

            # Logo Upload
            uploaded_logo = st.file_uploader("Upload a logo", type=["png", "jpg", "jpeg"])
            logo_base64 = None
            if uploaded_logo:
                logo_image = Image.open(uploaded_logo)
                logo_base64 = get_base64_image(logo_image)

            # Generate and display the interactive HTML
            html_content = generate_html(img_base64, call_to_action_text, description_text, logo_base64, img_width, img_height)
            st.components.v1.html(html_content, height=img_height + 150)

if __name__ == "__main__":
    main()
