'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setMessage('');
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/forgot-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email }),
        });
        const data = await response.json();
        setMessage(data.message);
        setIsLoading(false);
    };

    return (
        <main className="flex min-h-screen flex-col items-center justify-center shiny-gradient-bg p-4">
            <div className="w-full max-w-md bg-gradient-to-br from-slate-800/80 to-slate-900/60 backdrop-blur-lg p-8 rounded-2xl shadow-3d-glow border border-purple-500/30 text-center">
                <h1 className="text-4xl font-orbitron text-white mb-4">Reset Password</h1>
                
                <AnimatePresence mode="wait">
                    {!message ? (
                        <motion.div
                            key="form"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                        >
                            <p className="text-gray-300 mb-8">Enter your email and we'll send a reset link.</p>
                            <form onSubmit={handleSubmit} className="space-y-6">
                                <input 
                                    type="email" 
                                    value={email} 
                                    onChange={(e) => setEmail(e.target.value)} 
                                    required 
                                    placeholder="your.email@example.com"
                                    className="w-full p-3 bg-slate-900/50 rounded-md border border-gray-700 text-white" 
                                />
                                <motion.button 
                                    whileTap={{ scale: 0.95 }}
                                    type="submit" 
                                    disabled={isLoading}
                                    className="w-full py-3 font-bold text-white bg-gradient-to-r from-fuchsia-600 to-pink-600 rounded-md disabled:opacity-50"
                                >
                                    {isLoading ? 'Sending...' : 'Send Reset Link'}
                                </motion.button>
                            </form>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="success"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.5 }}
                        >
                            <p className="text-green-400 mb-6 text-lg">{message}</p>
                            <Link href="/login" className="w-full inline-block py-3 font-bold text-white bg-white/10 border border-white/20 rounded-md hover:bg-white/20 transition-all">
                                Go to Login Page
                            </Link>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </main>
    );
}