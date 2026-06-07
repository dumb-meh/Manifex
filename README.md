# 🎓 Manifex - AI-Powered Language Learning API

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai)](https://openai.com)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

> 🚀 A comprehensive AI-powered language learning platform offering personalized exercises for reading, writing, speaking, and presentation skills.

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [📦 Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
- [📚 API Documentation](#-api-documentation)
- [🎯 Available Services](#-available-services)
- [🔧 Configuration](#-configuration)
- [🐳 Docker Support](#-docker-support)
- [📖 API Usage Examples](#-api-usage-examples)

---


## ✨ Features

### 👔 Adult Learning
- ⚡ Word Flash: Quick word recognition drills
- 🧩 Word Parts Workshop: Learn prefixes, suffixes, and roots
- 📝 Sentence Builder: Construct complex sentences
- 💭 Phrase Maker: Create effective phrases
- 🎧 Auditory Discrimination: Distinguish similar sounds
- 🗺️ Phoneme Mapping: Map sounds to letters

### 🎤 Presentation
- 💪 Power Words: Learn impactful vocabulary
- 🔗 Flow Chain: Build coherent presentations
- 🎯 Context Spin: Adapt content to different contexts
- 🎓 Precision Drill: Practice precise communication

### 📖 Reading
- 📝 Sight Word Practice: Practice common sight words
- 📚 Reading Comprehension: Improve reading comprehension skills
- 🔤 Phoneme Flashcards: Learn phonemes through flashcards

### ✍️ Writing
- ✏️ Writing Practice: AI-powered writing assistance and scoring

### 🗣️ Speaking
- 👂 Listen & Speak: Practice listening and speaking
- 🔄 Phrase Repeat: Repeat and master phrases
- 🗨️ Pronunciation: Improve pronunciation skills
- 💬 Vocabulary Challenge: Expand your vocabulary

### 🔊 Speech Integration
- Text-to-speech and speech-to-text capabilities

### 🛠️ Platform Features
- RESTful API with clean, well-documented endpoints
- Docker-ready for easy deployment
- Automatic temporary file management
- Built-in Swagger UI and ReDoc documentation
- CORS enabled for cross-origin requests

---

## 🏗️ Architecture

```
Manifex/
├── 📱 app/
│   ├── 🔌 api/v1/          # API routes and versioning
│   ├── ⚙️ core/            # Core configuration
│   ├── 🎓 services/        # Learning modules
│   │   ├── 📖 Reading/
│   │   ├── ✍️ Writing/
│   │   ├── 🗣️ Speaking/
│   │   ├── 🎤 Presentation/
│   │   └── 👔 Adult/
│   └── 🛠️ utils/          # Helper utilities
├── 🐳 Docker files
└── 📄 Configuration files
```

---

## 🛠️ Tech Stack

- **Framework**: FastAPI 🚀
- **AI Engine**: OpenAI GPT 🤖
- **Server**: Uvicorn ⚡
- **Validation**: Pydantic 🔍
- **Containerization**: Docker 🐳
- **Audio Processing**: Speech-to-Text & Text-to-Speech 🔊

---

## 📦 Installation

### Prerequisites

- 🐍 Python 3.8+
- 🐳 Docker (optional)
- 🔑 OpenAI API Key

### Local Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd Manifex
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

---

## 🚀 Quick Start

### Running Locally

```bash
python main.py
```

The API will be available at `http://localhost:8061`

### Running with Docker

```bash
docker-compose up -d
```

---

## 📚 API Documentation

Once the server is running, visit:

- 📖 **Swagger UI**: `http://localhost:8061/docs`
- 🔧 **ReDoc**: `http://localhost:8061/redoc`

---

## 🎯 Available Services

### 🤖 Chatbot Services

| Service | Endpoint | Description |
|---------|----------|-------------|
| Mercury Web Assistant | `/api/v1/chatbot/web` | Manifex website support and navigation help |
| Mercury App Assistant | `/api/v1/chatbot/app` | Manifex app support and in-app feature guidance |

### 📖 Reading Services

| Service | Endpoint | Description |
|---------|----------|-------------|
| 📝 Sight Word Practice | `/api/v1/reading/sight-word-practice` | Practice common sight words |
| 📚 Reading Comprehension | `/api/v1/reading/comprehension` | Improve reading comprehension skills |
| 🔤 Phoneme Flashcards | `/api/v1/reading/phoneme-flashcards` | Learn phonemes through flashcards |

### ✍️ Writing Services

| Service | Endpoint | Description |
|---------|----------|-------------|
| ✏️ Writing Practice | `/api/v1/writing` | AI-powered writing assistance and scoring |

### 🗣️ Speaking Services

| Service | Endpoint | Description |
|---------|----------|-------------|
| 👂 Listen & Speak | `/api/v1/speaking/listen-speak` | Practice listening and speaking |
| 🔄 Phrase Repeat | `/api/v1/speaking/phrase-repeat` | Repeat and master phrases |
| 🗨️ Pronunciation | `/api/v1/speaking/pronunciation` | Improve pronunciation skills |
| 💬 Vocabulary Challenge | `/api/v1/speaking/vocabulary-challenge` | Expand your vocabulary |

### 🎤 Presentation Services

| Service | Endpoint | Description |
|---------|----------|-------------|
| 💪 Power Words | `/api/v1/presentation/power-words` | Learn impactful vocabulary |
| 🔗 Flow Chain | `/api/v1/presentation/flow-chain` | Build coherent presentations |
| 🎯 Context Spin | `/api/v1/presentation/context-spin` | Adapt content to contexts |
| 🎓 Precision Drill | `/api/v1/presentation/precision-drill` | Practice precise communication |

### 👔 Adult Learning Services

| Service | Endpoint | Description |
|---------|----------|-------------|
| ⚡ Word Flash | `/api/v1/adult/word-flash` | Quick word recognition drills |
| 🧩 Word Parts Workshop | `/api/v1/adult/word-parts-workshop` | Learn prefixes, suffixes, roots |
| 📝 Sentence Builder | `/api/v1/adult/sentence-builder` | Construct complex sentences |
| 💭 Phrase Maker | `/api/v1/adult/phrase-maker` | Create effective phrases |
| 🎧 Auditory Discrimination | `/api/v1/adult/auditory-discrimination` | Distinguish similar sounds |
| 🗺️ Phoneme Mapping | `/api/v1/adult/phenome-mapping` | Map sounds to letters |

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Application Settings

- **Host**: `0.0.0.0`
- **Port**: `8061`
- **Docs URL**: `/docs`
- **Temp Audio Directory**: `./temp_audio`

---

## 🐳 Docker Support

### Build Image

```bash
docker build -t manifex-ai .
```

### Run Container

```bash
docker run -p 8061:8061 -v $(pwd):/app manifex-ai
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

---

## 📖 API Usage Examples

### Example: Writing Service

```bash
curl -X POST "http://localhost:8061/api/v1/writing/generate-topic" \
  -H "Content-Type: application/json" \
  -d '{
    "difficulty": "intermediate",
    "category": "creative"
  }'
```

### Example: Reading Comprehension

```bash
curl -X POST "http://localhost:8061/api/v1/reading/comprehension/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "beginner",
    "topic": "science"
  }'
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- 🌟 Built with [FastAPI](https://fastapi.tiangolo.com/)
- 🤖 Powered by [OpenAI](https://openai.com/)
- 💙 Made with passion for education

---

## 📞 Support

For support, please open an issue in the GitHub repository.

---

<div align="center">

**Made with ❤️ for language learners worldwide** 🌍

</div>
