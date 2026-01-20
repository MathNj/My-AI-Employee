'use client';

import { useEffect, useState } from 'react';

interface Process {
  id: number;
  pid: number;
  name: string;
  status: string;
  cpu: number;
  memory: number;
  uptime: number;
  restarts: number;
}

interface LogEntry {
  timestamp: string;
  process: string;
  processId: string;
  level: 'info' | 'error' | 'warn' | 'PM2';
  message: string;
}

export default function Dashboard() {
  const [processes, setProcesses] = useState<Process[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'processes' | 'logs' | 'files' | 'metrics'>('overview');
  const [mounted, setMounted] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [hoveredProcess, setHoveredProcess] = useState<number | null>(null);
  const [animatingProcesses, setAnimatingProcesses] = useState<Set<number>>(new Set());
  const [logFilter, setLogFilter] = useState<'all' | 'info' | 'error' | 'warn' | 'PM2'>('all');
  const [logProcessFilter, setLogProcessFilter] = useState<string>('all');
  const [availableLogProcesses, setAvailableLogProcesses] = useState<string[]>([]);
  const [processViewMode, setProcessViewMode] = useState<'grid' | 'list'>('list');

  // Files state
  const [files, setFiles] = useState<any[]>([]);
  const [currentDir, setCurrentDir] = useState<string>('');
  const [parentDir, setParentDir] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [editingFile, setEditingFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createType, setCreateType] = useState<'file' | 'directory'>('file');
  const [createName, setCreateName] = useState('');

  // Metrics history for graphs
  const [cpuHistory, setCpuHistory] = useState<number[]>([]);
  const [memHistory, setMemHistory] = useState<number[]>([]);

  useEffect(() => {
    setMounted(true);
    fetchData();
    fetchFiles(currentDir);
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeTab === 'files') {
      fetchFiles(currentDir);
    }
  }, [activeTab, currentDir]);

  const fetchData = async () => {
    try {
      const [procsRes, logsRes] = await Promise.all([
        fetch('/api/processes'),
        fetch('/api/logs?lines=50')
      ]);
      const procsData = await procsRes.json();
      const logsData = await logsRes.json();

      // Animate changed processes
      const changedIds = new Set<number>();
      procsData.forEach((newProc: Process) => {
        const oldProc = processes.find(p => p.id === newProc.id);
        if (oldProc && (oldProc.cpu !== newProc.cpu || oldProc.memory !== newProc.memory)) {
          changedIds.add(newProc.id);
        }
      });
      setAnimatingProcesses(changedIds);
      setTimeout(() => setAnimatingProcesses(new Set()), 500);

      setProcesses(procsData);
      setLogs(logsData.logs || []);
      setAvailableLogProcesses(logsData.processes || []);

      // Update metrics history (keep last 30 data points)
      const newCpu = procsData.reduce((sum: number, p: Process) => sum + p.cpu, 0);
      const newMem = procsData.reduce((sum: number, p: Process) => sum + p.memory, 0);
      setCpuHistory(prev => [...prev.slice(-29), newCpu]);
      setMemHistory(prev => [...prev.slice(-29), newMem]);

      setLoading(false);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const handleProcessAction = async (id: number, action: string) => {
    try {
      await fetch(`/api/processes/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      });
      fetchData();
    } catch (error) {
      console.error('Error performing action:', error);
    }
  };

  const fetchFiles = async (dir: string) => {
    try {
      const res = await fetch(`/api/files?dir=${encodeURIComponent(dir)}`);
      const data = await res.json();
      setFiles(data.files || []);
      setCurrentDir(data.currentDir || '');
      setParentDir(data.parentDir || '');
    } catch (error) {
      console.error('Error fetching files:', error);
      setFiles([]);
    }
  };

  const handleFileClick = async (file: any) => {
    if (file.type === 'directory') {
      setCurrentDir(file.path);
      setSelectedFile(null);
      setEditingFile(null);
    } else {
      setSelectedFile(file.name);
      // Load file content for editing
      try {
        const res = await fetch('/api/files', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'read', path: file.path }),
        });
        const data = await res.json();
        setFileContent(data.content || '');
        setEditingFile(file.name);
      } catch (error) {
        console.error('Error reading file:', error);
      }
    }
  };

  const handleSaveFile = async () => {
    if (!editingFile) return;
    try {
      const filePath = currentDir ? `${currentDir}/${editingFile}` : editingFile;
      await fetch('/api/files', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: filePath, content: fileContent }),
      });
      fetchFiles(currentDir);
      setSelectedFile(null);
      setEditingFile(null);
      setFileContent('');
    } catch (error) {
      console.error('Error saving file:', error);
    }
  };

  const handleDeleteFile = async (file: any) => {
    if (!confirm(`Delete ${file.name}?`)) return;
    try {
      await fetch('/api/files', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: file.path }),
      });
      fetchFiles(currentDir);
      if (selectedFile === file.name) {
        setSelectedFile(null);
        setEditingFile(null);
      }
    } catch (error) {
      console.error('Error deleting file:', error);
    }
  };

  const handleCreate = async () => {
    if (!createName.trim()) return;
    try {
      await fetch('/api/files', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: createType === 'directory' ? 'createDir' : 'createFile',
          path: currentDir || '.',
          name: createName,
          content: '',
        }),
      });
      fetchFiles(currentDir);
      setShowCreateModal(false);
      setCreateName('');
    } catch (error) {
      console.error('Error creating:', error);
    }
  };

  const formatBytes = (bytes: number): string => {
    if (!bytes) return '0 MB';
    const mb = bytes / (1024 * 1024);
    return mb >= 1024 ? `${(mb / 1024).toFixed(1)} GB` : `${mb.toFixed(1)} MB`;
  };

  const formatUptime = (seconds: number): string => {
    if (!seconds || seconds < 0) return '-';
    // Check if uptime is in milliseconds (very large number) instead of seconds
    const uptimeInSeconds = seconds > 10000000000 ? seconds / 1000 : seconds;
    const days = Math.floor(uptimeInSeconds / 86400);
    const hours = Math.floor((uptimeInSeconds % 86400) / 3600);
    const mins = Math.floor((uptimeInSeconds % 3600) / 60);
    return days > 0 ? `${days}d ${hours}h ${mins}m` : hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'online': return 'text-blue-400 border-blue-400 bg-blue-400/10';
      case 'stopped': return 'text-red-400 border-red-400 bg-red-400/10';
      case 'stopping': return 'text-yellow-400 border-yellow-400 bg-yellow-400/10';
      case 'launching': return 'text-blue-400 border-blue-400 bg-blue-400/10';
      default: return 'text-gray-400 border-gray-400 bg-gray-400/10';
    }
  };

  const onlineCount = processes.filter(p => p.status === 'online').length;
  const totalCpu = processes.reduce((sum, p) => sum + p.cpu, 0);
  const totalMem = processes.reduce((sum, p) => sum + p.memory, 0);

  return (
    <div className="min-h-screen bg-black font-mono text-xs" style={{
      fontFamily: 'JetBrains Mono, Fira Code, Roboto Mono, monospace'
    }}>
      {/* Animated background grid */}
      <div className="fixed inset-0 opacity-5 pointer-events-none">
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(rgba(0, 255, 255, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
          animation: 'gridMove 20s linear infinite'
        }}></div>
        {/* Scanline effect */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="w-full h-[2px] bg-cyan-400/20 animate-scanline"></div>
        </div>
      </div>

      {/* Main Container - Three Column Grid */}
      <div className="h-screen flex gap-0 relative z-10">

        {/* LEFT COLUMN - The Controller (20%) */}
        <div className="w-[20%] border-r border-cyan-900/50 flex flex-col bg-black/95 backdrop-blur-sm">

          {/* Header */}
          <div className="border-b border-cyan-900/50 p-3">
            <div className="text-cyan-400 text-sm font-bold animate-wave">:: PM2_CONTROLLER ::</div>
            <div className="text-gray-500 text-[10px] mt-1">DIGITAL EMPLOYEE OS v2.0</div>
          </div>

          {/* Status Widget */}
          <div className="border-b border-cyan-900/50 p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-2 h-2 rounded-full ${onlineCount > 0 ? 'bg-blue-400 animate-ping animate-glowPulse' : 'bg-red-400 animate-glowPulse'}`}></div>
              <div className={`w-2 h-2 rounded-full ${onlineCount > 0 ? 'bg-blue-400 animate-pulse' : 'bg-red-400 animate-pulse'}`}></div>
              <span className="text-cyan-300 text-[10px] animate-flicker">SYSTEM_STATUS</span>
            </div>
            <div className={`text-sm font-bold transition-all duration-300 ${onlineCount > 0 ? 'text-blue-400' : 'text-red-400'}`}>
              {onlineCount > 0 ? 'OPERATIONAL' : 'OFFLINE'}
            </div>
          </div>

          {/* Key Metrics */}
          <div className="border-b border-cyan-900/50 p-3 flex-1 overflow-auto">
            <div className="text-cyan-400 text-[10px] mb-3">:: SYSTEM_METRICS ::</div>

            <div className="space-y-3">
              <div className="group">
                <div className="flex justify-between text-gray-400 text-[10px] mb-1">
                  <span>PROCESSES</span>
                  <span className="text-cyan-300 group-hover:text-cyan-200 transition-colors">{processes.length}</span>
                </div>
                <div className="w-full bg-gray-900 h-1 rounded overflow-hidden">
                  <div
                    className="bg-cyan-500 h-full transition-all duration-500 ease-out relative overflow-hidden"
                    style={{ width: `${(processes.length / 10) * 100}%` }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-[shimmer_2s_infinite]"></div>
                  </div>
                </div>
              </div>

              <div className="group">
                <div className="flex justify-between text-gray-400 text-[10px] mb-1">
                  <span>ONLINE</span>
                  <span className="text-blue-400 group-hover:text-blue-300 transition-colors">{onlineCount}</span>
                </div>
                <div className="w-full bg-gray-900 h-1 rounded overflow-hidden animate-pulseBorder">
                  <div
                    className="bg-blue-500 h-full transition-all duration-500 ease-out relative overflow-hidden"
                    style={{ width: `${(onlineCount / processes.length) * 100 || 0}%` }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-dataFlow"></div>
                  </div>
                </div>
              </div>

              <div className="group">
                <div className="flex justify-between text-gray-400 text-[10px] mb-1">
                  <span>CPU_LOAD</span>
                  <span className="text-yellow-400 group-hover:text-yellow-300 transition-colors">{totalCpu.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-900 h-1 rounded overflow-hidden">
                  <div
                    className="bg-yellow-500 h-full transition-all duration-500 ease-out relative overflow-hidden"
                    style={{ width: `${Math.min(totalCpu, 100)}%` }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-[shimmer_2s_infinite]"></div>
                  </div>
                </div>
              </div>

              <div className="group">
                <div className="flex justify-between text-gray-400 text-[10px] mb-1">
                  <span>MEMORY</span>
                  <span className="text-purple-400 group-hover:text-purple-300 transition-colors">{formatBytes(totalMem)}</span>
                </div>
                <div className="w-full bg-gray-900 h-1 rounded overflow-hidden">
                  <div
                    className="bg-purple-500 h-full transition-all duration-500 ease-out relative overflow-hidden"
                    style={{ width: `${(totalMem / 4000000000) * 100}%` }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-[shimmer_2s_infinite]"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Resource Allocation */}
            <div className="mt-4 p-2 border border-gray-800 rounded bg-black/30">
              <div className="text-cyan-400 text-[9px] mb-2">:: RESOURCE_ALLOCATION ::</div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 text-[8px]">SYSTEM</span>
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-cyan-400 rounded animate-pulse"></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 text-[8px]">USER</span>
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-blue-400 rounded animate-pulse"></div>
                    <div className="w-2 h-2 bg-blue-400 rounded animate-pulse" style={{ animationDelay: '0.3s' }}></div>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 text-[8px]">IDLE</span>
                  <div className="w-2 h-2 bg-gray-600 rounded"></div>
                </div>
              </div>
            </div>

            {/* Active Processes List */}
            <div className="mt-4">
              <div className="text-cyan-400 text-[10px] mb-2">:: ACTIVE_PROCESSES ::</div>
              <div className="space-y-1">
                {processes.slice(0, 8).map(p => (
                  <div
                    key={p.id}
                    className="flex items-center gap-2 text-[10px] p-1.5 rounded border border-transparent hover:border-cyan-500/30 hover:bg-cyan-950/30 transition-all cursor-pointer group"
                    onMouseEnter={() => setHoveredProcess(p.id)}
                    onMouseLeave={() => setHoveredProcess(null)}
                  >
                    <div className={`w-1.5 h-1.5 rounded-full ${p.status === 'online' ? 'bg-blue-400 animate-pulse' : 'bg-red-400'}`}></div>
                    <span className="text-gray-400 flex-1 truncate group-hover:text-cyan-300 transition-colors">{p.name}</span>
                    <span className={`text-cyan-300 transition-all duration-300 ${animatingProcesses.has(p.id) ? 'scale-125 font-bold text-yellow-400' : ''}`}>{p.cpu.toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="mt-4">
              <div className="text-cyan-400 text-[10px] mb-2">:: QUICK_ACTIONS ::</div>
              <div className="grid grid-cols-2 gap-2">
                <button className="p-2 border border-gray-800 rounded bg-black/30 hover:border-cyan-500/50 hover:bg-cyan-950/20 transition-all text-[8px] text-gray-400 hover:text-cyan-300 group">
                  <div className="text-lg mb-1 group-hover:scale-110 transition-transform text-cyan-300">⟳</div>
                  REFRESH
                </button>
                <button className="p-2 border border-gray-800 rounded bg-black/30 hover:border-blue-500/50 hover:bg-blue-950/20 transition-all text-[8px] text-gray-400 hover:text-blue-300 group">
                  <div className="text-lg mb-1 group-hover:scale-110 transition-transform text-blue-300">▶</div>
                  START ALL
                </button>
                <button className="p-2 border border-gray-800 rounded bg-black/30 hover:border-yellow-500/50 hover:bg-yellow-950/20 transition-all text-[8px] text-gray-400 hover:text-yellow-300 group">
                  <div className="text-lg mb-1 group-hover:scale-110 transition-transform text-yellow-300">❚❚</div>
                  PAUSE
                </button>
                <button className="p-2 border border-gray-800 rounded bg-black/30 hover:border-red-500/50 hover:bg-red-950/20 transition-all text-[8px] text-gray-400 hover:text-red-300 group">
                  <div className="text-lg mb-1 group-hover:scale-110 transition-transform text-red-300">■</div>
                  STOP ALL
                </button>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="border-t border-cyan-900/50 p-2 text-gray-600 text-[9px]">
            <div>LATENCY: {mounted ? (Math.random() * 2 + 0.5).toFixed(2) : '--.--'}ms</div>
            <div>UPTIME: {mounted ? formatUptime(Date.now() / 1000) : '--:--'}</div>
          </div>
        </div>

        {/* CENTER COLUMN - The Workspace (55%) */}
        <div className="w-[55%] flex flex-col bg-black/90 backdrop-blur-sm">

          {/* Navigation Tabs */}
          <div className="border-b border-cyan-900/50 flex">
            {(['overview', 'processes', 'logs', 'files', 'metrics'] as const).map((tab, i) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 text-[10px] font-bold transition-all duration-300 relative flex-1 hover:bg-cyan-900/10 ${
                  activeTab === tab
                    ? 'bg-cyan-500/20 text-cyan-400'
                    : 'text-gray-500 hover:text-gray-300'
                }`}
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <span className="relative z-10 inline-block hover:scale-105 transition-transform">[{tab.toUpperCase()}]</span>
                {activeTab === tab && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400">
                    <div className="h-full bg-cyan-300 animate-[shimmer_2s_infinite]"></div>
                  </div>
                )}
                {activeTab === tab && (
                  <div className="absolute inset-0 bg-cyan-400/5 animate-pulse"></div>
                )}
              </button>
            ))}
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-auto p-4 min-h-0">
            {activeTab === 'overview' && (
              <div className="animate-fadeIn h-full flex flex-col">
                {/* Quick Stats */}
                <div className="grid grid-cols-4 gap-3 mb-4">
                  <div className="bg-gray-900/50 border border-cyan-500/30 rounded-lg p-2 backdrop-blur-sm hover:border-cyan-400 hover:shadow-[0_0_20px_rgba(6,182,212,0.3)] transition-all duration-300 group relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
                    <div className="text-gray-500 text-[8px] mb-1 relative z-10">PROCESSES</div>
                    <div className="text-xl font-bold text-cyan-400 group-hover:scale-110 transition-transform relative z-10">{processes.length}</div>
                    <div className="text-[7px] text-gray-600 mt-1 relative z-10">Total monitored</div>
                  </div>
                  <div className="bg-gray-900/50 border border-blue-500/30 rounded-lg p-2 backdrop-blur-sm hover:border-blue-400 hover:shadow-[0_0_20px_rgba(74,222,128,0.3)] transition-all duration-300 group relative overflow-hidden animate-fadeIn" style={{ animationDelay: '0.1s' }}>
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-green-400/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
                    <div className="text-gray-500 text-[8px] mb-1 relative z-10">ONLINE</div>
                    <div className="text-xl font-bold text-blue-400 group-hover:scale-110 transition-transform relative z-10">{onlineCount}</div>
                    <div className="text-[7px] text-gray-600 mt-1 relative z-10">Active processes</div>
                  </div>
                  <div className="bg-gray-900/50 border border-yellow-500/30 rounded-lg p-2 backdrop-blur-sm hover:border-yellow-400 hover:shadow-[0_0_20px_rgba(250,204,21,0.3)] transition-all duration-300 group relative overflow-hidden animate-fadeIn" style={{ animationDelay: '0.2s' }}>
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-yellow-400/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
                    <div className="text-gray-500 text-[8px] mb-1 relative z-10">CPU_USAGE</div>
                    <div className="text-xl font-bold text-yellow-400 group-hover:scale-110 transition-transform relative z-10">{totalCpu.toFixed(1)}%</div>
                    <div className="text-[7px] text-gray-600 mt-1 relative z-10">Total load</div>
                  </div>
                  <div className="bg-gray-900/50 border border-purple-500/30 rounded-lg p-2 backdrop-blur-sm hover:border-purple-400 hover:shadow-[0_0_20px_rgba(168,85,247,0.3)] transition-all duration-300 group relative overflow-hidden animate-fadeIn" style={{ animationDelay: '0.3s' }}>
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-purple-400/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
                    <div className="text-gray-500 text-[8px] mb-1 relative z-10">MEMORY</div>
                    <div className="text-xl font-bold text-purple-400 group-hover:scale-110 transition-transform relative z-10">{(totalMem / 1024 / 1024 / 1024).toFixed(2)} GB</div>
                    <div className="text-[7px] text-gray-600 mt-1 relative z-10">System memory</div>
                  </div>
                </div>

                {/* Navigation Cards */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div
                    onClick={() => setActiveTab('processes')}
                    className="bg-gray-900/50 border border-cyan-500/30 rounded-lg p-3 backdrop-blur-sm hover:border-cyan-400 hover:scale-[1.02] hover:shadow-[0_0_30px_rgba(6,182,212,0.4)] transition-all duration-300 cursor-pointer group relative overflow-hidden animate-fadeIn"
                    style={{ animationDelay: '0.4s' }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    <div className="flex items-center gap-2 mb-2 relative z-10">
                      <div className="w-8 h-8 bg-cyan-500/20 rounded-lg flex items-center justify-center text-lg group-hover:bg-cyan-500/30 group-hover:animate-float transition-all text-cyan-300">
                        ⚙️
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-cyan-400 group-hover:scale-105 transition-transform">PM2 Control</h3>
                        <p className="text-gray-500 text-[8px]">Process monitoring & management</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-[8px] relative z-10">
                      <div className="flex items-center gap-1 group-hover:animate-slideIn" style={{ animationDelay: '0.1s' }}>
                        <div className="w-1 h-1 rounded-full bg-cyan-400 animate-pulse"></div>
                        <span className="text-gray-400">Start/Stop</span>
                      </div>
                      <div className="flex items-center gap-1 group-hover:animate-slideIn" style={{ animationDelay: '0.2s' }}>
                        <div className="w-1 h-1 rounded-full bg-blue-400 animate-pulse"></div>
                        <span className="text-gray-400">Logs</span>
                      </div>
                      <div className="flex items-center gap-1 group-hover:animate-slideIn" style={{ animationDelay: '0.3s' }}>
                        <div className="w-1 h-1 rounded-full bg-purple-400 animate-pulse"></div>
                        <span className="text-gray-400">Files</span>
                      </div>
                    </div>
                  </div>

                  <a
                    href="http://localhost:8501"
                    target="_blank"
                    className="bg-gray-900/50 border border-orange-500/30 rounded-lg p-3 backdrop-blur-sm hover:border-orange-400 hover:scale-[1.02] hover:shadow-[0_0_30px_rgba(251,146,60,0.4)] transition-all duration-300 block group relative overflow-hidden animate-fadeIn"
                    style={{ animationDelay: '0.5s' }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    <div className="flex items-center gap-2 mb-2 relative z-10">
                      <div className="w-8 h-8 bg-orange-500/20 rounded-lg flex items-center justify-center text-lg group-hover:bg-orange-500/30 group-hover:animate-float transition-all text-orange-300">
                        ◫
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-orange-400 group-hover:scale-105 transition-transform">Ad Management</h3>
                        <p className="text-gray-500 text-[8px]">E-commerce monitoring dashboard</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-[8px] relative z-10">
                      <div className="flex items-center gap-1 group-hover:animate-slideIn" style={{ animationDelay: '0.1s' }}>
                        <div className="w-1 h-1 rounded-full bg-orange-400 animate-pulse"></div>
                        <span className="text-gray-400">Stockouts</span>
                      </div>
                      <div className="flex items-center gap-1 group-hover:animate-slideIn" style={{ animationDelay: '0.2s' }}>
                        <div className="w-1 h-1 rounded-full bg-yellow-400 animate-pulse"></div>
                        <span className="text-gray-400">Revenue</span>
                      </div>
                      <div className="flex items-center gap-1 group-hover:animate-slideIn" style={{ animationDelay: '0.3s' }}>
                        <div className="w-1 h-1 rounded-full bg-red-400 animate-pulse"></div>
                        <span className="text-gray-400">Products</span>
                      </div>
                    </div>
                  </a>
                </div>

                {/* Two Column Layout */}
                <div className="grid grid-cols-2 gap-3 flex-1 min-h-0">
                  {/* Active Processes */}
                  <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-3 backdrop-blur-sm hover:border-cyan-500/30 transition-all duration-300 animate-fadeIn flex flex-col min-h-0" style={{ animationDelay: '0.6s' }}>
                    <div className="flex items-center justify-between mb-2 shrink-0">
                      <h3 className="text-xs font-bold text-gray-300">:: ACTIVE_PROCESSES ::</h3>
                      <button
                        onClick={() => setActiveTab('processes')}
                        className="text-cyan-400 text-[8px] hover:text-cyan-300 hover:underline hover:scale-105 transition-transform"
                      >
                        VIEW ALL →
                      </button>
                    </div>
                    {loading ? (
                      <div className="text-center py-4">
                        <div className="text-3xl text-cyan-400 animate-spin inline-block" style={{ animationDuration: '1s' }}>◉</div>
                        <div className="text-cyan-700 mt-3 animate-pulse text-[10px]">LOADING...</div>
                      </div>
                    ) : processes.length === 0 ? (
                      <div className="text-gray-600 text-center py-4 animate-pulse text-[10px]">[ NO PROCESSES ]</div>
                    ) : (
                      <div className="space-y-1.5 overflow-auto flex-1">
                        {processes.slice(0, 5).map((p, i) => (
                          <div
                            key={p.id}
                            className="flex items-center justify-between p-2 bg-black/30 rounded border border-gray-800 hover:border-cyan-500/50 hover:bg-cyan-950/20 hover:shadow-[0_0_15px_rgba(6,182,212,0.2)] transition-all cursor-pointer group animate-fadeIn shrink-0"
                            style={{ animationDelay: `${0.6 + i * 0.1}s` }}
                            onClick={() => setActiveTab('processes')}
                          >
                            <div className="flex items-center gap-2">
                              <div className={`w-1 h-1 rounded-full ${p.status === 'online' ? 'bg-blue-400 animate-pulse' : 'bg-red-400'}`}></div>
                              <span className="font-medium text-white text-[10px] group-hover:text-cyan-300 transition-colors">{p.name}</span>
                            </div>
                            <div className="flex items-center gap-3 text-[8px] text-gray-500">
                              <span>CPU: <span className="text-yellow-400">{p.cpu.toFixed(1)}%</span></span>
                              <span>MEM: <span className="text-purple-400">{formatBytes(p.memory)}</span></span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Recent Logs */}
                  <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-3 backdrop-blur-sm hover:border-cyan-500/30 transition-all duration-300 animate-fadeIn flex flex-col min-h-0" style={{ animationDelay: '0.7s' }}>
                    <div className="flex items-center justify-between mb-2 shrink-0">
                      <h3 className="text-xs font-bold text-gray-300">:: RECENT_LOGS ::</h3>
                      <button
                        onClick={() => setActiveTab('logs')}
                        className="text-cyan-400 text-[8px] hover:text-cyan-300 hover:underline hover:scale-105 transition-transform"
                      >
                        VIEW ALL →
                      </button>
                    </div>
                    {logs.length === 0 ? (
                      <div className="text-gray-600 text-center py-4 animate-pulse text-[10px]">[ NO LOGS ]</div>
                    ) : (
                      <div className="space-y-1 font-mono text-[8px] overflow-auto flex-1">
                        {logs.slice(0, 8).map((log, i) => (
                          <div
                            key={i}
                            className="flex gap-2 p-1.5 bg-black/30 rounded hover:bg-black/50 hover:scale-[1.02] hover:shadow-lg transition-all border-l-2 animate-fadeIn shrink-0"
                            style={{
                              animationDelay: `${0.7 + i * 0.05}s`,
                              borderColor:
                                log.level === 'error' ? '#ef4444' :
                                log.level === 'warn' ? '#f59e0b' :
                                log.level === 'PM2' ? '#8b5cf6' :
                                '#06b6d4'
                            }}
                          >
                            <span className="text-gray-600 shrink-0">{log.timestamp.split('T')[1]?.substring(0, 8) || log.timestamp}</span>
                            <span className={`px-1 py-0.5 text-[7px] rounded shrink-0 ${
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
                            <span className="text-gray-400 break-all">{log.message.substring(0, 40)}{log.message.length > 40 ? '...' : ''}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* System Status Footer */}
                <div className="mt-3 pt-2 border-t border-gray-800 shrink-0 animate-fadeIn" style={{ animationDelay: '1.2s' }}>
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div className="group">
                      <div className="text-gray-600 text-[8px] mb-1 group-hover:text-cyan-400 transition-colors">SYSTEM_HEALTH</div>
                      <div className={`text-xs font-bold transition-all duration-300 ${onlineCount === processes.length && processes.length > 0 ? 'text-blue-400 group-hover:scale-110' : onlineCount > 0 ? 'text-yellow-400 group-hover:scale-110' : 'text-red-400 group-hover:scale-110'}`}>
                        {onlineCount === processes.length && processes.length > 0 ? 'OPTIMAL' : onlineCount > 0 ? 'WARNING' : 'CRITICAL'}
                      </div>
                    </div>
                    <div className="group">
                      <div className="text-gray-600 text-[8px] mb-1 group-hover:text-cyan-400 transition-colors">TOTAL_RESTARTS</div>
                      <div className="text-xs font-bold text-yellow-400 group-hover:scale-110 transition-transform">{processes.reduce((sum, p) => sum + (p.restarts || 0), 0)}</div>
                    </div>
                    <div className="group">
                      <div className="text-gray-600 text-[8px] mb-1 group-hover:text-cyan-400 transition-colors">UPTIME_RATIO</div>
                      <div className="text-xs font-bold text-blue-400 group-hover:scale-110 transition-transform">
                        {processes.length > 0 ? ((onlineCount / processes.length) * 100).toFixed(0) : '0'}%
                      </div>
                    </div>
                  </div>
                  <div className="text-center text-gray-700 text-[8px] mt-2">
                    <div className="group inline-block">
                      <span className="group-hover:text-cyan-400 transition-colors">Digital Employee OS v2.0</span>
                      <span className="mx-2">|</span>
                      <span className="group-hover:text-cyan-400 transition-colors">Auto-refresh: 3s</span>
                      <span className="mx-2">|</span>
                      <span className="text-gray-600">{mounted ? lastUpdate.toLocaleTimeString() : '--:--:--'}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'processes' && (
              <div>
                {/* Header with stats */}
                <div className="flex items-center justify-between mb-4">
                  <div className="text-cyan-400 text-sm font-bold">:: PROCESS_CONTROL ::</div>
                  <div className="flex items-center gap-4 text-[9px]">
                    <div className="flex items-center gap-1">
                      <div className={`w-1.5 h-1.5 rounded-full ${onlineCount > 0 ? 'bg-blue-400 animate-pulse' : 'bg-red-400'}`}></div>
                      <span className="text-gray-500">{onlineCount} ONLINE</span>
                    </div>
                    <div className="text-gray-500">|</div>
                    <button
                      onClick={() => setProcessViewMode(processViewMode === 'grid' ? 'list' : 'grid')}
                      className="flex items-center gap-1 px-2 py-1 border border-gray-700 rounded hover:border-cyan-500/50 transition-all text-gray-400 hover:text-cyan-300"
                    >
                      [{processViewMode === 'grid' ? '▦' : '☰'} {processViewMode.toUpperCase()}]
                    </button>
                  </div>
                </div>

                {loading ? (
                  <div className="text-center py-20">
                    <div className="text-4xl text-cyan-400 animate-spin" style={{ animationDuration: '1s' }}>◉</div>
                    <div className="text-cyan-700 mt-4 animate-pulse">INITIALIZING...</div>
                  </div>
                ) : processes.length === 0 ? (
                  <div className="text-center py-20 text-gray-600 animate-pulse">
                    [ NO_PROCESSES_DETECTED ]
                  </div>
                ) : (
                  <div className={`${processViewMode === 'grid' ? 'grid grid-cols-2 gap-3' : 'grid grid-cols-1 gap-3'}`}>
                    {processes.map(p => (
                      <div
                        key={p.id}
                        className={`relative overflow-hidden rounded-lg border transition-all duration-300 ${
                          hoveredProcess === p.id ? 'scale-[1.01] shadow-2xl' : 'shadow-lg'
                        } ${getStatusColor(p.status)} group`}
                        onMouseEnter={() => setHoveredProcess(p.id)}
                        onMouseLeave={() => setHoveredProcess(null)}
                        style={{
                          background: `linear-gradient(135deg, ${
                            p.status === 'online'
                              ? 'rgba(0, 255, 0, 0.05)'
                              : 'rgba(239, 68, 68, 0.05)'
                          } 0%, transparent 100%)`
                        }}
                      >
                        {/* Animated border glow effect */}
                        <div className={`absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${
                          p.status === 'online'
                            ? 'shadow-[0_0_20px_rgba(0,255,0,0.3)]'
                            : 'shadow-[0_0_20px_rgba(239,68,68,0.3)]'
                        }`}></div>

                        {/* Process Header */}
                        <div className="relative p-4 bg-black/40 backdrop-blur-sm">
                          <div className="flex justify-between items-start">
                            {/* Process Info */}
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <div className={`w-2 h-2 rounded-full ${
                                  p.status === 'online' ? 'bg-blue-400 animate-pulse' : 'bg-red-400'
                                }`}></div>
                                <h3 className="text-sm font-bold text-white">{p.name}</h3>
                                <span className={`px-2 py-0.5 text-[8px] font-bold rounded ${
                                  p.status === 'online' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'
                                }`}>
                                  {p.status}
                                </span>
                              </div>
                              <div className="flex gap-4 text-[10px] text-gray-500">
                                <span>PID: <span className="text-cyan-400 font-mono">{p.pid}</span></span>
                                <span>ID: <span className="text-cyan-400 font-mono">{p.id}</span></span>
                                <span>MODE: <span className="text-gray-300">{p.mode === 'fork_mode' ? 'FORK' : 'CLUSTER'}</span></span>
                              </div>
                            </div>

                            {/* Status Badge */}
                            <div className={`text-xs font-bold px-3 py-1.5 rounded border ${getStatusColor(p.status)} ml-4`}>
                              {p.status.toUpperCase()}
                            </div>
                          </div>

                          {/* Quick Stats Bar */}
                          <div className="mt-3 grid grid-cols-3 gap-3">
                            {/* CPU */}
                            <div className="bg-black/50 rounded p-2 border border-gray-800">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-gray-600 text-[8px]">CPU</span>
                                <span className={`text-xs font-bold ${
                                  p.cpu > 50 ? 'text-red-400' : p.cpu > 20 ? 'text-yellow-400' : 'text-blue-400'
                                }`}>
                                  {p.cpu.toFixed(1)}%
                                </span>
                              </div>
                              <div className="w-full bg-gray-900 h-1.5 rounded-full overflow-hidden">
                                <div
                                  className={`h-full rounded-full transition-all duration-500 ${
                                    p.cpu > 50 ? 'bg-red-500' : p.cpu > 20 ? 'bg-yellow-500' : 'bg-blue-500'
                                  } ${animatingProcesses.has(p.id) ? 'animate-pulse' : ''}`}
                                  style={{ width: `${Math.min(p.cpu, 100)}%` }}
                                ></div>
                              </div>
                            </div>

                            {/* Memory */}
                            <div className="bg-black/50 rounded p-2 border border-gray-800">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-gray-600 text-[8px]">MEMORY</span>
                                <span className="text-xs font-bold text-purple-400">
                                  {formatBytes(p.memory)}
                                </span>
                              </div>
                              <div className="w-full bg-gray-900 h-1.5 rounded-full overflow-hidden">
                                <div
                                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-full rounded-full transition-all duration-500"
                                  style={{ width: `${Math.min((p.memory / 500000000) * 100, 100)}%` }}
                                ></div>
                              </div>
                            </div>

                            {/* Uptime */}
                            <div className="bg-black/50 rounded p-2 border border-gray-800">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-gray-600 text-[8px]">UPTIME</span>
                                <span className="text-xs font-bold text-cyan-400">
                                  {formatUptime(p.uptime)}
                                </span>
                              </div>
                              <div className="text-[9px] text-gray-500 mt-1">
                                Restarts: {p.restarts}
                              </div>
                            </div>
                          </div>

                          {/* Action Buttons */}
                          <div className="mt-3 flex gap-2">
                            {p.status === 'online' ? (
                              <>
                                <button
                                  onClick={() => handleProcessAction(p.id, 'restart')}
                                  className="flex-1 px-3 py-2 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/50 text-cyan-400 hover:from-cyan-500/30 hover:to-blue-500/30 text-[9px] font-bold transition-all duration-200 hover:scale-105 active:scale-95"
                                >
                                  ↻ RESTART
                                </button>
                                <button
                                  onClick={() => handleProcessAction(p.id, 'stop')}
                                  className="flex-1 px-3 py-2 bg-gradient-to-r from-red-500/20 to-orange-500/20 border border-red-500/50 text-red-400 hover:from-red-500/30 hover:to-orange-500/30 text-[9px] font-bold transition-all duration-200 hover:scale-105 active:scale-95"
                                >
                                  ◼ STOP
                                </button>
                              </>
                            ) : (
                              <button
                                onClick={() => handleProcessAction(p.id, 'start')}
                                className="flex-1 px-3 py-2 bg-gradient-to-r from-blue-500/20 to-emerald-500/20 border border-blue-500/50 text-blue-400 hover:from-blue-500/30 hover:to-emerald-500/30 text-[9px] font-bold transition-all duration-200 hover:scale-105 active:scale-95"
                              >
                                ▶ START
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Progress indicator at bottom */}
                        <div className={`h-1 ${
                          p.status === 'online' ? 'bg-blue-500' : 'bg-red-500'
                        } transition-all duration-300`}></div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'logs' && (
              <div>
                <div className="text-cyan-400 text-sm font-bold mb-4">:: SYSTEM_LOGS ::</div>

                {/* Log Filters */}
                <div className="mb-3 space-y-2">
                  {/* Level Filter */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-gray-500 text-[9px]">LEVEL:</span>
                    {(['all', 'info', 'error', 'warn', 'PM2'] as const).map((level) => (
                      <button
                        key={level}
                        onClick={() => setLogFilter(level)}
                        className={`px-2 py-1 text-[9px] font-bold transition-all duration-200 ${
                          logFilter === level
                            ? level === 'error' ? 'bg-red-500/20 text-red-400 border border-red-500'
                            : level === 'warn' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500'
                            : level === 'PM2' ? 'bg-purple-500/20 text-purple-400 border border-purple-500'
                            : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500'
                            : 'text-gray-500 border border-gray-700 hover:border-gray-500'
                        }`}
                      >
                        [{level.toUpperCase()}]
                      </button>
                    ))}
                  </div>

                  {/* Process Filter */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-gray-500 text-[9px]">PROCESS:</span>
                    <button
                      onClick={() => setLogProcessFilter('all')}
                      className={`px-2 py-1 text-[9px] font-bold transition-all duration-200 ${
                        logProcessFilter === 'all'
                          ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500'
                          : 'text-gray-500 border border-gray-700 hover:border-gray-500'
                      }`}
                    >
                      [ALL]
                    </button>
                    {availableLogProcesses.map((proc) => (
                      <button
                        key={proc}
                        onClick={() => setLogProcessFilter(proc)}
                        className={`px-2 py-1 text-[9px] font-bold transition-all duration-200 ${
                          logProcessFilter === proc
                            ? 'bg-blue-500/20 text-blue-400 border border-blue-500'
                            : 'text-gray-500 border border-gray-700 hover:border-gray-500'
                        }`}
                      >
                        [{proc.toUpperCase()}]
                      </button>
                    ))}
                  </div>
                </div>

                {/* Logs Display */}
                <div className="border border-gray-800 bg-black p-3 h-[450px] overflow-auto text-[10px] font-mono rounded">
                  {logs.length === 0 ? (
                    <div className="text-gray-600 animate-pulse">[ NO_LOGS_AVAILABLE ]</div>
                  ) : (
                    <div className="space-y-1">
                      {logs
                        .filter(log =>
                          (logFilter === 'all' || log.level === logFilter) &&
                          (logProcessFilter === 'all' || log.process === logProcessFilter)
                        )
                        .slice(0, 100)
                        .map((log, i) => (
                          <div
                            key={i}
                            className={`mb-1 p-2 rounded transition-all duration-200 animate-fadeIn border-l-2 ${
                              log.level === 'error'
                                ? 'bg-red-900/10 border-red-500 hover:bg-red-900/20'
                                : log.level === 'warn'
                                ? 'bg-yellow-900/10 border-yellow-500 hover:bg-yellow-900/20'
                                : log.level === 'PM2'
                                ? 'bg-purple-900/10 border-purple-500 hover:bg-purple-900/20'
                                : 'bg-cyan-900/10 border-cyan-500 hover:bg-cyan-900/20'
                            }`}
                            style={{ animationDelay: `${Math.min(i * 20, 500)}ms` }}
                          >
                            <div className="flex items-start gap-2">
                              <span className="text-gray-600 shrink-0">{log.timestamp.split('T')[1]?.substring(0, 8) || log.timestamp}</span>
                              <span className={`px-1.5 py-0.5 text-[8px] font-bold rounded shrink-0 ${
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
                              <span className={`text-gray-300 break-all ${log.level === 'error' ? 'text-red-200' : ''}`}>
                                {log.message}
                              </span>
                            </div>
                          </div>
                        ))}
                    </div>
                  )}
                </div>

                {/* Log Stats */}
                <div className="mt-2 flex items-center justify-between text-[9px]">
                  <span className="text-gray-500">
                    Showing {logs.filter(l =>
                      (logFilter === 'all' || l.level === logFilter) &&
                      (logProcessFilter === 'all' || l.process === logProcessFilter)
                    ).length} of {logs.length} logs
                  </span>
                  <button
                    onClick={fetchData}
                    className="px-2 py-1 bg-cyan-500/20 text-cyan-400 border border-cyan-500 hover:bg-cyan-500/30 transition-all duration-200 hover:scale-105"
                  >
                    [REFRESH]
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'files' && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="text-cyan-400 text-sm font-bold">:: FILE_BROWSER ::</div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => { setCreateType('file'); setShowCreateModal(true); }}
                      className="px-3 py-1 border border-cyan-500/30 rounded text-[9px] text-cyan-400 hover:border-cyan-400 hover:bg-cyan-950/20 transition-all"
                    >
                      [+ FILE]
                    </button>
                    <button
                      onClick={() => { setCreateType('directory'); setShowCreateModal(true); }}
                      className="px-3 py-1 border border-blue-500/30 rounded text-[9px] text-blue-400 hover:border-blue-400 hover:bg-blue-950/20 transition-all"
                    >
                      [+ FOLDER]
                    </button>
                  </div>
                </div>

                {/* Breadcrumb */}
                <div className="mb-3 flex items-center gap-2 text-[10px]">
                  <button
                    onClick={() => { setCurrentDir(''); setSelectedFile(null); setEditingFile(null); }}
                    className="text-gray-500 hover:text-cyan-400 transition-colors"
                  >
                    [ROOT]
                  </button>
                  {currentDir && currentDir.split('/').map((part, i, arr) => (
                    <span key={i} className="flex items-center gap-2">
                      <span className="text-gray-600">/</span>
                      <button
                        onClick={() => { setCurrentDir(arr.slice(0, i + 1).join('/')); setEditingFile(null); }}
                        className="text-gray-500 hover:text-cyan-400 transition-colors"
                      >
                        {part.toUpperCase()}
                      </button>
                    </span>
                  ))}
                </div>

                {/* Editor Panel */}
                {editingFile && (
                  <div className="mb-3 border border-cyan-500/30 rounded bg-black/50 p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-cyan-400 text-[10px]">EDITING: {editingFile}</span>
                      <div className="flex gap-2">
                        <button
                          onClick={handleSaveFile}
                          className="px-2 py-1 bg-blue-500/20 border border-blue-500/30 rounded text-[8px] text-blue-400 hover:bg-blue-500/30 transition-all"
                        >
                          [SAVE]
                        </button>
                        <button
                          onClick={() => { setEditingFile(null); setSelectedFile(null); setFileContent(''); }}
                          className="px-2 py-1 bg-red-500/20 border border-red-500/30 rounded text-[8px] text-red-400 hover:bg-red-500/30 transition-all"
                        >
                          [CANCEL]
                        </button>
                      </div>
                    </div>
                    <textarea
                      value={fileContent}
                      onChange={(e) => setFileContent(e.target.value)}
                      className="w-full h-40 bg-black border border-gray-700 rounded p-2 text-[9px] font-mono text-gray-300 focus:border-cyan-500 focus:outline-none resize-none"
                      spellCheck={false}
                    />
                  </div>
                )}

                {/* Files List */}
                <div className="border border-gray-800 bg-black p-3 h-[350px] overflow-auto text-[10px] font-mono rounded">
                  {parentDir && (
                    <div
                      onClick={() => { setCurrentDir(parentDir); setSelectedFile(null); setEditingFile(null); }}
                      className="flex items-center gap-2 p-2 hover:bg-cyan-900/20 rounded cursor-pointer transition-all mb-1"
                    >
                      <span className="text-gray-500">..</span>
                      <span className="text-gray-400">[PARENT]</span>
                    </div>
                  )}

                  {files.length === 0 ? (
                    <div className="text-gray-600 animate-pulse">[ DIRECTORY_EMPTY ]</div>
                  ) : (
                    <div className="space-y-1">
                      {files.map((file, i) => (
                        <div
                          key={i}
                          className={`flex items-center gap-2 p-2 rounded transition-all duration-200 border-l-2 animate-fadeIn group ${
                            file.type === 'directory'
                              ? 'hover:bg-cyan-900/20 border-cyan-500 hover:border-cyan-400'
                              : 'hover:bg-purple-900/20 border-purple-500 hover:border-purple-400'
                          } ${selectedFile === file.name ? 'bg-purple-900/30 border-purple-400' : ''}`}
                          style={{ animationDelay: `${i * 20}ms` }}
                        >
                          <div
                            onClick={() => handleFileClick(file)}
                            className="flex items-center gap-2 flex-1 min-w-0"
                          >
                            <span className={`text-lg shrink-0 ${file.type === 'directory' ? 'text-cyan-300' : 'text-purple-300'}`}>
                              {file.type === 'directory' ? '◉' : '◫'}
                            </span>
                            <span className={`flex-1 truncate ${file.type === 'directory' ? 'text-cyan-200' : 'text-gray-200'}`}>
                              {file.name}
                            </span>
                            <span className="text-gray-400 text-[9px] shrink-0">
                              {file.type === 'file' ? formatBytes(file.size) : '<DIR>'}
                            </span>
                          </div>
                          <button
                            onClick={(e) => { e.stopPropagation(); handleDeleteFile(file); }}
                            className="px-2 py-1 bg-red-500/10 border border-red-500/30 rounded text-[8px] text-red-400 opacity-0 group-hover:opacity-100 hover:bg-red-500/20 transition-all shrink-0"
                          >
                            [DEL]
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* File Stats */}
                <div className="mt-2 flex items-center justify-between text-[9px] text-gray-500">
                  <span>{files.length} items</span>
                  <span>{currentDir || 'root'}</span>
                </div>

                {/* Create Modal */}
                {showCreateModal && (
                  <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 animate-fadeIn">
                    <div className="bg-gray-900 border border-cyan-500/30 rounded-lg p-4 w-80">
                      <div className="text-cyan-400 text-sm font-bold mb-3">
                        :: CREATE_{createType.toUpperCase()} ::
                      </div>
                      <input
                        type="text"
                        value={createName}
                        onChange={(e) => setCreateName(e.target.value)}
                        placeholder={`${createType} name...`}
                        className="w-full bg-black border border-gray-700 rounded p-2 text-[10px] text-gray-300 focus:border-cyan-500 focus:outline-none mb-3"
                        autoFocus
                        onKeyDown={(e) => { if (e.key === 'Enter') handleCreate(); }}
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={handleCreate}
                          className="flex-1 px-3 py-2 bg-blue-500/20 border border-blue-500/30 rounded text-[9px] text-blue-400 hover:bg-blue-500/30 transition-all"
                        >
                          [CREATE]
                        </button>
                        <button
                          onClick={() => { setShowCreateModal(false); setCreateName(''); }}
                          className="flex-1 px-3 py-2 bg-gray-700/20 border border-gray-600/30 rounded text-[9px] text-gray-400 hover:bg-gray-700/30 transition-all"
                        >
                          [CANCEL]
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'metrics' && (
              <div>
                <div className="text-cyan-400 text-sm font-bold mb-4">:: PERFORMANCE_METRICS ::</div>

                {/* Real-time Graphs */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  {/* CPU History Graph */}
                  <div className="border border-gray-800 bg-black p-3 rounded">
                    <div className="flex justify-between items-center mb-2">
                      <div className="text-gray-500 text-[9px]">CPU_HISTORY (30s)</div>
                      <div className="text-yellow-400 text-xs font-bold">{totalCpu.toFixed(1)}%</div>
                    </div>
                    <div className="h-24 relative">
                      <svg viewBox="0 0 100 40" className="w-full h-full" preserveAspectRatio="none">
                        {/* Grid lines */}
                        {[0, 25, 50, 75, 100].map((x, i) => (
                          <line key={i} x1={x} y1="0" x2={x} y2="40" stroke="#1f2937" strokeWidth="0.5" />
                        ))}
                        {[0, 10, 20, 30, 40].map((y, i) => (
                          <line key={i} x1="0" y1={y} x2="100" y2={y} stroke="#1f2937" strokeWidth="0.5" />
                        ))}
                        {/* CPU Line Graph */}
                        <polyline
                          fill="none"
                          stroke="url(#cpuGradient)"
                          strokeWidth="1.5"
                          points={cpuHistory.map((val, i) => {
                            const x = (i / (cpuHistory.length - 1 || 1)) * 100;
                            const y = 40 - (val / 10) * 40;
                            return `${x},${y}`;
                          }).join(' ')}
                          className="transition-all duration-300"
                        />
                        {/* Fill gradient */}
                        <polygon
                          fill="url(#cpuFillGradient)"
                          opacity="0.3"
                          points={`0,40 ${cpuHistory.map((val, i) => {
                            const x = (i / (cpuHistory.length - 1 || 1)) * 100;
                            const y = 40 - (val / 10) * 40;
                            return `${x},${y}`;
                          }).join(' ')} 100,40`}
                        />
                        <defs>
                          <linearGradient id="cpuGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#f59e0b" />
                            <stop offset="100%" stopColor="#ef4444" />
                          </linearGradient>
                          <linearGradient id="cpuFillGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.5" />
                            <stop offset="100%" stopColor="#f59e0b" stopOpacity="0" />
                          </linearGradient>
                        </defs>
                      </svg>
                    </div>
                  </div>

                  {/* Memory History Graph */}
                  <div className="border border-gray-800 bg-black p-3 rounded">
                    <div className="flex justify-between items-center mb-2">
                      <div className="text-gray-500 text-[9px]">MEMORY_HISTORY (30s)</div>
                      <div className="text-purple-400 text-xs font-bold">{formatBytes(totalMem)}</div>
                    </div>
                    <div className="h-24 relative">
                      <svg viewBox="0 0 100 40" className="w-full h-full" preserveAspectRatio="none">
                        {/* Grid lines */}
                        {[0, 25, 50, 75, 100].map((x, i) => (
                          <line key={i} x1={x} y1="0" x2={x} y2="40" stroke="#1f2937" strokeWidth="0.5" />
                        ))}
                        {[0, 10, 20, 30, 40].map((y, i) => (
                          <line key={i} x1="0" y1={y} x2="100" y2={y} stroke="#1f2937" strokeWidth="0.5" />
                        ))}
                        {/* Memory Line Graph */}
                        <polyline
                          fill="none"
                          stroke="url(#memGradient)"
                          strokeWidth="1.5"
                          points={memHistory.map((val, i) => {
                            const x = (i / (memHistory.length - 1 || 1)) * 100;
                            const maxMem = 4000000000; // 4GB
                            const y = 40 - (val / maxMem) * 40;
                            return `${x},${y}`;
                          }).join(' ')}
                          className="transition-all duration-300"
                        />
                        {/* Fill gradient */}
                        <polygon
                          fill="url(#memFillGradient)"
                          opacity="0.3"
                          points={`0,40 ${memHistory.map((val, i) => {
                            const x = (i / (memHistory.length - 1 || 1)) * 100;
                            const maxMem = 4000000000; // 4GB
                            const y = 40 - (val / maxMem) * 40;
                            return `${x},${y}`;
                          }).join(' ')} 100,40`}
                        />
                        <defs>
                          <linearGradient id="memGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#8b5cf6" />
                            <stop offset="100%" stopColor="#ec4899" />
                          </linearGradient>
                          <linearGradient id="memFillGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.5" />
                            <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
                          </linearGradient>
                        </defs>
                      </svg>
                    </div>
                  </div>
                </div>

                {/* Overview Stats */}
                <div className="grid grid-cols-4 gap-2 mb-4">
                  <div className="border border-cyan-500/30 p-2 rounded hover:border-cyan-500 transition-all group">
                    <div className="text-gray-600 text-[8px] mb-1">PROCESSES</div>
                    <div className="text-xl font-bold text-cyan-400 group-hover:scale-110 transition-transform">{processes.length}</div>
                  </div>
                  <div className="border border-blue-500/30 p-2 rounded hover:border-blue-500 transition-all group">
                    <div className="text-gray-600 text-[8px] mb-1">ONLINE</div>
                    <div className="text-xl font-bold text-blue-400 group-hover:scale-110 transition-transform">{onlineCount}</div>
                  </div>
                  <div className="border border-yellow-500/30 p-2 rounded hover:border-yellow-500 transition-all group">
                    <div className="text-gray-600 text-[8px] mb-1">AVG_CPU</div>
                    <div className="text-xl font-bold text-yellow-400 group-hover:scale-110 transition-transform">
                      {processes.length > 0 ? (totalCpu / processes.length).toFixed(1) : '0'}%
                    </div>
                  </div>
                  <div className="border border-purple-500/30 p-2 rounded hover:border-purple-500 transition-all group">
                    <div className="text-gray-600 text-[8px] mb-1">TOTAL_MEM</div>
                    <div className="text-xl font-bold text-purple-400 group-hover:scale-110 transition-transform">{formatBytes(totalMem)}</div>
                  </div>
                </div>

                {/* System Health */}
                <div className="border border-gray-800 bg-black p-3 rounded mb-4">
                  <div className="text-gray-500 text-[9px] mb-3">:: SYSTEM_HEALTH ::</div>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="text-center">
                      <div className="text-gray-600 text-[8px] mb-1">UPTIME_RATIO</div>
                      <div className="text-2xl font-bold text-blue-400">
                        {processes.length > 0 ? ((onlineCount / processes.length) * 100).toFixed(0) : '0'}%
                      </div>
                      <div className="w-full bg-gray-900 h-1 rounded mt-2 overflow-hidden">
                        <div
                          className="bg-blue-500 h-full transition-all duration-500"
                          style={{ width: `${(onlineCount / Math.max(processes.length, 1)) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-gray-600 text-[8px] mb-1">TOTAL_RESTARTS</div>
                      <div className="text-2xl font-bold text-yellow-400">
                        {processes.reduce((sum, p) => sum + p.restarts, 0)}
                      </div>
                      <div className="text-[8px] text-gray-600 mt-2">All processes</div>
                    </div>
                    <div className="text-center">
                      <div className="text-gray-600 text-[8px] mb-1">HELIATH_STATUS</div>
                      <div className={`text-xl font-bold ${onlineCount === processes.length && processes.length > 0 ? 'text-blue-400' : onlineCount > 0 ? 'text-yellow-400' : 'text-red-400'}`}>
                        {onlineCount === processes.length && processes.length > 0 ? 'HEALTHY' : onlineCount > 0 ? 'WARNING' : 'CRITICAL'}
                      </div>
                      <div className="text-[8px] text-gray-600 mt-2">Overall system</div>
                    </div>
                  </div>
                </div>

                {/* Process Details Table */}
                <div className="border border-gray-800 bg-black p-3 rounded mb-4">
                  <div className="text-gray-500 text-[9px] mb-3">:: PROCESS_DETAILS ::</div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-[9px]">
                      <thead>
                        <tr className="text-gray-500 border-b border-gray-800">
                          <th className="text-left py-2 px-2">PROCESS</th>
                          <th className="text-left py-2 px-2">STATUS</th>
                          <th className="text-right py-2 px-2">CPU</th>
                          <th className="text-right py-2 px-2">MEMORY</th>
                          <th className="text-right py-2 px-2">UPTIME</th>
                          <th className="text-right py-2 px-2">RESTARTS</th>
                        </tr>
                      </thead>
                      <tbody>
                        {processes.map((p) => (
                          <tr key={p.id} className={`border-b border-gray-900 hover:bg-cyan-900/10 transition-colors ${animatingProcesses.has(p.id) ? 'bg-cyan-900/5' : ''}`}>
                            <td className="py-2 px-2 text-cyan-300">{p.name}</td>
                            <td className="py-2 px-2">
                              <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold ${
                                p.status === 'online' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'
                              }`}>
                                {p.status.toUpperCase()}
                              </span>
                            </td>
                            <td className="py-2 px-2 text-right text-yellow-400">{p.cpu.toFixed(2)}%</td>
                            <td className="py-2 px-2 text-right text-purple-400">{formatBytes(p.memory)}</td>
                            <td className="py-2 px-2 text-right text-gray-400">{formatUptime(p.uptime)}</td>
                            <td className="py-2 px-2 text-right text-gray-400">{p.restarts}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Charts */}
                <div className="grid grid-cols-2 gap-4">
                  {/* Memory Distribution */}
                  <div className="border border-gray-800 bg-black p-3 rounded">
                    <div className="text-gray-500 text-[9px] mb-3">MEMORY_DISTRIBUTION</div>
                    <div className="space-y-3">
                      {processes.map((p) => (
                        <div key={p.id} className="space-y-1">
                          <div className="flex justify-between text-[9px]">
                            <span className="text-gray-400 truncate flex-1">{p.name}</span>
                            <span className="text-purple-400 ml-2">{formatBytes(p.memory)}</span>
                            <span className="text-gray-600 ml-2">{((p.memory / totalMem) * 100 || 0).toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-gray-900 h-1.5 rounded-full overflow-hidden">
                            <div
                              className="bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 h-full rounded-full transition-all duration-500 ease-out relative"
                              style={{ width: `${(p.memory / totalMem) * 100 || 0}%` }}
                            >
                              <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* CPU Distribution */}
                  <div className="border border-gray-800 bg-black p-3 rounded">
                    <div className="text-gray-500 text-[9px] mb-3">CPU_DISTRIBUTION</div>
                    <div className="space-y-3">
                      {processes.map((p) => (
                        <div key={p.id} className="space-y-1">
                          <div className="flex justify-between text-[9px]">
                            <span className="text-gray-400 truncate flex-1">{p.name}</span>
                            <span className={`text-yellow-400 ml-2 ${animatingProcesses.has(p.id) ? 'animate-pulse' : ''}`}>{p.cpu.toFixed(2)}%</span>
                          </div>
                          <div className="w-full bg-gray-900 h-1.5 rounded-full overflow-hidden">
                            <div
                              className="bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500 h-full rounded-full transition-all duration-500 ease-out"
                              style={{ width: `${Math.min(p.cpu * 5, 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Resource Usage Gauge */}
                <div className="mt-4 border border-gray-800 bg-black p-3 rounded">
                  <div className="text-gray-500 text-[9px] mb-3">RESOURCE_UTILIZATION</div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="flex justify-between text-[9px] mb-2">
                        <span className="text-purple-400">MEMORY</span>
                        <span className="text-gray-400">{((totalMem / 4000000000) * 100).toFixed(1)}%</span>
                      </div>
                      <div className="relative h-4 bg-gray-900 rounded-full overflow-hidden">
                        <div
                          className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min((totalMem / 4000000000) * 100, 100)}%` }}
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
                        </div>
                      </div>
                      <div className="text-[8px] text-gray-600 mt-1 text-right">4 GB max</div>
                    </div>
                    <div>
                      <div className="flex justify-between text-[9px] mb-2">
                        <span className="text-yellow-400">CPU</span>
                        <span className="text-gray-400">{totalCpu.toFixed(1)}%</span>
                      </div>
                      <div className="relative h-4 bg-gray-900 rounded-full overflow-hidden">
                        <div
                          className="absolute inset-y-0 left-0 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(totalCpu, 100)}%` }}
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
                        </div>
                      </div>
                      <div className="text-[8px] text-gray-600 mt-1 text-right">{processes.length} cores</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN - The Stream (25%) */}
        <div className="w-[25%] border-l border-cyan-900/50 flex flex-col bg-black/95 backdrop-blur-sm">

          {/* Header */}
          <div className="border-b border-cyan-900/50 p-3">
            <div className="text-cyan-400 text-sm font-bold">:: LIVE_FEED ::</div>
            <div className="text-gray-500 text-[10px] mt-1">REAL-TIME_DATA_STREAM</div>
          </div>

          {/* Summary Metrics */}
          <div className="border-b border-cyan-900/50 p-3">
            <div className="grid grid-cols-2 gap-2">
              <div className="border border-gray-800 p-2 rounded hover:border-cyan-500/50 transition-all duration-300 group">
                <div className="text-gray-600 text-[9px]">UPTIME</div>
                <div className="text-cyan-400 text-sm font-bold group-hover:scale-110 transition-transform">99.9%</div>
              </div>
              <div className="border border-gray-800 p-2 rounded hover:border-blue-500/50 transition-all duration-300 group">
                <div className="text-gray-600 text-[9px]">REQS</div>
                <div className="text-blue-400 text-sm font-bold group-hover:scale-110 transition-transform">42K</div>
              </div>
              <div className="border border-gray-800 p-2 rounded hover:border-red-500/50 transition-all duration-300 group">
                <div className="text-gray-600 text-[9px]">ERRORS</div>
                <div className="text-red-400 text-sm font-bold group-hover:scale-110 transition-transform">0</div>
              </div>
              <div className="border border-gray-800 p-2 rounded hover:border-yellow-500/50 transition-all duration-300 group">
                <div className="text-gray-600 text-[9px]">LOAD</div>
                <div className="text-yellow-400 text-sm font-bold group-hover:scale-110 transition-transform">{totalCpu.toFixed(0)}%</div>
              </div>
            </div>
          </div>

          {/* Cognitive Stream */}
          <div className="flex-1 overflow-hidden flex flex-col">
            <div className="p-3 border-b border-cyan-900/50">
              <div className="text-cyan-400 text-[10px]">:: COGNITIVE_STREAM ::</div>
            </div>
            <div className="flex-1 overflow-auto p-3 font-mono text-[9px]">
              {logs.length === 0 ? (
                <div className="text-gray-700 animate-pulse">[ AWAITING_DATA_STREAM ]</div>
              ) : (
                <div className="space-y-2">
                  {logs.slice(0, 15).map((log, i) => (
                    <div
                      key={i}
                      className="mb-2 leading-tight p-1 rounded hover:bg-cyan-900/10 transition-all duration-200 animate-slideIn"
                      style={{ animationDelay: `${i * 30}ms` }}
                    >
                      <span className="text-gray-700">[{log.timestamp}]</span>
                      <span className="text-gray-500 ml-1">{log.message.substring(0, 50)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Production Metrics */}
          <div className="border-t border-cyan-900/50 p-3">
            <div className="text-cyan-400 text-[10px] mb-2">:: PRODUCTION_METRICS ::</div>
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-gray-500 text-[9px] mb-1">
                  <span>MEMORY_USAGE</span>
                  <span className="text-purple-400">{((totalMem / 4000000000) * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-900 h-1 rounded overflow-hidden">
                  <div
                    className="bg-purple-500 h-full transition-all duration-500 ease-out"
                    style={{ width: `${Math.min((totalMem / 4000000000) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-gray-500 text-[9px] mb-1">
                  <span>CAPACITY</span>
                  <span className="text-cyan-400">{((onlineCount / Math.max(processes.length, 1)) * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-900 h-1 rounded overflow-hidden">
                  <div
                    className="bg-cyan-500 h-full transition-all duration-500 ease-out"
                    style={{ width: `${(onlineCount / Math.max(processes.length, 1)) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="border-t border-cyan-900/50 p-2 text-gray-700 text-[9px]">
            <div>UPDATED: {mounted ? lastUpdate.toLocaleTimeString() : '--:--:--'}</div>
            <div className="flex items-center gap-2">
              <span>REFRESH: 3s</span>
              <div className={`w-1.5 h-1.5 rounded-full ${mounted ? 'bg-blue-400 animate-pulse' : 'bg-gray-600'}`}></div>
            </div>
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

        @keyframes slideIn {
          from { opacity: 0; transform: translateX(-10px); }
          to { opacity: 1; transform: translateX(0); }
        }

        @keyframes pulseGlow {
          0%, 100% { box-shadow: 0 0 5px rgba(6, 182, 212, 0.3); }
          50% { box-shadow: 0 0 20px rgba(6, 182, 212, 0.6); }
        }

        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }

        @keyframes bounceIn {
          0% { transform: scale(0.3); opacity: 0; }
          50% { transform: scale(1.05); }
          70% { transform: scale(0.9); }
          100% { transform: scale(1); opacity: 1; }
        }

        @keyframes rotate {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @keyframes borderDraw {
          0% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
          50% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
          100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
        }

        @keyframes typewriter {
          from { width: 0; }
          to { width: 100%; }
        }

        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }

        @keyframes gradientShift {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }

        @keyframes scaleIn {
          from { transform: scale(0); opacity: 0; }
          to { transform: scale(1); opacity: 1; }
        }

        @keyframes ripple {
          0% { transform: scale(0); opacity: 1; }
          100% { transform: scale(4); opacity: 0; }
        }

        @keyframes breathe {
          0%, 100% { opacity: 0.6; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.05); }
        }

        @keyframes scanline {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(100vh); }
        }

        @keyframes flicker {
          0%, 100% { opacity: 1; }
          41% { opacity: 1; }
          42% { opacity: 0.8; }
          43% { opacity: 1; }
          45% { opacity: 0.3; }
          46% { opacity: 1; }
        }

        @keyframes dataFlow {
          0% { background-position: 0% 50%; }
          100% { background-position: 200% 50%; }
        }

        @keyframes pulseBorder {
          0%, 100% { border-color: rgba(6, 182, 212, 0.3); }
          50% { border-color: rgba(6, 182, 212, 0.8); }
        }

        @keyframes glowPulse {
          0%, 100% { box-shadow: 0 0 5px rgba(6, 182, 212, 0.2); }
          50% { box-shadow: 0 0 20px rgba(6, 182, 212, 0.6), 0 0 30px rgba(6, 182, 212, 0.4); }
        }

        @keyframes rotate3d {
          0% { transform: rotateY(0deg); }
          100% { transform: rotateY(360deg); }
        }

        @keyframes wave {
          0% { transform: translateX(0) translateY(0); }
          25% { transform: translateX(-5px) translateY(5px); }
          50% { transform: translateX(0) translateY(0); }
          75% { transform: translateX(5px) translateY(-5px); }
          100% { transform: translateX(0) translateY(0); }
        }

        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out forwards;
        }

        .animate-slideIn {
          animation: slideIn 0.2s ease-out forwards;
        }

        .animate-bounceIn {
          animation: bounceIn 0.6s ease-out forwards;
        }

        .animate-float {
          animation: float 3s ease-in-out infinite;
        }

        .animate-scaleIn {
          animation: scaleIn 0.3s ease-out forwards;
        }

        .animate-breathe {
          animation: breathe 4s ease-in-out infinite;
        }

        .animate-scanline {
          animation: scanline 8s linear infinite;
        }

        .animate-flicker {
          animation: flicker 3s infinite;
        }

        .animate-dataFlow {
          animation: dataFlow 3s linear infinite;
        }

        .animate-pulseBorder {
          animation: pulseBorder 2s ease-in-out infinite;
        }

        .animate-glowPulse {
          animation: glowPulse 2s ease-in-out infinite;
        }

        .animate-wave {
          animation: wave 3s ease-in-out infinite;
        }

        /* Custom Scrollbar Styles */
        ::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }

        ::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.3);
          border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb {
          background: rgba(6, 182, 212, 0.3);
          border-radius: 3px;
          transition: background 0.3s;
        }

        ::-webkit-scrollbar-thumb:hover {
          background: rgba(6, 182, 212, 0.6);
        }

        ::-webkit-scrollbar-corner {
          background: rgba(0, 0, 0, 0.3);
        }

        /* Firefox scrollbar */
        * {
          scrollbar-width: thin;
          scrollbar-color: rgba(6, 182, 212, 0.3) rgba(0, 0, 0, 0.3);
        }
      `}</style>
    </div>
  );
}
