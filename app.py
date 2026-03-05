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
        # Fixed: Wrapping in int() ensures these are whole numbers
        name_size = int(W * 0.06) 
        pos_size = int(W * 0.04)

        try:
            # Note: arial.ttf must be in your GitHub root folder
            font_name = ImageFont.truetype("arial.ttf", name_size)
            font_pos = ImageFont.truetype("arial.ttf", pos_size) 
        except:
            font_name = font_pos = ImageFont.load_default()

        # --- 3. DYNAMIC COORDINATES ---
        center_x = W // 2
        
        # Fixed: Percentage digits for standard certificate layouts
        name_y = int(H * 0.39) 
        pos_y = int(H * 0.55) 
           
        # --- 4. DRAW TEXT ---
        # Fixed: Colors must be whole numbers (20, 40, 80) NOT (0.20, 0.40, 0.80)
        navy_blue = (20, 40, 80)
        
        draw.text((center_x, name_y), name.upper(), fill=navy_blue, font=font_name, anchor="mm")
        draw.text((center_x, pos_y), position, fill=navy_blue, font=font_pos, anchor="mm")

        # 5. SEND TO BROWSER
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=100)
        img_io.seek(0)
        
        return send_file(
            img_io, 
            mimetype='image/jpeg', 
            as_attachment=True, 
            download_name=f"{name.replace(' ', '_')}_LUCU_Cert.jpg"
        )

    except Exception as e:
        # This will now catch and show any remaining errors clearly
        return f"An unexpected error occurred: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)