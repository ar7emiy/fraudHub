import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const api = {
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  getEntities: async (filters = {}) => {
    const response = await apiClient.get('/entities', { params: filters });
    return response.data;
  },

  getEntityDetails: async (entityName) => {
    const encodedName = encodeURIComponent(entityName);
    const response = await apiClient.get(`/entity/${encodedName}`);
    return response.data;
  },

  updateEntityStatus: async (entityName, status) => {
    const encodedName = encodeURIComponent(entityName);
    const response = await apiClient.put(`/entity/${encodedName}/status`, { status });
    return response.data;
  },

  getStatusHistory: async (entityName) => {
    const encodedName = encodeURIComponent(entityName);
    const response = await apiClient.get(`/entity/${encodedName}/status-history`);
    return response.data;
  },

  getCommunities: async () => {
    const response = await apiClient.get('/communities');
    return response.data;
  },

  getNetworkData: async () => {
    const response = await apiClient.get('/network-data');
    return response.data;
  },

  reloadData: async () => {
    const response = await apiClient.post('/reload');
    return response.data;
  }
};

export default api;