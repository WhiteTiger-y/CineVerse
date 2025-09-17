'use client';

import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function LoginPage() {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier: identifier, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to login');
      }

  const userData = await response.json();
  // Persist access_token for subsequent authenticated requests
  login(userData);
      router.push('/chat');

    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center shiny-gradient-bg p-4">
      <div className="w-full max-w-md bg-gradient-to-br from-slate-800/80 to-slate-900/60 backdrop-blur-lg p-8 rounded-2xl shadow-3d-glow border border-purple-500/30">
        <h1 className="text-4xl font-orbitron text-center font-bold text-white mb-8">
          Login
        </h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300">Email or Username</label>
            <input
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
              className="mt-1 w-full p-3 bg-slate-900/50 rounded-md border border-gray-700 text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
            />
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
           <div className="text-right text-sm">
              <Link href="/forgot-password" className="font-medium text-purple-400 hover:text-purple-300">
                Forgot password?
              </Link>
            </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <div>
            <motion.button 
              whileTap={{ scale: 0.95 }}
              transition={{ duration: 0.1 }}
              type="submit" 
              className="w-full py-3 px-4 font-bold text-white bg-gradient-to-r from-fuchsia-600 to-pink-600 rounded-md hover:opacity-90 transition-opacity"
            >
              Login
            </motion.button>
          </div>
        </form>
        <div className="text-center mt-6 space-y-2">
            <p className="text-xs text-yellow-400/80">
                Note: This application is in its alpha testing phase.
            </p>
            <p className="text-sm text-gray-400">
                Don&apos;t have an account?{' '}
                <Link href="/signup" className="font-medium text-purple-400 hover:text-purple-300">
                    Sign up
                </Link>
            </p>
        </div>
      </div>
    </main>
  );
}