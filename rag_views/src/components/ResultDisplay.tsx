import React from 'react';

interface ResultDisplayProps {
  result: string;
  loading: boolean;
  error: string | null;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, loading, error }) => {
  if (loading) {
    return <div className="result-display loading">正在查询...请稍候</div>;
  }

  if (error) {
    return <div className="result-display error">错误: {error}</div>;
  }

  return (
    <div className="result-display">
      <h3>查询结果</h3>
      <div className="result-content">
        {result ? result : '暂无结果，请输入问题进行查询'}
      </div>
    </div>
  );
};

export default ResultDisplay;