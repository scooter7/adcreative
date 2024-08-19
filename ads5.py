import os
import streamlit as st
import base64
from io import BytesIO
from PIL import Image

# Main function to handle the Streamlit app logic
def main():
    st.title("Image Text and Logo Overlay App")

    uploaded_images = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    uploaded_logo = st.file_uploader("Upload logo image", type=["jpg", "jpeg", "png"])

    logo_base64 = None
    if uploaded_logo:
        logo = Image.open(uploaded_logo)
        buffered_logo = BytesIO()
        logo.save(buffered_logo, format="PNG")
        logo_base64 = base64.b64encode(buffered_logo.getvalue()).decode()

    if uploaded_images:
        st.write("Images uploaded successfully!")
        for uploaded_image in uploaded_images:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    if uploaded_logo:
        st.write("Logo uploaded successfully!")
        st.image(uploaded_logo, caption="Uploaded Logo", use_column_width=True)

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
        "IP Targeting": {
            "300x250": (300, 250),
            "728x90": (728, 90),
        },
        "Mobile Footprinting": {
            "300x250": (300, 250),
            "728x90": (728, 90),
        },
        "Audience Select": {
            "300x250": (300, 250),
            "728x90": (728, 90),
        },
        "Spotify": {
            "640x640": (640, 640),
            "300x250": (300, 250),
        },
        "YouTube": {
            "1280x720": (1280, 720),
            "300x250": (300, 250),
        },
    }

    selected_image_sizes = []
    for channel, sizes in image_sizes.items():
        with st.expander(f"{channel}"):
            st.write(f"Select ad sizes for {channel}:")
            for label, dimensions in sizes.items():
                if st.checkbox(label, key=f"{channel}_{label}"):
                    selected_image_sizes.append((channel, label, dimensions))

    if st.button("Merge and Download"):
        if uploaded_images and selected_cta_positions and selected_desc_positions and selected_logo_positions:
            st.write("Processing images...")

            images_data = []
            for image in uploaded_images:
                for call_to_action_text, description_text in zip(call_to_action_texts, description_texts):
                    for cta_position in selected_cta_positions:
                        for desc_position in selected_desc_positions:
                            for logo_position in selected_logo_positions:
                                if cta_position != desc_position and cta_position != logo_position and desc_position != logo_position:
                                    for channel, label, dimensions in selected_image_sizes:
                                        img = Image.open(image)
                                        img_resized = img.resize(dimensions, Image.ANTIALIAS)
                                        buffered = BytesIO()
                                        img_resized.save(buffered, format="PNG")
                                        img_base64 = base64.b64encode(buffered.getvalue()).decode()

                                        images_data.append({
                                            'img_base64': img_base64,
                                            'call_to_action_text': call_to_action_text,
                                            'description_text': description_text,
                                            'logo_base64': logo_base64 if uploaded_logo else None,
                                            'cta_bg_color': call_to_action_bg_color,
                                            'cta_text_color': call_to_action_text_color,
                                            'desc_bg_color': description_bg_color,
                                            'desc_text_color': description_text_color
                                        })

            add_draggable_functionality(images_data, dimensions[0], dimensions[1])

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

                    // Ensure consistent padding around the text
                    target.style.padding = '2px';

                    // Adjust font size based on container size
                    let newFontSize = Math.min(event.rect.width, event.rect.height) / 5;
                    target.style.fontSize = newFontSize + 'px';

                    // Handle resizing for logos
                    if (target.id.includes('logoImage')) {
                        let img = target.querySelector('img');
                        img.style.width = '100%';
                        img.style.height = '100%';
                    }
                }

            function saveImage() {
                console.log("Merge and Download button clicked");
                var images = document.querySelectorAll("[id^='imageContainer_']");
                images.forEach(function(imageContainer, index) {
                    html2canvas(imageContainer).then(function(canvas) {
                        console.log("Canvas generated for image " + index + ", preparing download...");
                        var dataURL = canvas.toDataURL('image/png');
                        var link = document.createElement('a');
                        link.href = dataURL;
                        link.download = 'final_image_' + index + '.png';
                        console.log("Triggering download for image " + index + "...");
                        link.click();
                        console.log("Download triggered for image " + index + ".");
                    }).catch(function(error) {
                        console.error("Error capturing the image " + index + ": ", error);
                    });
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

    js_part += """
        </script>
    """

    # Combine HTML and JS into the final component
    st.components.v1.html(html_content + js_part, height=img_height * len(images_data) + 300)

if __name__ == "__main__":
    main()
