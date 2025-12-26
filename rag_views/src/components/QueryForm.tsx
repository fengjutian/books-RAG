import React, { useState } from 'react';
import { Form, Button, Space } from '@douyinfe/semi-ui';
import { IconSearch } from '@douyinfe/semi-icons';

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
    <Form onSubmit={handleSubmit} layout="horizontal">
      <Space spacing={20} style={{ width: '100%', display: 'flex' }}>
        <Form.Input
          field="query"
          placeholder="输入您的问题..."
          disabled={isLoading}
          style={{ flex: 1, minWidth: 0 }}
          size="large"
          prefix={<IconSearch />}
          initValue={query}
          onChange={(value) => setQuery(value || '')}
        />
        <Button
          type="primary"
          theme="solid"
          htmlType="submit"
          loading={isLoading}
          disabled={isLoading || !query.trim()}
          size="large"
        >
          {isLoading ? '查询中...' : '查询'}
        </Button>
      </Space>
    </Form>
  );
};

export default QueryForm;
