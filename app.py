from flask import Flask, render_template, request, send_file, flash, redirect, url_for, make_response
import os
import io 
import csv 
import datetime 
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "lucu_secret_key_2026"

def is_student_registered(input_name, selected_ministry):
    try:
        with open('registered_students.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (row['name'].strip().upper() == input_name.strip().upper() and 
                    row['category'].strip() == selected_ministry):
                    return True
            return False
    except FileNotFoundError:
        return False

@app.route("/admin/lucu_admin_2026")
def admin_dashboard():
    downloads = []
    try:
        if os.path.exists('downloads.csv'):
            with open('downloads.csv', mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                downloads = list(reader)
    except Exception as e:
        flash(f"Admin Error: {e}", "error")
    return render_template("admin.html", downloads=downloads)

@app.route("/")
def home():
    return render_template("index.html") 

@app.route("/generate", methods=["POST"])
def generate():
    name = request.form.get("student_name")
    adm_no = request.form.get("adm_no") 
    ministry = request.form.get("ministry") 
    
    if not name or not adm_no or not ministry:
        flash("Error: All fields are required!", "error")
        return redirect(url_for('home'))
    
    # FIXED: Calling the function correctly
    def is_student_registered(input_name, selected_ministry):
        flash(f"Registration Error: {name} not found in {ministry}.", "error")
        return redirect(url_for('home'))

    if request.cookies.get(f"done_{name.replace(' ', '_')}"):
        flash("System Note: You have already downloaded the certificate.", "error")
        return redirect(url_for('home'))

    clean_adm = adm_no.strip()
    if not (clean_adm.endswith("21") or clean_adm.endswith("22")):
        flash("Registration Error: Only forth years are eligible.", "error")
        return redirect(url_for('home'))

    try:
        # --- ASSET CONFIGURATION ---
        configs = {
            "Forth Years": {
                "bg": "certificate_forth_years.jpg",
                "sig_p": "sig_pm.png",
                "sig_c": "sig_chair.png",
                "name_y": 0.39,   # Original position
                "sig_y": 0.72     # Original signature height
            },
            "Network Evangelistic": {
                "bg": "certificate_network.jpg",
                "sig_p": "sig_pm_network.png",
                "sig_c": "sig_chair_network.png",
                "name_y": 0.49,   # TOUCHES THE LINE for Network
                "sig_y": 0.75     # Adjusts signatures for Network layout
            }
        }

        cfg = configs.get(ministry, configs["Forth Years"])

        img = Image.open(cfg["bg"]).convert("RGBA")
        W, H = img.size
        draw = ImageDraw.Draw(img)
        
        try:
            sig_pm = Image.open(os.path.join("static", cfg["sig_p"])).convert("RGBA")
            sig_chair = Image.open(os.path.join("static", cfg["sig_c"])).convert("RGBA")
            
            sig_pm = sig_pm.resize((int(W * 0.15), int(H * 0.08)))
            sig_chair = sig_chair.resize((int(W * 0.15), int(H * 0.08)))
            
            # Using dynamic sig_y from config
            img.paste(sig_pm, (int(W * 0.15), int(H * cfg["sig_y"])), sig_pm) 
            img.paste(sig_chair, (int(W * 0.68), int(H * cfg["sig_y"])), sig_chair)
        except FileNotFoundError:
            print(f"Signature files for {ministry} not found.")

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
        # Using dynamic name_y from config to ensure it touches the line
        name_y = int(H * cfg["name_y"]) 
        draw.text((center_x, name_y), name.upper(), fill=(0, 51, 153), font=font_name, anchor="mm")

        # --- LOG DOWNLOAD ---
        try:
            log_file = 'downloads.csv'
            file_exists = os.path.isfile(log_file)
            with open(log_file, mode='a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Timestamp', 'Name', 'Admission_No', 'Ministry'])
                writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name.upper(), adm_no, ministry])
        except Exception as e:
            print(f"Logging failed: {e}")

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