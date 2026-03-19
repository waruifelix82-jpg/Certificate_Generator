from flask import Flask, render_template, request, send_file
import os
import io 
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route("/")
def home():
    return render_template("index.html") 

@app.route("/generate", methods=["POST"])
def generate():
    name = request.form.get("student_name")

    if not name:
        return "Error: Name is required!", 400
    
    try:
        # 1. Load your template
        img = Image.open("certificate.jpg").convert("RGB")
        W, H = img.size
        draw = ImageDraw.Draw(img)
        
        # 2. INCREASED FONT SIZING
        # Changed from 0.06 to 0.15 for much better visibility
        name_size = int(W * 0.15) 

        try:
            # Note: Ensure arial.ttf is in your project folder on Vercel
            font_name = ImageFont.truetype("arial.ttf", name_size)
        except:
            # If font file is missing, this default is often very small
            font_name = ImageFont.load_default()

        # 3. ADJUSTED COORDINATES
        center_x = W // 2
        # Moved from 0.39 to 0.42 to sit closer to the presentation line
        name_y = int(H * 0.21) 
           
        # 4. DRAW NAME
        # Using a slightly darker Navy Blue (0, 32, 96) for professional look
        draw.text((center_x, name_y), name.upper(), fill=(0, 32, 96), font=font_name, anchor="mm")

        # 5. Send to Browser
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=100) # Max quality for deployment
        img_io.seek(0)
        
        return send_file(
            img_io, 
            mimetype='image/jpeg', 
            as_attachment=True, 
            download_name=f"{name.replace(' ', '_')}_Certificate.jpg"
        )

    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)