'use client';

import { useEffect, useState, useRef, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';

function OtpForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const identifier = searchParams.get('identifier') || '';
  const usernameFromQuery = searchParams.get('username') || '';
  const displayName = usernameFromQuery || identifier;
  const [digits, setDigits] = useState(['', '', '', '', '', '']);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const inputsRef = useRef([]);

  useEffect(() => {
    if (inputsRef.current[0]) inputsRef.current[0].focus();
  }, []);

  const onChangeDigit = (idx, val) => {
    if (!/^[0-9]?$/.test(val)) return;
    const next = [...digits];
    next[idx] = val;
    setDigits(next);
    if (val && idx < 5) inputsRef.current[idx + 1]?.focus();
  };

  const onKeyDown = (idx, e) => {
    if (e.key === 'Backspace' && !digits[idx] && idx > 0) {
      inputsRef.current[idx - 1]?.focus();
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    const code = digits.join('');
    if (code.length !== 6) {
      setError('Please enter the 6-digit code.');
      return;
    }
    setIsLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier, otp_code: code }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Verification failed');
      setMessage('Verified! Redirecting to login...');
      setTimeout(() => router.push('/login'), 1000);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setError('');
    setMessage('');
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/resend-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Could not resend');
      setMessage('Code resent! Check your email.');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center shiny-gradient-bg p-4">
      <div className="w-full max-w-md bg-gradient-to-br from-slate-800/80 to-slate-900/60 backdrop-blur-lg p-8 rounded-2xl shadow-3d-glow border border-purple-500/30 text-center">
  <h1 className="text-4xl font-orbitron font-bold text-white mb-1">Verify your account</h1>
  <p className="text-lg text-white font-semibold mb-1">{displayName}</p>
  <p className="text-gray-300 mb-6">Enter the 6-digit code sent to {identifier}</p>

        <form onSubmit={handleVerify}>
          <div className="flex justify-center gap-2 mb-6">
            {digits.map((d, i) => (
              <motion.input
                key={i}
                ref={(el) => (inputsRef.current[i] = el)}
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.2, delay: i * 0.03 }}
                className="w-12 h-14 text-center text-2xl rounded-md bg-slate-900/50 border border-gray-700 text-white focus:ring-2 focus:ring-purple-500 outline-none"
                maxLength={1}
                value={d}
                onChange={(e) => onChangeDigit(i, e.target.value)}
                onKeyDown={(e) => onKeyDown(i, e)}
              />
            ))}
          </div>
          {error && <p className="text-red-400 mb-2">{error}</p>}
          {message && <p className="text-green-400 mb-2">{message}</p>}
          <motion.button
            whileTap={{ scale: 0.95 }}
            disabled={isLoading}
            className="w-full py-3 font-bold text-white bg-gradient-to-r from-fuchsia-600 to-pink-600 rounded-md disabled:opacity-50"
          >
            {isLoading ? 'Verifying...' : 'Verify'}
          </motion.button>
        </form>

        <button onClick={handleResend} className="mt-4 text-sm text-purple-400 hover:text-purple-300">Resend code</button>
      </div>
    </main>
  );
}

export default function VerifyOtpPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <OtpForm />
    </Suspense>
  );
}
