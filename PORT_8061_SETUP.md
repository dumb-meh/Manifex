# Docker Configuration Updated to Port 8061

## Updated Files:
- ✅ Dockerfile: EXPOSE 8061 and CMD uses --port 8061
- ✅ docker-compose.yml: Port mapping "8061:8061"  
- ✅ main.py: Local uvicorn.run() uses port=8061

## Running the Application:

### Method 1: Docker Compose (Recommended)
```bash
# Build and start the container
docker-compose up --build

# Or run in background
docker-compose up -d --build

# Stop the container
docker-compose down
```

### Method 2: Direct Docker
```bash
# Build the image
docker build -t writing-api .

# Run the container
docker run -p 8061:8061 --env-file .env writing-api

# Or with volume mounting for development
docker run -p 8061:8061 -v ${PWD}:/app --env-file .env writing-api
```

### Method 3: Local Development
```bash
# Run locally without Docker
uvicorn main:app --reload --host 0.0.0.0 --port 8061

# Or simply
python main.py
```

## API Endpoints:

### Base URL: http://localhost:8061

### Topic Generation:
```bash
POST http://localhost:8061/writing/topic
Content-Type: application/json

{
  "topic": "Music"
}
```

### Writing Scoring:
```bash
POST http://localhost:8061/writing/final  
Content-Type: application/json

{
  "topic": "Music",
  "related_words": ["Harmony", "Crescendo", "Ballad", "Maestro", "Amplification"],
  "user_paragraph": "Your paragraph here..."
}
```

### API Documentation:
- Swagger UI: http://localhost:8061/docs
- ReDoc: http://localhost:8061/redoc

## Testing the New Port:

### Quick Health Check:
```bash
curl http://localhost:8061/docs
```

### Test Topic Endpoint:
```bash
curl -X POST "http://localhost:8061/writing/topic" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Test Final Endpoint:
```bash
curl -X POST "http://localhost:8061/writing/final" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Music",
    "related_words": ["test"],
    "user_paragraph": "Short test paragraph."
  }'
```

## Environment Variables:
Make sure your .env file is properly configured:
```
OPENAI_API_KEY=your_key_here
GroqAPIKey=your_groq_key_here
```

## Docker Commands:
```bash
# View running containers
docker ps

# View logs
docker-compose logs -f

# Restart service
docker-compose restart

# Clean up
docker-compose down --volumes --rmi all
```