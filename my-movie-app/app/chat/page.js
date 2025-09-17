'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter } from 'next/navigation';
import MessageList from '../components/MessageList';
import InputBar from '../components/InputBar';
import Navbar from '../components/Navbar';

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
    return [{ sender: 'bot', text: `Welcome! How can I help find the perfect movie for you today?` }];
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
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(user?.access_token ? { 'Authorization': `Bearer ${user.access_token}` } : {})
        },
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
    <main className="flex flex-col h-screen w-screen shiny-gradient-bg">
      <Navbar user={user} handleLogout={handleLogout} />
      
      {/* This container will fill the remaining space and prevent page scroll */}
      <div className="flex-grow flex items-center justify-center p-4 overflow-hidden">
        <div className="w-full max-w-3xl h-full bg-transparent rounded-2xl flex flex-col drop-shadow-3d-glow">
          
          {/* This is now the ONLY scrollable element */}
          <div className="flex-grow bg-chat-area dotted-texture overflow-y-auto rounded-t-2xl">
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
      </div>
    </main>
  );
}
