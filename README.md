# SMARTTOEFL AI

SMARTTOEFL AI adalah aplikasi latihan TOEFL berbasis AI yang berjalan secara lokal. Aplikasi ini memakai FastAPI sebagai backend, Vue 3 sebagai frontend, SQLite untuk menyimpan riwayat latihan, Chroma vector database untuk RAG, serta mendukung dua penyedia LLM: OpenAI API (`gpt-4o-mini`) dan Ollama lokal.

Tujuan utama project ini adalah membantu user berlatih soal TOEFL ITP yang akademik dan realistis (Grammar, Vocabulary, dan Reading), menjawab soal, mendapatkan evaluasi bilingual Inggris/Indonesia, serta melihat riwayat, analitik, dan estimasi skor TOEFL ITP.

## Section dan Level

Section yang tersedia:

- **Grammar** — soal Structure & Written Expression (subject-verb agreement, tense, inversion, subjunctive, reduced clause, dll).
- **Vocabulary** — soal closest meaning dari kata akademik di dalam kalimat.
- **Reading** — passage akademik diikuti beberapa pertanyaan (main idea, detail, vocabulary in context, inference, reference).

Level disesuaikan dengan estimasi TOEFL ITP:

| Level        | Estimasi TOEFL ITP |
| ------------ | ------------------ |
| Easy         | 400–450            |
| Intermediate | 450–520            |
| Advanced     | 550–650            |

## Mode Soal

- **Dataset** — soal diambil dari bank soal JSON lokal (`backend/app/dataset/questions`).
- **AI Generate** — soal baru dibuat oleh LLM (OpenAI atau Ollama) sesuai category, difficulty, dan pola TOEFL.
- **Hybrid** — soal dataset dijadikan acuan, lalu divariasikan oleh LLM.

Jika LLM gagal atau tidak aktif, sistem otomatis fallback ke bank soal lokal sehingga tidak pernah crash.

## Fitur Utama

- Generate soal TOEFL ITP-style berdasarkan category, difficulty, dan mode.
- Bank soal lokal: 10 soal Grammar/Vocabulary per level dan 3 passage Reading per level.
- Reading menampilkan passage lalu beberapa pertanyaan bertipe variatif.
- Evaluasi jawaban dengan feedback bilingual Inggris/Indonesia.
- Menampilkan correct answer, explanation, translation, why wrong, grammar tip, TOEFL tip, topic, dan rekomendasi kelemahan.
- Menyimpan riwayat latihan ke SQLite.
- Analytics: akurasi per category, per difficulty, weakness topics, dan estimasi skor TOEFL ITP.
- AI Tutor: deteksi kelemahan dari history dan rekomendasi belajar.
- Mendukung OpenAI API maupun Ollama lokal lewat konfigurasi `.env`.

## Teknologi

Backend:

- FastAPI
- SQLAlchemy
- SQLite
- LangChain
- ChromaDB
- HuggingFace sentence-transformers embedding
- OpenAI API (`gpt-4o-mini`)
- Ollama (LLM lokal)
- python-dotenv
- pypdf

Frontend:

- Vue 3
- Vite
- Pinia
- Vue Router
- Axios
- Tailwind CSS
- Chart.js
- Lucide icons
- Lottie animation

## Struktur Project

```text
.
+-- backend/
|   +-- app/
|   |   +-- api/routes/
|   |   |   +-- question.py          # Generate soal dan evaluasi jawaban
|   |   |   +-- history.py           # Riwayat latihan
|   |   |   +-- analytics.py         # Statistik latihan
|   |   |   +-- recommendation.py    # Rekomendasi belajar
|   |   |   +-- weakness.py          # Analisis kelemahan
|   |   +-- core/
|   |   |   +-- database.py          # Konfigurasi SQLite
|   |   +-- dataset/                 # Dataset TOEFL dan vocabulary
|   |   +-- models/
|   |   |   +-- history.py           # Model tabel practice_history
|   |   +-- services/
|   |   |   +-- rag_service.py       # Load dataset, build vectorstore, retrieve context
|   |   |   +-- llm_service.py       # Prompt dan komunikasi ke Ollama
|   |   +-- main.py                  # Entry point FastAPI
|   +-- build_rag.py                 # Script build ulang Chroma vectorstore
|   +-- transcribe_audio.py          # Script transkripsi audio listening
|   +-- requirements.txt
+-- frontend/
    +-- ui/
        +-- src/
        |   +-- pages/
        |   |   +-- Practice.vue     # Halaman utama generate dan submit jawaban
        |   |   +-- Dashboard.vue    # Dashboard progress
        |   |   +-- History.vue      # Riwayat latihan
        |   |   +-- Analytics.vue    # Analitik tambahan
        |   +-- components/
        |   |   +-- QuestionCard.vue # Tampilan soal dan opsi jawaban
        |   +-- services/
        |   |   +-- api.js           # Axios config
        |   |   +-- questionService.js
        |   +-- store/
        |   |   +-- useToeflStore.js # State management Pinia
        |   +-- router/
        |   |   +-- index.js
        +-- package.json
```

