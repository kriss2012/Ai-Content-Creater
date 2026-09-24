# ✍️ CollabWrite AI — Intelligent Content Generation & Collaborative Editor

CollabWrite AI is a full-featured generative writing studio and document collaboration workstation powered by Google Gemini and Flask. It bridges the gap between raw LLM drafting and focused editorial workflows, featuring structured long-form generation, point-of-view controls, multi-version document history, and in-editor refinement.

---

## 🚀 Key Features

- **Multi-Format Generation**: Tailored generators for structured blog posts, video production scripts (scene numbers + VFX/VO formatting), and viral social media posts.
- **Tone & Perspective Tuning**: Configurable voice tone (Professional, Conversational, Persuasive, Energetic) and point-of-view (First, Second, or Third person).
- **Persistent Version History**: Rolling revision control with up to 20 historical snapshots per document.
- **In-Editor Copilot**: Live context-aware rewriting, summarization, proofreading, and vocabulary enhancement.
- **Zero-Friction Local Deployment**: Single-file architecture with zero external database dependencies.

---

## 🛠️ Quick Start

### 1. Clone & Set Up Environment

```bash
cd Ai-Content-Creater
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

Copy the configuration template:

```bash
cp .env.example .env
```

Add your free [Google Gemini API key](https://aistudio.google.com/) to `.env`:

```bash
GEMINI_API_KEY=your_actual_gemini_key_here
```

### 3. Launch Platform

```bash
python Ai-Content.py
```

Navigate to `http://127.0.0.1:5000` in your web browser.

---

## 🏛️ Architecture Overview

- **Frontend**: Responsive single-page application built with clean HTML5/CSS3 and native ES6 JavaScript.
- **Backend API**: Python 3 / Flask lightweight microservice handling generation pipelines and persistent JSON storage.
- **Inference Engine**: Google Gemini 2.5 Flash via REST API with structured prompt engineering.

---

## 📋 API Specification

### Content Generation
- **Endpoint**: `POST /api/ai-generator`
- **Request Parameters**:
  - `tool_type` (string): `blog-post`, `video-script`, or `social-media`.
  - `topic` (string): Subject of the document.
  - `tone` (string): Target writing tone.
  - `pov` (string): Point of view perspective.
  - `keywords` (string, optional): Comma-separated focus keywords.
- **Response**: Generated markdown document text.

### In-Editor Copilot
- **Endpoint**: `POST /api/ai-editor`
- **Request Parameters**:
  - `prompt` (string): Editorial instruction (e.g. "Simplify vocabulary").
  - `text` (string): Selected document text.
- **Response**: Refined text replacement.

### Document Persistence
- `GET /api/documents`: List saved documents.
- `POST /api/documents`: Create a new document.
- `GET /api/documents/<doc_id>`: Retrieve specific document with full history.
- `POST /api/documents/<doc_id>`: Save document edits.
- `DELETE /api/documents/<doc_id>`: Remove document.

---

## 📜 License

MIT License.
