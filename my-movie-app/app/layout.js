import { Inter, Orbitron } from 'next/font/google';
import './globals.css';
import { AuthProvider } from './context/AuthContext'; // Import the provider

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const orbitron = Orbitron({ subsets: ['latin'], weight: '700', variable: '--font-orbitron' });

export const metadata = {
  title: 'CineVerse AI',
  description: 'Your conversational movie recommender',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${orbitron.variable}`}>
        {/* Wrap your entire application with the AuthProvider */}
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}