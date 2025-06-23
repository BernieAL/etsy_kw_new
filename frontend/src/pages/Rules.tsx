import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  EyeIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { monitoringRulesApi } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { RuleForm } from '../components/RuleForm';
import type { MonitoringRule, CreateMonitoringRuleForm } from '../types';

export function Rules() {
  const [selectedRule, setSelectedRule] = useState<MonitoringRule | null>(null);
  const [activeTab, setActiveTab] = useState<'list' | 'create'>('list');
  const [showEditForm, setShowEditForm] = useState(false);
  const queryClient = useQueryClient();

  // Fetch monitoring rules
  const { data: rules = [], isLoading, error } = useQuery({
    queryKey: ['monitoring-rules'],
    queryFn: () => monitoringRulesApi.getAll(),
  });

  // Create rule mutation
  const createMutation = useMutation({
    mutationFn: (ruleData: CreateMonitoringRuleForm) => monitoringRulesApi.create(ruleData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-rules'] });
      setActiveTab('list');
    },
  });

  // Update rule mutation
  const updateMutation = useMutation({
    mutationFn: ({ ruleId, ruleData }: { ruleId: string; ruleData: Partial<CreateMonitoringRuleForm> }) => 
      monitoringRulesApi.update(ruleId, ruleData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-rules'] });
      setShowEditForm(false);
      setSelectedRule(null);
    },
  });

  // Delete rule mutation
  const deleteMutation = useMutation({
    mutationFn: (ruleId: string) => monitoringRulesApi.delete(ruleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-rules'] });
    },
  });

  const handleCreateRule = (data: CreateMonitoringRuleForm) => {
    createMutation.mutate(data);
  };

  const handleUpdateRule = (data: CreateMonitoringRuleForm) => {
    if (selectedRule) {
      updateMutation.mutate({ ruleId: selectedRule.id, ruleData: data });
    }
  };

  const handleDeleteRule = (ruleId: string) => {
    if (confirm('Are you sure you want to delete this rule?')) {
      deleteMutation.mutate(ruleId);
    }
  };

  const handleEditRule = (rule: MonitoringRule) => {
    setSelectedRule(rule);
    setShowEditForm(true);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Monitoring Rules</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your Etsy monitoring rules and configurations
          </p>
        </div>
        <button
          onClick={() => setActiveTab('create')}
          className="btn-primary flex items-center gap-x-2"
        >
          <PlusIcon className="h-4 w-4" />
          New Rule
        </button>
      </div>

      {/* Error Banner - Shows in both tabs */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400" aria-hidden="true" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Error loading monitoring rules
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error.message || 'Failed to load monitoring rules. Please try again later.'}</p>
              </div>
              <div className="mt-4">
                <button
                  onClick={() => window.location.reload()}
                  className="bg-red-50 text-red-700 hover:bg-red-100 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('list')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'list'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Existing Rules
          </button>
          <button
            onClick={() => setActiveTab('create')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'create'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Create New Rule
          </button>
        </nav>
      </div>

      {/* Rules List Tab */}
      {activeTab === 'list' && (
        <div className="card">
          {rules.length === 0 ? (
            <div className="text-center py-12">
              <div className="mx-auto h-12 w-12 text-gray-400">
                <CheckCircleIcon className="h-12 w-12" />
              </div>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No rules</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating your first monitoring rule.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setActiveTab('create')}
                  className="btn-primary"
                >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  New Rule
                </button>
              </div>
            </div>
          ) : (
            <div className="overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rule Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Keywords
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Checked
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {rules.map((rule) => (
                    <tr key={rule.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {rule.rule_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {rule.user_email}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {rule.scraper_configs.map(config => 
                            config.params.keyword || 'N/A'
                          ).join(', ')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          rule.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {rule.is_active ? (
                            <>
                              <CheckCircleIcon className="h-3 w-3 mr-1" />
                              Active
                            </>
                          ) : (
                            <>
                              <XCircleIcon className="h-3 w-3 mr-1" />
                              Inactive
                            </>
                          )}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {rule.last_checked 
                          ? new Date(rule.last_checked).toLocaleDateString()
                          : 'Never'
                        }
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => setSelectedRule(rule)}
                            className="text-primary-600 hover:text-primary-900"
                            title="View details"
                          >
                            <EyeIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleEditRule(rule)}
                            className="text-gray-600 hover:text-gray-900"
                            title="Edit rule"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteRule(rule.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Delete rule"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Create Rule Form Tab */}
      {activeTab === 'create' && (
        <div className="card">
          <RuleForm
            onSubmit={handleCreateRule}
            onCancel={() => setActiveTab('list')}
            isLoading={createMutation.isPending}
          />
        </div>
      )}

      {/* Edit Rule Modal */}
      {showEditForm && selectedRule && (
        <RuleForm
          rule={selectedRule}
          onSubmit={handleUpdateRule}
          onCancel={() => {
            setShowEditForm(false);
            setSelectedRule(null);
          }}
          isLoading={updateMutation.isPending}
        />
      )}

      {/* Rule Details Modal */}
      {selectedRule && !showEditForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">Rule Details</h3>
                <button
                  onClick={() => setSelectedRule(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircleIcon className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-3 text-sm">
                <div>
                  <strong>Name:</strong> {selectedRule.rule_name}
                </div>
                <div>
                  <strong>Email:</strong> {selectedRule.user_email}
                </div>
                <div>
                  <strong>Keywords:</strong> {selectedRule.scraper_configs.map(config => 
                    config.params.keyword || 'N/A'
                  ).join(', ')}
                </div>
                <div>
                  <strong>Status:</strong> {selectedRule.is_active ? 'Active' : 'Inactive'}
                </div>
                <div>
                  <strong>Created:</strong> {new Date(selectedRule.created_at).toLocaleDateString()}
                </div>
                {selectedRule.last_checked && (
                  <div>
                    <strong>Last Checked:</strong> {new Date(selectedRule.last_checked).toLocaleDateString()}
                  </div>
                )}
                {selectedRule.monitor_sellers.length > 0 && (
                  <div>
                    <strong>Monitored Sellers:</strong> {selectedRule.monitor_sellers.join(', ')}
                  </div>
                )}
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => handleEditRule(selectedRule)}
                  className="btn-primary"
                >
                  Edit Rule
                </button>
                <button
                  onClick={() => setSelectedRule(null)}
                  className="btn-secondary"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 