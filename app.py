from flask import Flask, render_template, request, send_file, flash, redirect, url_for, make_response
import os
import io 
import csv 
import datetime 
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "lucu_secret_key_2026"

def is_student_registered(input_name, selected_ministry):
    # Mapping ministries to their specific files
    if "Network" in selected_ministry:
        filename = 'registered_et.csv'
    elif "Creative" in selected_ministry:
        filename = 'registered_creative.csv'
    elif "Publicity" in selected_ministry:
        filename = 'registered_publicity.csv'
    else:
        filename = 'registered_students.csv' # Default for Forth Years
    
    if not os.path.exists(filename):
        print(f"!!! ERROR: {filename} NOT FOUND")
        return False

    try:
        with open(filename, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            headers = [h.lower().strip() for h in next(reader)]
            
            name_index = -1
            if 'name' in headers:
                name_index = headers.index('name')
            else:
                name_index = 0
            
            user_input = " ".join(input_name.strip().upper().split())
            
            for row in reader:
                if not row: continue 
                
                raw_csv_name = row[name_index]
                csv_name = " ".join(raw_csv_name.strip().upper().split())
                
                if csv_name == user_input:
                    print(f"SUCCESS: Found {csv_name} in {filename}")
                    return True
            
            print(f"FAILED: '{user_input}' not found in {filename}")
            return False
    except Exception as e:
        print(f"CSV ERROR in {filename}: {e}")
        return False

@app.route("/admin/lucu_admin_2026")
def admin_dashboard():
    downloads = []
    # Admin dashboard will remain empty on Vercel as downloads.csv cannot be updated
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
    
    if not is_student_registered(name, ministry):
        flash(f"Error: {name} is not registered under {ministry}.", "error")
        return redirect(url_for('home'))

    if request.cookies.get(f"done_{name.replace(' ', '_')}"):
        flash("System Note: You have already downloaded the certificate.", "error")
        return redirect(url_for('home'))

    clean_adm = adm_no.strip()
    if not (clean_adm.endswith("21") or clean_adm.endswith("22")):
        flash("Registration Error: Only fourth years are eligible.", "error")
        return redirect(url_for('home'))

    try:
        configs = {
            "Forth Years": {
                "bg": "certificate_forth_years.jpg",
                "sig_p": "sig_pm.png",
                "sig_c": "sig_chair.png",
                "name_y": 0.39,   
                "sig_y": 0.72     
            },
            "Network Evangelistic": {
                "bg": "certificate_network.jpg",
                "sig_p": "sig_pm_network.png",
                "sig_c": "sig_chair_network.png",
                "name_y": 0.49,   
                "sig_y": 0.75     
            },
            "Publicity and Media": {
                "bg": "certificate_pm.jpg",
                "sig_p": "sig_pm.png", 
                "sig_c": "sig_chair.png",
                "name_y": 0.53,   
                "sig_y": 0.75     
            },
            "Creative Ministry": {
                "bg": "certificate_creative.jpg",
                "sig_p": "sig_pm.png", 
                "sig_c": "sig_chair.png",
                "name_y": 0.57,   
                "sig_y": 0.67
            }
        }

        cfg = configs.get(ministry, configs["Forth Years"])

        img = Image.open(cfg["bg"]).convert("RGBA")
        W, H = img.size
        draw = ImageDraw.Draw(img)
        
        try:
            sig_pm_path = os.path.join("static", cfg["sig_p"])
            sig_chair_path = os.path.join("static", cfg["sig_c"])
            sig_pm = Image.open(sig_pm_path).convert("RGBA")
            sig_chair = Image.open(sig_chair_path).convert("RGBA")
            sig_pm = sig_pm.resize((int(W * 0.15), int(H * 0.08)))
            sig_chair = sig_chair.resize((int(W * 0.15), int(H * 0.08)))
            img.paste(sig_pm, (int(W * 0.15), int(H * cfg["sig_y"])), sig_pm) 
            img.paste(sig_chair, (int(W * 0.68), int(H * cfg["sig_y"])), sig_chair)
        except Exception as e:
            print(f"Signature error: {e}")

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

        name_y = int(H * cfg["name_y"]) 
        draw.text((W // 2, name_y), name.upper(), fill=(0, 51, 153), font=font_name, anchor="mm")

        # --- CSV LOGGING DISABLED FOR VERCEL COMPATIBILITY ---
        # log_file = 'downloads.csv'
        # file_exists = os.path.isfile(log_file)
        # with open(log_file, mode='a', encoding='utf-8', newline='') as f:
        #     writer = csv.writer(f)
        #     if not file_exists:
        #         writer.writerow(['Timestamp', 'Name', 'Admission_No', 'Ministry'])
        #     writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name.upper(), adm_no, ministry])

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