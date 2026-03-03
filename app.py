from flask import Flask, render_template, request, send_file
import os
import io  # Required for Vercel and downloading without saving files
from PIL import Image, ImageDraw, ImageFont

# Set folders for Vercel compatibility
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- ROUTES ---

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
        
        # 2. FONT LOADING (Increased Size)
        try:
            # Name: Bold and Large (85)
            # Position: Bold and Large (70)
            font_name = ImageFont.truetype("arial.ttf", 35)
            font_pos = ImageFont.truetype("arial.ttf", 40) 
        except:
            font_name = font_pos = ImageFont.load_default()

        # 3. COORDINATES (FIXED FOR THE RED LINE)
        center_x = W // 2
        
        # name_y: Adjusted to sit exactly on your template's red line
        name_y = 250   
        
        # pos_y: Adjusted to sit in the blank space after "Position of"
        pos_y = 350
           
        # 4. DRAW TEXT (Using Navy Blue for both to match LUCU Logo)
        # anchor="mm" ensures it stays perfectly centered
        draw.text((center_x, name_y), name.upper(), fill=(20, 40, 80), font=font_name, anchor="mm")
        draw.text((center_x, pos_y), position, fill=(20, 40, 80), font=font_pos, anchor="mm")

        # 5. SEND TO BROWSER (Vercel Memory Fix)
        # We don't save to the 'static' folder (to avoid 3-logo or permission issues)
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        return send_file(
            img_io, 
            mimetype='image/jpeg', 
            as_attachment=True, 
            download_name=f"{name.replace(' ', '_')}_LUCU_Cert.jpg"
        )

    except FileNotFoundError:
        return "Error: 'certificate.jpg' not found.", 404
    except Exception as e:
        return f"An unexpected error occurred: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)