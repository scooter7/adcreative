import streamlit as st
import base64
from PIL import Image
from io import BytesIO

# Helper function to convert image to base64 for embedding in HTML
def convert_image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Helper function to create draggable and resizable HTML elements
def create_draggable_resizable_element(id, text, top, left, bg_color, text_color):
    return f"""
    <div id="{id}" style="position: absolute; top: {top}px; left: {left}px; cursor: move; background-color:{bg_color}; color:{text_color}; padding: 10px; resize: both; overflow: auto;">
        {text}
    </div>
    """

# Render HTML with draggable elements
def render_html(images):
    html_content = ""

    for image in images:
        html_content += f"""
        <div id="imageContainer" style="position: relative; width: {image['width']}px; height: {image['height']}px; background-image: url('data:image/png;base64,{image['image_base64']}'); background-size: contain; background-repeat: no-repeat;">
        """

        for i, (cta_text, desc_text) in enumerate(zip(image["cta_texts"], image["desc_texts"])):
            html_content += create_draggable_resizable_element(
                id=f"ctaText{i}",
                text=cta_text,
                top=50 + i * 100,
                left=50,
                bg_color=image['cta_bg_color'],
                text_color=image['cta_text_color']
            )
            html_content += create_draggable_resizable_element(
                id=f"descText{i}",
                text=desc_text,
                top=150 + i * 100,
                left=50,
                bg_color=image['desc_bg_color'],
                text_color=image['desc_text_color']
            )

        if image["logo_base64"]:
            html_content += f"""
            <div id="logoImage" style="position: absolute; top: 250px; left: 50px; cursor: move; resize: both; overflow: auto;">
                <img src="data:image/png;base64,{image['logo_base64']}" style="width: 100px; height: auto;">
            </div>
            """

        html_content += """
        </div>
        <button onclick="saveImage()">Save Image</button>
        <br><br>
        """

    # Adding JavaScript for drag-and-drop functionality and saving images
    html_content += """
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    <script>
        // Function to enable dragging and resizing of elements
        function dragElement(elmnt) {
            var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
            elmnt.onmousedown = function(e) {
                e = e || window.event;
                e.preventDefault();
                pos3 = e.clientX;
                pos4 = e.clientY;
                document.onmouseup = closeDragElement;
                document.onmousemove = function(e) {
                    e.preventDefault();
                    pos1 = pos3 - e.clientX;
                    pos2 = pos4 - e.clientY;
                    pos3 = e.clientX;
                    pos4 = e.clientY;
                    elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
                    elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
                };
            };

            function closeDragElement() {
                document.onmouseup = null;
                document.onmousemove = null;
            }
        }

        // Function to save the edited image
        function saveImage() {
            var imageContainer = document.getElementById("imageContainer");
            html2canvas(imageContainer).then(canvas => {
                var link = document.createElement('a');
                link.href = canvas.toDataURL();
                link.download = 'final_image.png';
                link.click();
            });
        }

        // Attach dragElement function to all created elements
        for (var i = 0; i < {len(images[0]["cta_texts"])}; i++) {
            dragElement(document.getElementById("ctaText" + i));
            dragElement(document.getElementById("descText" + i));
        }
        if (document.getElementById("logoImage")) {
            dragElement(document.getElementById("logoImage"));
        }
    </script>
    """

    return html_content

# Main function to handle the Streamlit app logic
def main():
    st.title("Image Text and Logo Overlay App")

    # Allow user to upload multiple images and a logo
    uploaded_images = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    uploaded_logo = st.file_uploader("Upload logo image", type=["jpg", "jpeg", "png"])

    # Display uploaded images
    if uploaded_images:
        st.write("Images uploaded successfully!")
        for uploaded_image in uploaded_images:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    # Display uploaded logo
    if uploaded_logo:
        st.write("Logo uploaded successfully!")
        st.image(uploaded_logo, caption="Uploaded Logo", use_column_width=True)

    # Input fields for Call to Action and Description texts
    num_pairs = st.number_input("Number of Call to Action + Description Pairs", min_value=1, step=1)
    call_to_action_texts = [st.text_input(f"Call to Action Text {i + 1}") for i in range(num_pairs)]
    description_texts = [st.text_input(f"Description Text {i + 1}") for i in range(num_pairs)]

    # Color pickers for text and background colors
    call_to_action_text_color = st.color_picker("Call to Action Text Color", "#FFFFFF")
    call_to_action_bg_color = st.color_picker("Call to Action Background Color", "#000000")
    description_text_color = st.color_picker("Description Text Color", "#FFFFFF")
    description_bg_color = st.color_picker("Description Background Color", "#000000")

    # Button to create and download images with overlays
    if uploaded_images and st.button("Create and Download"):
        images_with_html = []

        for image in uploaded_images:
            img = Image.open(image)
            img_width, img_height = img.size
            img_base64 = convert_image_to_base64(img)

            logo_base64 = None
            if uploaded_logo:
                logo = Image.open(uploaded_logo)
                logo_base64 = convert_image_to_base64(logo)

            images_with_html.append({
                "image_base64": img_base64,
                "logo_base64": logo_base64,
                "width": img_width,
                "height": img_height,
                "cta_texts": call_to_action_texts,
                "desc_texts": description_texts,
                "cta_text_color": call_to_action_text_color,
                "cta_bg_color": call_to_action_bg_color,
                "desc_text_color": description_text_color,
                "desc_bg_color": description_bg_color
            })

        # Render and display HTML with draggable elements
        st.components.v1.html(render_html(images_with_html), height=1000)

if __name__ == "__main__":
    main()
