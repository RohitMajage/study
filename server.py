from flask import Flask, request, send_from_directory, jsonify
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create uploads directory if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Store download logs in memory
download_logs = []

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin.html')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/download.html')
def download():
    return send_from_directory('.', 'download.html')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # Log the download
    user = request.args.get('user', 'Unknown')
    download_logs.append({
        'user': user,
        'file': filename,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    return send_from_directory('uploads', filename)

@app.route('/uploads/', methods=['GET'])
def list_files():
    files = os.listdir('uploads')
    return jsonify(files)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("Upload request received")  # Debug log
        if 'file' not in request.files:
            print("No file part in request")  # Debug log
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("No selected file")  # Debug log
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            print(f"Invalid file type: {file.filename}")  # Debug log
            return jsonify({'error': 'File type not allowed. Please upload only PDF, DOC, DOCX, PPT, or PPTX files'}), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        
        # Check if file already exists
        if os.path.exists(file_path):
            print(f"File already exists: {filename}")  # Debug log
            return jsonify({'error': 'A file with this name already exists'}), 400
        
        file.save(file_path)
        print(f"File saved successfully: {filename}")  # Debug log
        return jsonify({'message': 'File uploaded successfully'})
    except Exception as e:
        print(f"Error during upload: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

@app.route('/logs')
def get_logs():
    return jsonify(download_logs)

@app.route('/uploads/<path:filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_path = os.path.join('uploads', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': 'File deleted successfully'})
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0') 