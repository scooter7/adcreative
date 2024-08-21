import os
import streamlit as st
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Main function to handle the Streamlit app logic
def main():
    st.title("Image Text and Logo Overlay App")

    uploaded_images = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    uploaded_logo = st.file_uploader("Upload logo image", type=["jpg", "jpeg", "png"])

    logo_base64 = None
    logo_image = None
    if uploaded_logo:
        logo = Image.open(uploaded_logo)
        logo = logo.convert("RGBA")  # Ensure logo is in RGBA format
        buffered_logo = BytesIO()
        logo.save(buffered_logo, format="PNG")
        logo_base64 = base64.b64encode(buffered_logo.getvalue()).decode()
        logo_image = logo

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

    # Radio button to mix CTAs and Descriptions
    mix_cta_desc = st.radio("Mix CTAs and Descriptions", ("No", "Yes"))

    call_to_action_text_color = st.color_picker("Call to Action Text Color", "#FFFFFF")
    call_to_action_bg_color = st.color_picker("Call to Action Background Color", "#000000")
    description_text_color = st.color_picker("Description Text Color", "#FFFFFF")
    description_bg_color = st.color_picker("Description Background Color", "#000000")

    # Option to choose the shape of the text containers
    text_shape = st.selectbox("Select Text Container Shape", ["Rectangle", "Pill-shaped"])

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
        if uploaded_images:
            st.write("Processing images...")

            images_data = []

            if mix_cta_desc == "Yes":
                # Produce all combinations of CTA and Description
                for call_to_action_text in call_to_action_texts:
                    for description_text in description_texts:
                        for image in uploaded_images:
                            for channel, label, dimensions in selected_image_sizes:
                                img = Image.open(image)
                                img_resized = img.resize(dimensions, Image.LANCZOS)
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
                                    'desc_text_color': description_text_color,
                                    'text_shape': text_shape,
                                    'image': img_resized
                                })
            else:
                # Produce images without mixing CTAs and Descriptions
                for call_to_action_text, description_text in zip(call_to_action_texts, description_texts):
                    for image in uploaded_images:
                        for channel, label, dimensions in selected_image_sizes:
                            img = Image.open(image)
                            img_resized = img.resize(dimensions, Image.LANCZOS)
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
                                'desc_text_color': description_text_color,
                                'text_shape': text_shape,
                                'image': img_resized
                            })

            add_draggable_functionality(images_data, dimensions[0], dimensions[1])

            # Trigger the download after rendering and manipulation
            save_and_download_images(images_data, logo_image)

