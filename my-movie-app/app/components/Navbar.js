'use client';

import Link from 'next/link';

export default function Navbar({ user, handleLogout }) {
  return (
    <nav className="w-full bg-title-dark shadow-lg p-4">
      <div className="max-w-5xl mx-auto flex justify-between items-center">
        {/* Left Side: Title and Welcome Message */}
        <div>
          <h1 className="text-xl md:text-2xl font-orbitron font-bold text-white/90 tracking-widest">
            CineVerse AI
          </h1>
          <p className="text-xs text-gray-400">
            Welcome, {user?.username}
          </p>
        </div>

        {/* Right Side: Account and Logout Buttons */}
        <div className="flex items-center gap-4">
          <Link href="/account" className="text-sm font-medium text-gray-300 hover:text-white bg-white/10 px-4 py-2 rounded-md transition-colors duration-200">
            Account
          </Link>
          <button onClick={handleLogout} className="text-sm font-medium text-gray-300 hover:text-white transition-colors duration-200">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}