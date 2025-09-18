'use client';

import { useEffect, useRef, useState } from 'react';

// Lazy-load face-api to reduce initial bundle
let faceapiPromise;
async function loadFaceApi() {
  if (!faceapiPromise) {
    faceapiPromise = (async () => {
      const faceapi = await import('@vladmandic/face-api');
      await faceapi.nets.tinyFaceDetector.loadFromUri('/models');
      await faceapi.nets.faceExpressionNet.loadFromUri('/models');
      await faceapi.nets.ageGenderNet.loadFromUri('/models');
      return faceapi;
    })();
  }
  return faceapiPromise;
}

export default function EmotionCapture({ onChange, intervalMs = 200 }) {
  const videoRef = useRef(null);
  const [enabled, setEnabled] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!enabled) return;
    let stream;
    let stopped = false;
  let rafId;
  let timeoutId;
    let faceapi;

    const start = async () => {
      try {
        faceapi = await loadFaceApi();
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: 320, height: 240 } });
        if (!videoRef.current) return;
        videoRef.current.srcObject = stream;
        await videoRef.current.play();

        const options = new faceapi.TinyFaceDetectorOptions({ inputSize: 224, scoreThreshold: 0.5 });

        const tick = async () => {
          if (stopped) return;
          try {
            const result = await faceapi
              .detectSingleFace(videoRef.current, options)
              .withFaceExpressions()
              .withAgeAndGender();
            if (result) {
              const expressions = result.expressions || {};
              // find dominant expression
              const entries = Object.entries(expressions);
              const dominant = entries.length ? entries.reduce((a, b) => (a[1] > b[1] ? a : b))[0] : '';
              const age = result.age ? Math.round(result.age) : undefined;
              const gender = result.gender || undefined;
              onChange?.({ expression: dominant, age, gender });
            }
          } catch (e) {
            // swallow per-frame errors
          }
          if (intervalMs <= 16) {
            rafId = requestAnimationFrame(tick);
          } else {
            timeoutId = setTimeout(tick, intervalMs);
          }
        };
        if (intervalMs <= 16) {
          rafId = requestAnimationFrame(tick);
        } else {
          timeoutId = setTimeout(tick, intervalMs);
        }
      } catch (e) {
        setError(e.message || 'Camera error');
        setEnabled(false);
      }
    };
    start();

    return () => {
      stopped = true;
      if (rafId) cancelAnimationFrame(rafId);
      if (timeoutId) clearTimeout(timeoutId);
      if (stream) {
        stream.getTracks().forEach((t) => t.stop());
      }
    };
  }, [enabled, onChange, intervalMs]);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="text-white text-sm">Webcam Context</div>
          <span className={`text-[10px] px-2 py-0.5 rounded-full border ${enabled ? 'bg-green-600/30 border-green-400 text-green-100' : 'bg-white/10 border-white/30 text-white/80'}`}>
            {enabled ? 'Capturing' : 'Stopped'}
          </span>
        </div>
        <button
          type="button"
          onClick={() => setEnabled((v) => !v)}
          className={`text-xs px-2 py-1 rounded border ${enabled ? 'bg-green-600/70 border-green-500' : 'bg-white/10 border-white/20'} text-white`}
        >
          {enabled ? 'Stop' : 'Start'}
        </button>
      </div>
      {error && <div className="text-xs text-red-300">{error}</div>}
      <video ref={videoRef} className={`w-full rounded ${enabled ? 'opacity-100' : 'opacity-40'}`} muted playsInline />
      <p className="text-xs text-gray-300">We detect dominant expression, age, and gender locally in your browser. No raw video is sent to the server.</p>
    </div>
  );
}
