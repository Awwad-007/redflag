import axios from 'axios';
import type { AnalysisResult } from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000, // 2 min for AI analysis
});

export async function analyzeContract(file: File): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<AnalysisResult>('/api/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  return response.data;
}

export async function analyzeText(text: string): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append('text', text);

  const response = await api.post<AnalysisResult>('/api/analyze-text', formData);
  return response.data;
}

export default api;
