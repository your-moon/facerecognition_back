# Face Recognition API

A FastAPI-based face recognition service that can identify faces from images using face_recognition library. The service supports multiple reference photos per person and includes performance optimizations like caching and image preprocessing.

## Features

- Face detection and recognition using `face_recognition` library
- Multiple reference photos per person support
- Base64 image input support
- Performance optimizations with caching
- Docker support
- FastAPI development server with hot reload
- RESTful API endpoints

## Project Structure

```
.
├── faces/              # Directory for reference face images
│   ├── person1/       # Each person has their own directory
│   │   ├── photo1.jpg
│   │   └── photo2.jpg
│   └── person2/
│       ├── image1.jpg
│       └── image2.jpg
├── main.py            # FastAPI application
├── face_recog.py      # Face recognition logic
├── Dockerfile         # Docker configuration
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Prerequisites

- Python 3.9+
- Docker (optional)

## Installation

### Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd face-recognition
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install "fastapi[standard]"  # Install FastAPI with all optional dependencies
```

### Docker Setup

1. Build the Docker image:
```bash
docker build -t face-recognition-app .
```

2. Run the container:
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/faces:/app/faces \
  --name face-recognition \
  face-recognition-app
```

## Development

### Running in Development Mode

```bash
# Using FastAPI CLI (Recommended)
fastapi dev main.py

# Alternative methods
uvicorn main:app --reload  # Using uvicorn directly
python -m uvicorn main:app --reload  # Using Python module
```

The FastAPI CLI (`fastapi dev`) provides:
- Automatic code reloading
- Better error messages
- Debug toolbar
- Performance profiling
- API documentation at /docs

### Docker Development

1. Build the image:
```bash
docker build -t face-recognition-app .
```

2. Run with development mode:
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd):/app \
  -v $(pwd)/faces:/app/faces \
  --name face-recognition \
  face-recognition-app
```

### API Endpoints

#### 1. Face Recognition with File Upload
```bash
curl -X POST "http://localhost:8000/recognize-face" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg"
```

#### 2. Face Recognition with Base64 Image
```bash
curl -X POST "http://localhost:8000/recognize-face-base64" \
  -H "Content-Type: application/json" \
  -d '{"frame": "data:image/jpeg;base64,/9j/4AAQSkZJRgAB..."}'
```

### Response Format

```json
{
  "status": "success",
  "faces_found": 1,
  "results": [
    {
      "name": "person_name",
      "confidence": 0.92,
      "location": {
        "top": 50,
        "right": 150,
        "bottom": 200,
        "left": 100
      },
      "matched": true
    }
  ]
}
```

### Performance Optimization

- The application uses caching to store face encodings
- Cache is stored in `face_encodings_cache.pkl`
- Cache expires after 24 hours
- Images are automatically resized if too large

## Production Deployment

1. Update Dockerfile CMD to production mode:
```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

2. Build and run:
```bash
docker build -t face-recognition-app .
docker run -d -p 8000:8000 -v $(pwd)/faces:/app/faces face-recognition-app
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Debug toolbar: http://localhost:8000/_debug (in development mode)

## Environment Variables

- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here] 