import React from 'react';
import { Upload, Button } from '@douyinfe/semi-ui';
import { IconUpload } from '@douyinfe/semi-icons';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
  // 由于我们只是将文件传递给父组件处理，而不是实际上传到服务器
  // 所以使用beforeUpload来捕获文件并阻止默认上传行为
  const handleBeforeUpload = (beforeUploadProps: any) => {
    // 由于Semi Design的Upload组件传递的是FileItem对象，我们需要获取原始的File对象
    const file = beforeUploadProps.file as File;
    onFileUpload(file);
    // 返回false阻止默认上传行为
    return false;
  };

  return (
    <Upload
      accept=".pdf,.txt,.docx"
      beforeUpload={handleBeforeUpload}
      showUploadList={false}
    >
      <Button theme="solid" type="primary" icon={<IconUpload />} size="large">
        选择文件上传
      </Button>
    </Upload>
  );
};

export default FileUpload;