def add_draggable_functionality(images_data, img_width, img_height):
    html_parts = []

    # Iterate over each image and its associated data
    for index, data in enumerate(images_data):
        cta_id = f"ctaText_{index}"
        desc_id = f"descText_{index}"
        logo_id = f"logoImage_{index}"

        # Determine border-radius based on selected shape
        if data['text_shape'] == "Pill-shaped":
            border_radius = "50px"  # Making the container pill-shaped
        else:
            border_radius = "0px"  # Rectangle

        # Generate HTML for each image
        html_part = f"""
            <div id="imageContainer_{index}" style="position: relative; width: {img_width}px; height: {img_height}px; background-image: url('data:image/png;base64,{data['img_base64']}'); background-size: contain; background-repeat: no-repeat;">
                <div id="{cta_id}" class="draggable resizable" style="position: absolute; top: 50px; left: 50px; background-color:{data['cta_bg_color']}; color:{data['cta_text_color']}; padding: 10px; font-size: 16px; display: inline-block; border-radius: {border_radius}; border: 2px solid {data['cta_bg_color']};">
                    {data['call_to_action_text']}
                </div>
                <div id="{desc_id}" class="draggable resizable" style="position: absolute; top: 150px; left: 50px; background-color:{data['desc_bg_color']}; color:{data['desc_text_color']}; padding: 10px; font-size: 16px; display: inline-block; border-radius: {border_radius}; border: 2px solid {data['desc_bg_color']};">
                    {data['description_text']}
                </div>
                <div id="{logo_id}" class="draggable resizable logo-grabbable" style="position: absolute; top: 250px; left: 50px; padding: 20px; cursor: move; display: inline-block; opacity: 1;">
                    <img src="data:image/png;base64,{data['logo_base64']}" style="width: 100%; height: auto; pointer-events: none;">
                </div>
            </div>
            <div style="margin-top: 10px;">
                <label>CTA Transparency: <input type="range" min="0" max="100" value="100" class="slider" id="ctaSlider_{index}" oninput="adjustOpacity('{cta_id}', this.value)"></label>
                <label>Description Transparency: <input type="range" min="0" max="100" value="100" class="slider" id="descSlider_{index}" oninput="adjustOpacity('{desc_id}', this.value)"></label>
                <label>Logo Transparency: <input type="range" min="0" max="100" value="100" class="slider" id="logoSlider_{index}" oninput="adjustOpacity('{logo_id}', this.value)"></label>
            </div>
        """
        html_parts.append(html_part)

    # Combine all HTML parts into a single string
    html_content = "\n".join(html_parts)

    # Generate JavaScript for each image
    js_part = """
        <script src="https://cdn.jsdelivr.net/npm/interactjs@1.10.11/dist/interact.min.js"></script>
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

            function adjustOpacity(elementId, value) {
                document.getElementById(elementId).style.opacity = value / 100;
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
                target.style.padding = '10px';

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

            // Apply interactions to each element with unique IDs
    """
    for index in range(len(images_data)):
        js_part += f"""
            applyInteractions('ctaText_{index}');
            applyInteractions('descText_{index}');
            applyInteractions('logoImage_{index}');
            adjustOpacity('ctaText_{index}', 100);
            adjustOpacity('descText_{index}', 100);
            adjustOpacity('logoImage_{index}', 100);
        """

    js_part += """
        </script>
    """

    # Combine HTML and JS into the final component
    st.components.v1.html(html_content + js_part, height=img_height * len(images_data) + 300)

def save_and_download_images(images_data, logo_image):
    for index, data in enumerate(images_data):
        img = data['image']
        draw = ImageDraw.Draw(img)

        # Font settings
        font_path = "arial.ttf"  # Update with the path to a valid .ttf font file if necessary
        font_size = 20
        font = ImageFont.truetype(font_path, font_size) if os.path.exists(font_path) else ImageFont.load_default()

        # Calculate text size and position
        cta_text_bbox = draw.textbbox((0, 0), data['call_to_action_text'], font=font)
        desc_text_bbox = draw.textbbox((0, 0), data['description_text'], font=font)

        cta_text_size = (cta_text_bbox[2] - cta_text_bbox[0], cta_text_bbox[3] - cta_text_bbox[1])
        desc_text_size = (desc_text_bbox[2] - desc_text_bbox[0], desc_text_bbox[3] - desc_text_bbox[1])

        cta_position = (50, 50)
        desc_position = (50, 150)

        # Draw the CTA and Description texts with background
        draw.rectangle(
            [cta_position, (cta_position[0] + cta_text_size[0] + 20, cta_position[1] + cta_text_size[1] + 10)],
            fill=data['cta_bg_color'],
            outline=data['cta_bg_color'],
        )
        draw.text((cta_position[0] + 10, cta_position[1] + 5), data['call_to_action_text'], fill=data['cta_text_color'], font=font)

        draw.rectangle(
            [desc_position, (desc_position[0] + desc_text_size[0] + 20, desc_position[1] + desc_text_size[1] + 10)],
            fill=data['desc_bg_color'],
            outline=data['desc_bg_color'],
        )
        draw.text((desc_position[0] + 10, desc_position[1] + 5), data['description_text'], fill=data['desc_text_color'], font=font)

        # Place the logo on the image
        if logo_image:
            logo_position = (50, 250)
            logo_resized = logo_image.resize((100, 100), Image.LANCZOS)
            img.paste(logo_resized, logo_position, logo_resized)

        # Save the image to a BytesIO object
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Display download link
        st.markdown(
            f'<a href="data:image/png;base64,{img_str}" download="final_image_{index}.png">Download final_image_{index}.png</a>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