## Dataset

Dataset utama berada di:

```text
backend/app/dataset
```

Dataset dibagi menjadi dua fungsi:

1. **Knowledge untuk RAG / AI Tutor** — materi penjelasan: `grammar/`, `vocabulary/`, `reading/`, `overview/`.
2. **Bank soal untuk Practice** — file JSON di `questions/`.

Struktur dataset:

```text
backend/app/dataset/
+-- grammar/                 # knowledge RAG
+-- reading/                 # knowledge RAG
+-- vocabulary/              # knowledge RAG
+-- overview/                # knowledge RAG
+-- questions/               # bank soal Practice (JSON)
|   +-- grammar_easy.json
|   +-- grammar_intermediate.json
|   +-- grammar_advanced.json
|   +-- vocabulary_easy.json
|   +-- vocabulary_intermediate.json
|   +-- vocabulary_advanced.json
|   +-- reading_easy.json
|   +-- reading_intermediate.json
|   +-- reading_advanced.json
+-- listening/
|   +-- audio/
|   +-- transcript/
+-- speaking/
    +-- prompts/
    +-- rubric/
```

Format JSON Grammar/Vocabulary:

```json
{
  "id": "grammar_adv_001",
  "section": "grammar",
  "difficulty": "advanced",
  "estimated_toefl_range": "550-650",
  "topic": "inversion",
  "question": "Not until the early twentieth century ____ to improve the living conditions of workers.",
  "options": { "A": "did governments begin", "B": "governments began", "C": "began governments", "D": "had governments begun" },
  "answer": "A",
  "explanation": "After 'Not until', the sentence requires inversion: auxiliary + subject + main verb."
}
```

Format JSON Reading (passage + beberapa pertanyaan):

```json
{
  "id": "reading_adv_001",
  "section": "reading",
  "difficulty": "advanced",
  "estimated_toefl_range": "550-650",
  "topic": "technology and employment",
  "passage": "Although technological innovation has generally improved productivity...",
  "questions": [
    {
      "id": "reading_adv_001_q1",
      "type": "main_idea",
      "question": "What is the main idea of the passage?",
      "options": { "A": "...", "B": "...", "C": "...", "D": "..." },
      "answer": "C",
      "explanation": "..."
    }
  ]
}
```

Dataset yang dipakai langsung oleh RAG hanya file:

```text
.txt
.pdf
```

File audio `.mp3` tidak langsung dibaca RAG. Audio perlu ditranskrip dulu menjadi `.txt` lewat `backend/transcribe_audio.py`.

### Sumber Dataset

Sumber utama project ini adalah official TOEFL/ETS resources, seperti:

- TOEFL iBT lesson plans.
- TOEFL iBT test overview.
- TOEFL teacher FAQ.
- TOEFL practice test.
- TOEFL listening audio resources.

Untuk kategori Vocabulary, ETS tidak menyediakan satu wordlist resmi TOEFL yang berdiri sendiri. Karena itu dataset vocabulary diperkuat dengan academic vocabulary resources, seperti Academic Vocabulary List/Core Academic Words. File vocabulary yang sudah masuk:

```text
backend/app/dataset/vocabulary/acadCore.txt
backend/app/dataset/vocabulary/general-core.pdf
```

File `acadCore.xlsx` tetap disimpan sebagai sumber asli, tetapi RAG memakai versi `.txt` karena loader saat ini hanya mendukung `.txt` dan `.pdf`.

## RAG dan Vectorstore

RAG diproses oleh:

```text
backend/app/services/rag_service.py
```

### Bagaimana RAG dipakai saat runtime

RAG aktif saat `USE_RAG=true` dan provider LLM aktif (`openai`/`ollama`):

