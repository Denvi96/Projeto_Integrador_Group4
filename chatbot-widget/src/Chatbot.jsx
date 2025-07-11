import React, { useState } from 'react';

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { from: 'bot', text: 'Olá! Sou o JP, assistente virtual. Em que posso ajudar?' }
  ]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { from: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);

    // Chama sua API FastAPI
    try {
      const res = await fetch('http://localhost:8000/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto: input }),
      });
      const data = await res.json();

      const botMessage = { from: 'bot', text: data.resposta };
      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      const errorMsg = { from: 'bot', text: 'Erro na comunicação com o servidor.' };
      setMessages(prev => [...prev, errorMsg]);
    }
    setInput('');
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', fontFamily: 'Arial, sans-serif' }}>
      <div style={{
        height: 400,
        border: '1px solid #ccc',
        borderRadius: 8,
        padding: 10,
        overflowY: 'auto',
        marginBottom: 10,
        background: '#f9f9f9'
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            textAlign: msg.from === 'user' ? 'right' : 'left',
            margin: '10px 0'
          }}>
            <span style={{
              display: 'inline-block',
              padding: '8px 12px',
              borderRadius: 20,
              background: msg.from === 'user' ? '#4a90e2' : '#e2e2e2',
              color: msg.from === 'user' ? 'white' : 'black',
              maxWidth: '80%'
            }}>
              {msg.text}
            </span>
          </div>
        ))}
      </div>
      <input
        type="text"
        placeholder="Digite sua pergunta..."
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={onKeyDown}
        style={{
          width: '100%',
          padding: 10,
          borderRadius: 8,
          border: '1px solid #ccc',
          fontSize: 16,
          boxSizing: 'border-box'
        }}
      />
    </div>
  );
}
