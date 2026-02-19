# QR Code Generator API + Web UI

Full-stack web service for generating QR codes. REST API + beautiful web interface.

## Features

- 🎨 **Web UI** - Simple, beautiful interface for generating QR codes
- 🔌 **REST API** - Programmatic access via HTTP endpoints
- 📱 **Multiple sizes** - Generate QR codes from 200x200 to 500x500 pixels
- 📥 **Download** - Download QR codes as PNG images
- ✅ **Error handling** - Proper validation and error responses

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run locally

```bash
python app.py
```

Open http://localhost:5000 in your browser.

## API Endpoints

### `POST /api/generate`

Generate QR code and get base64-encoded image.

**Request:**
```json
{
  "text": "https://example.com",
  "size": 300
}
```

**Response:**
```json
{
  "qr_code": "base64_encoded_png_string",
  "text": "https://example.com",
  "size": 300,
  "timestamp": "2025-02-14T10:30:00"
}
```

### `POST /api/generate/image`

Generate QR code and return PNG image directly.

**Request:**
```json
{
  "text": "Hello World",
  "size": 400
}
```

**Response:** PNG image file

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "QR Code Generator API"
}
```

## Usage Examples

### cURL

```bash
# Generate QR code
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "https://github.com", "size": 300}'

# Get PNG image
curl -X POST http://localhost:5000/api/generate/image \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World"}' \
  --output qrcode.png
```

### Python

```python
import requests

response = requests.post('http://localhost:5000/api/generate', json={
    'text': 'https://example.com',
    'size': 300
})

data = response.json()
qr_base64 = data['qr_code']

# Save image
import base64
img_data = base64.b64decode(qr_base64)
with open('qrcode.png', 'wb') as f:
    f.write(img_data)
```

### JavaScript

```javascript
fetch('http://localhost:5000/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'https://example.com', size: 300 })
})
.then(res => res.json())
.then(data => {
  const img = document.createElement('img');
  img.src = 'data:image/png;base64,' + data.qr_code;
  document.body.appendChild(img);
});
```

## Deployment

### Railway

1. Connect GitHub repo to Railway
2. Railway auto-detects Python
3. Set start command: `python app.py` or `gunicorn app:app`
4. Deploy

### Render

1. New Web Service → Connect GitHub repo
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn app:app`
4. Deploy

### Vercel

Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [{"src": "app.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "app.py"}]
}
```

## Project Structure

```
qr-api/
├── app.py              # Flask app with API + web UI
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## License

MIT
