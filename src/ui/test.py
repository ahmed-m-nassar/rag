import streamlit as st
import numpy as np
import cv2
import base64
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from streamlit_javascript import st_javascript

# Title
st.title("📄 PDF Highlighter with JavaScript")

# Upload a PDF file
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    # Convert PDF to images
    pdf_path = "temp.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    images = convert_from_path(pdf_path)

    # Convert first page to OpenCV format
    img_pil = images[0]
    img_cv = np.array(img_pil)
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for OpenCV

    # Convert image to base64 for JavaScript
    img_pil.save("page.jpg", "JPEG")
    with open("page.jpg", "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()

    # JavaScript for drawing rectangles
    js_code = f"""
    <script>
    let img = new Image();
    img.src = 'data:image/jpeg;base64,{img_base64}';
    
    img.onload = function() {{
        let canvas = document.createElement('canvas');
        let ctx = canvas.getContext('2d');
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        document.body.appendChild(canvas);

        let rect = {{ x: 0, y: 0, w: 0, h: 0 }};
        let isDrawing = false;
        
        canvas.addEventListener('mousedown', function(e) {{
            rect.x = e.offsetX;
            rect.y = e.offsetY;
            isDrawing = true;
        }});

        canvas.addEventListener('mousemove', function(e) {{
            if (isDrawing) {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0);
                ctx.strokeStyle = 'red';
                ctx.strokeRect(rect.x, rect.y, e.offsetX - rect.x, e.offsetY - rect.y);
            }}
        }});

        canvas.addEventListener('mouseup', function(e) {{
            rect.w = e.offsetX - rect.x;
            rect.h = e.offsetY - rect.y;
            isDrawing = false;
            window.parent.postMessage(JSON.stringify(rect), '*');
        }});
    }};
    </script>
    """

    # Run JavaScript and get coordinates
    js_response = st_javascript(js_code)

    # Process selected region
    if js_response:
        try:
            coords = eval(js_response)  # Convert string to dict
            x1, y1, x2, y2 = coords["x"], coords["y"], coords["x"] + coords["w"], coords["y"] + coords["h"]

            # Draw rectangle on image
            img_copy = img_cv.copy()
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Convert back to PIL for Streamlit display
            img_pil_highlighted = Image.fromarray(cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB))
            st.image(img_pil_highlighted, caption="Highlighted PDF", use_column_width=True)

            # Extract text from selected area
            roi = img_cv[y1:y2, x1:x2]
            text = pytesseract.image_to_string(roi)
            
            st.write("🖍 **Extracted Text:**")
            st.text(text)
        except:
            st.error("⚠️ Error processing highlight coordinates.")

    # Cleanup
    import os
    os.remove("temp.pdf")
    os.remove("page.jpg")
