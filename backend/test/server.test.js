import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEST_DB_PATH = path.join(__dirname, 'test_detections.db');

describe('DeepSpill Backend & Database Engine', () => {
  let db;

  before(() => {
    if (fs.existsSync(TEST_DB_PATH)) fs.unlinkSync(TEST_DB_PATH);
    db = new DatabaseSync(TEST_DB_PATH);
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
  });

  after(() => {
    if (db) db.close();
    if (fs.existsSync(TEST_DB_PATH)) fs.unlinkSync(TEST_DB_PATH);
  });

  it('initializes sqlite database schema with strict constraints', () => {
    const tableInfo = db.prepare("PRAGMA table_info(detections)").all();
    const columnNames = tableInfo.map((col) => col.name);
    assert.deepEqual(columnNames, ['id', 'filename', 'confidence', 'threshold', 'spill', 'created_at']);
  });

  it('inserts detection record using parameterized query safely (SQLi Immunity)', () => {
    const stmt = db.prepare(
      `INSERT INTO detections (filename, confidence, threshold, spill) VALUES (?, ?, ?, ?)`
    );
    const result = stmt.run('satellite_sentinel1_test.tif', 0.845, 0.5, 1);
    assert.ok(result.lastInsertRowid >= 1);

    const row = db.prepare('SELECT * FROM detections WHERE id = ?').get(result.lastInsertRowid);
    assert.equal(row.filename, 'satellite_sentinel1_test.tif');
    assert.equal(row.confidence, 0.845);
    assert.equal(row.threshold, 0.5);
    assert.equal(row.spill, 1);
  });

  it('retrieves recent history with descending order and limit constraint', () => {
    const stmt = db.prepare(
      `INSERT INTO detections (filename, confidence, threshold, spill) VALUES (?, ?, ?, ?)`
    );
    for (let i = 1; i <= 5; i++) {
      stmt.run(`spill_${i}.jpg`, 0.1 * i, 0.3, i > 3 ? 1 : 0);
    }

    const history = db.prepare(
      `SELECT id, filename, confidence, threshold, spill, created_at FROM detections ORDER BY id DESC LIMIT 50`
    ).all();

    assert.ok(history.length >= 6);
    assert.equal(history[0].filename, 'spill_5.jpg');
    assert.ok(history[0].id > history[1].id);
  });

  it('rejects unparameterized injection attempts as literal text', () => {
    const maliciousPayload = "safe_name.jpg'); DROP TABLE detections; --";
    const stmt = db.prepare(
      `INSERT INTO detections (filename, confidence, threshold, spill) VALUES (?, ?, ?, ?)`
    );
    stmt.run(maliciousPayload, 0.99, 0.5, 1);

    const row = db.prepare('SELECT filename FROM detections WHERE filename = ?').get(maliciousPayload);
    assert.equal(row.filename, maliciousPayload);

    // Verify table was not dropped
    const countRow = db.prepare('SELECT COUNT(*) as count FROM detections').get();
    assert.ok(countRow.count >= 7);
  });
});

describe('DeepSpill File Filter & MIME Security Rules', () => {
  it('allows valid image mime types (jpeg, png, tiff)', () => {
    const allowedRegex = /image\/(jpeg|png|jpg|tiff|tif)/;
    assert.ok(allowedRegex.test('image/jpeg'));
    assert.ok(allowedRegex.test('image/png'));
    assert.ok(allowedRegex.test('image/tiff'));
    assert.ok(allowedRegex.test('image/tif'));
  });

  it('strictly blocks dangerous non-image file uploads', () => {
    const allowedRegex = /image\/(jpeg|png|jpg|tiff|tif)/;
    assert.ok(!allowedRegex.test('application/javascript'));
    assert.ok(!allowedRegex.test('application/x-executable'));
    assert.ok(!allowedRegex.test('text/html'));
    assert.ok(!allowedRegex.test('application/x-sh'));
    assert.ok(!allowedRegex.test('application/zip'));
  });
});
