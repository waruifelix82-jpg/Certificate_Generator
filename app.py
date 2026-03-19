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
    if not name:
        return "Error: Name is required!", 400
    
    try:
        # 1. Load your certificate template
        img = Image.open("certificate.jpg").convert("RGB")
        W, H = img.size
        draw = ImageDraw.Draw(img)
        
        # 2. MASSIVE FONT SIZE (0.15 is roughly 15% of the image width)
        name_size = int(W * 0.15) 

        # 3. THE FONT SELECTOR (Vercel Compatibility)
        font_name = None
        # List of possible font paths (Local file first, then Linux system fonts)
        font_paths = [
            "arial.ttf", 
            "Poppins-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        ]

        for path in font_paths:
            try:
                font_name = ImageFont.truetype(path, name_size)
                break # Stop if we find one that works!
            except:
                continue

        if font_name is None:
            font_name = ImageFont.load_default()
            print("Warning: No TTF font found. Text will be tiny.")

        # 4. POSITIONING (Centered on the dotted line)
        center_x = W // 2
        # 0.44 puts it right above the signature/presentation line
        name_y = int(H * 0.44) 
           
        # 5. DRAW THE NAME
        # fill=(0, 51, 153) is a nice LUCU Blue
        draw.text((center_x, name_y), name.upper(), fill=(0, 51, 153), font=font_name, anchor="mm")

        # 6. Save and Send
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
        return f"System Error: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)