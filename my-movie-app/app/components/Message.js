import { motion } from 'framer-motion';

export default function Message({ sender, text }) {
  const isUser = sender === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-lg px-5 py-3 rounded-2xl shadow-lg ${
          isUser
            // 4. "Blackish-pink" gradient for the user message
            ? 'bg-gradient-to-br from-fuchsia-900 via-pink-800 to-fuchsia-900 text-white rounded-br-none'
            // Bot bubble matches the glass theme
            : 'bg-slate-700/50 text-gray-200 rounded-bl-none'
        }`}
      >
        <p className="leading-relaxed">{text}</p>
      </div>
    </motion.div>
  );
}