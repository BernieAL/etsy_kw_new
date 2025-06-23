import { useQuery } from '@tanstack/react-query';
import { 
  ChartBarIcon, 
  BellIcon, 
  ClockIcon, 
  CheckCircleIcon 
} from '@heroicons/react/24/outline';
import { monitoringRulesApi, notificationsApi, monitoringApi } from '../services/api';

const stats = [
  { name: 'Total Rules', icon: ChartBarIcon, color: 'bg-blue-500' },
  { name: 'Active Rules', icon: CheckCircleIcon, color: 'bg-green-500' },
  { name: 'Notifications', icon: BellIcon, color: 'bg-yellow-500' },
  { name: 'Last Run', icon: ClockIcon, color: 'bg-purple-500' },
];

export function Dashboard() {
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

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your Etsy monitoring activity
        </p>
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
                      {rule.scraper_configs.map(config => config.params.keyword).join(', ')}
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
            onClick={() => monitoringApi.runMonitoring()}
            className="btn-primary"
          >
            Run Monitoring
          </button>
          <button className="btn-secondary">
            View All Rules
          </button>
        </div>
      </div>
    </div>
  );
} 