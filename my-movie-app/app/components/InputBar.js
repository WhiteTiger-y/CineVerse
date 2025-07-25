export default function InputBar({ input, setInput, handleSendMessage }) {
  return (
    <div className="p-4 bg-chat-area/50 backdrop-blur-sm rounded-b-2xl border-t border-white/10">
      <form onSubmit={handleSendMessage} className="flex items-center gap-3">
        {/* 1. Input field is now its own "glass" element */}
        <input
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-grow p-3 bg-black/30 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 placeholder-gray-500 border border-white/20"
        />
        {/* 2. The new floating "glass" button */}
        <button
          type="submit"
          className="font-bold px-6 py-3 text-white bg-white/10 border border-white/20 rounded-lg shadow-lg backdrop-blur-sm hover:bg-white/20 transition-all duration-200"
        >
          Send
        </button>
      </form>
    </div>
  );
}