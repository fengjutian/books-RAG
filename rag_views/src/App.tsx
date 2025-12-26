import { useState } from 'react'
import './App.css'
import FileUpload from './components/FileUpload'
import QueryForm from './components/QueryForm'
import ResultDisplay from './components/ResultDisplay'
import { uploadFile, query } from './services/api'

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
    <div className="app-container">
      <header>
        <h1>书籍RAG问答系统</h1>
      </header>
      <main>
        <section className="upload-section">
          <h2>上传书籍</h2>
          <FileUpload onFileUpload={handleFileUpload} />
        </section>
        
        <section className="query-section">
          <h2>问题查询</h2>
          <QueryForm onQuerySubmit={handleQuery} isLoading={loading} />
        </section>
        
        <section className="result-section">
          <ResultDisplay result={result} loading={loading} error={error} />
        </section>
      </main>
    </div>
  )
}

export default App
