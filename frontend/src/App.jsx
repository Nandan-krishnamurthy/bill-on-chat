import { useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [businessId, setBusinessId] = useState("demo-business");
  const [mode, setMode] = useState("owner");

  const handleSend = async () => {
    if (!message.trim()) return;

    const userMessage = message;

    setMessages((prev) => [
      ...prev,
      {
        sender: "You",
        text: userMessage,
      },
    ]);

    setMessage("");

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          business_id: businessId,
          mode: mode,
          message: userMessage,
        }),
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          sender: "Bot",
          text: data.reply_text,
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          sender: "Bot",
          text: "Failed to reach backend.",
        },
      ]);
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-shell">
        <h1 className="chat-title">Bill-on-Chat</h1>

        <div className="chat-controls">
          <div className="chat-control-group">
            <label className="chat-control-label" htmlFor="business-id">Business ID</label>
            <input
              id="business-id"
              className="chat-control-input"
              type="text"
              value={businessId}
              onChange={(e) => setBusinessId(e.target.value)}
            />
          </div>
          <div className="chat-control-group">
            <label className="chat-control-label" htmlFor="mode">Mode</label>
            <select
              id="mode"
              className="chat-control-select"
              value={mode}
              onChange={(e) => setMode(e.target.value)}
            >
              <option value="owner">owner</option>
              <option value="customer">customer</option>
            </select>
          </div>
        </div>

        <div className="chat-messages" role="log" aria-live="polite">
          {messages.map((msg, index) => (
            <div key={index} className="chat-bubble">
              <strong>{msg.sender}:</strong> {msg.text}
            </div>
          ))}
        </div>

        <div className="chat-input-wrap">
          <input
            className="chat-input"
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type a message..."
          />

          <button className="chat-send" onClick={handleSend}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;