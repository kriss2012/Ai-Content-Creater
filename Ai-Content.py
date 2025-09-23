import flask
import requests
import json
import os
import uuid
import time

# --- Core Flask App Setup ---
app = flask.Flask(__name__)

# --- CONFIGURATION ---
# The API key you provided has been added.
GEMINI_API_KEY = "AIzaSyA1L7pLPyFEnkB2y7i2AETbt3KFNQvhUYY" 

# --- Data Persistence ---
DATA_FILE = 'documents.json'

def load_documents():
    """Loads all documents from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_documents(documents):
    """Saves the entire documents dictionary to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(documents, f, indent=4)

# --- HTML & Frontend Code ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CollabWrite AI - Content Creation Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #1e293b; }
        ::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }
        .fade-in { animation: fadeIn 0.3s ease-in-out forwards; }
        @keyframes fadeIn { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }
        .doc-card .delete-btn { opacity: 0; transition: opacity 0.2s ease-in-out; }
        .doc-card:hover .delete-btn { opacity: 1; }
    </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen antialiased">

    <!-- Main Application Container -->
    <div id="app-container">

        <!-- DASHBOARD VIEW -->
        <div id="dashboard-view" class="p-8 fade-in">
            <div class="max-w-7xl mx-auto">
                <header class="flex flex-wrap justify-between items-center mb-10 gap-4">
                    <h1 class="text-3xl font-bold text-white">My Content</h1>
                    <button id="show-ai-generator-btn" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-3 rounded-lg text-sm transition-colors flex items-center gap-2">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3c.3 0 .6.1.8.4l4.9 4.9c.2.2.3.5.3.8v6.8c0 .3-.1.6-.4.8l-4.9 4.9c-.2.2-.5.3-.8.3s-.6-.1-.8-.4l-4.9-4.9c-.2-.2-.3-.5-.3-.8V9c0-.3.1-.6.4-.8l4.9-4.9c.2-.3.5-.4.8-.4z"></path></svg>
                        Create with AI
                    </button>
                </header>
                <div id="documents-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                    <!-- Document cards will be injected here -->
                </div>
            </div>
        </div>

        <!-- EDITOR VIEW (Initially hidden) -->
        <div id="editor-view" class="hidden flex-col min-h-screen">
             <header class="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700 p-3 flex items-center justify-between z-10 sticky top-0">
                <div class="flex items-center gap-4">
                     <button id="back-to-dashboard-btn" class="text-slate-400 hover:text-white">&larr; Dashboard</button>
                    <div><h1 id="doc-title" class="text-lg font-bold text-white"></h1></div>
                </div>
                <button class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-lg text-sm">Share</button>
            </header>
            <main class="flex-grow flex flex-col md:flex-row p-4 gap-4">
                <div class="flex-grow flex flex-col bg-slate-800 rounded-xl border border-slate-700 shadow-lg">
                    <textarea id="doc-content" class="w-full h-full flex-grow bg-transparent text-slate-200 p-4 resize-none focus:outline-none leading-relaxed"></textarea>
                    <footer id="editor-footer" class="p-3 bg-slate-800/50 border-t border-slate-700 text-xs text-slate-400 flex justify-end items-center gap-2"></footer>
                </div>
                <div class="w-full md:w-80 lg:w-96 flex flex-col gap-4">
                    <div id="ai-editing-panel" class="bg-slate-800 rounded-xl border border-slate-700 p-4"></div>
                    <div id="history-panel-container" class="bg-slate-800 rounded-xl border border-slate-700 p-4 flex-grow"></div>
                </div>
            </main>
        </div>
    </div>

    <!-- AI Content Generator Modal -->
    <div id="ai-generator-modal" class="fixed inset-0 z-50 hidden items-center justify-center bg-black/70 backdrop-blur-sm fade-in">
        <div class="bg-slate-800 w-full max-w-3xl p-8 rounded-lg shadow-xl border border-slate-700">
            <h2 class="text-2xl font-bold mb-2">Create New Content with AI</h2>
            <p class="text-slate-400 mb-6">Describe your idea, choose your format, and let the AI build your first draft.</p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Left Column: Inputs -->
                <div>
                    <div class="mb-4">
                        <label for="generator-doc-title" class="block text-sm font-medium text-slate-300 mb-1">Document Title</label>
                        <input type="text" id="generator-doc-title" placeholder="e.g., The Future of Remote Work" class="w-full bg-slate-700 p-2 rounded border border-slate-600">
                    </div>
                    <div class="mb-4">
                        <label for="generator-topic" class="block text-sm font-medium text-slate-300 mb-1">Topic / Idea</label>
                        <textarea id="generator-topic" rows="4" placeholder="e.g., A blog post exploring the pros and cons of a fully remote workforce, including productivity and company culture." class="w-full bg-slate-700 p-2 rounded border border-slate-600"></textarea>
                    </div>
                     <div class="mb-4">
                        <label for="generator-keywords" class="block text-sm font-medium text-slate-300 mb-1">Keywords (optional)</label>
                        <input type="text" id="generator-keywords" placeholder="e.g., productivity, collaboration, async" class="w-full bg-slate-700 p-2 rounded border border-slate-600">
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                           <label for="generator-tone" class="block text-sm font-medium text-slate-300 mb-1">Tone</label>
                           <select id="generator-tone" class="w-full bg-slate-700 p-2 rounded border border-slate-600"><option>Professional</option><option>Casual</option><option>Witty</option><option>Formal</option><option>Persuasive</option></select>
                        </div>
                        <div>
                           <label for="generator-pov" class="block text-sm font-medium text-slate-300 mb-1">Point of View</label>
                           <select id="generator-pov" class="w-full bg-slate-700 p-2 rounded border border-slate-600"><option>Third Person</option><option>First Person</option></select>
                        </div>
                    </div>
                </div>
                <!-- Right Column: Tools & Output -->
                <div>
                     <label class="block text-sm font-medium text-slate-300 mb-1">Content Type</label>
                     <div class="flex gap-2 mb-4" id="generator-tool-buttons">
                        <button class="generator-tool-btn flex-1 bg-slate-700 hover:bg-slate-600 p-3 rounded-lg" data-type="blog-post">📝 Blog Post</button>
                        <button class="generator-tool-btn flex-1 bg-slate-700 hover:bg-slate-600 p-3 rounded-lg" data-type="video-script">🎬 Video Script</button>
                        <button class="generator-tool-btn flex-1 bg-slate-700 hover:bg-slate-600 p-3 rounded-lg" data-type="social-media">📱 Social Post</button>
                    </div>
                    <div id="generator-output" class="h-64 bg-slate-900 rounded-lg p-3 text-sm flex items-center justify-center">
                        <span class="text-slate-500 text-center">Select a tool to begin.</span>
                    </div>
                </div>
            </div>
            <div class="flex justify-end gap-4 mt-8">
                <button id="cancel-generator-btn" class="bg-slate-600 hover:bg-slate-700 text-white py-2 px-4 rounded">Cancel</button>
                <button id="create-doc-from-ai-btn" class="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded" disabled>Create Document</button>
            </div>
        </div>
    </div>

