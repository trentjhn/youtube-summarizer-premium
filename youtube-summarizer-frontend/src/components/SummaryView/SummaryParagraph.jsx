import React from 'react';

const SummaryParagraph = ({ paragraph, isHighlighted }) => {
  return (
    <div 
      id={`paragraph-${paragraph.id}`}
      className={`summary-paragraph ${isHighlighted ? 'highlighted' : ''}`}
    >
      <p>{paragraph.content}</p>
    </div>
  );
};

export default SummaryParagraph;