- **Generate soal AI/Hybrid** — `get_context()` mengambil materi TOEFL relevan, lalu disuntik ke prompt sebagai referensi gaya/topik akademik.
- **AI Tutor (penjelasan jawaban)** — saat user submit, materi terkait diambil dari vectorstore agar penjelasan lebih akurat dan berbasis materi resmi.
- Embedding model dan vectorstore di-cache (singleton) dan di-*warm up* di background saat startup, sehingga query berikutnya cepat (sub-detik).
- Field `rag_used` muncul di response API dan ditampilkan sebagai badge **RAG** di kartu soal.
- Cek status RAG: `GET /api/rag/status` → `{ enabled, ready, top_k, provider }`.
- Mode `dataset` tidak memakai RAG (soal murni dari JSON).

### Build index

Alurnya:

1. `build_vectorstore()` membaca semua file `.txt` dan `.pdf` dari `app/dataset`.
2. PDF dibaca dengan `pypdf`.
3. TXT dibaca dengan `TextLoader`.
4. Dokumen dipotong menjadi chunk.
5. Embedding dibuat dengan model `sentence-transformers/all-MiniLM-L6-v2`.
6. Chroma menyimpan hasil index ke `app/vectorstore`.

Build ulang vectorstore:

```powershell
cd backend
venv\Scripts\activate
Remove-Item -Recurse -Force app\vectorstore
python build_rag.py
```

Vectorstore perlu di-build ulang jika:

- Dataset baru ditambahkan.
- Dataset lama dihapus.
- File dataset diubah.
- Folder `app/vectorstore` terhapus atau stale.

## Alur Generate Question

Alur saat user klik tombol Generate Question:

```text
Practice.vue
-> useToeflStore.js
-> questionService.js
-> api.js
-> GET /api/questions/generate?category=&difficulty=&mode=
-> backend/app/api/routes/question.py
-> llm_service.generate_question(category, difficulty, mode)
   - mode dataset -> question_bank (JSON lokal)
   - mode ai      -> OpenAI / Ollama, fallback ke dataset
   - mode hybrid  -> dataset jadi seed, divariasikan LLM
-> response { success, source, data }
-> currentQuestion di Pinia
-> QuestionCard.vue / ReadingCard.vue menampilkan soal
```

Detail proses backend:

1. Frontend mengirim `category`, `difficulty`, dan `mode`.
2. `llm_service.generate_question` memilih sumber soal sesuai `mode`.
3. Untuk mode `ai`/`hybrid`, prompt per-category dibangun (Grammar/Vocabulary/Reading) sesuai pola TOEFL ITP dan estimasi skor.
4. Jika `USE_RAG=true`, `rag_service.get_context()` mengambil materi TOEFL relevan dari vectorstore dan disuntikkan ke prompt (grounding). Field `rag_used` menandai apakah RAG dipakai.
5. Provider LLM (OpenAI atau Ollama) menghasilkan JSON, lalu divalidasi.
6. Jika LLM gagal/tidak aktif, backend fallback ke bank soal JSON lokal.
7. Response berisi `source` (`dataset`/`openai`/`ollama`), `rag_used`, dan `data` soal.
8. Frontend menampilkan QuestionCard (Grammar/Vocabulary) atau ReadingCard (Reading) lengkap dengan badge.

## Alur Submit dan Evaluasi Jawaban

Alur saat user memilih jawaban dan klik Submit Answer:

```text
QuestionCard.vue
-> emit submit-answer
-> Practice.vue membuat payload evaluasi
-> useToeflStore.js
-> questionService.js
-> POST /evaluate-answer
-> question.py
-> ask_llm() di llm_service.py
-> simpan PracticeHistory ke SQLite
-> response evaluasi
-> Practice.vue menampilkan feedback
-> fetchHistory()
-> fetchDashboard()
```

Backend menentukan benar atau salah secara deterministik:

```text
user_answer == correct_answer
```

LLM dipakai untuk membuat penjelasan, bukan untuk menentukan benar/salah.

Output evaluasi mencakup:

- `is_correct`
- `correct_answer`
- `translation`
- `explanation`
- `explanation_id`
- `why_wrong`
- `why_wrong_id`
- `grammar_tip`
- `grammar_tip_id`
- `toefl_tip`
- `toefl_tip_id`

## Database

Database memakai SQLite:

```text
backend/smarttoefl.db
```

Konfigurasi database:

```text
backend/app/core/database.py
```

Model history:

```text
backend/app/models/history.py
```

Tabel utama:

```text
practice_history
```

Data yang disimpan:

- Category
- Difficulty
- Question
- User answer
- Correct answer
- Is correct
- Analysis
- Grammar tip
- Improvement
- Weakness detected
- Created at

## Endpoint Backend

```text
GET    /
GET    /api/questions/generate
POST   /api/questions/check-answer
GET    /api/rag/status
POST   /generate-question        (legacy)
POST   /evaluate-answer          (legacy)
GET    /history
DELETE /history
GET    /analytics
GET    /recommendation
GET    /weakness-analysis
```

