# React前端集成指南

本文档介绍如何为现有的PDF RAG FastAPI后端项目集成React前端。

## 一、项目初始化

推荐使用Vite创建React项目，因为它速度快、配置简单，适合现代React开发。

### 1. 安装Node.js

确保已安装Node.js (推荐版本 18.x 或更高)。可以从 [Node.js官网](https://nodejs.org/) 下载安装。

### 2. 使用Vite创建React项目

在项目根目录下执行以下命令：

```bash
# 在当前目录创建React项目
npm create vite@latest frontend -- --template react

# 进入前端目录
cd frontend

# 安装依赖
npm install

# 安装必要的额外依赖
npm install axios marked
```

## 二、前端目录结构设计

创建完成后，前端目录结构如下：

```
frontend/
├── public/                  # 静态资源
│   └── vite.svg
├── src/                     # 源代码
│   ├── assets/              # 图片、样式等资源
│   ├── components/          # React组件
│   │   ├── FileUpload.jsx   # 文件上传组件
│   │   ├── QueryForm.jsx    # 查询表单组件
│   │   └── ResultDisplay.jsx # 结果显示组件
│   ├── services/            # API服务
│   │   └── api.js           # API请求封装
│   ├── App.jsx              # 主应用组件
│   ├── main.jsx             # 应用入口
│   └── index.css            # 全局样式
├── .gitignore
├── index.html
├── package.json
├── vite.config.js           # Vite配置
└── README.md
```

## 三、与FastAPI后端集成

### 1. 配置Vite代理

修改 `frontend/vite.config.js` 文件，添加代理配置，解决跨域问题：

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### 2. 封装API服务

创建 `frontend/src/services/api.js` 文件，封装API请求：

```javascript
import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 60000, // 60秒超时
});

// 上传PDF文件
export const uploadPDF = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload_pdf/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// 发送查询请求
export const queryPDF = (question) => {
  return api.post('/query/', { text: question });
};

export default api;
```

## 四、关键组件实现

### 1. 文件上传组件 (`FileUpload.jsx`)

```javascript
import React, { useState } from 'react';
import { uploadPDF } from '../services/api';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
    } else {
      setStatus({ type: 'error', message: '请选择PDF文件' });
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsProcessing(true);
    setStatus({ type: 'success', message: '正在上传并处理PDF文档...' });

    try {
      const response = await uploadPDF(file);
      setStatus({
        type: 'success',
        message: `✅ PDF上传成功！已处理 ${response.data.chunks} 个文本块`,
      });
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message;
      setStatus({ type: 'error', message: `❌ ${errorMessage}` });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="upload-section">
      <div className="upload-icon">📄</div>
      <h3>上传PDF文档</h3>
      <p>拖拽文件到此处或点击下方按钮选择文件</p>
      <input
        type="file"
        id="fileInput"
        accept=".pdf"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
      <button
        className="upload-btn"
        onClick={() => document.getElementById('fileInput').click()}
        disabled={isProcessing}
      >
        选择PDF文件
      </button>
      {file && (
        <div className="file-info">
          已选择: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
        </div>
      )}
      {file && (
        <button
          className="upload-btn"
          onClick={handleUpload}
          disabled={isProcessing}
          style={{ marginTop: '10px' }}
        >
          {isProcessing ? '处理中...' : '上传并处理'}
        </button>
      )}
      {status && (
        <div className={`status ${status.type}`}>{status.message}</div>
      )}
    </div>
  );
};

export default FileUpload;
```

### 2. 查询表单组件 (`QueryForm.jsx`)

```javascript
import React, { useState } from 'react';

const QueryForm = ({ onSubmit }) => {
  const [question, setQuestion] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim() && !isSubmitting) {
      setIsSubmitting(true);
      onSubmit(question.trim())
        .finally(() => setIsSubmitting(false));
    }
  };

  return (
    <div className="query-form">
      <h3>💬 智能问答</h3>
      <form onSubmit={handleSubmit}>
        <textarea
          className="query-input"
          placeholder="请输入您的问题..."
          rows={4}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={isSubmitting}
        />
        <button
          type="submit"
          className="query-btn"
          disabled={isSubmitting || !question.trim()}
        >
          {isSubmitting ? '提问中...' : '提问'}
        </button>
      </form>
      {isSubmitting && (
        <div className="loading">
          <div className="spinner"></div>
          <p>AI正在思考中...</p>
        </div>
      )}
    </div>
  );
};

export default QueryForm;
```

### 3. 结果显示组件 (`ResultDisplay.jsx`)

```javascript
import React from 'react';
import { marked } from 'marked';

const ResultDisplay = ({ result }) => {
  if (!result) return null;

  const htmlContent = marked.parse(result.answer);

  return (
    <div className="result-section">
      <h3>🤖 AI回答</h3>
      <div
        className="result-content"
        dangerouslySetInnerHTML={{ __html: htmlContent }}
      />
    </div>
  );
};

export default ResultDisplay;
```

### 4. 主应用组件 (`App.jsx`)

```javascript
import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import QueryForm from './components/QueryForm';
import ResultDisplay from './components/ResultDisplay';
import { queryPDF } from './services/api';
import './App.css';

function App() {
  const [result, setResult] = useState(null);

  const handleQuery = async (question) => {
    try {
      const response = await queryPDF(question);
      setResult(response.data);
      return response;
    } catch (error) {
      setResult({
        answer: `❌ 查询失败：${error.response?.data?.detail || error.message}`,
      });
      throw error;
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>📚 PDF RAG 智能问答系统</h1>
        <p>上传PDF文档，向AI提问获取智能答案</p>
      </div>

      <div className="main-content">
        <div className="left-panel">
          <FileUpload />
          <QueryForm onSubmit={handleQuery} />
        </div>

        <div className="right-panel">
          <ResultDisplay result={result} />
        </div>
      </div>
    </div>
  );
}

export default App;
```

### 5. 样式文件 (`App.css`)

可以将现有的CSS样式从 `static/index.html` 中复制过来，并进行适当调整：

```css
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 15px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  padding: 40px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  color: #333;
  font-size: 2.5em;
  margin-bottom: 10px;
}

.header p {
  color: #666;
  font-size: 1.1em;
}

.main-content {
  display: flex;
  gap: 30px;
  margin-top: 30px;
}

.left-panel {
  flex: 1;
}

.right-panel {
  flex: 1;
}

/* 上传组件样式 */
.upload-section {
  border: 2px dashed #ddd;
  border-radius: 10px;
  padding: 30px;
  text-align: center;
  transition: all 0.3s ease;
  height: fit-content;
  margin-bottom: 30px;
}

.upload-section.dragover {
  border-color: #667eea;
  background-color: #f8f9ff;
}

.upload-icon {
  font-size: 48px;
  color: #667eea;
  margin-bottom: 20px;
}

.upload-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.upload-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.upload-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.file-info {
  margin-top: 15px;
  color: #666;
}

/* 查询表单样式 */
.query-form {
  margin-top: 30px;
}

.query-input {
  width: 100%;
  padding: 15px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 16px;
  margin-bottom: 15px;
  resize: vertical;
}

.query-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  width: 100%;
}

/* 结果显示样式 */
.result-section {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9ff;
  border-radius: 10px;
}

.result-section h3 {
  color: #333;
  margin-bottom: 15px;
}

.result-content {
  color: #333;
  line-height: 1.7;
  font-size: 15px;
}

/* 状态提示样式 */
.status {
  margin-top: 10px;
  padding: 10px;
  border-radius: 5px;
  text-align: center;
}

.status.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* 加载动画 */
.loading {
  margin-top: 20px;
  text-align: center;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 2s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 20px;
    max-width: 100%;
  }

  .main-content {
    flex-direction: column;
    gap: 20px;
  }

  .left-panel, .right-panel {
    flex: none;
  }

  .upload-section {
    padding: 20px;
  }

  .header h1 {
    font-size: 2em;
  }
}
```

## 三、后端集成配置

### 1. 修改FastAPI静态文件配置

修改 `app/main.py` 文件，确保静态文件目录正确配置：

```python
# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")
```

### 2. 修改主页面路由

```python
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """主页面 - 显示React应用"""
    with open("frontend/dist/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
```

## 四、构建和部署

### 1. 构建前端应用

在前端目录下执行：

```bash
cd frontend
npm run build
```

构建完成后，会生成 `frontend/dist` 目录，包含生产环境的静态文件。

### 2. 运行后端应用

在项目根目录下执行：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python -m uvicorn app.main:app --reload
```

然后访问 `http://localhost:8000` 即可看到React前端界面。

## 五、开发流程

### 1. 开发模式

在开发过程中，可以同时运行前端开发服务器和后端服务器：

```bash
# 前端开发服务器 (端口 5173)
cd frontend
npm run dev

# 后端服务器 (端口 8000)
python -m uvicorn app.main:app --reload
```

前端开发服务器会自动代理API请求到后端服务器。

### 2. 代码规范

- 使用ES6+语法
- 组件命名使用大驼峰式
- 文件命名使用小驼峰式
- 使用函数式组件和Hooks

## 六、扩展建议

1. **添加状态管理**：对于复杂应用，可以使用Redux或Context API进行状态管理
2. **添加用户认证**：如果需要，可以集成用户认证功能
3. **添加错误处理**：增强错误处理和用户提示
4. **添加进度条**：文件上传和查询时添加进度条
5. **添加主题切换**：支持浅色/深色主题
6. **添加响应式设计**：优化移动端体验

## 七、常见问题

### 1. 跨域问题

确保Vite配置中的代理设置正确，或者在FastAPI中添加CORS中间件：

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PDF RAG FastAPI")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 文件上传大小限制

修改FastAPI配置，增加文件上传大小限制：

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(title="PDF RAG FastAPI", max_request_size=100 * 1024 * 1024)  # 100MB
```

### 3. 构建路径问题

如果构建后静态资源路径不正确，可以修改 `vite.config.js` 中的 `base` 配置：

```javascript
export default defineConfig({
  base: '/static/',
  // 其他配置
})
```

---

通过以上步骤，您可以成功为PDF RAG FastAPI后端项目集成React前端，提供现代化的用户界面和更好的用户体验。