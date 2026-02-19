"""
QR Code Generator API + Web UI
Flask backend with REST API endpoints for generating QR codes
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import qrcode
import io
import os
import base64
from datetime import datetime

app = Flask(__name__)
CORS(app)

# HTML template for web UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>QR Code Generator</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        .container {
            background: white;
            border-radius: 1rem;
            padding: 2.5rem;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 0.5rem;
            font-size: 1.75rem;
        }
        .subtitle {
            color: #666;
            margin-bottom: 2rem;
            font-size: 0.9rem;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 500;
        }
        input, select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e0e0e0;
            border-radius: 0.5rem;
            font-size: 1rem;
            transition: border-color 0.2s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 0.75rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 0.5rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0);
        }
        #result {
            margin-top: 2rem;
            text-align: center;
            display: none;
        }
        #qrImage {
            max-width: 100%;
            border: 2px solid #e0e0e0;
            border-radius: 0.5rem;
            padding: 1rem;
            background: white;
            margin: 1rem 0;
        }
        .download-btn {
            margin-top: 1rem;
            background: #28a745;
        }
        .api-info {
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid #e0e0e0;
            font-size: 0.85rem;
            color: #666;
        }
        .api-info code {
            background: #f5f5f5;
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>QR Code Generator</h1>
        <p class="subtitle">Generate QR codes instantly</p>
        
        <form id="qrForm">
            <div class="form-group">
                <label for="text">Text or URL:</label>
                <input type="text" id="text" name="text" placeholder="https://example.com" required>
            </div>
            <div class="form-group">
                <label for="size">Size:</label>
                <select id="size" name="size">
                    <option value="200">Small (200x200)</option>
                    <option value="300" selected>Medium (300x300)</option>
                    <option value="400">Large (400x400)</option>
                    <option value="500">Extra Large (500x500)</option>
                </select>
            </div>
            <button type="submit">Generate QR Code</button>
        </form>
        
        <div id="result">
            <h3>Your QR Code:</h3>
            <img id="qrImage" alt="QR Code">
            <button class="download-btn" onclick="downloadQR()">Download PNG</button>
        </div>
        
        <div class="api-info">
            <strong>API Endpoint:</strong><br>
            <code>POST /api/generate</code><br>
            Body: <code>{"text": "your text", "size": 300}</code><br>
            Returns: <code>{"qr_code": "base64_image", "text": "..."}</code>
        </div>
    </div>
    
    <script>
        document.getElementById('qrForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = document.getElementById('text').value;
            const size = parseInt(document.getElementById('size').value);
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, size })
                });
                const data = await response.json();
                
                document.getElementById('qrImage').src = 'data:image/png;base64,' + data.qr_code;
                document.getElementById('result').style.display = 'block';
                window.qrData = data.qr_code;
            } catch (error) {
                alert('Error generating QR code: ' + error.message);
            }
        });
        
        function downloadQR() {
            if (!window.qrData) return;
            const link = document.createElement('a');
            link.href = 'data:image/png;base64,' + window.qrData;
            link.download = 'qrcode-' + Date.now() + '.png';
            link.click();
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Web UI for generating QR codes"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/generate', methods=['POST'])
def generate_qr():
    """
    Generate QR code via API
    
    Request body:
    {
        "text": "text or URL to encode",
        "size": 300 (optional, default 300)
    }
    
    Returns:
    {
        "qr_code": "base64_encoded_png",
        "text": "encoded text",
        "size": 300
    }
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing "text" field'}), 400
        
        text = data['text']
        size = data.get('size', 300)
        
        # Validate size
        if not isinstance(size, int) or size < 100 or size > 1000:
            return jsonify({'error': 'Size must be between 100 and 1000'}), 400
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize if needed
        if size != 300:
            img = img.resize((size, size))
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        return jsonify({
            'qr_code': qr_base64,
            'text': text,
            'size': size,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate/image', methods=['POST'])
def generate_qr_image():
    """
    Generate QR code and return as PNG image
    
    Request body:
    {
        "text": "text or URL to encode",
        "size": 300 (optional)
    }
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing "text" field'}), 400
        
        text = data['text']
        size = data.get('size', 300)
        
        if not isinstance(size, int) or size < 100 or size > 1000:
            return jsonify({'error': 'Size must be between 100 and 1000'}), 400
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        if size != 300:
            img = img.resize((size, size))
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return send_file(buffer, mimetype='image/png', download_name='qrcode.png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'QR Code Generator API'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
