'use client';

import Link from 'next/link';
import { useAuth } from './context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function LandingPage() {
  const { user } = useAuth();
  const router = useRouter();

  // If the user is already logged in, redirect them to the chat page
  useEffect(() => {
    if (user) {
      router.push('/chat');
    }
  }, [user, router]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center shiny-gradient-bg text-white text-center p-8">
      <div className="bg-black/20 backdrop-blur-md p-10 rounded-2xl shadow-3d-glow border border-white/20">
        <h1 className="text-6xl font-orbitron font-bold mb-4 tracking-wider">
          CineVerse AI
        </h1>
        <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-8">
          Your personal movie sommelier. Engage in a conversation and discover the perfect film for any mood or occasion.
        </p>
        <div className="flex justify-center gap-4">
          <Link href="/login" className="px-8 py-3 font-bold text-white bg-gradient-to-r from-fuchsia-600 to-pink-600 rounded-md hover:opacity-90 transition-opacity">
              Login
          </Link>
          <Link href="/signup" className="px-8 py-3 font-bold text-white bg-white/10 border border-white/20 rounded-md hover:bg-white/20 transition-all">
              Sign Up
          </Link>
        </div>
      </div>
    </main>
  );
}