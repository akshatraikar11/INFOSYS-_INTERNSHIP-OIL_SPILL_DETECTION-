import { useState, useCallback, useEffect } from 'react'
import { predict, getHistory } from './api'
import './App.css'

const TABS = ['detect', 'history']

function App() {
  const [tab, setTab] = useState('detect')

  // ── Detection state ──────────────────────────────────────────────────────
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  // threshold = oil-pixel-area ratio (0–1), not a model probability
  const [threshold, setThreshold] = useState(0.1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [dragging, setDragging] = useState(false)

  // ── History state ────────────────────────────────────────────────────────
  const [history, setHistory] = useState([])
  const [histLoading, setHistLoading] = useState(false)
  const [histError, setHistError] = useState(null)

  const loadHistory = useCallback(async () => {
    setHistLoading(true)
    setHistError(null)
    try {
      setHistory(await getHistory())
    } catch (e) {
      setHistError(e.message)
    } finally {
      setHistLoading(false)
    }
  }, [])

  useEffect(() => {
    if (tab === 'history') loadHistory()
  }, [tab, loadHistory])

  // ── File handling ────────────────────────────────────────────────────────
  const handleFile = useCallback((f) => {
    if (!f || !f.type.startsWith('image/')) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
    setError(null)
  }, [])

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  const onUpload = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const data = await predict(file, { threshold })
      setResult(data)
      // refresh history count silently after a new detection
      if (tab === 'history') loadHistory()
    } catch (err) {
      setError(err.message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  // ── Helpers ──────────────────────────────────────────────────────────────
  // All three base64 fields come from the inference server as PNG
  const b64png = (b64) => `data:image/png;base64,${b64}`

  return (
    <div className="app">
      <header className="hero">
        <h1>🌊 DeepSpill</h1>
        <p>AI-powered oil spill detection from satellite &amp; aerial imagery</p>
      </header>

      <div className="info-grid">
        <div className="info-card">
          <h3>🌍 What is an oil spill?</h3>
          <p>Petroleum released into oceans or coastal waters, causing environmental and economic harm.</p>
        </div>
        <div className="info-card">
          <h3>🚀 Why early detection matters</h3>
          <p>Timely detection enables faster response and reduces marine pollution and ecosystem damage.</p>
        </div>
        <div className="info-card">
          <h3>🤖 How AI helps</h3>
          <p>Deep learning analyzes imagery to identify oil spills automatically, enabling 24/7 monitoring.</p>
        </div>
        <div className="info-card">
          <h3>🌱 Environmental impact</h3>
          <p>Spills harm marine habitats and wildlife; early detection reduces long-term ecological damage.</p>
        </div>
      </div>

      {/* ── Tab bar ── */}
      <div className="tab-bar">
        {TABS.map((t) => (
          <button
            key={t}
            className={`tab-btn ${tab === t ? 'active' : ''}`}
            onClick={() => setTab(t)}
          >
            {t === 'detect' ? '🔍 Detect' : '🕑 History'}
          </button>
        ))}
      </div>

      {/* ════════════ DETECT TAB ════════════ */}
      {tab === 'detect' && (
        <>
          <section className="section">
            <h2>⚙️ Settings</h2>
            <div className="settings-row">
              <div className="slider-wrap">
                {/* label clarified: this is an oil-pixel area ratio, not raw model probability */}
                <label>Oil-pixel area threshold — spill flagged when ratio ≥ this value</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={threshold}
                  onChange={(e) => setThreshold(Number(e.target.value))}
                />
                <div className="value">{threshold.toFixed(2)}</div>
              </div>
            </div>
          </section>

          <section className="section">
            <h2>📤 Upload image</h2>
            <div
              className={`upload-zone ${dragging ? 'dragging' : ''}`}
              onDrop={onDrop}
              onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
              onDragLeave={() => setDragging(false)}
              onClick={() => document.getElementById('file-input').click()}
            >
              <input
                id="file-input"
                type="file"
                accept="image/jpeg,image/png,image/jpg,image/tif,image/tiff"
                onChange={(e) => handleFile(e.target.files[0])}
              />
              {preview
                ? <p>📷 {file?.name} — click or drop another to replace</p>
                : <p>Drop an image here or click to choose (JPG, PNG, TIF)</p>}
            </div>
            <div style={{ marginTop: '1rem' }}>
              <button className="btn btn-primary" onClick={onUpload} disabled={!file || loading}>
                {loading ? <><span className="spinner" /> Running detection…</> : '🔍 Run detection'}
              </button>
            </div>
          </section>

          {error && <div className="error-msg">{error}</div>}

          {loading && (
            <div className="loading">
              <span className="spinner" />
              Processing image and running AI detection…
            </div>
          )}

          {result && !loading && (
            <>
              <section className="section">
                <h2>📋 Result</h2>
                <div className={`verdict ${result.confidence >= threshold ? 'spill' : 'no-spill'}`}>
                  {result.confidence >= threshold
                    ? `🚨 Oil spill detected (ratio: ${result.confidence?.toFixed(3) ?? '-'})`
                    : `✅ No oil spill detected (ratio: ${result.confidence?.toFixed(3) ?? '-'})`}
                </div>
                <div className="results-grid">
                  {result.originalBase64 && (
                    <figure className="result-card">
                      <img src={b64png(result.originalBase64)} alt="Original" />
                      <figcaption>Original image</figcaption>
                    </figure>
                  )}
                  {result.maskBase64 && (
                    <figure className="result-card">
                      <img src={b64png(result.maskBase64)} alt="Mask" />
                      <figcaption>Detection mask</figcaption>
                    </figure>
                  )}
                  {result.overlayBase64 && (
                    <figure className="result-card">
                      <img src={b64png(result.overlayBase64)} alt="Overlay" />
                      <figcaption>Overlay</figcaption>
                    </figure>
                  )}
                </div>
                <div className="download-row">
                  {result.overlayBase64 && (
                    <a className="btn btn-secondary" href={b64png(result.overlayBase64)} download="oil_spill_overlay.png">
                      ⬇️ Download overlay (PNG)
                    </a>
                  )}
                  {result.maskBase64 && (
                    <a className="btn btn-secondary" href={b64png(result.maskBase64)} download="oil_spill_mask.png">
                      ⬇️ Download mask (PNG)
                    </a>
                  )}
                </div>
              </section>

              <section className="section">
                <h2>📊 Detection metrics</h2>
                <div className="metrics-grid">
                  <div className="metric">
                    <div className="value">{(result.oil_pixel_ratio_05 ?? 0).toFixed(3)}</div>
                    <div className="label">High (&gt;50%)</div>
                  </div>
                  <div className="metric">
                    <div className="value">{(result.oil_pixel_ratio_03 ?? 0).toFixed(3)}</div>
                    <div className="label">Medium (&gt;30%)</div>
                  </div>
                  <div className="metric">
                    <div className="value">{(result.oil_pixel_ratio_01 ?? 0).toFixed(3)}</div>
                    <div className="label">Low (&gt;10%)</div>
                  </div>
                  <div className="metric">
                    <div className="value">{(result.oil_pixel_ratio_005 ?? 0).toFixed(3)}</div>
                    <div className="label">Ultra-sensitive (&gt;5%)</div>
                  </div>
                </div>
              </section>
            </>
          )}
        </>
      )}

      {/* ════════════ HISTORY TAB ════════════ */}
      {tab === 'history' && (
        <section className="section">
          <h2>🕑 Detection history</h2>
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}>
            <button className="btn btn-secondary" onClick={loadHistory} disabled={histLoading}>
              {histLoading ? <><span className="spinner" /> Loading…</> : '↻ Refresh'}
            </button>
          </div>
          {histError && <div className="error-msg">{histError}</div>}
          {!histLoading && !histError && history.length === 0 && (
            <p style={{ color: 'var(--textMuted)' }}>No detections yet. Run a detection first.</p>
          )}
          {history.length > 0 && (
            <div className="history-table-wrap">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>File</th>
                    <th>Ratio</th>
                    <th>Threshold</th>
                    <th>Result</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((row) => (
                    <tr key={row.id}>
                      <td>{row.id}</td>
                      <td className="filename">{row.filename}</td>
                      <td>{row.confidence.toFixed(3)}</td>
                      <td>{row.threshold.toFixed(2)}</td>
                      <td>
                        <span className={`badge ${row.spill ? 'badge-spill' : 'badge-clean'}`}>
                          {row.spill ? '🚨 Spill' : '✅ Clean'}
                        </span>
                      </td>
                      <td className="ts">{new Date(row.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      <footer className="footer">
        <p><strong>🛢️ DeepSpill</strong> · Oil Spill Detection AI · Powered by Deep Learning</p>
        <p>Upload satellite or aerial imagery to detect potential oil spills</p>
      </footer>
    </div>
  )
}

export default App
