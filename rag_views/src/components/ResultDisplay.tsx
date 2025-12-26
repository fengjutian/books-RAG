import React from 'react';
import { Spin, Typography, Empty } from '@douyinfe/semi-ui';
import { IconInfoCircle } from '@douyinfe/semi-icons';

interface ResultDisplayProps {
  result: string;
  loading: boolean;
  error: string | null;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, loading, error }) => {
  const { Paragraph } = Typography;

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: 200, 
        width: '100%' 
      }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        padding: '16px', 
        backgroundColor: '#fff1f0', 
        border: '1px solid #ffccc7', 
        borderRadius: '4px',
        color: '#f5222d'
      }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <IconInfoCircle style={{ marginRight: '8px' }} />
          <div>
            <div style={{ fontWeight: 'bold' }}>查询失败</div>
            <div>{error}</div>
          </div>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: 200, 
        width: '100%' 
      }}>
        <Empty
          description="暂无结果，请输入问题进行查询"
        >
          <IconInfoCircle style={{ fontSize: 48, color: '#ccc' }} />
        </Empty>
      </div>
    );
  }

  return (
    <div style={{ padding: '16px 0' }}>
      <Paragraph
        style={{ 
          lineHeight: 1.8, 
          fontSize: 16, 
          whiteSpace: 'pre-wrap', 
          wordBreak: 'break-word' 
        }}
      >
        {result}
      </Paragraph>
    </div>
  );
};

export default ResultDisplay;
