import React, { useState } from 'react';

const ExportPanel = ({ videoData }) => {
  const [exportFormat, setExportFormat] = useState('markdown');
  const [copied, setCopied] = useState(false);
  
  const exportAsMarkdown = () => {
    if (!videoData || !videoData.summary) return '';
    
    const summary = videoData.summary;
    let markdown = `# ${videoData.title}\n\n`;
    
    // Quick Takeaway
    markdown += `## Quick Takeaway\n\n${summary.quick_takeaway}\n\n`;
    
    // Key Points
    if (summary.key_points && summary.key_points.length > 0) {
      markdown += `## Key Points\n\n`;
      summary.key_points.forEach(point => {
        markdown += `- ${point}\n`;
      });
      markdown += '\n';
    }
    
    // Topics
    if (summary.topics && summary.topics.length > 0) {
      markdown += `## Topics\n\n`;
      summary.topics.forEach((topic, index) => {
        markdown += `${index + 1}. ${topic.topic_name}\n`;
      });
      markdown += '\n';
    }
    
    // Timestamps
    if (summary.timestamps && summary.timestamps.length > 0) {
      markdown += `## Key Moments\n\n`;
      summary.timestamps.forEach(ts => {
        markdown += `- **${ts.time}** - ${ts.description}\n`;
      });
      markdown += '\n';
    }
    
    // Full Summary
    markdown += `## Full Summary\n\n`;
    if (summary.full_summary && summary.full_summary.length > 0) {
      summary.full_summary.forEach(para => {
        markdown += `${para.content}\n\n`;
      });
    }
    
    return markdown;
  };
  
  const exportAsJSON = () => {
    if (!videoData) return '';
    return JSON.stringify(videoData, null, 2);
  };
  
  const exportAsText = () => {
    if (!videoData || !videoData.summary) return '';
    
    const summary = videoData.summary;
    let text = `${videoData.title}\n\n`;
    text += `${summary.quick_takeaway}\n\n`;
    
    if (summary.full_summary && summary.full_summary.length > 0) {
      summary.full_summary.forEach(para => {
        text += `${para.content}\n\n`;
      });
    }
    
    return text;
  };
  
  const getExportContent = () => {
    switch (exportFormat) {
      case 'markdown':
        return exportAsMarkdown();
      case 'json':
        return exportAsJSON();
      case 'text':
        return exportAsText();
      default:
        return '';
    }
  };
  
  const handleCopy = async () => {
    const content = getExportContent();
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };
  
  const handleDownload = () => {
    const content = getExportContent();
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${videoData.video_id}_summary.${exportFormat === 'json' ? 'json' : exportFormat === 'markdown' ? 'md' : 'txt'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  return (
    <div className="export-panel">
      <div className="export-panel__header">
        <h3>Export Summary</h3>
        <p className="export-panel__subtitle">Download or copy in your preferred format</p>
      </div>
      
      <div className="export-panel__format-selector">
        <label>Format:</label>
        <select 
          value={exportFormat} 
          onChange={(e) => setExportFormat(e.target.value)}
          className="export-panel__select"
        >
          <option value="markdown">Markdown (.md)</option>
          <option value="text">Plain Text (.txt)</option>
          <option value="json">JSON (.json)</option>
        </select>
      </div>
      
      <div className="export-panel__preview">
        <label>Preview:</label>
        <pre className="export-panel__preview-content">
          {getExportContent().substring(0, 500)}...
        </pre>
      </div>
      
      <div className="export-panel__actions">
        <button 
          onClick={handleCopy}
          className="btn btn-secondary"
        >
          {copied ? '✓ Copied!' : 'Copy to Clipboard'}
        </button>
        <button 
          onClick={handleDownload}
          className="btn btn-primary"
        >
          Download File
        </button>
      </div>
    </div>
  );
};

export default ExportPanel;

