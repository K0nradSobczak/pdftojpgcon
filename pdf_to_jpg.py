import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from pdf2image import convert_from_path
from PIL import Image

app = Flask(__name__)

def download_file(url, download_path):
    response = requests.get(url)
    with open(download_path, 'wb') as f:
        f.write(response.content)
    return download_path

def pdf_to_jpg(pdf_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    images = convert_from_path(pdf_path)
    jpg_files = []
    for i, image in enumerate(images):
        jpg_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
        image.save(jpg_path, 'JPEG')
        jpg_files.append(jpg_path)
    return jpg_files

@app.route('/convert', methods=['POST'])
def convert_pdf():
    data = request.json
    pdf_path = data['pdf_path']
    output_folder = data['output_folder']
    
    if not pdf_path or not output_folder:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Check if pdf_path is a URL
    if pdf_path.startswith('http://') or pdf_path.startswith('https://'):
        # Download the file from the URL
        try:
            local_pdf_path = download_file(pdf_path, 'downloaded_pdf.pdf')
        except Exception as e:
            return jsonify({'error': f'Failed to download PDF: {str(e)}'}), 500
    else:
        local_pdf_path = pdf_path
    
    try:
        jpg_files = pdf_to_jpg(local_pdf_path, output_folder)
        # Remove the local downloaded PDF if it was downloaded
        if pdf_path.startswith('http://') or pdf_path.startswith('https://'):
            os.remove(local_pdf_path)
        return jsonify({'jpg_files': jpg_files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/output/<path:filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory('/app/data/output', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
