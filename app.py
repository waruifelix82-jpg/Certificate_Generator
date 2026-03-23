from flask import Flask, render_template, request, send_file, flash, redirect, url_for, make_response
import os
import io 
import csv 
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "lucu_secret_key_2026"

def is_student_registered(input_name):
    try:
        with open('registered_students.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
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
    
    if not is_student_registered(name):
        flash("Registration Error: Your name was not found on the Elders list.", "error")
        return redirect(url_for('home'))

    if request.cookies.get(f"done_{name.replace(' ', '_')}"):
        flash("System Note: You have already downloaded the certificate.", "error")
        return redirect(url_for('home'))

    clean_adm = adm_no.strip()
    if not (clean_adm.endswith("21") or clean_adm.endswith("22")):
        flash("Registration Error: Only forth years are eligible.", "error")
        return redirect(url_for('home'))

    try:
        # Load background - Must convert to RGBA to handle transparent signatures
        img = Image.open("certificate.jpg").convert("RGBA")
        W, H = img.size
        draw = ImageDraw.Draw(img)
        
        # --- NEW: SIGNATURE SECTION ---
        # Load the signature files from the static folder
        try:
            sig_pm = Image.open(os.path.join("static", "sig_pm.png")).convert("RGBA")
            sig_chair = Image.open(os.path.join("static", "sig_chair.png")).convert("RGBA")

            # Resize signatures to fit the lines (adjust these numbers if needed)
            sig_pm = sig_pm.resize((int(W * 0.15), int(H * 0.08)))
            sig_chair = sig_chair.resize((int(W * 0.15), int(H * 0.08)))

            # Paste signatures onto the certificate
            # Coordinates based on your template: PM (Left), Chairperson (Right)
            img.paste(sig_pm, (int(W * 0.15), int(H * 0.72)), sig_pm) 
            img.paste(sig_chair, (int(W * 0.68), int(H * 0.72)), sig_chair)
        except FileNotFoundError:
            print("Signature files not found in static folder. Skipping signatures.")

        # --- TEXT SECTION (Original Logic) ---
        name_size = int(W * 0.04) 
        font_paths = ["arial.ttf", "Poppins-Bold.ttf", 
                      "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                      "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]

        font_name = None
        for path in font_paths:
            try:
                font_name = ImageFont.truetype(path, name_size)
                break
            except: continue

        if font_name is None:
            font_name = ImageFont.load_default()

        center_x = W // 2
        name_y = int(H * 0.39) 
        draw.text((center_x, name_y), name.upper(), fill=(0, 51, 153), font=font_name, anchor="mm")

        # Convert back to RGB to save as JPEG
        final_img = img.convert("RGB")
        img_io = io.BytesIO()
        final_img.save(img_io, 'JPEG', quality=100)
        img_io.seek(0)
        
        response = make_response(send_file(
            img_io, 
            mimetype='image/jpeg', 
            as_attachment=True, 
            download_name=f"{name.replace(' ', '_')}_Certificate.jpg"
        ))
        response.set_cookie(f"done_{name.replace(' ', '_')}", "true", max_age=31536000)
        return response

    except Exception as e:
        flash(f"System Error: {e}", "error")
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)