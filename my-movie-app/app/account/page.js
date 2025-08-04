'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function AccountPage() {
    const { user, login } = useAuth();
    const router = useRouter();

    const [newUsername, setNewUsername] = useState('');
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        if (!user) {
            router.push('/login');
        } else {
            setNewUsername(user.username);
        }
    }, [user, router]);

    const handleUsernameUpdate = async (e) => {
        e.preventDefault();
        setMessage(''); 
        setError('');
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/account/username`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user.user_id, new_username: newUsername }),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Failed to update username.");
            
            login(data);
            setMessage('Username updated successfully!');
        } catch (err) {
            // Correctly set the error message string
            setError(err.message);
        }
    };
    
    const handlePasswordUpdate = async (e) => {
        e.preventDefault();
        setMessage(''); 
        setError('');

        if (newPassword !== confirmPassword) {
            setError("New passwords do not match.");
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/account/password', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    user_id: user.user_id, 
                    old_password: oldPassword, 
                    new_password: newPassword 
                }),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Failed to update password.");
            
            setMessage(data.message);
            setOldPassword('');
            setNewPassword('');
            setConfirmPassword('');
        } catch (err) {
            // Correctly set the error message string
            setError(err.message);
        }
    };

    if (!user) {
        return null;
    }

    return (
        <main className="flex min-h-screen flex-col items-center justify-center shiny-gradient-bg p-4">
            <div className="w-full max-w-2xl bg-gradient-to-br from-slate-800/80 to-slate-900/60 backdrop-blur-lg p-8 rounded-2xl shadow-3d-glow border border-purple-500/30">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-4xl font-orbitron font-bold text-white">Account Management</h1>
                    <Link href="/chat" className="text-sm text-purple-400 hover:text-purple-300">← Back to Chat</Link>
                </div>

                {message && <p className="text-green-400 text-center mb-4">{message}</p>}
                {error && <p className="text-red-400 text-center mb-4">{error}</p>}

                {/* Profile Picture Section (Placeholder) */}
                <div className="mb-8 p-6 bg-slate-900/50 rounded-lg">
                    <h2 className="text-2xl font-bold text-white mb-4">Profile Picture</h2>
                    <p className="text-gray-400">Profile picture upload functionality is coming soon!</p>
                </div>

                {/* Username Change Form */}
                <form onSubmit={handleUsernameUpdate} className="mb-8 p-6 bg-slate-900/50 rounded-lg">
                    <h2 className="text-2xl font-bold text-white mb-4">Change Username</h2>
                    <label className="block text-sm font-medium text-gray-300">New Username</label>
                    <div className="flex gap-2 mt-1">
                        <input
                            type="text"
                            value={newUsername}
                            onChange={(e) => setNewUsername(e.target.value)}
                            maxLength="16"
                            required
                            className="flex-grow p-3 bg-slate-800/70 rounded-md border border-gray-700 text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
                        />
                        <button type="submit" className="px-6 py-2 font-bold text-white bg-purple-600 rounded-md hover:bg-purple-700 transition-colors">Save</button>
                    </div>
                </form>

                {/* Password Change Form */}
                <form onSubmit={handlePasswordUpdate} className="p-6 bg-slate-900/50 rounded-lg space-y-4">
                     <h2 className="text-2xl font-bold text-white mb-4">Change Password</h2>
                     <div>
                        <label className="block text-sm font-medium text-gray-300">Current Password</label>
                        <input type="password" value={oldPassword} onChange={(e) => setOldPassword(e.target.value)} required className="mt-1 w-full p-3 bg-slate-800/70 rounded-md border border-gray-700 text-white"/>
                     </div>
                     <div>
                        <label className="block text-sm font-medium text-gray-300">New Password</label>
                        <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required className="mt-1 w-full p-3 bg-slate-800/70 rounded-md border border-gray-700 text-white"/>
                     </div>
                     <div>
                        <label className="block text-sm font-medium text-gray-300">Confirm New Password</label>
                        <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required className="mt-1 w-full p-3 bg-slate-800/70 rounded-md border border-gray-700 text-white"/>
                     </div>
                     <button type="submit" className="w-full py-3 font-bold text-white bg-gradient-to-r from-fuchsia-600 to-pink-600 rounded-md hover:opacity-90 transition-opacity">Change Password</button>
                </form>
            </div>
        </main>
    );
}