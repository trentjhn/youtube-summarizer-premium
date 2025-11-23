import React from 'react';
import AIChatPanel from './AIChatPanel';
import NotesPanel from './NotesPanel';
import ExportPanel from './ExportPanel';

const RightSidebar = ({ activeTab, onTabChange, videoData }) => {
  return (
    <aside className="right-sidebar">
      <div className="right-sidebar__tabs">
        <button 
          className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => onTabChange('chat')}
        >
          AI Chat
        </button>
        <button 
          className={`tab ${activeTab === 'notes' ? 'active' : ''}`}
          onClick={() => onTabChange('notes')}
        >
          Notes
        </button>
        <button 
          className={`tab ${activeTab === 'export' ? 'active' : ''}`}
          onClick={() => onTabChange('export')}
        >
          Export
        </button>
      </div>
      
      <div className="right-sidebar__content">
        {activeTab === 'chat' && <AIChatPanel videoData={videoData} />}
        {activeTab === 'notes' && <NotesPanel />}
        {activeTab === 'export' && <ExportPanel videoData={videoData} />}
      </div>
    </aside>
  );
};

export default RightSidebar;