<script>
document.addEventListener('DOMContentLoaded', () => {
    let currentDocId = null, documents = {}, editorState = { history: [], saveTimeout: null }, generatedAiContent = '';
    const dashboardView = document.getElementById('dashboard-view'), editorView = document.getElementById('editor-view');
    const documentsGrid = document.getElementById('documents-grid'), docTitleEl = document.getElementById('doc-title');
    const docContentEl = document.getElementById('doc-content'), aiGeneratorModal = document.getElementById('ai-generator-modal');

    async function apiCall(endpoint, method = 'GET', body = null) {
        try {
            const options = { method, headers: { 'Content-Type': 'application/json' } };
            if (body) options.body = JSON.stringify(body);
            const response = await fetch(endpoint, options);
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'An unknown error occurred');
            return data;
        } catch (err) {
            console.error('API Call Failed:', err);
            alert(`Error: ${err.message}`);
            throw err;
        }
    }

    function switchView(view) {
        if (view === 'editor') {
            dashboardView.style.display = 'none';
            editorView.classList.remove('hidden');
            editorView.classList.add('flex', 'fade-in');
        } else {
            editorView.classList.add('hidden');
            editorView.classList.remove('flex', 'fade-in');
            dashboardView.style.display = 'block';
            loadDashboard();
        }
    }

    async function loadDashboard() {
        try {
            documents = await apiCall('/api/documents');
            documentsGrid.innerHTML = '';
            const sortedDocs = Object.entries(documents).sort((a, b) => b[1].modified_at - a[1].modified_at);
            if (sortedDocs.length === 0) {
                documentsGrid.innerHTML = `<p class="text-slate-500 col-span-full text-center">No documents yet. Create one with AI!</p>`;
            } else {
                sortedDocs.forEach(([docId, doc]) => {
                    const card = document.createElement('div');
                    card.className = 'doc-card bg-slate-800 p-4 rounded-lg border border-slate-700 group relative';
                    card.innerHTML = `
                        <div class="cursor-pointer" data-doc-id="${docId}">
                            <h3 class="font-bold text-white truncate">${doc.title}</h3>
                            <p class="text-xs text-slate-400 mt-2">Modified: ${new Date(doc.modified_at * 1000).toLocaleString()}</p>
                        </div>
                        <button class="delete-btn absolute top-3 right-3 text-slate-500 hover:text-red-400" data-doc-id="${docId}">
                           <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/><path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/></svg>
                        </button>`;
                    documentsGrid.appendChild(card);
                });
            }
        } catch (e) { console.error('Failed to load dashboard:', e); }
    }

    documentsGrid.addEventListener('click', e => {
        const docCard = e.target.closest('[data-doc-id]');
        if (!docCard) return;
        
        const docId = docCard.dataset.docId;
        if(e.target.closest('.delete-btn')) {
            if(confirm(`Are you sure you want to delete "${documents[docId].title}"?`)) {
                apiCall(`/api/documents/${docId}`, 'DELETE').then(loadDashboard);
            }
        } else if (e.target.closest('.cursor-pointer')) {
            openEditor(docId);
        }
    });

    async function openEditor(docId) {
        try {
            const doc = await apiCall(`/api/documents/${docId}`);
            currentDocId = docId;
            docTitleEl.textContent = doc.title;
            docContentEl.value = doc.content;
            editorState.history = doc.history || [];
            renderEditorPanels();
            switchView('editor');
        } catch (e) { console.error('Failed to open editor:', e); }
    }

    function renderEditorPanels() {
        const aiPanel = document.getElementById('ai-editing-panel');
        aiPanel.innerHTML = `
            <h3 class="text-lg font-bold text-white mb-4">AI Editing Tools</h3>
            <p class="text-sm text-slate-400 mb-4">Select text in the editor to enable tools.</p>
            <div id="ai-editing-tools" class="grid grid-cols-2 gap-2">
                <button class="ai-edit-btn" data-prompt="Improve the writing of the following text:">Improve</button>
                <button class="ai-edit-btn" data-prompt="Summarize the following text:">Summarize</button>
                <button class="ai-edit-btn" data-prompt="Rewrite the following text in a professional tone:">Make Professional</button>
                <button class="ai-edit-btn" data-prompt="Rewrite the following text in a casual tone:">Make Casual</button>
            </div>`;
        document.getElementById('history-panel-container').innerHTML = `
            <h3 class="text-lg font-bold text-white mb-4">Version History</h3>
            <div id="history-panel" class="space-y-3 overflow-y-auto h-48 pr-2"></div>`;
        renderHistory();
        
        document.querySelectorAll('.ai-edit-btn').forEach(btn => {
            btn.disabled = true;
            btn.classList.add('opacity-50', 'cursor-not-allowed');
        });
    }

    function renderHistory() {
        const panel = document.getElementById('history-panel');
        if (!panel || !editorState.history) return;
        panel.innerHTML = editorState.history.length > 0 ? '' : '<p class="text-sm text-slate-500">No saves yet.</p>';
        [...editorState.history].reverse().forEach(item => {
             const div = document.createElement('div');
             div.className = 'bg-slate-700/50 p-2 rounded-lg';
             div.innerHTML = `<p class="text-xs text-slate-300 truncate">${item.content}</p>
                            <p class="text-xs text-slate-500 mt-1">${new Date(item.timestamp * 1000).toLocaleTimeString()}</p>`;
             panel.appendChild(div);
        });
    }

    docContentEl.addEventListener('selectionchange', () => {
        const selection = docContentEl.value.substring(docContentEl.selectionStart, docContentEl.selectionEnd);
        document.querySelectorAll('.ai-edit-btn').forEach(btn => {
            btn.disabled = !selection;
            btn.classList.toggle('opacity-50', !selection);
            btn.classList.toggle('cursor-not-allowed', !selection);
        });
    });

    document.getElementById('editor-view').addEventListener('click', async e => {
        if (e.target.classList.contains('ai-edit-btn')) {
            const selection = docContentEl.value.substring(docContentEl.selectionStart, docContentEl.selectionEnd);
            if (!selection) return;

            const prompt = e.target.dataset.prompt;
            e.target.textContent = '...';
            try {
                const result = await apiCall('/api/ai-editor', 'POST', { prompt, text: selection });
                const newText = docContentEl.value.substring(0, docContentEl.selectionStart) + result.content + docContentEl.value.substring(docContentEl.selectionEnd);
                docContentEl.value = newText;
                saveCurrentDoc();
            } finally {
                e.target.textContent = e.target.dataset.prompt.split(' ')[0]; // Reset button text
            }
        }
    });
    
    async function saveCurrentDoc() {
        if (!currentDocId) return;
        try {
            const updatedDoc = await apiCall(`/api/documents/${currentDocId}`, 'POST', { content: docContentEl.value });
            editorState.history = updatedDoc.history;
            renderHistory();
        } catch (e) { console.error('Save failed:', e); }
    }

    document.getElementById('back-to-dashboard-btn').addEventListener('click', () => switchView('dashboard'));
    docContentEl.addEventListener('input', () => {
        clearTimeout(editorState.saveTimeout);
        editorState.saveTimeout = setTimeout(saveCurrentDoc, 1500);
    });

    const generatorModal = {
        el: document.getElementById('ai-generator-modal'), title: document.getElementById('generator-doc-title'),
        topic: document.getElementById('generator-topic'), output: document.getElementById('generator-output'),
        createBtn: document.getElementById('create-doc-from-ai-btn'), keywords: document.getElementById('generator-keywords'),
        tone: document.getElementById('generator-tone'), pov: document.getElementById('generator-pov')
    };
    
    document.getElementById('show-ai-generator-btn').addEventListener('click', () => generatorModal.el.classList.remove('hidden'));
    document.getElementById('cancel-generator-btn').addEventListener('click', () => generatorModal.el.classList.add('hidden'));

    document.getElementById('generator-tool-buttons').addEventListener('click', async (e) => {
        if (e.target.classList.contains('generator-tool-btn')) {
            const toolType = e.target.dataset.type, topic = generatorModal.topic.value.trim();
            if (!topic) { return alert('Please provide a topic.'); }

            generatorModal.output.innerHTML = '<span class="text-slate-400">🤖 AI is crafting your content...</span>';
            generatorModal.createBtn.disabled = true;
            
            try {
                const payload = {
                    tool_type: toolType, topic, keywords: generatorModal.keywords.value,
                    tone: generatorModal.tone.value, pov: generatorModal.pov.value
                };
                const result = await apiCall('/api/ai-generator', 'POST', payload);
                generatedAiContent = result.content;
                generatorModal.output.innerHTML = `<textarea class="w-full h-full bg-transparent text-slate-300 resize-none" readonly>${generatedAiContent}</textarea>`;
                generatorModal.createBtn.disabled = false;
            } catch (err) {
                 generatorModal.output.innerHTML = `<span class="text-red-400">Error: ${err.message}</span>`;
            }
        }
    });

    generatorModal.createBtn.addEventListener('click', async () => {
        const title = generatorModal.title.value.trim();
        if (!title) { return alert('Please provide a document title.'); }
        
        try {
            const newDoc = await apiCall('/api/documents', 'POST', { title, content: generatedAiContent });
            generatorModal.el.classList.add('hidden');
            openEditor(newDoc.doc_id);
        } catch (err) { /* apiCall already shows alert */ }
    });

    switchView('dashboard');
});
</script>
</body>
</html>
"""

# --- Backend API Endpoints ---
@app.route('/api/ai-generator', methods=['POST'])
def handle_ai_generator():
    if not GEMINI_API_KEY or "YOUR_API_KEY" in GEMINI_API_KEY:
        return flask.jsonify({"error": "API key not configured."}), 500

    data = flask.request.get_json()
    tool_type = data.get('tool_type')
    topic = data.get('topic')
    tone = data.get('tone', 'professional')
    pov = data.get('pov', 'third person')
    keywords = data.get('keywords', '')

    if not tool_type or not topic:
        return flask.jsonify({"error": "Missing tool_type or topic"}), 400

    base_prompts = {
        "blog-post": f"Generate a well-structured blog post about '{topic}'. Include a catchy title, an introduction, several main points with headings, and a conclusion.",
        "video-script": f"Create a short video script for a YouTube or social media video about '{topic}'. Structure it with scene numbers, visual descriptions (VFX), and narration/dialogue (VO).",
        "social-media": f"Write an engaging and concise social media post for platforms like LinkedIn or Twitter about '{topic}'. Include 2-3 relevant hashtags."
    }
    
    prompt = base_prompts.get(tool_type)
    if not prompt: return flask.jsonify({"error": "Invalid tool_type"}), 400

    # Enhance the prompt with more options
    prompt += f" The tone should be {tone}. Write it in the {pov}."
    if keywords:
        prompt += f" Please include the following keywords: {keywords}."
    
    try:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
        response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        result = response.json()
        content = result["candidates"][0]["content"]["parts"][0]["text"]
        return flask.jsonify({"content": content.strip()})
    except requests.exceptions.HTTPError as e:
        return flask.jsonify({"error": f"AI service error: {e.response.text}"}), e.response.status_code
    except Exception as e:
        return flask.jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/api/ai-editor', methods=['POST'])
def handle_ai_editor():
    """Handles in-editor AI requests like 'improve' or 'summarize'."""
    if not GEMINI_API_KEY or "YOUR_API_KEY" in GEMINI_API_KEY:
        return flask.jsonify({"error": "API key not configured."}), 500
    
    data = flask.request.get_json()
    prompt = data.get('prompt')
    text = data.get('text')
    if not prompt or not text:
        return flask.jsonify({"error": "Missing prompt or text"}), 400

    full_prompt = f"{prompt}\n\n---\n{text}\n---"
    
    try:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"role": "user", "parts": [{"text": full_prompt}]}]}
        response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        result = response.json()
        content = result["candidates"][0]["content"]["parts"][0]["text"]
        return flask.jsonify({"content": content.strip()})
    except Exception as e:
        return flask.jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    docs = load_documents()
    doc_list = {doc_id: {"title": data["title"], "modified_at": data["modified_at"]} for doc_id, data in docs.items()}
    return flask.jsonify(doc_list)

@app.route('/api/documents', methods=['POST'])
def create_document():
    data = flask.request.get_json()
    title = data.get('title')
    if not title: return flask.jsonify({"error": "Title is required"}), 400
    
    doc_id = str(uuid.uuid4())
    timestamp = time.time()
    new_doc = { "title": title, "content": data.get('content', ''), "created_at": timestamp, "modified_at": timestamp, "history": [{"content": data.get('content', ''), "timestamp": timestamp}] }
    
    documents = load_documents()
    documents[doc_id] = new_doc
    save_documents(documents)
    return flask.jsonify({"message": "Document created", "doc_id": doc_id}), 201

@app.route('/api/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    documents = load_documents()
    if doc_id in documents:
        del documents[doc_id]
        save_documents(documents)
        return flask.jsonify({"message": "Document deleted"}), 200
    return flask.jsonify({"error": "Document not found"}), 404

@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    doc = load_documents().get(doc_id)
    if not doc: return flask.jsonify({"error": "Document not found"}), 404
    return flask.jsonify(doc)

@app.route('/api/documents/<doc_id>', methods=['POST'])
def update_document(doc_id):
    documents = load_documents()
    if doc_id not in documents: return flask.jsonify({"error": "Document not found"}), 404
    
    data = flask.request.get_json()
    content = data.get('content')
    timestamp = time.time()
    
    documents[doc_id]['content'] = content
    documents[doc_id]['modified_at'] = timestamp
    
    if not documents[doc_id].get('history') or documents[doc_id]['history'][-1]['content'] != content:
        documents[doc_id].setdefault('history', []).append({"content": content, "timestamp": timestamp})

    if len(documents[doc_id]['history']) > 20: documents[doc_id]['history'].pop(0)

    save_documents(documents)
    return flask.jsonify(documents[doc_id])

@app.route('/')
def index():
    return HTML_TEMPLATE

if __name__ == '__main__':
    app.run(debug=True)

