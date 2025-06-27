// API Response Types
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

// Monitoring Rule Types
export interface MonitoringRule {
  id: string;
  rule_name: string;
  keyword: string;
  user_email: string;
  scraper_configs?: ScraperConfig[];
  schedule_interval?: string;
  monitor_listing_count: boolean;
  monitor_sellers: string[];
  monitor_price_changes: boolean;
  monitor_inventory_changes: boolean;
  monitor_description_changes: boolean;
  notification_threshold: number;
  created_at: string;
  last_checked?: string;
  is_active: boolean;
}

export interface ScraperConfig {
  scraper_id: string;
  params: Record<string, any>;
}

// Form Types
export interface CreateMonitoringRuleForm {
  rule_name: string;
  user_email: string;
  scraper_configs: ScraperConfig[];
  schedule_interval?: string;
  monitor_listing_count: boolean;
  monitor_sellers: string[];
  monitor_price_changes: boolean;
  monitor_inventory_changes: boolean;
  monitor_description_changes: boolean;
  notification_threshold: number;
}

// Notification Types
export interface Notification {
  id: number;
  rule_id: string;
  notification_type: string;
  message: string;
  created_at: string;
  keyword: string;
  user_email: string;
}

// Scraper Types
export interface ScraperInfo {
  scraper_id: string;
  name: string;
  description: string;
  required_params: string[];
}

// Dashboard Stats
export interface DashboardStats {
  total_rules: number;
  active_rules: number;
  total_notifications: number;
  unread_notifications: number;
  last_monitoring_run?: string;
}

// Historical Data
export interface HistoricalData {
  id: number;
  rule_id: string;
  scraper_results: ScraperResult[];
  scraped_at: string;
}

export interface ScraperResult {
  scraper_id: string;
  total_results?: number;
  listings?: Listing[];
  error?: string;
}

export interface Listing {
  id: string;
  title: string;
  price: string;
  shop: string;
  url: string;
  image_url?: string;
} 