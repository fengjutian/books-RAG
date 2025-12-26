import React, { useState } from 'react';

interface QueryFormProps {
  onQuerySubmit: (query: string) => void;
  isLoading: boolean;
}

const QueryForm: React.FC<QueryFormProps> = ({ onQuerySubmit, isLoading }) => {
  const [query, setQuery] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onQuerySubmit(query.trim());
      setQuery('');
    }
  };

  return (
    <form className="query-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="输入您的问题..."
          disabled={isLoading}
        />
      </div>
      <button type="submit" disabled={isLoading || !query.trim()}>
        {isLoading ? '查询中...' : '查询'}
      </button>
    </form>
  );
};

export default QueryForm;