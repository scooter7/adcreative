import os
import streamlit as st
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Main function to handle the Streamlit app logic
def main():
    st.title("Image Text and Logo Overlay App")

    uploaded_images = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    uploaded_logo = st.file_uploader("Upload logo image", type=["jpg", "jpeg", "png"])

    logo_image = None
    if uploaded_logo:
        logo_image = Image.open(uploaded_logo).convert("RGBA")

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

    if st.button("Merge and Download Images"):
        if uploaded_images:
            st.write("Processing images...")

            images = []

            if mix_cta_desc == "Yes":
                # Produce all combinations of CTA and Description
                for call_to_action_text in call_to_action_texts:
                    for description_text in description_texts:
                        for uploaded_image in uploaded_images:
                            for channel, label, dimensions in selected_image_sizes:
                                img = Image.open(uploaded_image).resize(dimensions).convert("RGBA")
                                combined_img = overlay_texts_and_logo(img, call_to_action_text, description_text, call_to_action_text_color, call_to_action_bg_color, description_text_color, description_bg_color, logo_image, text_shape)
                                images.append(combined_img)
            else:
                # Produce images without mixing CTAs and Descriptions
                for call_to_action_text, description_text in zip(call_to_action_texts, description_texts):
                    for uploaded_image in uploaded_images:
                        for channel, label, dimensions in selected_image_sizes:
                            img = Image.open(uploaded_image).resize(dimensions).convert("RGBA")
                            combined_img = overlay_texts_and_logo(img, call_to_action_text, description_text, call_to_action_text_color, call_to_action_bg_color, description_text_color, description_bg_color, logo_image, text_shape)
                            images.append(combined_img)

            # Save images and offer download
            for i, img in enumerate(images):
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_bytes = buffered.getvalue()
                st.download_button(label=f"Download Image {i + 1}", data=img_bytes, file_name=f"image_{i + 1}.png", mime="image/png")

def overlay_texts_and_logo(img, cta_text, desc_text, cta_text_color, cta_bg_color, desc_text_color, desc_bg_color, logo_image, text_shape):
    draw = ImageDraw.Draw(img, "RGBA")

    # Placeholder for font selection
    font = ImageFont.load_default()

    # Draw Call to Action text
    cta_bbox = draw.textbbox((0, 0), cta_text, font=font)
    cta_text_width = cta_bbox[2] - cta_bbox[0]
    cta_text_height = cta_bbox[3] - cta_bbox[1]

    # Apply text background shape
    if text_shape == "Pill-shaped":
        cta_bg = Image.new("RGBA", (cta_text_width + 20, cta_text_height + 20), cta_bg_color)
        draw.rounded_rectangle((50, 50, 50 + cta_text_width + 20, 50 + cta_text_height + 20), fill=cta_bg_color, radius=25)
    else:
        draw.rectangle((50, 50, 50 + cta_text_width + 20, 50 + cta_text_height + 20), fill=cta_bg_color)

    # Draw Call to Action text on top of background
    draw.text((60, 60), cta_text, fill=cta_text_color, font=font)

    # Draw Description text
    desc_bbox = draw.textbbox((0, 0), desc_text, font=font)
    desc_text_width = desc_bbox[2] - desc_bbox[0]
    desc_text_height = desc_bbox[3] - desc_bbox[1]

    if text_shape == "Pill-shaped":
        desc_bg = Image.new("RGBA", (desc_text_width + 20, desc_text_height + 20), desc_bg_color)
        draw.rounded_rectangle((50, 150, 50 + desc_text_width + 20, 150 + desc_text_height + 20), fill=desc_bg_color, radius=25)
    else:
        draw.rectangle((50, 150, 50 + desc_text_width + 20, 150 + desc_text_height + 20), fill=desc_bg_color)

    # Draw Description text on top of background
    draw.text((60, 160), desc_text, fill=desc_text_color, font=font)

    # Overlay logo if uploaded
    if logo_image:
        logo_width, logo_height = logo_image.size
        img.paste(logo_image, (50, 250), logo_image)

    return img

if __name__ == "__main__":
    main()
