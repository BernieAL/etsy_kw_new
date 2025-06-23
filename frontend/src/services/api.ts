import axios from 'axios';
import type { 
  MonitoringRule, 
  CreateMonitoringRuleForm, 
  Notification, 
  ScraperInfo,
  DashboardStats 
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Monitoring Rules API
export const monitoringRulesApi = {
  // Get all monitoring rules
  getAll: async (userEmail?: string): Promise<MonitoringRule[]> => {
    const params = userEmail ? { user_email: userEmail } : {};
    const response = await api.get('/monitoring-rules', { params });
    return response.data;
  },

  // Get a specific monitoring rule
  getById: async (ruleId: string): Promise<MonitoringRule> => {
    const response = await api.get(`/monitoring-rules/${ruleId}`);
    return response.data;
  },

  // Create a new monitoring rule
  create: async (ruleData: CreateMonitoringRuleForm): Promise<MonitoringRule> => {
    const response = await api.post('/monitoring-rules', ruleData);
    return response.data;
  },

  // Delete a monitoring rule
  delete: async (ruleId: string): Promise<void> => {
    await api.delete(`/monitoring-rules/${ruleId}`);
  },

  // Update a monitoring rule (if your backend supports it)
  update: async (ruleId: string, ruleData: Partial<CreateMonitoringRuleForm>): Promise<MonitoringRule> => {
    const response = await api.put(`/monitoring-rules/${ruleId}`, ruleData);
    return response.data;
  },
};

// Notifications API
export const notificationsApi = {
  // Get all notifications
  getAll: async (userEmail?: string): Promise<Notification[]> => {
    const params = userEmail ? { user_email: userEmail } : {};
    const response = await api.get('/notifications', { params });
    return response.data;
  },

  // Mark notification as read (if your backend supports it)
  markAsRead: async (notificationId: number): Promise<void> => {
    await api.patch(`/notifications/${notificationId}/read`);
  },
};

// Monitoring API
export const monitoringApi = {
  // Run monitoring cycle
  runMonitoring: async (): Promise<{ message: string }> => {
    const response = await api.post('/monitoring/run');
    return response.data;
  },

  // Get available scrapers
  getScrapers: async (): Promise<ScraperInfo[]> => {
    const response = await api.get('/scrapers');
    return response.data;
  },

  // Test a scraper
  testScraper: async (scraperId: string, params: Record<string, any>): Promise<any> => {
    const response = await api.post(`/scrapers/${scraperId}/test`, { params });
    return response.data;
  },
};

// Health check
export const healthApi = {
  check: async (): Promise<{ status: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

// Dashboard API
export const dashboardApi = {
  // Get dashboard statistics
  getStats: async (userEmail?: string): Promise<DashboardStats> => {
    const params = userEmail ? { user_email: userEmail } : {};
    const response = await api.get('/dashboard/stats', { params });
    return response.data;
  },
};

export default api; 