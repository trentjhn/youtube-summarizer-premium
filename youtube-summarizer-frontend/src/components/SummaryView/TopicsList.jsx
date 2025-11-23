import React from 'react';

const TopicsList = ({ topics, onClick }) => {
  return (
    <ul className="topics-list">
      {topics.map((topic, index) => (
        <li 
          key={index}
          className="topic-item"
          onClick={() => onClick && onClick(topic.summary_section_id)}
        >
          <span className="topic-number">{index + 1}</span>
          <span className="topic-name">{topic.topic_name}</span>
        </li>
      ))}
    </ul>
  );
};

export default TopicsList;

