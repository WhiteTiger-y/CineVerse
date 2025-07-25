/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)'],
        orbitron: ['var(--font-orbitron)'],
      },
      colors: {
        'title-dark': '#20002e',
        'chat-area': '#2a1136',
      },
      dropShadow: {
        '3d-glow': [
          '0 30px 20px rgba(0, 0, 0, 0.4)',      // A dark shadow for depth
          '0 0px 50px rgba(225, 0, 255, 0.4)' // A vibrant purple glow
        ]
      }
    },
  },
  plugins: [],
};