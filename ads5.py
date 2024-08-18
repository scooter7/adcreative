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

                                        add_draggable_functionality(
                                            img_base64,
                                            call_to_action_text,
                                            description_text,
                                            logo_base64 if uploaded_logo else None,
                                            dimensions[0],
                                            dimensions[1],
                                            call_to_action_text_color,
                                            call_to_action_bg_color,
                                            description_text_color,
                                            description_bg_color
                                        )

def add_draggable_functionality(img_base64, call_to_action_text, description_text, logo_base64, img_width, img_height, cta_text_color, cta_bg_color, desc_text_color, desc_bg_color):
    st.components.v1.html(f"""
        <div id="imageContainer" style="position: relative; width: {img_width}px; height: {img_height}px; background-image: url('data:image/png;base64,{img_base64}'); background-size: contain; background-repeat: no-repeat; border: 1px solid #ccc;">
            <div id="ctaText" class="draggable resizable" style="position: absolute; top: 50px; left: 50px; background-color:{cta_bg_color}; color:{cta_text_color}; padding: 5px;">
                {call_to_action_text}
            </div>
            <div id="descText" class="draggable resizable" style="position: absolute; top: 150px; left: 50px; background-color:{desc_bg_color}; color:{desc_text_color}; padding: 5px;">
                {description_text}
            </div>
            <div id="logoImage" class="draggable resizable" style="position: absolute; top: 250px; left: 50px;">
                <img src="data:image/png;base64,{logo_base64}" style="width: auto; height: auto;">
            </div>
        </div>

        <button onclick="saveImage()" style="margin-top: 20px;">Save Image</button>

        <script src="https://cdn.jsdelivr.net/npm/interactjs@1.10.11/dist/interact.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/0.4.1/html2canvas.min.js"></script>
        <script>
            // Make elements draggable and resizable
            interact('.draggable')
                .draggable({{
                    inertia: true,
                    modifiers: [
                        interact.modifiers.restrictRect({{ restriction: 'parent', endOnly: true }})
                    ],
                    autoScroll: true,
                    onmove: dragMoveListener
                }})
                .resizable({{
                    edges: {{ left: true, right: true, bottom: true, top: true }},
                    inertia: true,
                    modifiers: [
                        interact.modifiers.restrictEdges({{ outer: 'parent' }}),
                        interact.modifiers.restrictSize({{ min: {{ width: 50, height: 20 }} }})
                    ],
                    onmove: resizeMoveListener
                }});

            function dragMoveListener(event) {{
                var target = event.target;
                // keep the dragged position in the data-x/data-y attributes
                var x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
                var y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

                // translate the element
                target.style.transform = 'translate(' + x + 'px, ' + y + 'px)';

                // update the position attributes
                target.setAttribute('data-x', x);
                target.setAttribute('data-y', y);
            }}

            function resizeMoveListener(event) {{
                var target = event.target,
                    x = (parseFloat(target.getAttribute('data-x')) || 0),
                    y = (parseFloat(target.getAttribute('data-y')) || 0);

                // update the element's style
                target.style.width = event.rect.width + 'px';
                target.style.height = event.rect.height + 'px';

                // translate when resizing from top or left edges
                x += event.deltaRect.left;
                y += event.deltaRect.top;

                target.style.transform = 'translate(' + x + 'px,' + y + 'px)';

                target.setAttribute('data-x', x);
                target.setAttribute('data-y', y);
            }}

            window.saveImage = function() {{
                html2canvas(document.getElementById('imageContainer')).then(function(canvas) {{
                    var dataURL = canvas.toDataURL('image/png');
                    var link = document.createElement('a');
                    link.href = dataURL;
                    link.download = 'final_image.png';
                    link.click();
                }});
            }};
        </script>
    """, height=img_height + 300)

if __name__ == "__main__":
    main()
