from flask import Flask, render_template, request, send_file, flash, redirect, url_for, make_response
import os
import io 
import csv # Added to read your list
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "lucu_secret_key_2026"

# --- NEW: Function to check the CSV file ---
def is_student_registered(input_name):
    try:
        # Opens your created CSV file
        with open('registered_students.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # We compare everything in UPPERCASE so "John" matches "JOHN"
            registered_names = [row['name'].strip().upper() for row in reader]
            return input_name.strip().upper() in registered_names
    except FileNotFoundError:
        return False

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
    
    # 1. CHECK IF REGISTERED IN CSV
    if not is_student_registered(name):
        flash("Registration Error: Your name was not found on the Elders list.", "error")
        return redirect(url_for('home'))

    # 2. CHECK IF ALREADY DOWNLOADED (Cookie Check)
    # This prevents the same device from downloading twice
    if request.cookies.get(f"done_{name.replace(' ', '_')}"):
        flash("System Note: You have already downloaded the certificate.", "error")#error
        return redirect(url_for('home'))

    # 3. INTAKE RESTRICTION
    clean_adm = adm_no.strip()
    if not (clean_adm.endswith("21") or clean_adm.endswith("22")):
        flash("Registration Error: Only forth years are  eligible.", "error")
        return redirect(url_for('home'))

    try:
        img = Image.open("certificate.jpg").convert("RGB")
        W, H = img.size
        draw = ImageDraw.Draw(img)
        
        # PRESERVING YOUR ORIGINAL MEASUREMENT
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
        
        # 4. SEND FILE AND SET "DOWNLOADED" COOKIE
        response = make_response(send_file(
            img_io, 
            mimetype='image/jpeg', 
            as_attachment=True, 
            download_name=f"{name.replace(' ', '_')}_Certificate.jpg"
        ))
        # Mark as downloaded for 1 year
        response.set_cookie(f"done_{name.replace(' ', '_')}", "true", max_age=31536000)
        return response

    except Exception as e:
        flash(f"System Error: {e}", "error")
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)