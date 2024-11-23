from flask import Flask, render_template, request, send_file, send_from_directory
import cv2
import numpy as np
from fpdf import FPDF
import os
import uuid

app = Flask(__name__, static_folder='public')

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
PDF_FOLDER = 'pdfs'

for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER, PDF_FOLDER]:
    os.makedirs(folder, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/icons/<path:filename>')
def serve_icon(filename):
    return send_from_directory('public/icons', filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if not request.files:
        return 'No file part', 400
    
    processed_paths = []
    for key, file in request.files.items():
        if file.filename == '':
            return 'No selected file', 400
        if file:
            filename = str(uuid.uuid4()) + '.jpg'
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            processed_path = process_image(file_path)
            processed_paths.append(processed_path)
    
    pdf_path = create_pdf(processed_paths)
    return send_file(pdf_path, as_attachment=True)

def process_image(file_path):
    img = cv2.imread(file_path)
    # We're no longer converting to grayscale or applying thresholding
    # Just save the original image
    processed_filename = os.path.basename(file_path)
    processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
    cv2.imwrite(processed_path, img)
    return processed_path

def create_pdf(image_paths):
    pdf = FPDF()
    for image_path in image_paths:
        pdf.add_page()
        # Get the dimensions of the image
        img = cv2.imread(image_path)
        img_height, img_width = img.shape[:2]
        # Calculate the aspect ratio
        aspect_ratio = img_height / img_width
        # Set the width to 190 (A4 page width minus margins)
        width = 190
        # Calculate the height based on the aspect ratio
        height = width * aspect_ratio
        # If the height exceeds the page height, adjust both width and height
        if height > 277:  # 297 (A4 height) - 20 (margins)
            height = 277
            width = height / aspect_ratio
        # Center the image on the page
        x = (210 - width) / 2
        y = (297 - height) / 2
        pdf.image(image_path, x=x, y=y, w=width, h=height)
    pdf_filename = str(uuid.uuid4()) + '.pdf'
    pdf_path = os.path.join(PDF_FOLDER, pdf_filename)
    pdf.output(pdf_path, "F")
    return pdf_path

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