Keterangan:

- `GET /` untuk health check backend.
- `GET /api/questions/generate?category=&difficulty=&mode=` untuk membuat soal. `mode` = `dataset` / `ai` / `hybrid`.
- `POST /api/questions/check-answer` untuk mengevaluasi satu jawaban, menyimpan history, dan memberi rekomendasi kelemahan.
- `POST /generate-question` dan `POST /evaluate-answer` adalah endpoint lama yang tetap dipertahankan agar kompatibel.
- `GET /history` untuk mengambil riwayat latihan.
- `DELETE /history` untuk menghapus riwayat latihan.
- `GET /analytics` untuk statistik latihan (akurasi per category/difficulty, weakness topics, estimasi skor TOEFL).
- `GET /recommendation` untuk rekomendasi belajar.
- `GET /weakness-analysis` untuk ringkasan kelemahan.

Contoh response `GET /api/questions/generate` (Grammar/Vocabulary):

```json
{
  "success": true,
  "source": "dataset",
  "data": {
    "id": "grammar_adv_001",
    "section": "grammar",
    "difficulty": "advanced",
    "estimated_toefl_range": "550-650",
    "topic": "inversion",
    "question": "...",
    "options": { "A": "...", "B": "...", "C": "...", "D": "..." },
    "answer": "A",
    "explanation": "..."
  }
}
```

Untuk Reading, `data` berisi `passage` dan array `questions`. Field `source` bernilai `dataset`, `openai`, atau `ollama`.

Contoh response `POST /api/questions/check-answer`:

```json
{
  "is_correct": false,
  "correct_answer": "A",
  "correct_answer_text": "A. did governments begin",
  "explanation": "...",
  "weakness_detected": "inversion",
  "recommendation": "Practice inversion after negative adverbials such as Not until, Never, Rarely, and Seldom."
}
```

## Konfigurasi LLM Provider (.env)

Salin `backend/.env.example` menjadi `backend/.env`, lalu pilih provider lewat `LLM_PROVIDER`.

Menggunakan OpenAI API (stabil, kualitas soal lebih baik):

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
```

Menggunakan Ollama lokal (gratis, offline, tanpa API key):

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b
```

Tanpa LLM (selalu pakai bank soal lokal):

```env
LLM_PROVIDER=dataset
```

Grounding RAG (default aktif) dapat diatur lewat:

```env
USE_RAG=true
RAG_TOP_K=3
```

Catatan:

- `LLM_PROVIDER=openai` cocok untuk generate soal TOEFL yang lebih stabil.
- `LLM_PROVIDER=ollama` tetap bisa dipakai sebagai alternatif gratis.
- Jika provider error atau mode `dataset`, sistem fallback ke bank soal JSON lokal.
- `USE_RAG=true` membuat soal AI (mode `ai`/`hybrid`) dan penjelasan AI Tutor di-grounding dengan materi TOEFL dari vectorstore. Set `false` untuk mematikan RAG.
- File `.env` sudah masuk `.gitignore`, jadi API key tidak ikut ter-commit.

## Cara Menjalankan Backend

Masuk ke folder backend:

```powershell
cd backend
```

Buat dan aktifkan virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

Install dependency:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Siapkan file `.env` (pilih provider LLM):

```powershell
Copy-Item .env.example .env
# lalu edit .env sesuai provider (openai / ollama / dataset)
```

Install model Ollama (hanya jika `LLM_PROVIDER=ollama`):

```powershell
ollama pull qwen2.5:1.5b
ollama list
```

Build RAG vectorstore (untuk grounding soal AI & AI Tutor; cukup sekali, ulangi hanya jika dataset berubah):

```powershell
python build_rag.py
```

Jalankan backend:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Cek backend:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{"message":"SMARTTOEFL AI Backend Running"}
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Cara Menjalankan Frontend

Masuk ke folder frontend:

```powershell
cd frontend\ui
```

Install dependency:

```powershell
npm install
```

Jalankan development server:

```powershell
npm run dev
```

Buka URL Vite, biasanya:

```text
http://127.0.0.1:5173/
```

Jika menggunakan file `.env`, pastikan:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Screenshot

Letakkan screenshot di folder `docs/screenshots/` lalu tampilkan di sini:

```text
docs/screenshots/practice.png    # Halaman Practice (soal + mode + badge)
docs/screenshots/dashboard.png   # Dashboard progress + estimasi TOEFL
docs/screenshots/history.png     # Riwayat latihan
docs/screenshots/analytics.png   # Analytics (akurasi per category/difficulty)
```

