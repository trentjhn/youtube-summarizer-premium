import React from 'react';

const QuickTakeaway = ({ text }) => {
  return (
    <div className="quick-takeaway">
      <div className="quick-takeaway__icon">💡</div>
      <p className="quick-takeaway__text">{text}</p>
    </div>
  );
};

export default QuickTakeaway;

