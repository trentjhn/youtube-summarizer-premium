import React, { useState } from 'react';
import PropTypes from 'prop-types';

const AIChatPanel = ({ videoData }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleSendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);
    
    try {
      // Call backend API to chat with video context
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          video_id: videoData.video_id,
          message: input,
          conversation_history: messages
        })
      });

      const data = await response.json();

      if (data.success) {
        setMessages([...messages, userMessage, { role: 'assistant', content: data.response }]);
      } else {
        // Handle API error response
        setMessages([...messages, userMessage, {
          role: 'assistant',
          content: `Error: ${data.error || 'Failed to get response. Please try again.'}`
        }]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      // Add error message to chat
      setMessages([...messages, userMessage, {
        role: 'assistant',
        content: 'Sorry, I encountered a network error. Please check your connection and try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="ai-chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-placeholder">
            <p>Ask me anything about this video!</p>
            <div className="suggested-questions">
              <button onClick={() => setInput("What are the main arguments?")}>
                What are the main arguments?
              </button>
              <button onClick={() => setInput("Summarize the key takeaways")}>
                Summarize the key takeaways
              </button>
            </div>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div key={`msg-${idx}-${msg.role}`} className={`chat-message chat-message--${msg.role}`}>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        
        {loading && <div className="chat-loading">Thinking...</div>}
      </div>
      
      <div className="chat-input">
        <input 
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Ask a question..."
        />
        <button onClick={handleSendMessage} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};

AIChatPanel.propTypes = {
  videoData: PropTypes.shape({
    video_id: PropTypes.string.isRequired,
    title: PropTypes.string,
    summary: PropTypes.object
  }).isRequired
};

export default AIChatPanel;

