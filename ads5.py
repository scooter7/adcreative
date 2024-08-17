import streamlit as st
from PIL import Image

defmain():
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

    num_pairs = st.number_input("Number of Call to Action + Description Pairs", min_value=1, step=1)
    call_to_action_texts = [st.text_input(f"Call to Action Text {i + 1}") for i inrange(num_pairs)]
    description_texts = [st.text_input(f"Description Text {i + 1}") for i inrange(num_pairs)]
    
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

    # Accordion style for ad sizes
    image_sizes = {
        "IP Targeting, Mobile Footprinting, + Audience Select": {
            "Wide Skyscraper (160×600)": (160, 600),
            "Medium Rectangle (300×250)": (300, 250),
            "Mobile Leaderboard (300×50)": (300, 50),
            "Mobile Leaderboard (320×50)": (320, 50),
            "Leaderboard (728×90)": (728, 90)
        },
        "Retargeting or Outreach": {
            "Wide Skyscraper (160×600)": (160, 600),
            "Super Wide Skyscraper (300×600)": (300, 600),
            "Medium Rectangle (300×250)": (300, 250),
            "Mobile Leaderboard (320×50)": (320, 50),
            "Tall Mobile Leaderboard (320×100)": (320, 100),
            "Large Rectangle (336×280)": (336, 280),
            "Leaderboard (728×90)": (728, 90)
        },
        "Google My Business (GMB)": {
            "Image (400×300)": (400, 300)
        },
        "LinkedIn Carousel Ads": {
            "Carousel Ads (1080×1080)": (1080, 1080)
        },
        "LinkedIn Conversation Ads / Sponsored Message Companion Banner": {
            "Conversation Ad / Sponsored Message Companion Banner (300×250)": (300, 250)
        },
        "LinkedIn Dynamic Ads": {
            "Dynamic Ads (100×100)": (100, 100)
        },
        "LinkedIn Sponsored Ads": {
            "Sponsored Ads (1200×627)": (1200, 627),
            "Sponsored Ads (1200×1200)": (1200, 1200),
            "Sponsored Ads (1080×1080)": (1080, 1080)
        },
        "Meta": {
            "Sponsored Ads (1200×628)": (1200, 628),
            "Sponsored Ads (1080×1080)": (1080, 1080),
            "Carousel Ads (1080×1080)": (1080, 1080),
            "Meta Stories + Reels (1080×1920)": (1080, 1920)
        },
        "Mobile Location Targeting": {
            "Medium Rectangle (300×250)": (300, 250),
            "Mobile Leaderboard (320×50)": (320, 50),
            "Mobile Interstitial (320×480)": (320, 480),
            "Leaderboard (728×90)": (728, 90)
        },
        "OTT/Connected TV": {
            "Connect TV/ OTT (300×250)": (300, 250),
            "Connect TV/ OTT (300×600)": (300, 600),
            "Connect TV/ OTT (728×90)": (728, 90)
        },
        "Outbrain": {
            "Outbrain (1200×800)": (1200, 800)
        },
        "Pandora": {
            "Pandora (300×250)": (300, 250),
            "Pandora (500×500)": (500, 500)
        },
        "Pre-roll": {
            "Companion (300×250)": (300, 250)
        },
        "Spotify": {
            "Spotify (640×640 Companion Image)": (640, 640)
        },
        "YouTube": {
            "Companion (300×60)": (300, 60)
        }
    }

    selected_image_sizes = []
    for channel, sizes in image_sizes.items():
        with st.expander(channel):
            for label, size in sizes.items():
                if st.checkbox(label):
                    selected_image_sizes.append(size)

    if st.button("Merge and Download"):
        if uploaded_images and selected_cta_positions and selected_desc_positions and selected_logo_positions:
            st.write("Processing images...")
            images_with_text = []
            for image in uploaded_images:
                img = Image.open(image)
                for cta_position in selected_cta_positions:
                    for desc_position in selected_desc_positions:
                        for logo_position in selected_logo_positions:
                            if cta_position != desc_position and cta_position != logo_position and desc_position != logo_position:
                                for call_to_action_text, description_text inzip(call_to_action_texts, description_texts):
                                    merged_img = merge_text_with_image(
                                        img,
                                        call_to_action_text,
                                        description_text,
                                        [width_percentage_cta, width_percentage_desc],
                                        [height_percentage_cta, height_percentage_desc],
                                        [call_to_action_text_color, description_text_color],
                                        [call_to_action_bg_color, description_bg_color],
                                        cta_position,
                                        desc_position,
                                        logo_position,
                                        logo_width_percentage,
                                        logo_height_percentage,
                                        uploaded_logo
                                    )
                                    images_with_text.append(merged_img)
            download_images(images_with_text, selected_image_sizes, image_sizes)
            st.write("Images processed and available for download!")

if __name__ == "__main__":
    main()
