'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/use-auth';

interface GustoConnectionStatus {
  connected: boolean;
  company_name?: string;
  last_sync?: string;
  token_expires_at?: string;
}

interface SyncResponse {
  success: boolean;
  message: string;
  synced_entries: number;
  skipped_entries: number;
  errors: string[];
}

export default function GustoIntegrationPage() {
  const { user, getAccessToken } = useAuth();
  const [connectionStatus, setConnectionStatus] = useState<GustoConnectionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);
  const [syncResult, setSyncResult] = useState<SyncResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Fetch connection status on component mount
  useEffect(() => {
    fetchConnectionStatus();
  }, []);

  const fetchConnectionStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = await getAccessToken();
      const response = await fetch('/api/v1/gusto/status', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch status: ${response.statusText}`);
      }

      const status = await response.json();
      setConnectionStatus(status);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch connection status');
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    try {
      setConnecting(true);
      setError(null);

      const token = await getAccessToken();
      const response = await fetch('/api/v1/gusto/authorize', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to initiate connection: ${response.statusText}`);
      }

      const { authorization_url } = await response.json();
      
      // Redirect to Gusto OAuth
      window.location.href = authorization_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initiate Gusto connection');
    } finally {
      setConnecting(false);
    }
  };

  const handleSync = async () => {
    try {
      setSyncing(true);
      setError(null);
      setSyncResult(null);

      const token = await getAccessToken();
      const response = await fetch('/api/v1/gusto/sync', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Sync failed: ${response.statusText}`);
      }

      const result = await response.json();
      setSyncResult(result);
      
      // Refresh connection status after successful sync
      if (result.success) {
        await fetchConnectionStatus();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to sync salary data');
    } finally {
      setSyncing(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect your Gusto account? This will remove access to your payroll data.')) {
      return;
    }

    try {
      setDisconnecting(true);
      setError(null);

      const token = await getAccessToken();
      const response = await fetch('/api/v1/gusto/disconnect', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to disconnect: ${response.statusText}`);
      }

      // Refresh status after disconnect
      await fetchConnectionStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to disconnect Gusto account');
    } finally {
      setDisconnecting(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2">Loading Gusto integration status...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Gusto Integration</h1>
              <p className="text-gray-600 mt-1">
                Connect your Gusto payroll account to automatically sync salary data
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">G</span>
              </div>
              <span className="font-semibold text-gray-900">Gusto</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Error Alert */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <span className="text-red-500 text-xl">⚠️</span>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="mt-1 text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Sync Result Alert */}
        {syncResult && (
          <div className={`border rounded-lg p-4 ${
            syncResult.success 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <span className={`text-xl ${
                  syncResult.success ? 'text-green-500' : 'text-red-500'
                }`}>
                  {syncResult.success ? '✅' : '❌'}
                </span>
              </div>
              <div className="ml-3">
                <h3 className={`text-sm font-medium ${
                  syncResult.success ? 'text-green-800' : 'text-red-800'
                }`}>
                  {syncResult.success ? 'Sync Successful' : 'Sync Failed'}
                </h3>
                <p className={`mt-1 text-sm ${
                  syncResult.success ? 'text-green-700' : 'text-red-700'
                }`}>
                  {syncResult.message}
                </p>
                {syncResult.success && (
                  <div className="mt-2 text-sm text-green-700">
                    <p>• Synced: {syncResult.synced_entries} entries</p>
                    <p>• Skipped: {syncResult.skipped_entries} entries</p>
                    {syncResult.errors.length > 0 && (
                      <p>• Errors: {syncResult.errors.length}</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Connection Status Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              {connectionStatus?.connected ? (
                <span className="text-green-500 mr-2">✅</span>
              ) : (
                <span className="text-red-500 mr-2">❌</span>
              )}
              Connection Status
            </h2>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              connectionStatus?.connected 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {connectionStatus?.connected ? 'Connected' : 'Not Connected'}
            </span>
          </div>

          <p className="text-gray-600 mb-4">Current status of your Gusto integration</p>

          {connectionStatus?.connected && (
            <div className="space-y-3 pt-4 border-t border-gray-200">
              {connectionStatus.company_name && (
                <div className="flex justify-between">
                  <span className="font-medium text-gray-700">Company</span>
                  <span className="text-gray-900">{connectionStatus.company_name}</span>
                </div>
              )}

              {connectionStatus.last_sync && (
                <div className="flex justify-between">
                  <span className="font-medium text-gray-700">Last Sync</span>
                  <span className="text-gray-900">{formatDate(connectionStatus.last_sync)}</span>
                </div>
              )}

              {connectionStatus.token_expires_at && (
                <div className="flex justify-between">
                  <span className="font-medium text-gray-700">Token Expires</span>
                  <span className="text-gray-900">{formatDate(connectionStatus.token_expires_at)}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Actions Card */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Actions</h2>
          <p className="text-gray-600 mb-6">Manage your Gusto integration and sync salary data</p>

          {!connectionStatus?.connected ? (
            <button 
              onClick={handleConnect} 
              disabled={connecting}
              className="btn-primary w-full flex items-center justify-center"
            >
              {connecting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Connecting...
                </>
              ) : (
                <>
                  <span className="mr-2">🔗</span>
                  Connect Gusto Account
                </>
              )}
            </button>
          ) : (
            <div className="space-y-3">
              <button 
                onClick={handleSync} 
                disabled={syncing}
                className="btn-primary w-full flex items-center justify-center"
              >
                {syncing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Syncing...
                  </>
                ) : (
                  <>
                    <span className="mr-2">🔄</span>
                    Sync Salary Data
                  </>
                )}
              </button>

              <button 
                onClick={handleDisconnect} 
                disabled={disconnecting}
                className="btn-outline w-full flex items-center justify-center"
              >
                {disconnecting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                    Disconnecting...
                  </>
                ) : (
                  <>
                    <span className="mr-2">🔓</span>
                    Disconnect Account
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Information Card */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">About Gusto Integration</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start space-x-3">
              <span className="text-green-500 text-2xl">💰</span>
              <div>
                <h4 className="font-medium text-gray-900">Automatic Salary Sync</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Import your current and historical salary data directly from Gusto
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <span className="text-blue-500 text-2xl">📅</span>
              <div>
                <h4 className="font-medium text-gray-900">Historical Data</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Access your complete compensation history for accurate analysis
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <span className="text-purple-500 text-2xl">🔒</span>
              <div>
                <h4 className="font-medium text-gray-900">Secure Connection</h4>
                <p className="text-sm text-gray-600 mt-1">
                  OAuth 2.0 with PKCE ensures your data remains secure
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <span className="text-orange-500 text-2xl">⚡</span>
              <div>
                <h4 className="font-medium text-gray-900">Real-time Updates</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Keep your WageLift data synchronized with your payroll
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="font-medium text-gray-900 mb-3">Data Privacy & Security</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                All tokens are encrypted and stored securely
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                Only compensation data is accessed, no personal information
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                You can disconnect at any time
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                Data is used only for salary analysis within WageLift
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
} 