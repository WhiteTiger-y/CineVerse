import Message from './Message';

export default function MessageList() {
  return (
    <div className="flex-grow p-4 overflow-y-auto">
      <Message sender="bot" text="Hi! I'm your movie sommelier. What are you in the mood for?" />
      <Message sender="user" text="I had a long week, just want something visually stunning but not too complicated." />
      <Message sender="bot" text="I understand. In that case, I'd recommend 'Avatar: The Way of Water'. It's a visual masterpiece with a straightforward story. How does that sound?" />
    </div>
  );
}