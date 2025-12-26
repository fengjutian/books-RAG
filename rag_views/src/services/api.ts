import axios from 'axios';

const API_BASE_URL = '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 文件上传API
export const uploadFile = async (file: File): Promise<{ success: boolean; message: string }> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

// 查询API
export const query = async (question: string): Promise<{ success: boolean; answer: string }> => {
  const response = await apiClient.post('/query', { question });
  return response.data;
};

// 获取已上传文件列表API
export const getFiles = async (): Promise<{ success: boolean; files: string[] }> => {
  const response = await apiClient.get('/files');
  return response.data;
};

export default {
  uploadFile,
  query,
  getFiles,
};
