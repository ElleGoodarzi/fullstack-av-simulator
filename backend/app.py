from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from lane_detection import detect_lane
import os
import time

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    upload_path = file.filename
    file.save(upload_path)
    
    start = time.time()
    
    if upload_path.lower().endswith(('.mp4', '.avi', '.mov')):
        position, output_path = detect_lane(video_path=upload_path)
    else:
        position, output_path = detect_lane(image_path=upload_path)
    
    fps = 1 / (time.time() - start)  # Calculate FPS
    
    os.remove(upload_path)  # Cleanup
    
    if output_path is None:
        return jsonify({'error': 'Processing failed - no lanes detected'}), 500
    
    return jsonify({'lane_position': position, 'output_path': output_path, 'fps': fps})

@app.route('/<filename>')
def serve_output(filename):
    return send_from_directory('.', filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'}

if __name__ == '__main__':
    app.run(debug=True)