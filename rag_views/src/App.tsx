import { useState } from 'react'
import './App.css'
import { Layout, Card, Typography, Space } from '@douyinfe/semi-ui'
import { IconBook, IconSearch, IconUpload } from '@douyinfe/semi-icons'
import FileUpload from './components/FileUpload'
import QueryForm from './components/QueryForm'
import ResultDisplay from './components/ResultDisplay'
import { uploadFile, query } from './services/api'

const { Header, Content } = Layout
const { Title, Text } = Typography

function App() {
  const [result, setResult] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileUpload = async (file: File) => {
    setLoading(true)
    setError(null)
    try {
      const response = await uploadFile(file)
      if (response.success) {
        alert(response.message)
      } else {
        setError(response.message)
      }
    } catch (err) {
      setError('文件上传失败，请重试')
      console.error('Upload error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleQuery = async (question: string) => {
    setLoading(true)
    setError(null)
    setResult('')
    try {
      const response = await query(question)
      if (response.success) {
        setResult(response.answer)
      } else {
        setError('查询失败，请重试')
      }
    } catch (err) {
      setError('查询失败，请检查网络连接')
      console.error('Query error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Header style={{ 
        background: '#fff', 
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)', 
        padding: '0 40px', 
        display: 'flex', 
        alignItems: 'center' 
      }}>
        <IconBook size="extra-large" style={{ marginRight: 16, color: '#1890ff' }} />
        <Title heading={2} style={{ margin: 0, color: '#333' }}>
          书籍RAG问答系统
        </Title>
      </Header>
      
      <Content style={{ padding: '40px', maxWidth: 1200, margin: '0 auto', width: '100%' }}>
        <Space vertical style={{ width: '100%', marginBottom: '24px' }}>
          <Card
            title={
              <Space align="center">
                <IconUpload size="large" style={{ color: '#1890ff' }} />
                <Text strong>上传书籍</Text>
              </Space>
            }
            style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)', borderRadius: '8px' }}
          >
            <FileUpload onFileUpload={handleFileUpload} />
          </Card>
          
          <Card
            title={
              <Space align="center">
                <IconSearch size="large" style={{ color: '#1890ff' }} />
                <Text strong>问题查询</Text>
              </Space>
            }
            style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)', borderRadius: '8px' }}
          >
            <QueryForm onQuerySubmit={handleQuery} isLoading={loading} />
          </Card>
          
          <Card
            title={<Text strong>查询结果</Text>}
            style={{ 
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)', 
              borderRadius: '8px', 
              minHeight: 300 
            }}
          >
            <ResultDisplay result={result} loading={loading} error={error} />
          </Card>
        </Space>
      </Content>
    </Layout>
  )
}

export default App
