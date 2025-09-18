
'use client';

import { useEffect, useRef, useState } from 'react';

// Use @tensorflow-models/face-landmarks-detection for browser-based face detection
let detectorPromise;
async function loadDetector() {
  if (!detectorPromise) {
    detectorPromise = (async () => {
      const tf = await import('@tensorflow/tfjs');
      const faceLandmarksDetection = await import('@tensorflow-models/face-landmarks-detection');
      // Load the MediaPipe FaceMesh model
      const model = faceLandmarksDetection.SupportedModels.MediaPipeFaceMesh;
      const detector = await faceLandmarksDetection.createDetector(model, {
        runtime: 'tfjs',
        maxFaces: 1,
      });
      return detector;
    })();
  }
  return detectorPromise;
}


export default function EmotionCapture({ onChange, intervalMs = 200, setWebcamActive }) {
  const videoRef = useRef(null);
  const [enabled, setEnabled] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (setWebcamActive) setWebcamActive(enabled);
    if (!enabled) return;
    let stream;
    let stopped = false;
    let rafId;
    let timeoutId;
    let detector;

    const start = async () => {
      try {
        detector = await loadDetector();
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: 320, height: 240 } });
        if (!videoRef.current) return;
        videoRef.current.srcObject = stream;
        await videoRef.current.play();

        const tick = async () => {
          if (stopped) return;
          try {
            const faces = await detector.estimateFaces(videoRef.current, { flipHorizontal: false });
            if (faces && faces.length > 0) {
              // Only bounding box and landmarks are available
              onChange?.({ face: true, box: faces[0].box, keypoints: faces[0].keypoints });
            } else {
              onChange?.({ face: false });
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
      <p className="text-xs text-gray-300">We detect faces and landmarks locally in your browser. No raw video is sent to the server.</p>
    </div>
  );
}
