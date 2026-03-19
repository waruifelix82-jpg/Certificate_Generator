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
    # Now only getting the name
    name = request.form.get("student_name")

    if not name:
        return "Error: Name is required!", 400
    
    try:
        # 1. Load your template
        img = Image.open("certificate.jpg").convert("RGB")
        W, H = img.size
        draw = ImageDraw.Draw(img)
        
        # 2. Dynamic Font Sizing
        name_size = int(W * 0.06) 

        try:
            font_name = ImageFont.truetype("arial.ttf", name_size)
        except:
            font_name = ImageFont.load_default()

        # 3. Dynamic Coordinates
        center_x = W // 2
        name_y = int(H * 0.39) # Adjust this if the name is too high or low
           
        # 4. Draw Name Only
        # Using the Navy Blue color (20, 40, 80)
        draw.text((center_x, name_y), name.upper(), fill=(20, 40, 80), font=font_name, anchor="mm")

        # 5. Send to Browser
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=95)
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