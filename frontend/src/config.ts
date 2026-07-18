// Centralized configuration for frontend connection to AWS backend stack
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');
export const AWS_REGION = import.meta.env.VITE_AWS_REGION || 'ap-south-1';
export const ORG_NAME = import.meta.env.VITE_ORG_NAME || 'demo-org-99';
