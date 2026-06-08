# SMARTTOEFL AI

SMARTTOEFL AI adalah aplikasi latihan TOEFL berbasis web yang berjalan secara lokal. Aplikasi ini memakai FastAPI sebagai backend, Vue 3 sebagai frontend, SQLite untuk menyimpan riwayat latihan, Chroma vector database untuk RAG, dan Ollama sebagai LLM lokal.

Tujuan utama project ini adalah membantu user membuat soal TOEFL secara adaptif, menjawab soal, mendapatkan evaluasi bilingual Inggris/Indonesia, serta melihat riwayat dan analitik latihan.

## Fitur Utama

- Generate soal TOEFL berdasarkan kategori dan tingkat kesulitan.
- Kategori utama yang tersedia di UI: Grammar, Vocabulary, dan Reading.
- Evaluasi jawaban user dengan feedback bilingual.
- Menampilkan correct answer, explanation, translation, why wrong, grammar tip, dan TOEFL strategy tip.
- Menyimpan riwayat latihan ke SQLite.
- Menampilkan analytics, weakness analysis, dan recommendation.
- Menggunakan dataset lokal dari `backend/app/dataset`.
- Menggunakan RAG dengan Chroma vectorstore.
- Menggunakan Ollama lokal, jadi tidak membutuhkan API key LLM eksternal.

## Teknologi

Backend:

- FastAPI
- SQLAlchemy
- SQLite
- LangChain
- ChromaDB
- HuggingFace sentence-transformers embedding
- Ollama
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

Struktur dataset:

```text
backend/app/dataset/
+-- grammar/
+-- reading/
+-- vocabulary/
+-- overview/
+-- listening/
|   +-- audio/
|   +-- transcript/
+-- speaking/
    +-- prompts/
    +-- rubric/
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
-> POST /generate-question
-> backend/app/api/routes/question.py
-> get_context() dari rag_service.py
-> ask_llm_generate() dari llm_service.py
-> Ollama qwen2.5:1.5b
-> response JSON soal
-> currentQuestion di Pinia
-> QuestionCard.vue menampilkan soal
```

Detail proses backend:

1. Frontend mengirim `category` dan `difficulty`.
2. Backend mengambil konteks dari Chroma vectorstore.
3. Backend membuat prompt berisi TOEFL material dari RAG.
4. Ollama generate soal dalam format JSON.
5. Backend membersihkan dan validasi JSON.
6. Jika LLM gagal, backend memakai fallback question.
7. Response dikirim kembali ke frontend.

Contoh response:

```json
{
  "question": "Choose the closest meaning of the word research.",
  "options": [
    "A. Guess",
    "B. Study",
    "C. Ignore",
    "D. Sleep"
  ],
  "answer": "B",
  "explanation": "Research means careful study.",
  "difficulty": "Easy",
  "category": "Vocabulary"
}
```

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
POST   /generate-question
POST   /evaluate-answer
GET    /history
DELETE /history
GET    /analytics
GET    /recommendation
GET    /weakness-analysis
```

Keterangan:

- `GET /` untuk health check backend.
- `POST /generate-question` untuk membuat soal baru.
- `POST /evaluate-answer` untuk mengevaluasi jawaban dan menyimpan history.
- `GET /history` untuk mengambil riwayat latihan.
- `DELETE /history` untuk menghapus riwayat latihan.
- `GET /analytics` untuk statistik latihan.
- `GET /recommendation` untuk rekomendasi belajar.
- `GET /weakness-analysis` untuk ringkasan kelemahan.

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

Install model Ollama:

```powershell
ollama pull qwen2.5:1.5b
```

Pastikan Ollama berjalan:

```powershell
ollama list
```

Build RAG vectorstore:

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

## Workflow Penggunaan

1. Jalankan Ollama.
2. Jalankan backend FastAPI.
3. Jalankan frontend Vue.
4. Buka halaman web.
5. Pilih kategori: Grammar, Vocabulary, atau Reading.
6. Pilih difficulty: Easy, Intermediate, atau Advanced.
7. Klik Generate Question.
8. Pilih jawaban.
9. Klik Submit Answer.
10. Lihat hasil evaluasi dan tips.
11. Buka Dashboard/History untuk melihat progress.

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
