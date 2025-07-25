import Message from './Message';

export default function MessageList({ messages }) {
  return (
    <div className="flex-grow p-4 overflow-y-auto">
      {messages.map((msg, index) => (
        <Message key={index} sender={msg.sender} text={msg.text} />
      ))}
    </div>
  );
}