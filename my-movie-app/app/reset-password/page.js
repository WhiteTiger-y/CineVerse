'use client';

import { useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';

function ResetPasswordForm() {
    const searchParams = useSearchParams();
    const token = searchParams.get('token');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');

        if (newPassword !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        setIsLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/reset-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, new_password: newPassword }),
            });
            const data = await response.json();
            if(response.ok) {
                setMessage(data.message);
                setError('');
            } else {
                setError(data.detail);
                setMessage('');
            }
        } catch (err) {
            setError("An unexpected error occurred.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="flex min-h-screen flex-col items-center justify-center shiny-gradient-bg p-4">
            <div className="w-full max-w-md bg-gradient-to-br from-slate-800/80 to-slate-900/60 backdrop-blur-lg p-8 rounded-2xl shadow-3d-glow border border-purple-500/30 text-center">
                <h1 className="text-4xl font-orbitron text-white mb-8">Set New Password</h1>

                <AnimatePresence mode="wait">
                    {!message ? (
                        <motion.div
                            key="form"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                        >
                            <form onSubmit={handleSubmit} className="space-y-6">
                                <div>
                                    <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="Enter your new password" required className="w-full p-3 bg-slate-900/50 rounded-md border border-gray-700 text-white" />
                                </div>
                                <div>
                                    <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Confirm new password" required className="w-full p-3 bg-slate-900/50 rounded-md border border-gray-700 text-white" />
                                </div>

                                {error && <p className="text-red-400 text-sm">{error}</p>}
                                <motion.button 
                                    whileTap={{ scale: 0.95 }}
                                    type="submit" 
                                    disabled={isLoading}
                                    className="w-full py-3 font-bold text-white bg-gradient-to-r from-fuchsia-600 to-pink-600 rounded-md disabled:opacity-50"
                                >
                                    {isLoading ? 'Updating...' : 'Update Password'}
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

// The main export uses Suspense to handle the useSearchParams hook
export default function ResetPasswordPage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <ResetPasswordForm />
        </Suspense>
    );
}