'use client';

import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [emailStatus, setEmailStatus] = useState('');
  const { login } = useAuth();
  const router = useRouter();

  const handleEmailCheck = async () => {
    if (!email) {
        setEmailStatus('');
        return;
    };
    try {
      const response = await fetch('http://127.0.0.1:8000/check-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await response.json();
      if (!data.exists) {
        setEmailStatus("Email not found. Please sign up.");
      } else {
        setEmailStatus("");
      }
    } catch (err) {
      console.error("Email check failed", err);
      setEmailStatus("Could not verify email.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch('http://127.0.0.1:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to login');
      }

      const userData = await response.json();
      login(userData);
      router.push('/chat');

    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center shiny-gradient-bg p-4">
      <div className="w-full max-w-md bg-slate-800/80 backdrop-blur-sm p-8 rounded-2xl shadow-3d-glow border border-white/20">
        <h1 className="text-4xl font-orbitron text-center font-bold text-white mb-8">
          Login
        </h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onBlur={handleEmailCheck}
              required
              className="mt-1 w-full p-3 bg-slate-900/50 rounded-md border border-gray-700 text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
            />
            {emailStatus && <p className="text-yellow-400 text-xs mt-1">{emailStatus}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 w-full p-3 bg-slate-900/50 rounded-md border border-gray-700 text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
            />
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <div>
            <button type="submit" className="w-full py-3 px-4 font-bold text-white bg-gradient-to-r from-fuchsia-600 to-pink-600 rounded-md hover:opacity-90 transition-opacity">
              Login
            </button>
          </div>
        </form>
        <p className="mt-6 text-center text-sm text-gray-400">
          Don't have an account?{' '}
          <Link href="/signup" className="font-medium text-purple-400 hover:text-purple-300">
            Sign up
          </Link>
        </p>
      </div>
    </main>
  );
}