import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import type { MonitoringRule, CreateMonitoringRuleForm } from '../types';

// Form validation schema
const ruleFormSchema = z.object({
  rule_name: z.string().min(1, 'Rule name is required'),
  user_email: z.string().email('Valid email is required'),
  scraper_configs: z.array(z.object({
    scraper_id: z.string(),
    params: z.object({
      keyword: z.string().min(1, 'Keyword is required'),
      max_listings: z.number().min(1).max(100).optional(),
    }),
  })).min(1, 'At least one scraper configuration is required'),
  schedule_interval: z.string().optional(),
  monitor_listing_count: z.boolean(),
  monitor_sellers: z.array(z.string()),
  monitor_price_changes: z.boolean(),
  monitor_inventory_changes: z.boolean(),
  monitor_description_changes: z.boolean(),
  notification_threshold: z.number().min(0),
});

type RuleFormData = z.infer<typeof ruleFormSchema>;

interface RuleFormProps {
  rule?: MonitoringRule;
  onSubmit: (data: CreateMonitoringRuleForm) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function RuleForm({ rule, onSubmit, onCancel, isLoading = false }: RuleFormProps) {
  const [sellers, setSellers] = useState<string[]>(rule?.monitor_sellers || []);
  const [newSeller, setNewSeller] = useState('');

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
    reset,
  } = useForm<RuleFormData>({
    resolver: zodResolver(ruleFormSchema),
    defaultValues: {
      rule_name: rule?.rule_name || '',
      user_email: rule?.user_email || '',
      scraper_configs: rule?.scraper_configs || [{ scraper_id: 'search', params: { keyword: '', max_listings: 20 } }],
      schedule_interval: rule?.schedule_interval || '3600',
      monitor_listing_count: rule?.monitor_listing_count || false,
      monitor_sellers: rule?.monitor_sellers || [],
      monitor_price_changes: rule?.monitor_price_changes || false,
      monitor_inventory_changes: rule?.monitor_inventory_changes || false,
      monitor_description_changes: rule?.monitor_description_changes || false,
      notification_threshold: rule?.notification_threshold || 5,
    },
  });

  const addSeller = () => {
    if (newSeller.trim() && !sellers.includes(newSeller.trim())) {
      setSellers([...sellers, newSeller.trim()]);
      setNewSeller('');
    }
  };

  const removeSeller = (sellerToRemove: string) => {
    setSellers(sellers.filter(seller => seller !== sellerToRemove));
  };

  const handleFormSubmit = (data: RuleFormData) => {
    onSubmit({
      ...data,
      monitor_sellers: sellers,
    });
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-6 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-medium text-gray-900">
            {rule ? 'Edit Rule' : 'Create New Rule'}
          </h3>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Rule Name *
              </label>
              <input
                type="text"
                {...register('rule_name')}
                className="input-field mt-1"
                placeholder="e.g., Pearl Necklace Monitor"
              />
              {errors.rule_name && (
                <p className="mt-1 text-sm text-red-600">{errors.rule_name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Email *
              </label>
              <input
                type="email"
                {...register('user_email')}
                className="input-field mt-1"
                placeholder="user@example.com"
              />
              {errors.user_email && (
                <p className="mt-1 text-sm text-red-600">{errors.user_email.message}</p>
              )}
            </div>
          </div>

          {/* Scraper Configuration */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Keywords *
            </label>
            <Controller
              name="scraper_configs.0.params.keyword"
              control={control}
              render={({ field }) => (
                <input
                  {...field}
                  type="text"
                  className="input-field"
                  placeholder="e.g., pearl necklace, silver ring"
                />
              )}
            />
            {errors.scraper_configs && (
              <p className="mt-1 text-sm text-red-600">{errors.scraper_configs.message}</p>
            )}
          </div>

          {/* Monitoring Options */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Monitoring Options</h4>
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  {...register('monitor_listing_count')}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">Monitor listing count changes</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  {...register('monitor_price_changes')}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">Monitor price changes</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  {...register('monitor_inventory_changes')}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">Monitor inventory changes</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  {...register('monitor_description_changes')}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">Monitor description changes</span>
              </label>
            </div>
          </div>

          {/* Seller Monitoring */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Monitor Specific Sellers
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={newSeller}
                onChange={(e) => setNewSeller(e.target.value)}
                className="input-field flex-1"
                placeholder="Enter seller name"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSeller())}
              />
              <button
                type="button"
                onClick={addSeller}
                className="btn-secondary"
              >
                Add
              </button>
            </div>
            {sellers.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {sellers.map((seller) => (
                  <span
                    key={seller}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                  >
                    {seller}
                    <button
                      type="button"
                      onClick={() => removeSeller(seller)}
                      className="ml-1 text-primary-600 hover:text-primary-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Notification Threshold */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Notification Threshold
            </label>
            <input
              type="number"
              {...register('notification_threshold', { valueAsNumber: true })}
              className="input-field mt-1"
              min="0"
              max="100"
            />
            <p className="mt-1 text-sm text-gray-500">
              Minimum change amount to trigger notifications
            </p>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={onCancel}
              className="btn-secondary"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : rule ? 'Update Rule' : 'Create Rule'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 