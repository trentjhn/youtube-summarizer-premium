import React, { useState } from 'react';

const NotesPanel = () => {
  const [notes, setNotes] = useState('');
  
  return (
    <div className="notes-panel">
      <div className="notes-panel__header">
        <h3>Your Notes</h3>
        <p className="notes-panel__subtitle">Take notes while reading</p>
      </div>
      
      <textarea
        className="notes-panel__textarea"
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Start typing your notes here..."
      />
      
      <div className="notes-panel__footer">
        <span className="notes-panel__count">
          {notes.length} characters
        </span>
      </div>
    </div>
  );
};

export default NotesPanel;

