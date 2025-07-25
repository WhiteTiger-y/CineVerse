'use client';

import React, { createContext, useState, useContext, useEffect } from 'react';

// Create the context
const AuthContext = createContext(null);

// Create the provider component
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  // Check localStorage for a logged-in user when the app loads
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedUser = localStorage.getItem('cineverse_user');
      if (savedUser) {
        setUser(JSON.parse(savedUser));
      }
    }
  }, []);

  // Login function
  const login = (userData) => {
    localStorage.setItem('cineverse_user', JSON.stringify(userData));
    setUser(userData);
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('cineverse_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use the auth context easily
export function useAuth() {
  return useContext(AuthContext);
}