import streamlit as st
from PIL import Image, ImageDraw
import base64
from io import BytesIO

# Utility function to convert PIL Image to base64 string
def pil_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Function to add draggable functionality to images
def add_draggable_functionality(images_data, img_width, img_height):
    html_parts = []

    # Iterate over each image and its associated data
    for index, data in enumerate(images_data):
        cta_id = f"ctaText_{index}"
        desc_id = f"descText_{index}"
        logo_id = f"logoImage_{index}"

        # Generate HTML for each image
        html_part = f"""
            <div id="imageContainer_{index}" style="position: relative; width: {img_width}px; height: {img_height}px; background-image: url('data:image/png;base64,{data['img_base64']}'); background-size: contain; background-repeat: no-repeat;">
                <div id="{cta_id}" class="draggable resizable" style="position: absolute; top: 50px; left: 50px; background-color:{data['cta_bg_color']}; color:{data['cta_text_color']}; padding: 5px; font-size: 16px; display: inline-block;">
                    {data['call_to_action_text']}
                </div>
                <div id="{desc_id}" class="draggable resizable" style="position: absolute; top: 150px; left: 50px; background-color:{data['desc_bg_color']}; color:{data['desc_text_color']}; padding: 5px; font-size: 16px; display: inline-block;">
                    {data['description_text']}
                </div>
                <div id="{logo_id}" class="draggable resizable" style="position: absolute; top: 250px; left: 50px; padding: 5px; display: inline-block;">
                    <img src="data:image/png;base64,{data['logo_base64']}" style="width: 100%; height: auto;">
                </div>
            </div>
        """
        html_parts.append(html_part)

    # Combine all HTML parts into a single string
    html_content = "\n".join(html_parts)

    # Generate JavaScript for each image
    js_part = """
        <script src="https://cdn.jsdelivr.net/npm/interactjs@1.10.11/dist/interact.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/0.4.1/html2canvas.min.js"></script>
        <script>
            function applyInteractions(elementId) {
                interact('#' + elementId).draggable({
                    inertia: true,
                    modifiers: [
                        interact.modifiers.restrictRect({
                            restriction: 'parent',
                            endOnly: true
                        })
                    ],
                    autoScroll: true,
                    onmove: dragMoveListener
                }).resizable({
                    edges: { left: true, right: true, bottom: true, top: true },
                    inertia: true,
                    modifiers: [
                        interact.modifiers.restrictEdges({
                            outer: 'parent'
                        }),
                        interact.modifiers.restrictSize({
                            min: { width: 50, height: 20 }
                        })
                    ],
                    onmove: resizeMoveListener
                });
            }

            function dragMoveListener(event) {
                var target = event.target,
                    x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx,
                    y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

                target.style.transform = 'translate(' + x + 'px, ' + y + 'px)';

                target.setAttribute('data-x', x);
                target.setAttribute('data-y', y);
            }

            function resizeMoveListener(event) {
                var target = event.target,
                    x = (parseFloat(target.getAttribute('data-x')) || 0),
                    y = (parseFloat(target.getAttribute('data-y')) || 0);

                // Ensure the background fits tightly around the text with padding
                target.style.width = 'auto';
                target.style.height = 'auto';
                target.style.whiteSpace = 'nowrap';

                // Calculate and set the new font size based on the container size
                let newFontSize = Math.min(event.rect.width, event.rect.height) / 5;
                target.style.fontSize = newFontSize + 'px';

                // Keep the padding consistent around the text and logo
                target.style.padding = '5px';

                x += event.deltaRect.left;
                y += event.deltaRect.top;

                target.style.transform = 'translate(' + x + 'px,' + y + 'px)';

                target.setAttribute('data-x', x);
                target.setAttribute('data-y', y);

                // Adjust the logo resizing
                if (target.id.includes('logoImage')) {
                    let img = target.querySelector('img');
                    img.style.width = event.rect.width + 'px';
                    img.style.height = event.rect.height + 'px';
                }
            }

            function saveImage() {
                html2canvas(document.getElementById('container')).then(function(canvas) {
                    var dataURL = canvas.toDataURL('image/png');
                    var link = document.createElement('a');
                    link.href = dataURL;
                    link.download = 'final_image.png';
                    link.click();
                });
            }

            // Apply interactions to each element with unique IDs
    """
    for index in range(len(images_data)):
        js_part += f"""
            applyInteractions('ctaText_{index}');
            applyInteractions('descText_{index}');
            applyInteractions('logoImage_{index}');
        """

    js_part += "</script>"

    # Combine HTML and JS into the final component
    st.components.v1.html(html_content + js_part, height=img_height * len(images_data) + 300)

# Main Streamlit application
def main():
    st.title("Interactive Image Overlay App")

    uploaded_images = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], accept_multiple_files=False)
    uploaded_logo = st.file_uploader("Upload Logo", type=["jpg", "jpeg", "png"], accept_multiple_files=False)

    if uploaded_images and uploaded_logo:
        img = Image.open(uploaded_images)
        logo = Image.open(uploaded_logo)
        
        # Resize logo for preview
        logo_resized = logo.resize((100, 100))

        # Convert images to base64 for embedding in HTML
        img_base64 = pil_to_base64(img)
        logo_base64 = pil_to_base64(logo_resized)

        images_data = [{
            'img_base64': img_base64,
            'call_to_action_text': "Call to Action",
            'description_text': "Description Text",
            'logo_base64': logo_base64,
            'cta_bg_color': "#00000080",
            'cta_text_color': "#FFFFFF",
            'desc_bg_color': "#00000080",
            'desc_text_color': "#FFFFFF"
        }]

        add_draggable_functionality(images_data, img.width, img.height)

if __name__ == "__main__":
    main()
