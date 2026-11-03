const API_BASE = '/api';

export async function predict(imageFile, options = {}) {
  const formData = new FormData();
  formData.append('image', imageFile);
  const threshold = options.threshold != null ? options.threshold : 0.1;
  const res = await fetch(`${API_BASE}/predict?threshold=${encodeURIComponent(threshold)}`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(err.message || 'Prediction failed');
  }
  return res.json();
}

export async function getHistory() {
  const res = await fetch(`${API_BASE}/history`);
  if (!res.ok) throw new Error('Failed to load history');
  return res.json();
}
