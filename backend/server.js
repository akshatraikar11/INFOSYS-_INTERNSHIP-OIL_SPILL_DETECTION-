import express from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
// ponytail: node:sqlite is experimental in Node 22; upgrade to better-sqlite3 once
//           node-gyp build toolchain is available in the project's CI environment.
import { DatabaseSync } from 'node:sqlite';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = process.env.PORT || 3001;
const INFERENCE_URL = process.env.INFERENCE_URL || 'http://127.0.0.1:8000';
const DB_PATH = path.join(__dirname, '..', 'oil_spill_detections.db');

// CORS_ORIGINS: comma-separated list of allowed origins.
// Defaults to '*' in dev; set explicitly in production (e.g. "https://myapp.com").
const allowedOrigins = process.env.CORS_ORIGINS
  ? process.env.CORS_ORIGINS.split(',').map((s) => s.trim())
  : null;

// ── Database ──────────────────────────────────────────────────────────────────
const db = new DatabaseSync(DB_PATH);
db.exec(`
  CREATE TABLE IF NOT EXISTS detections (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT,
    confidence  REAL,
    threshold   REAL,
    spill       INTEGER,
    created_at  TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
  )
`);

// ── Express setup ─────────────────────────────────────────────────────────────
const app = express();
app.use(
  cors(
    allowedOrigins
      ? {
          origin: (origin, cb) => {
            // allow non-browser requests (curl, Postman) and listed origins
            if (!origin || allowedOrigins.includes(origin)) cb(null, true);
            else cb(new Error(`CORS: origin ${origin} not allowed`));
          },
        }
      : undefined // open — fine for local dev
  )
);
app.use(express.json());

const TMP_DIR = path.join(__dirname, 'tmp');
fs.mkdirSync(TMP_DIR, { recursive: true });

const upload = multer({
  dest: TMP_DIR,
  limits: { fileSize: 20 * 1024 * 1024 },
  fileFilter: (_req, file, cb) => {
    if (/image\/(jpeg|png|jpg|tiff|tif)/.test(file.mimetype)) cb(null, true);
    else cb(new Error('Only JPG, PNG, TIF images are allowed'));
  },
});

// ── Routes ────────────────────────────────────────────────────────────────────
app.post('/api/predict', upload.single('image'), async (req, res) => {
  if (!req.file) return res.status(400).json({ message: 'No image file uploaded' });

  const threshold = req.query.threshold != null ? parseFloat(req.query.threshold) : 0.1;
  const tmpPath = req.file.path;
  try {
    const buf = fs.readFileSync(tmpPath);
    // Pass through the original MIME type so the inference server gets the right format
    const mime = req.file.mimetype || 'image/jpeg';
    const body = new FormData();
    body.append('image', new Blob([buf], { type: mime }), req.file.originalname || 'image.jpg');
    body.append('threshold', String(threshold));

    const inferenceRes = await fetch(`${INFERENCE_URL}/predict`, { method: 'POST', body });
    if (!inferenceRes.ok) {
      const errText = await inferenceRes.text();
      throw new Error(
        inferenceRes.status === 502
          ? 'Inference service not running. Start it with: cd inference && uvicorn server:app --port 8000'
          : errText || 'Inference failed'
      );
    }
    const data = await inferenceRes.json();

    // Persist summary (no base64 blobs in DB)
    db.prepare(
      `INSERT INTO detections (filename, confidence, threshold, spill) VALUES (?, ?, ?, ?)`
    ).run(req.file.originalname || 'unknown', data.confidence ?? 0, threshold, data.confidence >= threshold ? 1 : 0);

    res.json(data);
  } catch (err) {
    res.status(500).json({ message: err.message || 'Prediction failed' });
  } finally {
    if (fs.existsSync(tmpPath)) fs.unlinkSync(tmpPath);
  }
});

app.get('/api/history', (_req, res) => {
  const rows = db.prepare(
    `SELECT id, filename, confidence, threshold, spill, created_at FROM detections ORDER BY id DESC LIMIT 50`
  ).all();
  res.json(rows);
});

// ── Static frontend (production build) ───────────────────────────────────────
const frontendDist = path.join(__dirname, '..', 'frontend', 'dist');
if (fs.existsSync(frontendDist)) {
  app.use(express.static(frontendDist));
  app.get('*', (req, res) => {
    if (!req.path.startsWith('/api')) res.sendFile(path.join(frontendDist, 'index.html'));
  });
} else {
  console.warn('[warn] frontend/dist not found — run "npm run build" in frontend/ to enable static serving.');
}

const server = app.listen(PORT, () => {
  console.log(`DeepSpill backend running at http://localhost:${PORT}`);
  console.log(`Inference service expected at ${INFERENCE_URL}`);
  if (allowedOrigins) console.log(`CORS restricted to: ${allowedOrigins.join(', ')}`);
});

// ── Graceful shutdown ─────────────────────────────────────────────────────────
function shutdown(signal) {
  console.log(`\n[${signal}] Shutting down…`);
  server.close(() => {
    db.close();
    process.exit(0);
  });
  // Force-exit if connections linger beyond 5 s
  setTimeout(() => process.exit(1), 5000).unref();
}
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT',  () => shutdown('SIGINT'));
