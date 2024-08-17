import streamlit as st
import base64
from PIL import Image
from io import BytesIO

def get_image_as_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def main():
    st.title("Interactive Image with Draggable Elements")

    # Input fields for CTA and Description text
    cta_text = st.text_input("Enter Call to Action Text", value="Call to Action")
    desc_text = st.text_input("Enter Description Text", value="Description Text")

    # Upload main image
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if uploaded_image:
        img = Image.open(uploaded_image)
        img_width, img_height = img.size
        img_base64 = get_image_as_base64(img)

        # Upload logo image
        uploaded_logo = st.file_uploader("Upload a logo image", type=["jpg", "jpeg", "png"])

        if uploaded_logo:
            logo = Image.open(uploaded_logo)
            logo_base64 = get_image_as_base64(logo)
        else:
            logo_base64 = ""

        # Initial positions for the elements
        initial_cta_position = {"top": 50, "left": 50}
        initial_desc_position = {"top": 150, "left": 50}
        initial_logo_position = {"top": 250, "left": 50}

        # Display the image and draggable elements
        st.components.v1.html(f"""
            <div style="position: relative; display: inline-block; background-image: url('data:image/png;base64,{img_base64}'); background-size: contain; background-repeat: no-repeat; width: {img_width}px; height: {img_height}px;">
                <div id="ctaText" style="position: absolute; top: {initial_cta_position['top']}px; left: {initial_cta_position['left']}px; cursor: move; font-size: 24px; color: white;">
                    {cta_text}
                </div>
                <div id="descText" style="position: absolute; top: {initial_desc_position['top']}px; left: {initial_desc_position['left']}px; cursor: move; font-size: 18px; color: yellow;">
                    {desc_text}
                </div>
                <div id="logoImage" style="position: absolute; top: {initial_logo_position['top']}px; left: {initial_logo_position['left']}px; cursor: move;">
                    <img src="data:image/png;base64,{logo_base64}" style="width: 100px; height: auto;">
                </div>
                <!-- Hidden inputs to store the positions -->
                <input type="hidden" id="ctaPos" name="ctaPos">
                <input type="hidden" id="descPos" name="descPos">
                <input type="hidden" id="logoPos" name="logoPos">
            </div>

            <script>
                function dragElement(elmnt, posInputId) {{
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
                        document.getElementById(posInputId).value = elmnt.style.top + "," + elmnt.style.left;
                    }}
                }}

                // Enable dragging and updating of hidden input fields
                dragElement(document.getElementById("ctaText"), "ctaPos");
                dragElement(document.getElementById("descText"), "descPos");
                dragElement(document.getElementById("logoImage"), "logoPos");
            </script>
        """, height=img_height + 50)  # Add some height to accommodate dragging

        # Capture the positions from the hidden input fields
        cta_pos = st.text_input("CTA Position", value="", key="ctaPos")
        desc_pos = st.text_input("Description Position", value="", key="descPos")
        logo_pos = st.text_input("Logo Position", value="", key="logoPos")

        if st.button("Save Positions"):
            st.write("Call to Action Position:", cta_pos)
            st.write("Description Position:", desc_pos)
            st.write("Logo Position:", logo_pos)
            # You can now use these positions to adjust the elements in the final image

if __name__ == "__main__":
    main()
