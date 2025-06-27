import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { 
  ChartBarIcon, 
  BellIcon, 
  ClockIcon, 
  CheckCircleIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { monitoringRulesApi, notificationsApi, monitoringApi } from '../services/api';
import { useState } from 'react';

const stats = [
  { name: 'Total Rules', icon: ChartBarIcon, color: 'bg-blue-500' },
  { name: 'Active Rules', icon: CheckCircleIcon, color: 'bg-green-500' },
  { name: 'Notifications', icon: BellIcon, color: 'bg-yellow-500' },
  { name: 'Last Run', icon: ClockIcon, color: 'bg-purple-500' },
];

export function Dashboard() {
  const navigate = useNavigate();
  const [proxyConfig, setProxyConfig] = useState({
    host: '',
    port: '',
    user: '',
    pass: ''
  });
  
  // Fetch monitoring rules
  const { data: rules = [], isLoading: rulesLoading } = useQuery({
    queryKey: ['monitoring-rules'],
    queryFn: () => monitoringRulesApi.getAll(),
  });

  // Fetch notifications
  const { data: notifications = [], isLoading: notificationsLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.getAll(),
  });

  const activeRules = rules.filter(rule => rule.is_active);
  const recentNotifications = notifications.slice(0, 5);

  const handleViewAllRules = () => {
    navigate('/rules');
  };

  const handleNewRule = () => {
    navigate('/rules?tab=create');
  };

  const handleRunMonitoring = async () => {
    try {
      await monitoringApi.runMonitoring();
      // Optionally refresh the data after running monitoring
      // You could invalidate queries here if needed
    } catch (error) {
      console.error('Failed to run monitoring:', error);
    }
  };

  const handleTestScrape = async () => {
    try {
      const result = await testScrape({
        scraper_id: "search",
        params: {
          keyword: "silver ring",
          max_listings: 5
        }
      });

      if (result.success) {
        const proxyInfo = result.result.proxy_used ? " (with proxy)" : "";
        const dataInfo = result.result.data_optimized ? " (data optimized)" : "";
        const listingsCount = result.result.listings ? result.result.listings.length : 0;
        const totalResults = result.result.total_results || 0;
        
        if (listingsCount === 0) {
          alert(`Test scrape completed but no listings found.${proxyInfo}${dataInfo}\n\nThis could mean:\n• Etsy is blocking the request\n• The page structure has changed\n• A proxy is needed\n\nCheck the backend logs for more details.`);
        } else {
          alert(`Test scrape successful!${proxyInfo}${dataInfo}\n\nKeyword: ${result.result.keyword}\nTotal Results: ${totalResults}\nListings Found: ${listingsCount}\n\nCheck the backend logs for more details.`);
        }
      } else {
        const errorMsg = result.detail || result.result?.error || 'Unknown error';
        alert(`Test scrape failed: ${errorMsg}\n\nThis could be due to:\n• Etsy blocking the request\n• Network issues\n• Invalid parameters\n\nCheck the backend logs for more details.`);
      }
    } catch (error) {
      console.error('Test scrape failed:', error);
      alert('Test scrape failed. Check the console for details.');
    }
  };

  const handleTestProxy = async () => {
    try {
      const result = await testScrape({
        scraper_id: "proxy_test",
        params: {}
      });

      if (result.success) {
        const proxyInfo = result.result.proxy_used ? " (with proxy)" : " (NO PROXY)";
        const ipDetection = result.result.ip_detection || "Unknown";
        
        alert(`Proxy test completed!${proxyInfo}\n\nIP Detection: ${ipDetection}\nProxy Host: ${result.result.proxy_host}\nProxy Port: ${result.result.proxy_port}\n\nCheck the backend logs for detailed bot detection results.`);
      } else {
        const errorMsg = result.detail || result.result?.error || 'Unknown error';
        alert(`Proxy test failed: ${errorMsg}\n\nCheck the backend logs for more details.`);
      }
    } catch (error) {
      console.error('Proxy test failed:', error);
      alert('Proxy test failed. Check the console for details.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Overview of your Etsy monitoring activity
          </p>
        </div>
        <button
          onClick={handleNewRule}
          className="btn-primary flex items-center gap-x-2"
        >
          <PlusIcon className="h-4 w-4" />
          New Rule
        </button>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-6 w-6 text-blue-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Rules</p>
              <p className="text-2xl font-semibold text-gray-900">
                {rulesLoading ? '...' : rules.length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircleIcon className="h-6 w-6 text-green-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Rules</p>
              <p className="text-2xl font-semibold text-gray-900">
                {rulesLoading ? '...' : activeRules.length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BellIcon className="h-6 w-6 text-yellow-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Notifications</p>
              <p className="text-2xl font-semibold text-gray-900">
                {notificationsLoading ? '...' : notifications.length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClockIcon className="h-6 w-6 text-purple-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Last Run</p>
              <p className="text-sm font-semibold text-gray-900">
                {activeRules.length > 0 
                  ? new Date(activeRules[0].last_checked || '').toLocaleDateString()
                  : 'Never'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent rules */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Rules</h3>
          {rulesLoading ? (
            <div className="text-center py-4 text-gray-500">Loading...</div>
          ) : rules.length === 0 ? (
            <div className="text-center py-4 text-gray-500">No rules created yet</div>
          ) : (
            <div className="space-y-3">
              {rules.slice(0, 5).map((rule) => (
                <div key={rule.id} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{rule.rule_name}</p>
                    <p className="text-xs text-gray-500">
                      {rule.keyword || 'N/A'}
                    </p>
                  </div>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    rule.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {rule.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent notifications */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Notifications</h3>
          {notificationsLoading ? (
            <div className="text-center py-4 text-gray-500">Loading...</div>
          ) : recentNotifications.length === 0 ? (
            <div className="text-center py-4 text-gray-500">No notifications yet</div>
          ) : (
            <div className="space-y-3">
              {recentNotifications.map((notification) => (
                <div key={notification.id} className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <BellIcon className="h-5 w-5 text-yellow-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">{notification.message}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(notification.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="flex space-x-4">
          <button
            onClick={handleRunMonitoring}
            className="btn-primary"
          >
            Run Monitoring
          </button>
          <button 
            onClick={handleTestScrape}
            className="btn-secondary"
          >
            Test Scrape
          </button>
          <button 
            onClick={handleTestProxy}
            className="btn-secondary"
          >
            Test Proxy
          </button>
          <button 
            onClick={handleViewAllRules}
            className="btn-secondary"
          >
            View All Rules
          </button>
        </div>
      </div>
    </div>
  );
} 