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
    position = request.form.get("position")

    if not name or not position:
        return "Error: Missing name or position!", 400
    
    try:
        # 1. Load your template
        img = Image.open("certificate.jpg").convert("RGB")
        W, H = img.size
        draw = ImageDraw.Draw(img)
        
        # --- 2. DYNAMIC FONT LOADING ---
        # Instead of '50', we use a percentage of image width (W)
        # This makes the font large on all devices
        name_size = int(W * 0.06) 
        pos_size = int(W * 0.04)

        try:
            font_name = ImageFont.truetype("arial.ttf", name_size)
            font_pos = ImageFont.truetype("arial.ttf", pos_size) 
        except:
            font_name = font_pos = ImageFont.load_default()

        # --- 3. DYNAMIC COORDINATES ---
        center_x = W // 2
        
        # We use percentages of Height (H) to keep text on the lines
        name_y = int(H * 0.40) 
        pos_y = int(H * 0.54) 
           
        # 4. DRAW TEXT
        draw.text((center_x, name_y), name.upper(), fill=(20, 40, 80), font=font_name, anchor="mm")
        draw.text((center_x, pos_y), position, fill=(20, 40, 80), font=font_pos, anchor="mm")

        # 5. SEND TO BROWSER
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        return send_file(
            img_io, 
            mimetype='image/jpeg', 
            as_attachment=True, 
            download_name=f"{name.replace(' ', '_')}_LUCU_Cert.jpg"
        )

    except Exception as e:
        return f"An unexpected error occurred: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)