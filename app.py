from flask import Flask, render_template, request, send_file
import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# --- INITIALIZATION ---
if not os.path.exists('static'):
    os.makedirs('static')

def init_db():
    conn = sqlite3.connect("student.db")
    conn.execute("CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY, name TEXT, pos TEXT)")
    conn.close()

# --- ROUTES ---

@app.route("/")
def home():
    return render_template("index.html") 

@app.route("/generate", methods=["POST"])
def generate():
    # 1. Get data from the form
    name = request.form.get("student_name")
    position = request.form.get("position")

    if not name or not position:
        return "Error: Missing name or position!", 400
    
    # 2. Save to Database
    try:
        with sqlite3.connect("student.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO students (name, pos) VALUES (?, ?)", (name, position))
            con.commit()
    except Exception as e:
        print(f"Database Error: {e}")

    # 3. Draw on Image
    try:
        # Load your template
        img = Image.open("certificate.jpg").convert("RGB")
        W, H = img.size
        draw = ImageDraw.Draw(img)
        
        # --- LOGO PLACEMENT (CENTERED TOP) ---
        try:
            logo = Image.open("static/logo.png")
            logo.thumbnail((220, 220), Image.Resampling.LANCZOS)
            logo_x = (W - logo.width) // 2
            # Pasting logo 50 pixels from the top
            img.paste(logo, (logo_x, 50), logo if logo.mode == 'RGBA' else None)
        except Exception as e:
            print(f"Logo skipped: {e}")

        # --- FONT LOADING ---
        try:
            # Using bold size for the name
            font_name = ImageFont.truetype("arial.ttf", 85) 
            font_pos = ImageFont.truetype("arial.ttf", 45)
        except:
            font_name = font_pos = ImageFont.load_default()

        # --- EXACT COORDINATES ---
        # W // 2 is the center of the paper horizontally
        center_x = W // 2

        # name_y: Increase this number to move the name LOWER on the page.
        # pos_y: Increase this to move the position LOWER.
        name_y = 1000 # This should now sit right on the red line
        pos_y = 1400   # This sits in the blank space below

        # Write Name (Navy Blue/Black)
        # 'mm' anchor means the MIDDLE of the text is placed at center_x
        draw.text((center_x, name_y), name.upper(), fill=(20, 40, 80), font=font_name, anchor="mm")
        
        # Write Position (Dark Grey)
        draw.text((center_x, pos_y), position, fill=(60, 60, 60), font=font_pos, anchor="mm")

        # 4. Save and Send
        file_name = f"{name.replace(' ', '_')}_LUCU_Cert.jpg"
        output_path = os.path.join("static", file_name)
        img.save(output_path, quality=95)
        
        return send_file(output_path, as_attachment=True)

    except FileNotFoundError:
        return "Error: 'certificate.jpg' not found.", 404
    except Exception as e:
        return f"An unexpected error occurred: {e}", 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True)