'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function SignupPage() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [mobileNo, setMobileNo] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const [apiError, setApiError] = useState('');
  const [success, setSuccess] = useState('');
  const [emailStatus, setEmailStatus] = useState('');
  const [mobileStatus, setMobileStatus] = useState('');
  
  const [validationErrors, setValidationErrors] = useState({});
  
  const router = useRouter();

  const handleMobileChange = (e) => {
    const value = e.target.value;
    const numericValue = value.replace(/\D/g, '');
    setMobileNo(numericValue);
  };

  const handleMobileCheck = async () => {
    if (!mobileNo || mobileNo.length < 10) {
        setMobileStatus('');
        return;
    }
    try {
      const response = await fetch('http://127.0.0.1:8000/check-mobile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mobile_no: mobileNo }),
      });
      const data = await response.json();
      if (data.exists) {
        setMobileStatus("Mobile number already registered.");
      } else {
        setMobileStatus("");
      }
    } catch (err) {
      console.error("Mobile check failed", err);
      setMobileStatus("Could not verify mobile number.");
    }
  };

  const handleEmailCheck = async () => {
    if (!email) {
        setEmailStatus('');
        return;
    };
    try {
      const response = await fetch('http://127.0.0.1:8000/check-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await response.json();
      if (data.exists) {
        setEmailStatus("Email already registered. Please log in.");
      } else {
        setEmailStatus("");
      }
    } catch (err) {
      console.error("Email check failed", err);
      setEmailStatus("Could not verify email.");
    }
  };

  const validateForm = () => {
    const errors = {};
    if (!firstName) errors.firstName = 'First name is required.';
    if (!mobileNo) errors.mobileNo = 'Mobile number is required.';
    if (!email) errors.email = 'Email is required.';
    if (!password) errors.password = 'Password is required.';
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError('');
    setSuccess('');

    const isFormValid = validateForm();
    if (!isFormValid) return;

    if (emailStatus || mobileStatus) {
        setApiError("Please resolve the issues before signing up.");
        return;
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            first_name: firstName, 
            last_name: lastName, 
            mobile_no: mobileNo, 
            email, 
            password 
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create account');
      }
      
      const newUser = await response.json();
      router.push(`/signup-success?username=${newUser.username}&email=${newUser.email}`);

    } catch (err) {
      setApiError(err.message);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center shiny-gradient-bg p-4">
      <div className="w-full max-w-md bg-gradient-to-br from-slate-800/80 to-slate-900/60 backdrop-blur-lg p-8 rounded-2xl shadow-3d-glow border border-purple-500/30">
        <h1 className="text-4xl font-orbitron text-center font-bold text-white mb-8">
          Create Account
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          
          <div className="flex flex-col md:flex-row md:gap-4">
            <div className="w-full md:w-1/2">
              <label className="block text-sm font-medium text-gray-300">First Name <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                required
                className={`mt-1 w-full p-3 bg-slate-900/50 rounded-md border text-white focus:ring-2 focus:ring-purple-500 focus:outline-none ${validationErrors.firstName ? 'border-red-500' : 'border-gray-700'}`}
              />
            </div>
            <div className="w-full md:w-1/2 mt-4 md:mt-0">
              <label className="block text-sm font-medium text-gray-300">Last Name (Optional)</label>
              <input
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="mt-1 w-full p-3 bg-slate-900/50 rounded-md border border-gray-700 text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300">Mobile Number <span className="text-red-500">*</span></label>
            <input
              type="tel"
              value={mobileNo}
              onChange={handleMobileChange}
              onBlur={handleMobileCheck}
              maxLength="10"
              pattern="\d{10}"
              title="Please enter a 10-digit mobile number"
              required
              className={`mt-1 w-full p-3 bg-slate-900/50 rounded-md border text-white focus:ring-2 focus:ring-purple-500 focus:outline-none ${validationErrors.mobileNo ? 'border-red-500' : 'border-gray-700'}`}
            />
            {mobileStatus && <p className="text-yellow-400 text-xs mt-1">{mobileStatus}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300">Email <span className="text-red-500">*</span></label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onBlur={handleEmailCheck}
              required
              className={`mt-1 w-full p-3 bg-slate-900/50 rounded-md border text-white focus:ring-2 focus:ring-purple-500 focus:outline-none ${validationErrors.email ? 'border-red-500' : 'border-gray-700'}`}
            />
            {emailStatus && <p className="text-yellow-400 text-xs mt-1">{emailStatus}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300">Password <span className="text-red-500">*</span></label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className={`mt-1 w-full p-3 bg-slate-900/50 rounded-md border text-white focus:ring-2 focus:ring-purple-500 focus:outline-none ${validationErrors.password ? 'border-red-500' : 'border-gray-700'}`}
            />
          </div>

          {apiError && <p className="text-red-400 text-sm">{apiError}</p>}
          
          <div>
            <motion.button 
              whileTap={{ scale: 0.95 }}
              transition={{ duration: 0.1 }}
              type="submit" 
              className="w-full py-3 px-4 font-bold text-white bg-gradient-to-r from-fuchsia-600 to-pink-600 rounded-md hover:opacity-90 transition-opacity mt-2"
            >
              Sign Up
            </motion.button>
          </div>
        </form>
        <div className="text-center mt-6 space-y-2">
            <p className="text-xs text-yellow-400/80">
                Note: This application is in its alpha testing phase.
            </p>
            <p className="text-sm text-gray-400">
                Already have an account?{' '}
                <Link href="/login" className="font-medium text-purple-400 hover:text-purple-300">
                    Login
                </Link>
            </p>
        </div>
      </div>
    </main>
  );
}