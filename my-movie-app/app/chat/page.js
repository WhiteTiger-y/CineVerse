'use client';

import { useEffect, useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter } from 'next/navigation';
import Navbar from '../components/Navbar';
import MessageList from '../components/MessageList';
import InputBar from '../components/InputBar';
import EmotionCapture from '../components/EmotionCapture';

  const { user, logout } = useAuth();
  const router = useRouter();

  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState('');
  const [messages, setMessages] = useState([{ sender: 'bot', text: 'Welcome! How are you feeling today?' }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [context, setContext] = useState({ mood: '', expression: '', age: '', gender: '' });
  const [pollMs, setPollMs] = useState(200);
  const [webcamActive, setWebcamActive] = useState(false);
  const [detectionLog, setDetectionLog] = useState([]);
  const detectionTimer = useRef(null);

  // Redirect if not logged in
  useEffect(() => {
    if (!user) router.push('/login');
  }, [user, router]);

  // Load sessions on mount
  useEffect(() => {
    const loadSessions = async () => {
      if (!user?.access_token) return;
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/sessions`, {
        headers: { Authorization: `Bearer ${user.access_token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
        const last = typeof window !== 'undefined' ? localStorage.getItem('activeSessionId') : '';
        const initial = last || data[0]?.session_id || '';
        setActiveSessionId(initial);
      }
    };
    loadSessions();
  }, [user?.access_token]);

  // Persist active session
  useEffect(() => {
    if (typeof window !== 'undefined' && activeSessionId) {
      localStorage.setItem('activeSessionId', activeSessionId);
    }
  }, [activeSessionId]);

  // Load messages for the active session
  useEffect(() => {
    const loadMessages = async () => {
      if (!user?.access_token || !activeSessionId) return;
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/messages?session_id=${encodeURIComponent(activeSessionId)}`,
        { headers: { Authorization: `Bearer ${user.access_token}` } }
      );
      if (res.ok) {
        const data = await res.json();
        const mapped = data.map((m) => ({ sender: m.sender === 'bot' ? 'bot' : 'user', text: m.message }));
        setMessages(mapped.length ? mapped : [{ sender: 'bot', text: 'New chat started. How is your day going?' }]);
      } else {
        setMessages([{ sender: 'bot', text: 'New chat started. How is your day going?' }]);
      }
    };
    loadMessages();
  }, [user?.access_token, activeSessionId]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!user?.access_token) return;
    if (!input.trim() || isLoading) return;

    const userMessage = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    // Ensure we have a session id; create one if needed
    let sid = activeSessionId;
    if (!sid) {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/session`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${user.access_token}` },
        });
        if (res.ok) {
          const data = await res.json();
          sid = data.session_id;
          setActiveSessionId(sid);
          // refresh sessions list
          const sessionsRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/sessions`, {
            headers: { Authorization: `Bearer ${user.access_token}` },
          });
          if (sessionsRes.ok) setSessions(await sessionsRes.json());
        }
      } catch {}
    }
    const payload = {
      message: input,
      session_id: sid,
      mood: context.mood || undefined,
      expression: context.expression || undefined,
      age: context.age ? Number(context.age) : undefined,
      gender: context.gender || undefined,
    };
    setInput('');
    setIsLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${user.access_token}`,
        },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Request failed');
      }
      const botData = await response.json();
      setMessages((prev) => [...prev, { sender: 'bot', text: botData.message }]);
    } catch (err) {
      setMessages((prev) => [...prev, { sender: 'bot', text: `Sorry, an error occurred: ${err.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const handleNewChat = async () => {
    if (!user?.access_token) return;
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/session`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${user.access_token}` },
    });
    if (res.ok) {
      const data = await res.json();
      setActiveSessionId(data.session_id);
      setMessages([{ sender: 'bot', text: 'New chat started. How are you feeling today?' }]);
      const sessionsRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/sessions`, {
        headers: { Authorization: `Bearer ${user.access_token}` },
      });
      if (sessionsRes.ok) setSessions(await sessionsRes.json());
    }
  };

  const handleDeleteChat = async (sid) => {
    if (!user?.access_token) return;
    if (!confirm('Delete this chat? This cannot be undone.')) return;
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/session/${encodeURIComponent(sid)}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${user.access_token}` },
    });
    if (res.ok) {
      const filtered = sessions.filter((s) => s.session_id !== sid);
      setSessions(filtered);
      if (activeSessionId === sid) {
        const next = filtered[0]?.session_id || '';
        setActiveSessionId(next);
        setMessages([{ sender: 'bot', text: next ? 'Switched chat.' : 'Chat deleted. Start a new one?' }]);
      }
    }
  };

  if (!user) return null;

  return (
    <main className="flex flex-col h-screen w-screen shiny-gradient-bg">
      <Navbar user={user} handleLogout={handleLogout} />
      <div className="flex-grow flex items-center justify-center p-4 overflow-hidden">
        <div className="w-full max-w-6xl h-full bg-transparent rounded-2xl flex gap-4 drop-shadow-3d-glow relative min-h-0">
          {/* Sidebar */}
          <aside className="w-80 bg-slate-800/40 rounded-2xl p-3 border border-white/10 flex flex-col min-h-0 max-h-full">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-white font-semibold">Chats</h2>
              <button onClick={handleNewChat} className="text-xs px-2 py-1 bg-white/10 border border-white/20 rounded text-white hover:bg-white/20">New</button>
            </div>
            <div className="flex-1 min-h-0 max-h-48 overflow-y-auto space-y-1">
              {sessions.map((s) => (
                <div
                  key={s.session_id}
                  className={`group p-2 rounded cursor-pointer ${activeSessionId === s.session_id ? 'bg-white/15' : 'hover:bg-white/10'}`}
                  onClick={() => setActiveSessionId(s.session_id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-white truncate max-w-[160px]">{s.title || 'New Chat'}</div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteChat(s.session_id);
                      }}
                      className="opacity-60 group-hover:opacity-100 text-xs text-red-300 hover:text-red-200"
                    >
                      Delete
                    </button>
                  </div>
                  {s.last_message_preview && (
                    <div className="text-xs text-gray-300 truncate">{s.last_message_preview}</div>
                  )}
                </div>
              ))}
              {sessions.length === 0 && (
                <div className="text-xs text-gray-300">No chats yet.</div>
              )}
            </div>

            <div className="mt-3 border-t border-white/10 pt-2 space-y-2 overflow-y-auto max-h-72">
              <div className="text-white text-sm">Context</div>
              <input
                placeholder="Mood (e.g., calm)"
                value={context.mood}
                onChange={(e) => setContext((c) => ({ ...c, mood: e.target.value }))}
                className="w-full p-1 text-sm bg-black/30 text-white rounded border border-white/20"
              />
              <input
                placeholder="Expression (e.g., happy)"
                value={context.expression}
                readOnly={webcamActive}
                className={`w-full p-1 text-sm bg-black/30 text-white rounded border border-white/20 ${webcamActive ? 'opacity-60 cursor-not-allowed' : ''}`}
              />
              <div className="flex gap-1">
                <input
                  placeholder="Age"
                  value={context.age}
                  readOnly={webcamActive}
                  className={`w-1/2 p-1 text-sm bg-black/30 text-white rounded border border-white/20 ${webcamActive ? 'opacity-60 cursor-not-allowed' : ''}`}
                />
                <input
                  placeholder="Gender"
                  value={context.gender}
                  readOnly={webcamActive}
                  className={`w-1/2 p-1 text-sm bg-black/30 text-white rounded border border-white/20 ${webcamActive ? 'opacity-60 cursor-not-allowed' : ''}`}
                />
              </div>
              <div className="flex items-center justify-between text-xs text-gray-300">
                <label>Polling</label>
                <select
                  className="p-1 bg-black/30 text-white rounded border border-white/20"
                  value={pollMs}
                  onChange={(e) => setPollMs(Number(e.target.value))}
                >
                  <option value={100}>Fast (100ms)</option>
                  <option value={200}>Normal (200ms)</option>
                  <option value={500}>Slow (500ms)</option>
                </select>
              </div>
              <EmotionCapture
                intervalMs={pollMs}
                onChange={(data) => {
                  // If webcam is running, update context and log every 5 or 10 seconds
                  if (data && (data.expression || data.age || data.gender)) {
                    setContext((c) => ({ ...c, ...data }));
                  }
                }}
                setWebcamActive={setWebcamActive}
              />
              {/* Detection log */}
              {webcamActive && (
                <div className="mt-2 max-h-32 overflow-y-auto bg-black/20 rounded p-2 text-xs text-white border border-white/10">
                  <div className="mb-1 font-semibold text-[11px] text-gray-300">Detection Log</div>
                  {detectionLog.length === 0 ? (
                    <div className="text-gray-400">No detections yet.</div>
                  ) : (
                    detectionLog.map((log, i) => (
                      <div key={i} className="mb-1">
                        <span className="text-gray-400">[{log.time}]</span> Expression: <span className="text-pink-200">{log.expression || '-'}</span>, Age: <span className="text-blue-200">{log.age || '-'}</span>, Gender: <span className="text-green-200">{log.gender || '-'}</span>
                      </div>
                    ))
                  )}
                </div>
              )}
  // Log detections every 5 or 10 seconds when webcam is active
  useEffect(() => {
    if (!webcamActive) {
      if (detectionTimer.current) clearInterval(detectionTimer.current);
      return;
    }
    detectionTimer.current = setInterval(() => {
      setDetectionLog((log) => [
        ...log,
        {
          time: new Date().toLocaleTimeString(),
          expression: context.expression,
          age: context.age,
          gender: context.gender,
        },
      ].slice(-20)); // keep last 20 logs
    }, pollMs >= 10000 ? 10000 : 5000); // every 5s or 10s
    return () => {
      if (detectionTimer.current) clearInterval(detectionTimer.current);
    };
  }, [webcamActive, context.expression, context.age, context.gender, pollMs]);
            </div>
          </aside>

          {/* Chat area + input stacked */}
          <div className="flex flex-col flex-grow bg-chat-area dotted-texture rounded-2xl min-h-0 max-h-full w-full">
            <div className="flex-grow overflow-y-auto">
              <MessageList messages={messages} />
            </div>
            {isLoading && (
              <div className="p-2 text-sm text-pink-300 animate-pulse bg-chat-area text-center rounded-t-lg">
                Bot is typing...
              </div>
            )}
            <InputBar input={input} setInput={setInput} handleSendMessage={handleSendMessage} />
          </div>
        </div>
      </div>
    </main>
  );
}
