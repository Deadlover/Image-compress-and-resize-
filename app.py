from flask import Flask, request, jsonify, render_template,send_from_directory
from flask_uploads import UploadSet, configure_uploads, IMAGES
from PIL import Image
import os

app = Flask(__name__)

# Configuration for file uploads and resized images
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join('static/image', 'input')   # Original uploads destination
app.config['RESIZED_PHOTOS_DEST'] = os.path.join('static/image', 'output')  # Resized images destination

# Initialize UploadSet for photos
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/compress')
def compresspage():
    return render_template('compressimage.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' not in request.files:
        return jsonify({'error': 'File not uploaded'}), 400

    file = request.files['photo']
    target_mb = request.form.get('size')
    width = request.form.get('width')
    height = request.form.get('height')
    resize = request.form.get('resize')

    # Validate target size
    if target_mb is not None:
        try:
            target_mb = float(target_mb)
        except ValueError:
            return jsonify({'error': 'Size must be a valid number'}), 400
    else:
        target_mb = None  # No size limit provided

    # Validate width and height
    if width and height:
        try:
            width = float(width)
            height = float(height)
        except ValueError:
            return jsonify({'error': 'Width and height must be valid numbers'}), 400
    else:
        width = None
        height = None

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 400

    # Save original photo to 'image/input' folder
    filename = photos.save(file)

    # Resize and/or compress image
    if resize == 'True':
        print("resize**********************")
        resized_filename = resize_image(filename, height, width)
        return send_image(resized_filename)
    else:
        print("compress**********************")
        compressed_filename = compress(filename, target_mb)
        return send_image(compressed_filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def resize_image(filename, height=300, width=300):
    img = Image.open(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))
    img.thumbnail((width, height))
    resized_filename = f"resized_{filename}"
    img.save(os.path.join(app.config['RESIZED_PHOTOS_DEST'], resized_filename))
    return resized_filename

def send_image(filename):
    url = os.path.join(app.config['RESIZED_PHOTOS_DEST'], filename)
    print(url)
    return jsonify({'image_url': url,'filename':filename}), 200

def compress(filename, target_mb=2, quality=85, resize_factor=0.9):
    input_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    
    with Image.open(input_path) as img:
        output_path = os.path.join(app.config['RESIZED_PHOTOS_DEST'], f"compressed_{filename}")
        
        while True:
            img.save(output_path, quality=quality)
            current_size_mb = os.path.getsize(output_path) / (1024 * 1024)

            if current_size_mb <= target_mb or quality <= 10:
                break

            quality -= 5
            if current_size_mb > target_mb:
                img = img.resize((int(img.width * resize_factor), int(img.height * resize_factor)), Image.LANCZOS)
        
        print(f"Final file size: {current_size_mb} MB with quality: {quality} and size: {img.size}")

    return f"compressed_{filename}"

# @app.route('/download_image', methods=['POST'])
# def download_image():
#     print('*************')
#     print('*************',request.get_json())
#     data = request.get_json()
#     print(data)
#     filename = data.get('value')
#     print(filename)
#     return send_from_directory(
#         'static/image/output/',  # The directory where the image is stored
#         filename,         # The name of the image file
#         as_attachment=True  # This will trigger the download
#     )

if __name__ == '__main__':
    app.run(debug=True)
