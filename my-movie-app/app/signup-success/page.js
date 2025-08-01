'use client';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

// We wrap the component in a Suspense boundary because useSearchParams() requires it.
function SuccessContent() {
    const searchParams = useSearchParams();
    const username = searchParams.get('username');
    const email = searchParams.get('email');

    return (
        <main className="flex min-h-screen flex-col items-center justify-center shiny-gradient-bg p-4">
            <div className="w-full max-w-md bg-slate-800/80 backdrop-blur-sm p-8 rounded-2xl shadow-3d-glow border border-white/20 text-center">
                <h1 className="text-4xl font-orbitron font-bold text-green-400 mb-4">
                    Account Created!
                </h1>
                <p className="text-lg text-gray-300 mb-6">
                    Welcome to CineVerse AI. Your account has been successfully created.
                </p>
                <div className="bg-slate-900/50 p-4 rounded-md border border-gray-700 text-left mb-8">
                    <p className="text-md text-gray-400">Your auto-generated username is:</p>
                    <p className="text-2xl font-bold text-white text-center my-2">{username}</p>
                    <p className="text-sm text-gray-500 text-center">(You can use this or your email to log in)</p>
                </div>
                <Link href="/login" className="w-full inline-block py-3 px-4 font-bold text-white bg-gradient-to-r from-fuchsia-600 to-pink-600 rounded-md hover:opacity-90 transition-opacity">
                    Proceed to Login
                </Link>
            </div>
        </main>
    );
}

// The main export uses Suspense
export default function SignupSuccessPage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <SuccessContent />
        </Suspense>
    );
}