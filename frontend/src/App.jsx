import { useState, useCallback, useEffect, useRef } from 'react'
import { predict, getHistory, getSamples, fetchSampleBlob } from './api'
import './App.css'

const TABS = [
  { id: 'detect', label: '🛰️ Mission Control', icon: 'radar' },
  { id: 'history', label: '📜 Detection Ledger', icon: 'database' },
  { id: 'about', label: 'ℹ️ System Architecture', icon: 'info' }
]

const SENSOR_PRESETS = [
  { label: 'Sentinel-1 SAR (10.0 m/px)', gsd: 10.0, desc: 'ESA Copernicus C-band Radar Satellite' },
  { label: 'PlanetScope Optical (3.0 m/px)', gsd: 3.0, desc: 'Commercial RGB Constellation' },
  { label: 'Maritime Aerial Drone (0.2 m/px)', gsd: 0.2, desc: 'Low-Altitude UAV / Patrol Aircraft' }
]

function App() {
  const [tab, setTab] = useState('detect')

  // ── Input mode: 'upload' vs 'benchmark' ───────────────────────────────────
  const [inputMode, setInputMode] = useState('upload')

  // ── Detection state ──────────────────────────────────────────────────────
  const [file, setFile] = useState(null)
  const [fileSize, setFileSize] = useState(null)
  const [preview, setPreview] = useState(null)
  const [threshold, setThreshold] = useState(0.85)
  const [sensorGsd, setSensorGsd] = useState(10.0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [viewMode, setViewMode] = useState('all') // 'all', 'overlay', 'mask', 'original'

  const fileInputRef = useRef(null)

  // ── Benchmark Samples state ──────────────────────────────────────────────
  const [samples, setSamples] = useState([])
  const [selectedSample, setSelectedSample] = useState(null)

  // ── History state ────────────────────────────────────────────────────────
  const [history, setHistory] = useState([])
  const [histLoading, setHistLoading] = useState(false)
  const [histError, setHistError] = useState(null)

  // Load benchmark samples on mount
  useEffect(() => {
    getSamples().then(setSamples).catch(() => {})
  }, [])

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

  // ── File & Sample handling ───────────────────────────────────────────────
  const handleFile = useCallback((f) => {
    if (!f) return
    if (!f.type.startsWith('image/') && !f.name.match(/\.(png|jpe?g|tif|tiff|bmp)$/i)) {
      setError('Please select a valid satellite image (PNG, JPG, TIF, BMP).')
      return
    }
    setFile(f)
    setFileSize((f.size / 1024).toFixed(1) + ' KB')
    setPreview(URL.createObjectURL(f))
    setResult(null)
    setError(null)
    setSelectedSample(null)
  }, [])

  const clearSelectedFile = () => {
    setFile(null)
    setFileSize(null)
    setPreview(null)
    setResult(null)
    setError(null)
    setSelectedSample(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const selectSample = async (sample) => {
    try {
      setLoading(true)
      setSelectedSample(sample.id)
      const blob = await fetchSampleBlob(sample.id)
      const sampleFile = new File([blob], sample.name, { type: 'image/jpeg' })
      setFile(sampleFile)
      setFileSize((blob.size / 1024).toFixed(1) + ' KB')
      setPreview(URL.createObjectURL(blob))
      setResult(null)
      setError(null)
    } catch (err) {
      setError(`Failed to load benchmark sample: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const onUpload = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const data = await predict(file, { threshold })
      setResult(data)
      if (tab === 'history') loadHistory()
    } catch (err) {
      setError(err.message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const b64png = (b64) => `data:image/png;base64,${b64}`

  // Calculate physical metrics based on user-selected sensor GSD
  const ratio = result?.confidence ?? 0
  const isSpill = ratio >= 0.005
  // Real world ground area calculation: 256x256 pixels footprint * (GSD)^2
  const totalSceneAreaM2 = 256 * 256 * (sensorGsd * sensorGsd)
  const estimatedAreaM2 = ratio * totalSceneAreaM2
  const estimatedAreaKm2 = estimatedAreaM2 / 1000000.0
  const estimatedVolumeM3 = estimatedAreaKm2 * 75.0 // Bonn agreement average weighted volume

  // 4-Tier IMO Severity Classification
  const getSeverityTier = () => {
    if (!isSpill) return { tier: 0, title: 'MARITIME SURFACE CLEAR', class: 'tier-clear', icon: '✅', action: 'No contamination detected. Nominal ambient sea envelope.' }
    if (estimatedAreaKm2 >= 5.0) return { tier: 4, title: 'TIER 4 CATASTROPHIC CONTAMINATION', class: 'tier-catastrophic', icon: '🚨', action: 'National emergency skimmer dispatch & multi-vessel containment boom deployment required.' }
    if (estimatedAreaKm2 >= 1.5) return { tier: 3, title: 'TIER 3 MAJOR MARITIME OIL SPILL', class: 'tier-major', icon: '⚠️', action: 'Regional Coast Guard incident response & offshore skimming operations triggered.' }
    if (estimatedAreaKm2 >= 0.25) return { tier: 2, title: 'TIER 2 MODERATE CONTAMINATION', class: 'tier-moderate', icon: '⚠️', action: 'Local harbor containment booms and dispersant advisory dispatched.' }
    return { tier: 1, title: 'TIER 1 MINOR SHEEN DISCHARGE', class: 'tier-minor', icon: 'ℹ️', action: 'Localized operational sheen or bilge release. Logged for satellite re-pass monitoring.' }
  }

  const severity = getSeverityTier()

  return (
    <div className="app">
      {/* ── TOP MISSION CONTROL HEADER ── */}
      <header className="hud-header">
        <div className="hud-header-top">
          <div className="brand-badge">
            <span className="live-dot" />
            <span>SENTINEL-1 SAR MISSION CONTROL</span>
          </div>
          <div className="telemetry-pill">
            <span className="pill-dot green" />
            <span>MODEL: EFFICIENTNET-B0 U-NET</span>
            <span className="pill-acc">92.75% ACC</span>
          </div>
        </div>
        <div className="hud-title-row">
          <div>
            <h1 className="hud-title">DEEPSPILL AI</h1>
            <p className="hud-subtitle">Autonomous Satellite Radar &amp; Optical Maritime Oil Spill Detection System</p>
          </div>
        </div>
      </header>

      {/* ── NAVIGATION TABS ── */}
      <div className="hud-tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`hud-tab-btn ${tab === t.id ? 'active' : ''}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ════════════ MISSION CONTROL TAB ════════════ */}
      {tab === 'detect' && (
        <>
          {/* Main Inspection Grid */}
          <div className="control-grid">
            {/* Upload & Controls */}
            <div className="hud-card">
              <div className="card-header">
                <h3>📡 Satellite Imagery Input</h3>
                <span className="card-badge">INPUT TELEMETRY</span>
              </div>

              {/* Input Mode Selector (Upload vs Benchmark) */}
              <div className="input-mode-tabs">
                <button
                  type="button"
                  className={`input-mode-btn ${inputMode === 'upload' ? 'active' : ''}`}
                  onClick={() => setInputMode('upload')}
                >
                  📁 Upload Custom Image
                </button>
                <button
                  type="button"
                  className={`input-mode-btn ${inputMode === 'benchmark' ? 'active' : ''}`}
                  onClick={() => setInputMode('benchmark')}
                >
                  ⚡ Benchmark Scenes ({samples.length})
                </button>
              </div>

              {/* ── MODE 1: CUSTOM FILE UPLOAD ── */}
              {inputMode === 'upload' && (
                <div className="upload-container">
                  <input
                    ref={fileInputRef}
                    id="file-input"
                    type="file"
                    accept="image/jpeg,image/png,image/jpg,image/tif,image/tiff,image/bmp"
                    onChange={(e) => handleFile(e.target.files[0])}
                    style={{ display: 'none' }}
                  />

                  {preview ? (
                    <div className="selected-preview-card">
                      <div className="preview-top">
                        <img src={preview} alt="Upload Preview" className="preview-thumb-large" />
                        <div className="preview-info">
                          <div className="preview-badge">READY FOR ANALYSIS</div>
                          <div className="preview-name">{file?.name}</div>
                          <div className="preview-size">File size: {fileSize}</div>
                        </div>
                      </div>
                      <div className="preview-actions">
                        <button
                          type="button"
                          className="btn-change-file"
                          onClick={() => fileInputRef.current?.click()}
                        >
                          🔄 Replace Image
                        </button>
                        <button
                          type="button"
                          className="btn-remove-file"
                          onClick={clearSelectedFile}
                        >
                          ✕ Remove
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div
                      className={`upload-zone ${dragging ? 'dragging' : ''}`}
                      onDrop={onDrop}
                      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
                      onDragLeave={() => setDragging(false)}
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <div className="upload-icon">📁</div>
                      <h4>Click to Browse or Drag Image Here</h4>
                      <p className="upload-subtext">Upload any Sentinel-1 SAR scene, drone photo, or optical imagery</p>
                      
                      <button
                        type="button"
                        className="btn-browse-accent"
                        onClick={(e) => {
                          e.stopPropagation()
                          fileInputRef.current?.click()
                        }}
                      >
                        📂 Choose Satellite Image from Device
                      </button>

                      <div className="upload-formats">
                        Supports: <strong>PNG, JPG, GeoTIFF, BMP</strong> (Up to 4K)
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* ── MODE 2: BENCHMARK SCENES ── */}
              {inputMode === 'benchmark' && (
                <div className="benchmark-container">
                  <p className="section-desc">Select an authentic Sentinel-1 SAR acquisition from the research benchmark dataset:</p>
                  <div className="preset-grid">
                    {samples.map((s) => (
                      <button
                        key={s.id}
                        type="button"
                        className={`preset-btn ${selectedSample === s.id ? 'active' : ''}`}
                        onClick={() => selectSample(s)}
                        disabled={loading}
                      >
                        <div className="preset-name">{s.label}</div>
                        <div className="preset-meta">{s.name}</div>
                      </button>
                    ))}
                  </div>
                  {preview && selectedSample && (
                    <div className="benchmark-preview-banner">
                      <span>Active Benchmark Scene: <strong>{file?.name}</strong></span>
                      <button type="button" className="btn-mini-clear" onClick={clearSelectedFile}>✕ Clear</button>
                    </div>
                  )}
                </div>
              )}

              {/* ── SENSOR RESOLUTION (GSD) SELECTOR ── */}
              <div className="controls-panel">
                <div className="control-row">
                  <label htmlFor="sensor-gsd">Sensor Resolution (GSD)</label>
                  <select
                    id="sensor-gsd"
                    className="hud-select"
                    value={sensorGsd}
                    onChange={(e) => setSensorGsd(Number(e.target.value))}
                  >
                    {SENSOR_PRESETS.map((p) => (
                      <option key={p.label} value={p.gsd}>
                        {p.label}
                      </option>
                    ))}
                  </select>
                </div>
                <span className="slider-hint">
                  {SENSOR_PRESETS.find(p => p.gsd === sensorGsd)?.desc} (1 px = {sensorGsd}m × {sensorGsd}m)
                </span>
              </div>

              {/* ── CALIBRATED DECISION THRESHOLD SLIDER ── */}
              <div className="controls-panel">
                <div className="slider-header">
                  <label htmlFor="threshold-slider">Calibrated Decision Cutoff (T)</label>
                  <span className="slider-val">{threshold.toFixed(2)}</span>
                </div>
                <input
                  id="threshold-slider"
                  type="range"
                  min="0.10"
                  max="0.95"
                  step="0.05"
                  value={threshold}
                  onChange={(e) => setThreshold(Number(e.target.value))}
                  className="hud-slider"
                />
                <span className="slider-hint">Optimal Transfer U-Net threshold: <strong>0.80 – 0.85</strong> (from model_config.json)</span>
              </div>

              {/* ── LAUNCH ANALYSIS BUTTON ── */}
              <button
                className="btn-launch"
                onClick={onUpload}
                disabled={!file || loading}
              >
                {loading ? (
                  <>
                    <span className="radar-spinner" />
                    <span>RUNNING INFERENCE ON T4 / CPU...</span>
                  </>
                ) : (
                  <>
                    <span>🔍 ANALYZE MARITIME SCENE</span>
                  </>
                )}
              </button>

              {error && <div className="alert-box error">{error}</div>}
            </div>

            {/* Live Detection Analytics */}
            <div className="hud-card">
              <div className="card-header">
                <h3>📊 Physical Telemetry &amp; Assessment</h3>
                <span className="card-badge">IMO STANDARDS</span>
              </div>

              {!result && !loading && (
                <div className="empty-telemetry">
                  <div className="empty-radar">🌐</div>
                  <h4>No Active Scene Analyzed</h4>
                  <p>Upload a satellite image from your device or select a benchmark preset to initiate real-time radar segmentation.</p>
                </div>
              )}

              {loading && (
                <div className="loading-state">
                  <div className="scanning-radar" />
                  <h4>Segmenting SAR Backscatter Gradients...</h4>
                  <p>Filtering Marangoni wave damping &amp; morphological speckle</p>
                </div>
              )}

              {result && !loading && (
                <div className="results-container">
                  {/* Severity Banner */}
                  <div className={`severity-banner ${severity.class}`}>
                    <div className="sev-icon">{severity.icon}</div>
                    <div className="sev-content">
                      <h4>{severity.title}</h4>
                      <p>{severity.action}</p>
                    </div>
                  </div>

                  {/* Quantitative Metrics */}
                  <div className="metrics-triad">
                    <div className="metric-box">
                      <div className="m-val">{estimatedAreaKm2.toFixed(3)} km²</div>
                      <div className="m-lbl">Detected Slick Area</div>
                    </div>
                    <div className="metric-box">
                      <div className="m-val">{estimatedVolumeM3.toFixed(1)} m³</div>
                      <div className="m-lbl">Estimated Volume (Bonn)</div>
                    </div>
                    <div className="metric-box">
                      <div className="m-val">{(ratio * 100).toFixed(2)}%</div>
                      <div className="m-lbl">Scene Contamination</div>
                    </div>
                  </div>

                  {/* Multiscale Threshold Breakdown */}
                  <div className="sensitivity-breakdown">
                    <div className="breakdown-title">Radar Confidence Distribution</div>
                    <div className="breakdown-bar">
                      <div className="bar-seg high" style={{ width: `${Math.min(100, (result.oil_pixel_ratio_05 || 0) * 200)}%` }} title="High Confidence Core" />
                      <div className="bar-seg med" style={{ width: `${Math.min(100, (result.oil_pixel_ratio_03 || 0) * 150)}%` }} title="Medium Sheen" />
                      <div className="bar-seg low" style={{ width: `${Math.min(100, (result.oil_pixel_ratio_01 || 0) * 100)}%` }} title="Thin Fringe" />
                    </div>
                    <div className="breakdown-labels">
                      <span>Core Crude (&gt;50%): {(result.oil_pixel_ratio_05 || 0).toFixed(3)}</span>
                      <span>Medium Plume (&gt;30%): {(result.oil_pixel_ratio_03 || 0).toFixed(3)}</span>
                      <span>Fringe Sheen (&gt;10%): {(result.oil_pixel_ratio_01 || 0).toFixed(3)}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Comparative Multi-View Display */}
          {result && !loading && (
            <section className="hud-card comparison-section">
              <div className="card-header">
                <h3>🔬 Multimodal Radar Segmentation Gallery</h3>
                <div className="view-selector">
                  <button className={`view-btn ${viewMode === 'all' ? 'active' : ''}`} onClick={() => setViewMode('all')}>Tri-View</button>
                  <button className={`view-btn ${viewMode === 'overlay' ? 'active' : ''}`} onClick={() => setViewMode('overlay')}>Overlay</button>
                  <button className={`view-btn ${viewMode === 'mask' ? 'active' : ''}`} onClick={() => setViewMode('mask')}>Mask</button>
                  <button className={`view-btn ${viewMode === 'original' ? 'active' : ''}`} onClick={() => setViewMode('original')}>Original</button>
                </div>
              </div>

              <div className={`gallery-grid ${viewMode}`}>
                {(viewMode === 'all' || viewMode === 'original') && result.originalBase64 && (
                  <div className="gallery-item">
                    <img src={b64png(result.originalBase64)} alt="Original Satellite Scene" />
                    <div className="item-label">1. Original Satellite Scene</div>
                  </div>
                )}
                {(viewMode === 'all' || viewMode === 'mask') && result.maskBase64 && (
                  <div className="gallery-item">
                    <img src={b64png(result.maskBase64)} alt="Binarized Oil Spill Mask" />
                    <div className="item-label">2. Semantic Oil Spill Mask</div>
                  </div>
                )}
                {(viewMode === 'all' || viewMode === 'overlay') && result.overlayBase64 && (
                  <div className="gallery-item">
                    <img src={b64png(result.overlayBase64)} alt="Color Composite Overlay" />
                    <div className="item-label">3. Bonn Composite &amp; Contours</div>
                  </div>
                )}
              </div>

              <div className="download-action-bar">
                {result.overlayBase64 && (
                  <a className="btn-dl" href={b64png(result.overlayBase64)} download="deepspill_overlay.png">
                    ⬇️ Download High-Res Overlay (PNG)
                  </a>
                )}
                {result.maskBase64 && (
                  <a className="btn-dl secondary" href={b64png(result.maskBase64)} download="deepspill_mask.png">
                    ⬇️ Download Mask (PNG)
                  </a>
                )}
              </div>
            </section>
          )}
        </>
      )}

      {/* ════════════ HISTORY TAB ════════════ */}
      {tab === 'history' && (
        <section className="hud-card">
          <div className="card-header">
            <h3>📜 SQLite Detections Ledger (`oil_spill_detections.db`)</h3>
            <button className="btn-refresh" onClick={loadHistory} disabled={histLoading}>
              {histLoading ? 'Loading…' : '↻ Refresh Ledger'}
            </button>
          </div>
          {histError && <div className="alert-box error">{histError}</div>}
          {!histLoading && history.length === 0 && (
            <div className="empty-telemetry">
              <p>No detection records found in database. Run an image analysis to populate the ledger.</p>
            </div>
          )}
          {history.length > 0 && (
            <div className="table-responsive">
              <table className="hud-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Satellite Acquisition</th>
                    <th>Contamination Ratio</th>
                    <th>Decision Threshold</th>
                    <th>Status Verdict</th>
                    <th>Acquisition Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((row) => (
                    <tr key={row.id}>
                      <td className="id-cell">#{row.id}</td>
                      <td className="fn-cell">{row.filename}</td>
                      <td className="metric-cell">{(row.confidence || 0).toFixed(4)}</td>
                      <td className="metric-cell">{row.threshold?.toFixed(2) ?? '0.80'}</td>
                      <td>
                        <span className={`status-pill ${row.spill ? 'spill' : 'clean'}`}>
                          {row.spill ? '🚨 Oil Spill' : '✅ Clear'}
                        </span>
                      </td>
                      <td className="time-cell">{new Date(row.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {/* ════════════ ABOUT / ARCHITECTURE TAB ════════════ */}
      {tab === 'about' && (
        <section className="hud-card">
          <div className="card-header">
            <h3>🏛️ 3-Tier Enterprise Architecture &amp; Physical Specifications</h3>
            <span className="card-badge">INFOSYS SPRINGBOARD AI 6.0</span>
          </div>

          <div className="arch-grid">
            <div className="arch-card">
              <h4>1. Frontend Tier</h4>
              <p>React 18 + Vite SPA styled with cyber-maritime telemetry aesthetics, real-time drag-and-drop, multimodal image comparisons, and instant benchmark evaluation.</p>
            </div>
            <div className="arch-card">
              <h4>2. Backend Gateway Tier</h4>
              <p>Node.js 22 + Express REST API with multipart payload streaming, SQLite persistence (`node:sqlite`), and automated audit logging.</p>
            </div>
            <div className="arch-card">
              <h4>3. Python ML Inference Tier</h4>
              <p>FastAPI + TensorFlow 2.17 microservice powered by the SOTA <strong>EfficientNet-B0 Transfer Learning U-Net (92.75% Test Accuracy)</strong> with morphological speckle filtering.</p>
            </div>
          </div>

          <div className="specs-table-container">
            <h4>📈 Verified Performance Specifications</h4>
            <table className="hud-table">
              <tbody>
                <tr><td><strong>Model Architecture</strong></td><td>Pretrained EfficientNet-B0 Transfer Learning U-Net (9.05M Params)</td></tr>
                <tr><td><strong>Dataset Source</strong></td><td>Copernicus Sentinel-1 Synthetic Aperture Radar (SAR)</td></tr>
                <tr><td><strong>Held-Out Test Accuracy</strong></td><td><strong style={{ color: '#00F2FE' }}>92.75%</strong></td></tr>
                <tr><td><strong>Mean IoU (Jaccard Index)</strong></td><td>0.82</td></tr>
                <tr><td><strong>Sørensen-Dice (F1-Score)</strong></td><td>0.88</td></tr>
                <tr><td><strong>Recall on Oil Pixels</strong></td><td>89.0%</td></tr>
                <tr><td><strong>Precision</strong></td><td>87.0%</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* ── FOOTER ── */}
      <footer className="hud-footer">
        <div>
          <strong>DEEPSPILL AI</strong> · Infosys Springboard AI Internship 6.0 · Akshat Raikar
        </div>
        <div className="footer-sub">
          European Space Agency (ESA) Copernicus Sentinel-1 SAR Remote Sensing
        </div>
      </footer>
    </div>
  )
}

export default App
