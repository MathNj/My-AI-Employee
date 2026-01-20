'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface Process {
  id: number;
  pid: number;
  name: string;
  status: string;
  cpu: number;
  memory: number;
  uptime: number;
  restarts: number;
  mode: string;
}

interface LogEntry {
  timestamp: string;
  process: string;
  processId: string;
  level: string;
  message: string;
}

export default function OverviewPage() {
  const router = useRouter();
  const [processes, setProcesses] = useState<Process[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [procsRes, logsRes] = await Promise.all([
        fetch('/api/processes'),
        fetch('/api/logs?lines=10')
      ]);
      const procsData = await procsRes.json();
      const logsData = await logsRes.json();

      setProcesses(procsData);
      setLogs(logsData.logs || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const formatBytes = (bytes: number): string => {
    if (!bytes) return '0 MB';
    const mb = bytes / (1024 * 1024);
    return mb >= 1024 ? `${(mb / 1024).toFixed(1)} GB` : `${mb.toFixed(1)} MB`;
  };

  const formatUptime = (seconds: number): string => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const hours = Math.floor(mins / 60);
    return hours > 0 ? `${hours}h ${mins % 60}m` : `${mins}m`;
  };

  const onlineCount = processes.filter(p => p.status === 'online').length;
  const totalCpu = processes.reduce((sum, p) => sum + p.cpu, 0);
  const totalMem = processes.reduce((sum, p) => sum + p.memory, 0);

  return (
    <div className="min-h-screen bg-black font-mono text-xs" style={{
      fontFamily: 'JetBrains Mono, Fira Code, Roboto Mono, monospace'
    }}>
      {/* Animated background */}
      <div className="fixed inset-0 opacity-5 pointer-events-none">
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(rgba(0, 255, 255, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
          animation: 'gridMove 20s linear infinite'
        }}></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-cyan-400 animate-pulse mb-2">:: DIGITAL_EMPLOYEE_DASHBOARD ::</h1>
              <p className="text-gray-500 text-sm">Personal AI Employee System Monitor v2.0</p>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${onlineCount > 0 ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
              <span className={`text-sm ${onlineCount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {onlineCount > 0 ? 'SYSTEM ONLINE' : 'SYSTEM OFFLINE'}
              </span>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-900/50 border border-cyan-500/30 rounded-lg p-4 backdrop-blur-sm hover:border-cyan-400 transition-all duration-300 group">
            <div className="text-gray-500 text-[10px] mb-1">PROCESSES</div>
            <div className="text-2xl font-bold text-cyan-400 group-hover:scale-110 transition-transform">{processes.length}</div>
            <div className="text-[8px] text-gray-600 mt-1">Total monitored</div>
          </div>
          <div className="bg-gray-900/50 border border-green-500/30 rounded-lg p-4 backdrop-blur-sm hover:border-green-400 transition-all duration-300 group">
            <div className="text-gray-500 text-[10px] mb-1">ONLINE</div>
            <div className="text-2xl font-bold text-green-400 group-hover:scale-110 transition-transform">{onlineCount}</div>
            <div className="text-[8px] text-gray-600 mt-1">Active processes</div>
          </div>
          <div className="bg-gray-900/50 border border-yellow-500/30 rounded-lg p-4 backdrop-blur-sm hover:border-yellow-400 transition-all duration-300 group">
            <div className="text-gray-500 text-[10px] mb-1">CPU_USAGE</div>
            <div className="text-2xl font-bold text-yellow-400 group-hover:scale-110 transition-transform">{totalCpu.toFixed(1)}%</div>
            <div className="text-[8px] text-gray-600 mt-1">Total load</div>
          </div>
          <div className="bg-gray-900/50 border border-purple-500/30 rounded-lg p-4 backdrop-blur-sm hover:border-purple-400 transition-all duration-300 group">
            <div className="text-gray-500 text-[10px] mb-1">MEMORY</div>
            <div className="text-2xl font-bold text-purple-400 group-hover:scale-110 transition-transform">{(totalMem / 1024 / 1024 / 1024).toFixed(2)} GB</div>
            <div className="text-[8px] text-gray-600 mt-1">System memory</div>
          </div>
        </div>

        {/* Navigation Cards */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          {/* PM2 Dashboard */}
          <div
            onClick={() => router.push('/dashboard')}
            className="bg-gray-900/50 border border-cyan-500/30 rounded-lg p-6 backdrop-blur-sm hover:border-cyan-400 hover:scale-[1.02] transition-all duration-300 cursor-pointer group"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center text-2xl group-hover:bg-cyan-500/30 transition-all">
                ⚙️
              </div>
              <div>
                <h2 className="text-xl font-bold text-cyan-400 group-hover:glow-cyan transition-all">PM2 Dashboard</h2>
                <p className="text-gray-500 text-sm">Process monitoring & control</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-[9px]">
              <div className="flex items-center gap-1">
                <div className="w-1 h-1 rounded-full bg-cyan-400"></div>
                <span className="text-gray-400">Start/Stop/Restart</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-1 h-1 rounded-full bg-green-400"></div>
                <span className="text-gray-400">View Logs</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-1 h-1 rounded-full bg-purple-400"></div>
                <span className="text-gray-400">Files Browser</span>
              </div>
            </div>
          </div>

          {/* Ad Management */}
          <a
            href="http://localhost:8501"
            target="_blank"
            className="bg-gray-900/50 border border-orange-500/30 rounded-lg p-6 backdrop-blur-sm hover:border-orange-400 hover:scale-[1.02] transition-all duration-300 block group"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center text-2xl group-hover:bg-orange-500/30 transition-all">
                📊
              </div>
              <div>
                <h2 className="text-xl font-bold text-orange-400 group-hover:text-orange-300 transition-all">Ad Management</h2>
                <p className="text-gray-500 text-sm">E-commerce monitoring dashboard</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-[9px]">
              <div className="flex items-center gap-1">
                <div className="w-1 h-1 rounded-full bg-orange-400"></div>
                <span className="text-gray-400">Stockout Detection</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-1 h-1 rounded-full bg-yellow-400"></div>
                <span className="text-gray-400">Revenue Tracking</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-1 h-1 rounded-full bg-red-400"></div>
                <span className="text-gray-400">Top Products</span>
              </div>
            </div>
          </a>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-2 gap-6">
          {/* Active Processes */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6 backdrop-blur-sm">
            <h2 className="text-lg font-bold text-gray-300 mb-4">:: ACTIVE_PROCESSES ::</h2>
            {loading ? (
              <div className="text-center py-8">
                <div className="text-4xl text-cyan-400 animate-spin inline-block" style={{ animationDuration: '1s' }}>◉</div>
                <div className="text-cyan-700 mt-4 animate-pulse">LOADING...</div>
              </div>
            ) : processes.length === 0 ? (
              <div className="text-gray-600 text-center py-8 animate-pulse">[ NO PROCESSES ]</div>
            ) : (
              <div className="space-y-2">
                {processes.map((p) => (
                  <div
                    key={p.id}
                    className="flex items-center justify-between p-3 bg-black/30 rounded border border-gray-800 hover:border-cyan-500/50 transition-all cursor-pointer"
                    onClick={() => router.push('/dashboard')}
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-1.5 h-1.5 rounded-full ${p.status === 'online' ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                      <span className="font-medium text-white">{p.name}</span>
                    </div>
                    <div className="flex items-center gap-4 text-[10px] text-gray-500">
                      <span>CPU: <span className="text-yellow-400">{p.cpu.toFixed(1)}%</span></span>
                      <span>MEM: <span className="text-purple-400">{formatBytes(p.memory)}</span></span>
                      <span>UP: <span className="text-cyan-400">{formatUptime(p.uptime)}</span></span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Logs */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6 backdrop-blur-sm">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-gray-300">:: RECENT_LOGS ::</h2>
              <button
                onClick={() => router.push('/dashboard')}
                className="text-cyan-400 text-[10px] hover:text-cyan-300 hover:underline transition-all"
              >
                VIEW ALL →
              </button>
            </div>
            {logs.length === 0 ? (
              <div className="text-gray-600 text-center py-8 animate-pulse">[ NO LOGS ]</div>
            ) : (
              <div className="space-y-2 font-mono text-[10px] max-h-64 overflow-auto">
                {logs.map((log, i) => (
                  <div
                    key={i}
                    className="flex gap-2 p-2 bg-black/30 rounded hover:bg-black/50 transition-colors animate-fadeIn border-l-2"
                    style={{
                      animationDelay: `${i * 50}ms`,
                      borderColor:
                        log.level === 'error' ? '#ef4444' :
                        log.level === 'warn' ? '#f59e0b' :
                        log.level === 'PM2' ? '#8b5cf6' :
                        '#06b6d4'
                    }}
                  >
                    <span className="text-gray-600 shrink-0">{log.timestamp.split('T')[1]?.substring(0, 8) || log.timestamp}</span>
                    <span className={`px-1.5 py-0.5 text-[8px] rounded shrink-0 ${
                      log.level === 'error'
                        ? 'bg-red-500/20 text-red-400'
                        : log.level === 'warn'
                        ? 'bg-yellow-500/20 text-yellow-400'
                        : log.level === 'PM2'
                        ? 'bg-purple-500/20 text-purple-400'
                        : 'bg-cyan-500/20 text-cyan-400'
                    }`}>
                      {log.process}
                    </span>
                    <span className="text-gray-400 break-all">{log.message.substring(0, 60)}{log.message.length > 60 ? '...' : ''}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* System Status Footer */}
        <div className="mt-8 pt-4 border-t border-gray-800">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-gray-600 text-[9px] mb-1">SYSTEM_HEALTH</div>
              <div className={`text-sm font-bold ${onlineCount === processes.length && processes.length > 0 ? 'text-green-400' : onlineCount > 0 ? 'text-yellow-400' : 'text-red-400'}`}>
                {onlineCount === processes.length && processes.length > 0 ? 'OPTIMAL' : onlineCount > 0 ? 'WARNING' : 'CRITICAL'}
              </div>
            </div>
            <div>
              <div className="text-gray-600 text-[9px] mb-1">TOTAL_RESTARTS</div>
              <div className="text-sm font-bold text-yellow-400">{processes.reduce((sum, p) => sum + p.restarts, 0)}</div>
            </div>
            <div>
              <div className="text-gray-600 text-[9px] mb-1">UPTIME_RATIO</div>
              <div className="text-sm font-bold text-green-400">
                {processes.length > 0 ? ((onlineCount / processes.length) * 100).toFixed(0) : '0'}%
              </div>
            </div>
          </div>
          <div className="text-center text-gray-700 text-[9px] mt-3">
            <div>Digital Employee OS v2.0 | Auto-refresh: 5s | <span className="text-gray-600">{new Date().toLocaleTimeString()}</span></div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes gridMove {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-5px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
}
