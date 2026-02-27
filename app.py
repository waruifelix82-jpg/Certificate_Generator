from flask import Flask, render_template, request, send_file
import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont  # Fixed 'image' to 'Image'

app = Flask(__name__) # Fixed 'flask' to 'Flask'

# Ensure the static folder exists so we can save certificates
if not os.path.exists('static'):
    os.makedirs('static')

# Database setup
def init_db():
    conn = sqlite3.connect("student.db")
    conn.execute("CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY, name TEXT, pos TEXT)")
    conn.close()

# --- Routes (Must be indented all the way to the left) ---

@app.route("/")
def home():
    # Make sure you have a folder named 'templates' with index.html inside it!
    return render_template("index.html") 

@app.route("/generate", methods=["POST"])
def generate():
    # .get() returns None instead of crashing if the key is missing
    name = request.form.get("student_name")
    position = request.form.get("position")

    if not name or not position:
        return "Error: Missing name or position in form!", 400
    
    # ... rest of your code ...

    # 1. save to sqlite
    with sqlite3.connect("student.db") as con:
        cur = con.cursor() # Need a cursor to execute
        cur.execute("INSERT INTO students (name, pos) VALUES (?, ?)", (name, position))
        con.commit()

    # 2. Draw on image
    # Make sure "Certificate.jpg" is in the same folder as this script!
    try:
        img = Image.open("Certificate.jpg")
        draw = ImageDraw.Draw(img)
        
        # Coordinates: (x, y). Adjust based on your image size
        draw.text((512, 550), name, fill="black")
        draw.text((512, 680), position, fill="black")

        output_path = f"static/{name.replace(' ', '_')}_cert.jpg"
        img.save(output_path)
        
        return send_file(output_path, as_attachment=True)
    except FileNotFoundError:
        return "Error: Certificate.jpg template not found in folder!", 404

if __name__ == "__main__":
    init_db()
    app.run(debug=True) # Fixed 'debuge'