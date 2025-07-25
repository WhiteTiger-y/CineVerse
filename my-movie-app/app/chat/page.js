'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter } from 'next/navigation';
import MessageList from '../components/MessageList';
import InputBar from '../components/InputBar';

export default function ChatPage() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const [messages, setMessages] = useState(() => {
    if (typeof window !== 'undefined') {
      const savedMessages = localStorage.getItem('chatMessages');
      if (savedMessages && savedMessages.length > 2) {
        return JSON.parse(savedMessages);
      }
    }
    return [{ sender: 'bot', text: `Welcome to CineVerse! How can I help find the perfect movie for you today?` }];
  });

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('chatMessages', JSON.stringify(messages));
    }
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!user || !user.user_id) {
      console.error("Cannot send message: User or User ID is missing.");
      setMessages((prev) => [...prev, { sender: 'bot', text: "Error: You are not logged in correctly. Please try refreshing or logging in again." }]);
      return;
    }

    if (!input.trim() || isLoading) return;

    const userMessage = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          session_id: String(user.user_id),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Network response was not ok');
      }

      const botData = await response.json();
      const botMessage = { sender: 'bot', text: botData.message };
      setMessages((prev) => [...prev, botMessage]);

    } catch (error) {
      console.error('API call failed:', error);
      const errorMessage = {
        sender: 'bot',
        text: `Sorry, an error occurred: ${error.message}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    setMessages([{ sender: 'bot', text: "Welcome to CineVerse AI!" }]);
    router.push('/login');
  };

  if (!user) {
    return null;
  }

  return (
    <main className="flex min-h-screen items-center justify-center shiny-gradient-bg p-4">
      <div
        className="w-full max-w-3xl h-[85vh] bg-transparent rounded-2xl flex flex-col transition-all duration-300 hover:scale-[1.03] drop-shadow-3d-glow"
      >
        <div className="p-4 rounded-t-2xl shadow-lg bg-title-dark flex justify-between items-center">
          <h1 className="text-2xl font-orbitron text-center font-bold text-white/90 tracking-widest">
            CineVerse AI
          </h1>
          <button onClick={handleLogout} className="text-sm text-gray-300 hover:text-white transition-colors duration-200">
            Logout
          </button>
        </div>
        
        <div className="flex-grow bg-chat-area dotted-texture overflow-y-auto">
          <MessageList messages={messages} />
        </div>

        {isLoading && (
          <div className="p-2 text-sm text-pink-300 animate-pulse bg-chat-area text-center">
            Bot is typing...
          </div>
        )}
        <InputBar
          input={input}
          setInput={setInput}
          handleSendMessage={handleSendMessage}
        />
      </div>
    </main>
  );
}