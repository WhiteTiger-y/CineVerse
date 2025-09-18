'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import * as webllm from '@mlc-ai/web-llm';

// Simple hook to manage a WebLLM engine lifecycle and text generation
export default function useLocalLLM() {
  const engineRef = useRef(null);
  const [status, setStatus] = useState('idle'); // idle | loading | ready | error
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(null);
  const [modelId, setModelId] = useState('Llama-3.2-1B-Instruct-q4f32_1-MLC');

  const init = useCallback(async (id) => {
    const target = id || modelId;
    if (engineRef.current && status === 'ready' && target === modelId) return;
    setStatus('loading');
    setError('');
    try {
      // Create engine on main thread for simplicity
      const engine = await webllm.CreateMLCEngine(target, {
        logLevel: 'info',
        initProgressCallback: (report) => setProgress(report),
      });
      engineRef.current = engine;
      setModelId(target);
      setStatus('ready');
    } catch (e) {
      setError(e?.message || String(e));
      setStatus('error');
    }
  }, [modelId, status]);

  const generate = useCallback(async (messages, options = {}) => {
    if (!engineRef.current) throw new Error('Local model not initialized');
    const { systemPrefix = '', temperature = 0.6, maxTokens = 256 } = options;
    const fullMessages = systemPrefix
      ? [{ role: 'system', content: systemPrefix }, ...messages]
      : messages;
    const out = await engineRef.current.chat.completions.create({
      messages: fullMessages,
      temperature,
      max_tokens: maxTokens,
      stream: false,
    });
    return out?.choices?.[0]?.message?.content || '';
  }, []);

  return { init, status, error, progress, modelId, setModelId, ready: status === 'ready', generate };
}