Contoh penulisan di README:

```markdown
![Practice](docs/screenshots/practice.png)
![Dashboard](docs/screenshots/dashboard.png)
![History](docs/screenshots/history.png)
![Analytics](docs/screenshots/analytics.png)
```

## Workflow Penggunaan

1. Atur `backend/.env` (pilih `openai`, `ollama`, atau `dataset`).
2. Jalankan backend FastAPI.
3. Jalankan frontend Vue.
4. Buka halaman web.
5. Pilih category: Grammar, Vocabulary, atau Reading.
6. Pilih difficulty: Easy, Intermediate, atau Advanced.
7. Pilih mode: Dataset, AI Generate, atau Hybrid.
8. Klik Generate Question.
9. Jawab soal (untuk Reading, jawab semua pertanyaan di bawah passage).
10. Klik Submit, lihat hasil evaluasi, penjelasan, topic, dan rekomendasi.
11. Buka Dashboard/Analytics untuk melihat progress dan estimasi skor TOEFL.

## Catatan Kategori

Status kategori saat ini:

```text
Grammar    = aktif, dataset tersedia
Vocabulary = aktif, dataset tersedia
Reading    = aktif, dataset tersedia
Listening  = dataset audio ada, belum aktif di UI utama
Speaking   = dataset prompt/rubric ada, belum aktif di UI utama
```

Listening belum aktif karena audio `.mp3` harus ditranskrip dulu ke `.txt` agar bisa masuk RAG.

Alur listening jika ingin diaktifkan:

```text
MP3 audio
-> transcribe_audio.py
-> transcript .txt
-> build_rag.py
-> Chroma vectorstore
-> kategori Listening ditambahkan di UI
```

## Testing dan Validasi

Compile backend:

```powershell
cd backend
venv\Scripts\activate
python -m compileall app
```

Build frontend:

```powershell
cd frontend\ui
npm run build
```

Smoke test backend:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/
```

Test generate question:

```powershell
$body = @{ category='Vocabulary'; difficulty='Easy' } | ConvertTo-Json
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/generate-question `
  -Method Post `
  -Body $body `
  -ContentType 'application/json' `
  -TimeoutSec 180
```

## Troubleshooting

### Backend tidak bisa jalan karena port 8000 dipakai

Error:

```text
address 127.0.0.1:8000 already in use
```

Artinya backend sudah berjalan di port tersebut. Tutup proses lama atau gunakan port lain.

### Generate Question terasa lama atau mental

Penyebab umum:

- Ollama belum berjalan.
- Model `qwen2.5:1.5b` belum di-pull.
- Backend dijalankan lebih dari satu kali di port yang sama.
- LLM lokal sedang cold start atau sibuk.
- Vectorstore belum di-build.

Cek Ollama:

```powershell
ollama list
ollama pull qwen2.5:1.5b
```

Cek backend:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/
```

### Vectorstore kosong atau dataset tidak terbaca

Rebuild vectorstore:

```powershell
cd backend
venv\Scripts\activate
Remove-Item -Recurse -Force app\vectorstore
python build_rag.py
```

### File Excel tidak masuk RAG

RAG saat ini hanya membaca `.txt` dan `.pdf`. Jika dataset berbentuk `.xlsx`, ubah atau ekspor dulu ke `.txt`.

Contoh:

```text
acadCore.xlsx -> acadCore.txt
```

### Frontend tidak connect ke backend

Pastikan backend berjalan di:

```text
http://127.0.0.1:8000
```

Pastikan `.env` frontend:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Restart frontend setelah mengubah `.env`.

## File Generated Lokal

File/folder berikut dibuat lokal dan tidak wajib masuk repository:

```text
backend/venv/
backend/smarttoefl.db
backend/app/vectorstore/
frontend/ui/node_modules/
frontend/ui/dist/
.env
*.log
__pycache__/
```

## Ringkasan Alur Sistem

```text
User
-> Frontend Vue
-> Pinia Store
-> Axios Service
-> FastAPI Backend
-> RAG Context dari Chroma
-> Ollama LLM
-> JSON Response
-> UI menampilkan soal/evaluasi
-> SQLite menyimpan history
-> Dashboard dan History diperbarui
```

## Status Terakhir

- Backend compile: OK.
- Frontend build: OK.
- Vectorstore sudah di-rebuild.
- Dataset vocabulary sudah tersedia.
- Kategori Grammar, Vocabulary, dan Reading siap dicoba.
- Listening dan Speaking masih bisa dikembangkan sebagai fitur lanjutan.
