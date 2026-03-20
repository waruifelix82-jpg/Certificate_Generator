from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import io 
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__, template_folder='templates', static_folder='static')
# Secret key is required to use flash messages for the same-tab error
app.secret_key = "lucu_secret_key_2026"

@app.route("/")
def home():
    return render_template("index.html") 

@app.route("/generate", methods=["POST"])
def generate():
    name = request.form.get("student_name")
    adm_no = request.form.get("adm_no") 
    
    if not name or not adm_no:
        flash("Error: Name and Admission Number are required!", "error")
        return redirect(url_for('home'))
    
    # --- UPDATED RESTRICTION LOGIC ---
    # .strip() removes any accidental spaces the student might type at the end
    clean_adm = adm_no.strip()
    
    # Check if the string specifically ENDS with 21 or 22
    if not (clean_adm.endswith("21") or clean_adm.endswith("22")):
        flash("Registration Error: This certificate is only for admission numbers ending in 21 or 22.", "error")
        return redirect(url_for('home'))
    # ---------------------------------

    try:
        img = Image.open("certificate.jpg").convert("RGB")
        W, H = img.size
        draw = ImageDraw.Draw(img)
        
        # YOUR ORIGINAL MEASUREMENTS PRESERVED
        name_size = int(W * 0.04) 

        font_name = None
        font_paths = [
            "arial.ttf", 
            "Poppins-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        ]

        for path in font_paths:
            try:
                font_name = ImageFont.truetype(path, name_size)
                break
            except:
                continue

        if font_name is None:
            font_name = ImageFont.load_default()

        # YOUR ORIGINAL POSITIONING PRESERVED
        center_x = W // 2
        name_y = int(H * 0.39) 
           
        draw.text((center_x, name_y), name.upper(), fill=(0, 51, 153), font=font_name, anchor="mm")

        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=100)
        img_io.seek(0)
        
        return send_file(
            img_io, 
            mimetype='image/jpeg', 
            as_attachment=True, 
            download_name=f"{name.replace(' ', '_')}_Certificate.jpg"
        )

    except Exception as e:
        flash(f"System Error: {e}", "error")
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)