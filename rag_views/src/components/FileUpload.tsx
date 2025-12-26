import React, { useState } from 'react';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
  const [file, setFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = () => {
    if (file) {
      onFileUpload(file);
      setFile(null);
    }
  };

  return (
    <div className="file-upload">
      <input type="file" onChange={handleFileChange} accept=".pdf,.txt,.docx" />
      <button onClick={handleUpload} disabled={!file}>
        上传文件
      </button>
      {file && <p>已选择: {file.name}</p>}
    </div>
  );
};

export default FileUpload;
