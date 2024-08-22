import streamlit as st
import base64
from io import BytesIO
from PIL import Image

def main():
    st.title("Test Image Text and Logo Overlay")

    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    uploaded_logo = st.file_uploader("Upload a logo image", type=["jpg", "jpeg", "png"])

    logo_base64 = None
    if uploaded_logo:
        logo = Image.open(uploaded_logo)
        buffered_logo = BytesIO()
        logo.save(buffered_logo, format="PNG")
        logo_base64 = base64.b64encode(buffered_logo.getvalue()).decode()

    if uploaded_image:
        img = Image.open(uploaded_image)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        html_content = f"""
        <div id="imageContainer" style="position: relative; width: 500px; height: 500px; background-image: url('data:image/png;base64,{img_base64}'); background-size: contain; background-repeat: no-repeat;">
            <div id="ctaText" class="draggable resizable" style="position: absolute; top: 50px; left: 50px; background-color: #000; color: #fff; padding: 10px; font-size: 16px;">
                Call to Action
            </div>
            <div id="logoImage" class="draggable resizable" style="position: absolute; top: 150px; left: 50px; padding: 10px;">
                <img src="data:image/png;base64,{logo_base64}" style="width: 100px; height: 100px;">
            </div>
        </div>
        """

        js_script = """
        <script src="https://cdn.jsdelivr.net/npm/interactjs@1.10.11/dist/interact.min.js"></script>
        <script>
            interact('.draggable')
                .draggable({
                    inertia: true,
                    modifiers: [
                        interact.modifiers.restrictRect({
                            restriction: 'parent',
                            endOnly: true
                        })
                    ],
                    autoScroll: true,
                    onmove: dragMoveListener
                })
                .resizable({
                    edges: { left: true, right: true, bottom: true, top: true },
                    modifiers: [
                        interact.modifiers.restrictEdges({
                            outer: 'parent'
                        }),
                        interact.modifiers.restrictSize({
                            min: { width: 50, height: 20 }
                        })
                    ],
                    inertia: true,
                    onmove: resizeMoveListener
                });

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

                target.style.width = event.rect.width + 'px';
                target.style.height = event.rect.height + 'px';

                x += event.deltaRect.left;
                y += event.deltaRect.top;

                target.style.transform = 'translate(' + x + 'px,' + y + 'px)';

                target.setAttribute('data-x', x);
                target.setAttribute('data-y', y);

                // Ensure the image inside the logo container resizes correctly
                if (target.id === 'logoImage') {
                    let img = target.querySelector('img');
                    img.style.width = '100%';
                    img.style.height = 'auto';
                }
            }
        </script>
        """

        # Combine HTML and JS
        st.components.v1.html(html_content + js_script, height=600)

if __name__ == "__main__":
    main()
