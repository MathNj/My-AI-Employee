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

interface AdProduct {
  id: number;
  url: string;
  title: string;
  price: number;
  category: string;
  status: string;
  days_out: number;
  revenue_impact: number;
  is_top_selling: boolean;
  last_checked: string;
}

interface AdPerformanceData {
  ad_name: string;
  price: number;
  category: string;
  ad_spend_actual: number;
  sales_count: number;
  conversion_rate: number;
  total_stockout_days: number;
  roas: number;
  revenue: number;
}

interface PerformanceSummary {
  total_ad_spend: number;
  total_revenue: number;
  overall_roas: number;
  total_stockout_days: number;
}

interface HeatmapData {
  ad_name: string;
  metric_value: number;
  normalized: number;
  color_category: string;
}

export default function Dashboard() {
  const [processes, setProcesses] = useState<Process[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'processes' | 'logs' | 'files' | 'metrics' | 'ad-management'>('overview');
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

  // Ad management state
  const [adProducts, setAdProducts] = useState<AdProduct[]>([]);
  const [adSummary, setAdSummary] = useState<any>(null);
  const [adLoading, setAdLoading] = useState(false);
  const [adSubTab, setAdSubTab] = useState<'inventory' | 'performance' | 'topworst' | 'heatmap' | 'backinstock'>('inventory');
  const [performanceData, setPerformanceData] = useState<AdPerformanceData[]>([]);
  const [performanceSummary, setPerformanceSummary] = useState<PerformanceSummary | null>(null);
  const [topProducts, setTopProducts] = useState<any[]>([]);
  const [worstProducts, setWorstProducts] = useState<any[]>([]);
  const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([]);
  const [selectedMetric, setSelectedMetric] = useState('roas');
  const [topWorstCount, setTopWorstCount] = useState(10);
  const [stockCheckLoading, setStockCheckLoading] = useState(false);
  const [realStockData, setRealStockData] = useState<any[]>([]);
  const [lastStockCheck, setLastStockCheck] = useState<Date | null>(null);
  const [hasCheckedStock, setHasCheckedStock] = useState(false);

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

  useEffect(() => {
    if (activeTab === 'ad-management') {
      fetchAdData();
      // Load enhanced data based on sub-tab
      if (adSubTab === 'performance') {
        fetchPerformanceData();
      } else if (adSubTab === 'topworst') {
        fetchTopWorstProducts();
      } else if (adSubTab === 'heatmap') {
        fetchHeatmapData();
      } else if (adSubTab === 'backinstock') {
        // Automatically check real stock when opening back-in-stock tab
        if (!hasCheckedStock) {
          checkRealStock();
          setHasCheckedStock(true);
        } else {
          fetchPerformanceData();
        }
      }
    }
  }, [activeTab, adSubTab]);

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

  const fetchAdData = async () => {
    setAdLoading(true);
    try {
      const res = await fetch('/api/ad-data?action=products');
      const data = await res.json();
      setAdProducts(data.products || []);
      setAdSummary(data.summary || null);
    } catch (error) {
      console.error('Error fetching ad data:', error);
    } finally {
      setAdLoading(false);
    }
  };

  const refreshAdData = async () => {
    try {
      await fetch('/api/ad-data?action=refresh');
      await fetchAdData();
    } catch (error) {
      console.error('Error refreshing ad data:', error);
    }
  };

  // Check real stock via web scraping using ad_monitoring skill
  const checkRealStock = async () => {
    setStockCheckLoading(true);
    try {
      const res = await fetch('/api/ad-data?action=check-stock');
      const data = await res.json();

      if (data.success) {
        console.log('Stock check response:', data);

        // Merge scraped data with products - match by URL for accuracy
        const updatedProducts = adProducts.map(product => {
          // Try to match by URL first (most reliable)
          const scraped = data.stock_updates?.find((s: any) => {
            // Normalize URLs for comparison
            const normalizeUrl = (url: string) => url.replace(/^https?:\/\//, '').replace(/\/$/, '').toLowerCase();
            return normalizeUrl(s.url) === normalizeUrl(product.url);
          });

          if (scraped && scraped.scraped) {
            // Update with real scraped data - use API's days_out directly
            return {
              ...product,
              title: scraped.title || product.title,
              status: scraped.status,
              days_out: scraped.days_out ?? 0,  // Use API's calculated days_out
              price: scraped.price || product.price,
              last_checked: scraped.scraped_at,
              source: scraped.source || 'unknown'  // Track data source
            };
          }
          return product;
        });

        console.log('Updated products:', updatedProducts.filter(p => p.status === 'Out of Stock' || p.status === 'Low Stock'));

        // Update state first
        setAdProducts(updatedProducts);
        setRealStockData(data.stock_updates || []);
        setLastStockCheck(new Date());

        // Regenerate performance data with updated products (pass directly to avoid race condition)
        await fetchPerformanceDataWithProducts(updatedProducts);
      }
    } catch (error) {
      console.error('Error checking stock:', error);
    } finally {
      setStockCheckLoading(false);
    }
  };

  // Fetch performance data with specific products (avoids race condition)
  const fetchPerformanceDataWithProducts = async (products: any[]) => {
    try {
      const totalRevenue = products.reduce((sum, product) => {
        const seed = product.id * 123;
        let salesCount: number;

        if (product.price < 300) {
          salesCount = Math.floor(seededRandom(seed) * 50) + 1;
        } else if (product.price < 400) {
          salesCount = Math.floor(seededRandom(seed) * 30) + 1;
        } else {
          salesCount = Math.floor(seededRandom(seed) * 20) + 1;
        }

        return sum + (product.price * salesCount);
      }, 0);

      const adSpendPercentage = 0.05 + (seededRandom(999) * 0.05);
      const totalAdSpend = totalRevenue * adSpendPercentage;
      const overallROAS = totalRevenue / totalAdSpend;
      const totalStockoutDays = products.reduce((sum, p) => sum + p.days_out, 0);

      setPerformanceSummary({
        total_ad_spend: Math.round(totalAdSpend),
        total_revenue: Math.round(totalRevenue),
        overall_roas: Math.round(overallROAS * 100) / 100,
        total_stockout_days: totalStockoutDays
      });

      const performanceData = products.map(product => {
        const seed = product.id * 456;
        let salesCount: number;
        let conversionRate: number;

        if (product.price < 300) {
          salesCount = Math.floor(seededRandom(seed) * 50) + 1;
          conversionRate = 0.01 + (seededRandom(seed + 1) * 0.04);
        } else if (product.price < 400) {
          salesCount = Math.floor(seededRandom(seed) * 30) + 1;
          conversionRate = 0.01 + (seededRandom(seed + 1) * 0.03);
        } else {
          salesCount = Math.floor(seededRandom(seed) * 20) + 1;
          conversionRate = 0.01 + (seededRandom(seed + 1) * 0.02);
        }

        const revenue = product.price * salesCount;
        const adSpendPercent = 0.05 + (seededRandom(seed + 2) * 0.05);
        const adSpend = revenue * adSpendPercent;
        const roas = revenue / adSpend;

        return {
          ad_name: product.title,
          price: product.price,
          category: product.category,
          ad_spend_actual: Math.round(adSpend),
          sales_count: salesCount,
          conversion_rate: Math.round(conversionRate * 100) / 100,
          total_stockout_days: product.days_out, // Uses real scraped days_out
          roas: Math.round(roas * 100) / 100,
          revenue: Math.round(revenue)
        };
      });

      setPerformanceData(performanceData);
    } catch (error) {
      console.error('Error generating performance data:', error);
      setPerformanceSummary(null);
      setPerformanceData([]);
    }
  };

  // Seeded random number generator for consistent data
  const seededRandom = (seed: number): number => {
    const x = Math.sin(seed) * 10000;
    return x - Math.floor(x);
  };

  // Enhanced ad management fetch functions
  const fetchPerformanceData = async () => {
    try {
      // Generate realistic performance data based on price ranges
      // Budget (<₨300): 1-50 sales/month
      // Mid-range (₨300-₨400): 1-30 sales/month
      // Premium (>₨400): 1-20 sales/month
      // Uses seeded random based on product ID for consistency

      const totalRevenue = adProducts.reduce((sum, product) => {
        const seed = product.id * 123; // Unique seed per product
        let salesCount: number;

        if (product.price < 300) {
          salesCount = Math.floor(seededRandom(seed) * 50) + 1; // 1-50 sales
        } else if (product.price < 400) {
          salesCount = Math.floor(seededRandom(seed) * 30) + 1; // 1-30 sales
        } else {
          salesCount = Math.floor(seededRandom(seed) * 20) + 1; // 1-20 sales
        }

        return sum + (product.price * salesCount);
      }, 0);

      // Ad spend: 5-10% of revenue (10-20x ROAS - highly profitable)
      const adSpendPercentage = 0.05 + (seededRandom(999) * 0.05); // Seeded random 5-10%
      const totalAdSpend = totalRevenue * adSpendPercentage;
      const overallROAS = totalRevenue / totalAdSpend;
      const totalStockoutDays = adProducts.reduce((sum, p) => sum + p.days_out, 0);

      setPerformanceSummary({
        total_ad_spend: Math.round(totalAdSpend),
        total_revenue: Math.round(totalRevenue),
        overall_roas: Math.round(overallROAS * 100) / 100,
        total_stockout_days: totalStockoutDays
      });

      // Generate per-product performance data with seeded random values
      const performanceData = adProducts.map(product => {
        const seed = product.id * 456; // Different seed for performance metrics
        let salesCount: number;
        let conversionRate: number;

        if (product.price < 300) {
          salesCount = Math.floor(seededRandom(seed) * 50) + 1; // 1-50 sales
          conversionRate = 0.01 + (seededRandom(seed + 1) * 0.04); // 1-5% conversion
        } else if (product.price < 400) {
          salesCount = Math.floor(seededRandom(seed) * 30) + 1; // 1-30 sales
          conversionRate = 0.01 + (seededRandom(seed + 1) * 0.03); // 1-4% conversion
        } else {
          salesCount = Math.floor(seededRandom(seed) * 20) + 1; // 1-20 sales
          conversionRate = 0.01 + (seededRandom(seed + 1) * 0.02); // 1-3% conversion
        }

        const revenue = product.price * salesCount;
        // Ad spend: 5-10% of revenue (10-20x ROAS - highly profitable)
        const adSpendPercent = 0.05 + (seededRandom(seed + 2) * 0.05); // Seeded random 5-10%
        const adSpend = revenue * adSpendPercent;
        const roas = revenue / adSpend;

        return {
          ad_name: product.title,
          price: product.price,
          category: product.category,
          ad_spend_actual: Math.round(adSpend),
          sales_count: salesCount,
          conversion_rate: Math.round(conversionRate * 100) / 100,
          total_stockout_days: product.days_out,
          roas: Math.round(roas * 100) / 100,
          revenue: Math.round(revenue)
        };
      });

      setPerformanceData(performanceData);
    } catch (error) {
      console.error('Error generating performance data:', error);
      setPerformanceSummary(null);
      setPerformanceData([]);
    }
  };

  const fetchTopWorstProducts = async (metric: string = selectedMetric, count: number = topWorstCount) => {
    try {
      // First, ensure performance data is available
      if (performanceData.length === 0) {
        await fetchPerformanceData();
      }

      // Use existing performance data for consistency
      const productsWithPerformance = performanceData.map(data => ({
        ...data,
        price: data.price,
        days_out: data.total_stockout_days
      }));

      // Sort products by selected performance metric
      const sorted = [...productsWithPerformance].sort((a, b) => {
        if (metric === 'sales_count') return (b as any).sales_count - (a as any).sales_count;
        if (metric === 'Product_Price' || metric === 'price') return b.price - a.price;
        if (metric === 'total_stockout_days' || metric === 'days_out') return b.days_out - a.days_out;
        if (metric === 'revenue') return (b as any).revenue - (a as any).revenue;
        if (metric === 'roas') return (b as any).roas - (a as any).roas;
        if (metric === 'conversion_rate') return (b as any).conversion_rate - (a as any).conversion_rate;
        return 0;
      });

      const top = sorted.slice(0, count);
      const worst = sorted.slice(-count).reverse();

      setTopProducts(top);
      setWorstProducts(worst);
    } catch (error) {
      console.error('Error generating top/worst products:', error);
      setTopProducts([]);
      setWorstProducts([]);
    }
  };

  const fetchHeatmapData = async (metric: string = selectedMetric) => {
    try {
      // Ensure performance data is available for performance metrics
      if (performanceData.length === 0) {
        await fetchPerformanceData();
      }

      // Map metric names to data sources
      // Performance metrics: roas, revenue, sales_count, conversion_rate
      // Product metrics: Product_Price, total_stockout_days
      const performanceMetrics = ['roas', 'revenue', 'sales_count', 'conversion_rate'];
      const productMetrics = ['Product_Price', 'total_stockout_days', 'price', 'days_out'];

      // Use appropriate data source based on metric
      const sourceData = performanceMetrics.includes(metric) ? performanceData :
                          productMetrics.includes(metric) ? adProducts :
                          performanceData;

      // Map metric to property names
      const getMetricValue = (item: any, metric: string): number => {
        switch (metric) {
          case 'roas': return item.roas || 0;
          case 'revenue': return item.revenue || 0;
          case 'sales_count': return item.sales_count || 0;
          case 'conversion_rate': return item.conversion_rate || 0;
          case 'Product_Price':
          case 'price': return item.price || 0;
          case 'total_stockout_days':
          case 'days_out': return item.days_out || item.total_stockout_days || 0;
          default: return 0;
        }
      };

      const getName = (item: any): string => {
        return item.ad_name || item.title || 'Unknown';
      };

      // Get all values and find max for normalization
      const values = sourceData.map(item => getMetricValue(item, metric));
      const maxVal = Math.max(...values, 0.001); // Avoid division by zero

      // Generate heatmap data
      const data = sourceData.map((item, index) => {
        const value = getMetricValue(item, metric);
        const normalized = value / maxVal;

        // Determine color category
        let color_category = 'low';
        if (normalized > 0.7) color_category = 'high';
        else if (normalized > 0.4) color_category = 'medium';

        return {
          ad_name: getName(item),
          metric_value: value,
          normalized: Math.round(normalized * 100) / 100,
          color_category
        };
      });

      setHeatmapData(data);
    } catch (error) {
      console.error('Error generating heatmap data:', error);
      setHeatmapData([]);
    }
  };

  const formatBytes = (bytes: number): string => {
    if (!bytes) return '0 MB';
    const mb = bytes / (1024 * 1024);
    return mb >= 1024 ? `${(mb / 1024).toFixed(1)} GB` : `${mb.toFixed(1)} MB`;
  };

  const formatMetricValue = (product: any, metric: string): string => {
    switch (metric) {
      case 'roas':
        return `${(product.roas || 0).toFixed(1)}x`;
      case 'revenue':
        return `₨${(product.revenue || 0).toLocaleString()}`;
      case 'sales_count':
        return `${product.sales_count || 0} sales`;
      case 'conversion_rate':
        return `${((product.conversion_rate || 0) * 100).toFixed(1)}%`;
      case 'Product_Price':
      case 'price':
        return `₨${(product.price || 0).toLocaleString()}`;
      case 'total_stockout_days':
      case 'days_out':
        return `${product.days_out || 0} days`;
      default:
        return '0';
    }
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
      default: return 'text-gray-100 border-gray-400 bg-gray-400/10';
    }
  };

  const onlineCount = processes.filter(p => p.status === 'online').length;
  const totalCpu = processes.reduce((sum, p) => sum + p.cpu, 0);
  const totalMem = processes.reduce((sum, p) => sum + p.memory, 0);

  return (
    <div className="min-h-screen bg-black font-mono text-lg" style={{
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
            <div className="text-cyan-400 text-lg font-bold animate-wave">:: PM2_CONTROLLER ::</div>
            <div className="text-gray-300 text-[14px] mt-1">DIGITAL EMPLOYEE OS v2.0</div>
          </div>

          {/* Status Widget */}
          <div className="border-b border-cyan-900/50 p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-2 h-2 rounded-full ${onlineCount > 0 ? 'bg-blue-400 animate-ping animate-glowPulse' : 'bg-red-400 animate-glowPulse'}`}></div>
              <div className={`w-2 h-2 rounded-full ${onlineCount > 0 ? 'bg-blue-400 animate-pulse' : 'bg-red-400 animate-pulse'}`}></div>
              <span className="text-cyan-300 text-[14px] animate-flicker">SYSTEM_STATUS</span>
            </div>
            <div className={`text-lg font-bold transition-all duration-300 ${onlineCount > 0 ? 'text-blue-400' : 'text-red-400'}`}>
              {onlineCount > 0 ? 'OPERATIONAL' : 'OFFLINE'}
            </div>
          </div>

          {/* Key Metrics */}
          <div className="border-b border-cyan-900/50 p-3 flex-1 overflow-auto">
            <div className="text-cyan-400 text-[14px] mb-3">:: SYSTEM_METRICS ::</div>

            <div className="space-y-3">
              <div className="group">
                <div className="flex justify-between text-gray-100 text-[14px] mb-1">
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
                <div className="flex justify-between text-gray-100 text-[14px] mb-1">
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
                <div className="flex justify-between text-gray-100 text-[14px] mb-1">
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
                <div className="flex justify-between text-gray-100 text-[14px] mb-1">
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
              <div className="text-cyan-400 text-[13px] mb-2">:: RESOURCE_ALLOCATION ::</div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300 text-[14px]">SYSTEM</span>
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-cyan-400 rounded animate-pulse"></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300 text-[14px]">USER</span>
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-blue-400 rounded animate-pulse"></div>
                    <div className="w-2 h-2 bg-blue-400 rounded animate-pulse" style={{ animationDelay: '0.3s' }}></div>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300 text-[14px]">IDLE</span>
                  <div className="w-2 h-2 bg-gray-600 rounded"></div>
                </div>
              </div>
            </div>

            {/* Active Processes List */}
            <div className="mt-4">
              <div className="text-cyan-400 text-[14px] mb-2">:: ACTIVE_PROCESSES ::</div>
              <div className="space-y-1">
                {processes.slice(0, 8).map(p => (
                  <div
                    key={p.id}
                    className="flex items-center gap-2 text-[14px] p-1.5 rounded border border-transparent hover:border-cyan-500/30 hover:bg-cyan-950/30 transition-all cursor-pointer group"
                    onMouseEnter={() => setHoveredProcess(p.id)}
                    onMouseLeave={() => setHoveredProcess(null)}
                  >
                    <div className={`w-1.5 h-1.5 rounded-full ${p.status === 'online' ? 'bg-blue-400 animate-pulse' : 'bg-red-400'}`}></div>
                    <span className="text-gray-100 flex-1 truncate group-hover:text-cyan-300 transition-colors">{p.name}</span>
                    <span className={`text-cyan-300 transition-all duration-300 ${animatingProcesses.has(p.id) ? 'scale-125 font-bold text-yellow-400' : ''}`}>{p.cpu.toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="mt-4">
              <div className="text-cyan-400 text-[14px] mb-2">:: QUICK_ACTIONS ::</div>
              <div className="grid grid-cols-2 gap-2">
                <button className="p-2 border border-gray-800 rounded bg-black/30 hover:border-cyan-500/50 hover:bg-cyan-950/20 transition-all text-[14px] text-gray-100 hover:text-cyan-300 group">
                  <div className="text-lg mb-1 group-hover:scale-110 transition-transform text-cyan-300">⟳</div>
                  REFRESH
                </button>
                <button className="p-2 border border-gray-800 rounded bg-black/30 hover:border-blue-500/50 hover:bg-blue-950/20 transition-all text-[14px] text-gray-100 hover:text-blue-300 group">
                  <div className="text-lg mb-1 group-hover:scale-110 transition-transform text-blue-300">▶</div>
                  START ALL
                </button>
                <button className="p-2 border border-gray-800 rounded bg-black/30 hover:border-yellow-500/50 hover:bg-yellow-950/20 transition-all text-[14px] text-gray-100 hover:text-yellow-300 group">
                  <div className="text-lg mb-1 group-hover:scale-110 transition-transform text-yellow-300">❚❚</div>
                  PAUSE
                </button>
                <button className="p-2 border border-gray-800 rounded bg-black/30 hover:border-red-500/50 hover:bg-red-950/20 transition-all text-[14px] text-gray-100 hover:text-red-300 group">
                  <div className="text-lg mb-1 group-hover:scale-110 transition-transform text-red-300">■</div>
                  STOP ALL
                </button>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="border-t border-cyan-900/50 p-2 text-gray-200 text-[13px]">
            <div>LATENCY: {mounted ? (Math.random() * 2 + 0.5).toFixed(2) : '--.--'}ms</div>
            <div>UPTIME: {mounted ? formatUptime(Date.now() / 1000) : '--:--'}</div>
          </div>
        </div>

        {/* CENTER COLUMN - The Workspace (55%) */}
        <div className="w-[55%] flex flex-col bg-black/90 backdrop-blur-sm">

          {/* Navigation Tabs */}
          <div className="border-b border-cyan-900/50 flex">
            {(['overview', 'processes', 'logs', 'files', 'metrics', 'ad-management'] as const).map((tab, i) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 text-[14px] font-bold transition-all duration-300 relative flex-1 hover:bg-cyan-900/10 ${
                  activeTab === tab
                    ? 'bg-cyan-500/20 text-cyan-400'
                    : 'text-gray-300 hover:text-gray-300'
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
                    <div className="text-gray-300 text-[14px] mb-1 relative z-10">PROCESSES</div>
                    <div className="text-xl font-bold text-cyan-400 group-hover:scale-110 transition-transform relative z-10">{processes.length}</div>
                    <div className="text-[7px] text-gray-200 mt-1 relative z-10">Total monitored</div>
                  </div>
                  <div className="bg-gray-900/50 border border-blue-500/30 rounded-lg p-2 backdrop-blur-sm hover:border-blue-400 hover:shadow-[0_0_20px_rgba(74,222,128,0.3)] transition-all duration-300 group relative overflow-hidden animate-fadeIn" style={{ animationDelay: '0.1s' }}>
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-green-400/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
                    <div className="text-gray-300 text-[14px] mb-1 relative z-10">ONLINE</div>
                    <div className="text-xl font-bold text-blue-400 group-hover:scale-110 transition-transform relative z-10">{onlineCount}</div>
                    <div className="text-[7px] text-gray-200 mt-1 relative z-10">Active processes</div>
                  </div>
                  <div className="bg-gray-900/50 border border-yellow-500/30 rounded-lg p-2 backdrop-blur-sm hover:border-yellow-400 hover:shadow-[0_0_20px_rgba(250,204,21,0.3)] transition-all duration-300 group relative overflow-hidden animate-fadeIn" style={{ animationDelay: '0.2s' }}>
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-yellow-400/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
                    <div className="text-gray-300 text-[14px] mb-1 relative z-10">CPU_USAGE</div>
                    <div className="text-xl font-bold text-yellow-400 group-hover:scale-110 transition-transform relative z-10">{totalCpu.toFixed(1)}%</div>
                    <div className="text-[7px] text-gray-200 mt-1 relative z-10">Total load</div>
                  </div>
                  <div className="bg-gray-900/50 border border-purple-500/30 rounded-lg p-2 backdrop-blur-sm hover:border-purple-400 hover:shadow-[0_0_20px_rgba(168,85,247,0.3)] transition-all duration-300 group relative overflow-hidden animate-fadeIn" style={{ animationDelay: '0.3s' }}>
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-purple-400/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
                    <div className="text-gray-300 text-[14px] mb-1 relative z-10">MEMORY</div>
                    <div className="text-xl font-bold text-purple-400 group-hover:scale-110 transition-transform relative z-10">{(totalMem / 1024 / 1024 / 1024).toFixed(2)} GB</div>
                    <div className="text-[7px] text-gray-200 mt-1 relative z-10">System memory</div>
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
                        <h3 className="text-lg font-bold text-cyan-400 group-hover:scale-105 transition-transform">PM2 Control</h3>
                        <p className="text-gray-300 text-[14px]">Process monitoring & management</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-[14px] relative z-10">
                      <div className="flex items-center gap-1 group-hover:animate-slideIn" style={{ animationDelay: '0.1s' }}>
                        <div className="w-1 h-1 rounded-full bg-cyan-400 animate-pulse"></div>
                        <span className="text-gray-100">Start/Stop</span>
                      </div>
                      <div className="flex items-center gap-1 group-hover:animate-slideIn" style={{ animationDelay: '0.2s' }}>
                        <div className="w-1 h-1 rounded-full bg-blue-400 animate-pulse"></div>
                        <span className="text-gray-100">Logs</span>
                      </div>
                      <div className="flex items-center gap-1 group-hover:animate-slideIn" style={{ animationDelay: '0.3s' }}>
                        <div className="w-1 h-1 rounded-full bg-purple-400 animate-pulse"></div>
                        <span className="text-gray-100">Files</span>
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
                        <h3 className="text-lg font-bold text-orange-400 group-hover:scale-105 transition-transform">Ad Management</h3>
                        <p className="text-gray-300 text-[14px]">E-commerce monitoring dashboard</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-[14px] relative z-10">
                      <div className="flex items-center gap-1 group-hover:animate-slideIn" style={{ animationDelay: '0.1s' }}>
                        <div className="w-1 h-1 rounded-full bg-orange-400 animate-pulse"></div>
                        <span className="text-gray-100">Stockouts</span>
                      </div>
                      <div className="flex items-center gap-1 group-hover:animate-slideIn" style={{ animationDelay: '0.2s' }}>
                        <div className="w-1 h-1 rounded-full bg-yellow-400 animate-pulse"></div>
                        <span className="text-gray-100">Revenue</span>
                      </div>
                      <div className="flex items-center gap-1 group-hover:animate-slideIn" style={{ animationDelay: '0.3s' }}>
                        <div className="w-1 h-1 rounded-full bg-red-400 animate-pulse"></div>
                        <span className="text-gray-100">Products</span>
                      </div>
                    </div>
                  </a>
                </div>

                {/* Two Column Layout */}
                <div className="grid grid-cols-2 gap-3 flex-1 min-h-0">
                  {/* Active Processes */}
                  <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-3 backdrop-blur-sm hover:border-cyan-500/30 transition-all duration-300 animate-fadeIn flex flex-col min-h-0" style={{ animationDelay: '0.6s' }}>
                    <div className="flex items-center justify-between mb-2 shrink-0">
                      <h3 className="text-lg font-bold text-gray-300">:: ACTIVE_PROCESSES ::</h3>
                      <button
                        onClick={() => setActiveTab('processes')}
                        className="text-cyan-400 text-[14px] hover:text-cyan-300 hover:underline hover:scale-105 transition-transform"
                      >
                        VIEW ALL →
                      </button>
                    </div>
                    {loading ? (
                      <div className="text-center py-4">
                        <div className="text-3xl text-cyan-400 animate-spin inline-block" style={{ animationDuration: '1s' }}>◉</div>
                        <div className="text-cyan-700 mt-3 animate-pulse text-[14px]">LOADING...</div>
                      </div>
                    ) : processes.length === 0 ? (
                      <div className="text-gray-200 text-center py-4 animate-pulse text-[14px]">[ NO PROCESSES ]</div>
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
                              <span className="font-medium text-white text-[14px] group-hover:text-cyan-300 transition-colors">{p.name}</span>
                            </div>
                            <div className="flex items-center gap-3 text-[14px] text-gray-300">
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
                      <h3 className="text-lg font-bold text-gray-300">:: RECENT_LOGS ::</h3>
                      <button
                        onClick={() => setActiveTab('logs')}
                        className="text-cyan-400 text-[14px] hover:text-cyan-300 hover:underline hover:scale-105 transition-transform"
                      >
                        VIEW ALL →
                      </button>
                    </div>
                    {logs.length === 0 ? (
                      <div className="text-gray-200 text-center py-4 animate-pulse text-[14px]">[ NO LOGS ]</div>
                    ) : (
                      <div className="space-y-1 font-mono text-[14px] overflow-auto flex-1">
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
                            <span className="text-gray-200 shrink-0">{log.timestamp.split('T')[1]?.substring(0, 8) || log.timestamp}</span>
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
                            <span className="text-gray-100 break-all">{log.message.substring(0, 40)}{log.message.length > 40 ? '...' : ''}</span>
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
                      <div className="text-gray-200 text-[14px] mb-1 group-hover:text-cyan-400 transition-colors">SYSTEM_HEALTH</div>
                      <div className={`text-lg font-bold transition-all duration-300 ${onlineCount === processes.length && processes.length > 0 ? 'text-blue-400 group-hover:scale-110' : onlineCount > 0 ? 'text-yellow-400 group-hover:scale-110' : 'text-red-400 group-hover:scale-110'}`}>
                        {onlineCount === processes.length && processes.length > 0 ? 'OPTIMAL' : onlineCount > 0 ? 'WARNING' : 'CRITICAL'}
                      </div>
                    </div>
                    <div className="group">
                      <div className="text-gray-200 text-[14px] mb-1 group-hover:text-cyan-400 transition-colors">TOTAL_RESTARTS</div>
                      <div className="text-lg font-bold text-yellow-400 group-hover:scale-110 transition-transform">{processes.reduce((sum, p) => sum + (p.restarts || 0), 0)}</div>
                    </div>
                    <div className="group">
                      <div className="text-gray-200 text-[14px] mb-1 group-hover:text-cyan-400 transition-colors">UPTIME_RATIO</div>
                      <div className="text-lg font-bold text-blue-400 group-hover:scale-110 transition-transform">
                        {processes.length > 0 ? ((onlineCount / processes.length) * 100).toFixed(0) : '0'}%
                      </div>
                    </div>
                  </div>
                  <div className="text-center text-gray-500 text-[14px] mt-2">
                    <div className="group inline-block">
                      <span className="group-hover:text-cyan-400 transition-colors">Digital Employee OS v2.0</span>
                      <span className="mx-2">|</span>
                      <span className="group-hover:text-cyan-400 transition-colors">Auto-refresh: 3s</span>
                      <span className="mx-2">|</span>
                      <span className="text-gray-200">{mounted ? lastUpdate.toLocaleTimeString() : '--:--:--'}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'processes' && (
              <div>
                {/* Header with stats */}
                <div className="flex items-center justify-between mb-4">
                  <div className="text-cyan-400 text-lg font-bold">:: PROCESS_CONTROL ::</div>
                  <div className="flex items-center gap-4 text-[13px]">
                    <div className="flex items-center gap-1">
                      <div className={`w-1.5 h-1.5 rounded-full ${onlineCount > 0 ? 'bg-blue-400 animate-pulse' : 'bg-red-400'}`}></div>
                      <span className="text-gray-300">{onlineCount} ONLINE</span>
                    </div>
                    <div className="text-gray-300">|</div>
                    <button
                      onClick={() => setProcessViewMode(processViewMode === 'grid' ? 'list' : 'grid')}
                      className="flex items-center gap-1 px-2 py-1 border border-gray-700 rounded hover:border-cyan-500/50 transition-all text-gray-100 hover:text-cyan-300"
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
                  <div className="text-center py-20 text-gray-200 animate-pulse">
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
                                <h3 className="text-lg font-bold text-white">{p.name}</h3>
                                <span className={`px-2 py-0.5 text-[14px] font-bold rounded ${
                                  p.status === 'online' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'
                                }`}>
                                  {p.status}
                                </span>
                              </div>
                              <div className="flex gap-4 text-[14px] text-gray-300">
                                <span>PID: <span className="text-cyan-400 font-mono">{p.pid}</span></span>
                                <span>ID: <span className="text-cyan-400 font-mono">{p.id}</span></span>
                                <span>MODE: <span className="text-gray-300">{p.mode === 'fork_mode' ? 'FORK' : 'CLUSTER'}</span></span>
                              </div>
                            </div>

                            {/* Status Badge */}
                            <div className={`text-lg font-bold px-3 py-1.5 rounded border ${getStatusColor(p.status)} ml-4`}>
                              {p.status.toUpperCase()}
                            </div>
                          </div>

                          {/* Quick Stats Bar */}
                          <div className="mt-3 grid grid-cols-3 gap-3">
                            {/* CPU */}
                            <div className="bg-black/50 rounded p-2 border border-gray-800">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-gray-200 text-[14px]">CPU</span>
                                <span className={`text-lg font-bold ${
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
                                <span className="text-gray-200 text-[14px]">MEMORY</span>
                                <span className="text-lg font-bold text-purple-400">
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
                                <span className="text-gray-200 text-[14px]">UPTIME</span>
                                <span className="text-lg font-bold text-cyan-400">
                                  {formatUptime(p.uptime)}
                                </span>
                              </div>
                              <div className="text-[13px] text-gray-300 mt-1">
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
                                  className="flex-1 px-3 py-2 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/50 text-cyan-400 hover:from-cyan-500/30 hover:to-blue-500/30 text-[13px] font-bold transition-all duration-200 hover:scale-105 active:scale-95"
                                >
                                  ↻ RESTART
                                </button>
                                <button
                                  onClick={() => handleProcessAction(p.id, 'stop')}
                                  className="flex-1 px-3 py-2 bg-gradient-to-r from-red-500/20 to-orange-500/20 border border-red-500/50 text-red-400 hover:from-red-500/30 hover:to-orange-500/30 text-[13px] font-bold transition-all duration-200 hover:scale-105 active:scale-95"
                                >
                                  ◼ STOP
                                </button>
                              </>
                            ) : (
                              <button
                                onClick={() => handleProcessAction(p.id, 'start')}
                                className="flex-1 px-3 py-2 bg-gradient-to-r from-blue-500/20 to-emerald-500/20 border border-blue-500/50 text-blue-400 hover:from-blue-500/30 hover:to-emerald-500/30 text-[13px] font-bold transition-all duration-200 hover:scale-105 active:scale-95"
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
                <div className="text-cyan-400 text-lg font-bold mb-4">:: SYSTEM_LOGS ::</div>

                {/* Log Filters */}
                <div className="mb-3 space-y-2">
                  {/* Level Filter */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-gray-300 text-[13px]">LEVEL:</span>
                    {(['all', 'info', 'error', 'warn', 'PM2'] as const).map((level) => (
                      <button
                        key={level}
                        onClick={() => setLogFilter(level)}
                        className={`px-2 py-1 text-[13px] font-bold transition-all duration-200 ${
                          logFilter === level
                            ? level === 'error' ? 'bg-red-500/20 text-red-400 border border-red-500'
                            : level === 'warn' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500'
                            : level === 'PM2' ? 'bg-purple-500/20 text-purple-400 border border-purple-500'
                            : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500'
                            : 'text-gray-300 border border-gray-700 hover:border-gray-500'
                        }`}
                      >
                        [{level.toUpperCase()}]
                      </button>
                    ))}
                  </div>

                  {/* Process Filter */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-gray-300 text-[13px]">PROCESS:</span>
                    <button
                      onClick={() => setLogProcessFilter('all')}
                      className={`px-2 py-1 text-[13px] font-bold transition-all duration-200 ${
                        logProcessFilter === 'all'
                          ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500'
                          : 'text-gray-300 border border-gray-700 hover:border-gray-500'
                      }`}
                    >
                      [ALL]
                    </button>
                    {availableLogProcesses.map((proc) => (
                      <button
                        key={proc}
                        onClick={() => setLogProcessFilter(proc)}
                        className={`px-2 py-1 text-[13px] font-bold transition-all duration-200 ${
                          logProcessFilter === proc
                            ? 'bg-blue-500/20 text-blue-400 border border-blue-500'
                            : 'text-gray-300 border border-gray-700 hover:border-gray-500'
                        }`}
                      >
                        [{proc.toUpperCase()}]
                      </button>
                    ))}
                  </div>
                </div>

                {/* Logs Display */}
                <div className="border border-gray-800 bg-black p-3 h-[450px] overflow-auto text-[14px] font-mono rounded">
                  {logs.length === 0 ? (
                    <div className="text-gray-200 animate-pulse">[ NO_LOGS_AVAILABLE ]</div>
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
                              <span className="text-gray-200 shrink-0">{log.timestamp.split('T')[1]?.substring(0, 8) || log.timestamp}</span>
                              <span className={`px-1.5 py-0.5 text-[14px] font-bold rounded shrink-0 ${
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
                <div className="mt-2 flex items-center justify-between text-[13px]">
                  <span className="text-gray-300">
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
                  <div className="text-cyan-400 text-lg font-bold">:: FILE_BROWSER ::</div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => { setCreateType('file'); setShowCreateModal(true); }}
                      className="px-3 py-1 border border-cyan-500/30 rounded text-[13px] text-cyan-400 hover:border-cyan-400 hover:bg-cyan-950/20 transition-all"
                    >
                      [+ FILE]
                    </button>
                    <button
                      onClick={() => { setCreateType('directory'); setShowCreateModal(true); }}
                      className="px-3 py-1 border border-blue-500/30 rounded text-[13px] text-blue-400 hover:border-blue-400 hover:bg-blue-950/20 transition-all"
                    >
                      [+ FOLDER]
                    </button>
                  </div>
                </div>

                {/* Breadcrumb */}
                <div className="mb-3 flex items-center gap-2 text-[14px]">
                  <button
                    onClick={() => { setCurrentDir(''); setSelectedFile(null); setEditingFile(null); }}
                    className="text-gray-300 hover:text-cyan-400 transition-colors"
                  >
                    [ROOT]
                  </button>
                  {currentDir && currentDir.split('/').map((part, i, arr) => (
                    <span key={i} className="flex items-center gap-2">
                      <span className="text-gray-200">/</span>
                      <button
                        onClick={() => { setCurrentDir(arr.slice(0, i + 1).join('/')); setEditingFile(null); }}
                        className="text-gray-300 hover:text-cyan-400 transition-colors"
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
                      <span className="text-cyan-400 text-[14px]">EDITING: {editingFile}</span>
                      <div className="flex gap-2">
                        <button
                          onClick={handleSaveFile}
                          className="px-2 py-1 bg-blue-500/20 border border-blue-500/30 rounded text-[14px] text-blue-400 hover:bg-blue-500/30 transition-all"
                        >
                          [SAVE]
                        </button>
                        <button
                          onClick={() => { setEditingFile(null); setSelectedFile(null); setFileContent(''); }}
                          className="px-2 py-1 bg-red-500/20 border border-red-500/30 rounded text-[14px] text-red-400 hover:bg-red-500/30 transition-all"
                        >
                          [CANCEL]
                        </button>
                      </div>
                    </div>
                    <textarea
                      value={fileContent}
                      onChange={(e) => setFileContent(e.target.value)}
                      className="w-full h-40 bg-black border border-gray-700 rounded p-2 text-[13px] font-mono text-gray-300 focus:border-cyan-500 focus:outline-none resize-none"
                      spellCheck={false}
                    />
                  </div>
                )}

                {/* Files List */}
                <div className="border border-gray-800 bg-black p-3 h-[350px] overflow-auto text-[14px] font-mono rounded">
                  {parentDir && (
                    <div
                      onClick={() => { setCurrentDir(parentDir); setSelectedFile(null); setEditingFile(null); }}
                      className="flex items-center gap-2 p-2 hover:bg-cyan-900/20 rounded cursor-pointer transition-all mb-1"
                    >
                      <span className="text-gray-300">..</span>
                      <span className="text-gray-100">[PARENT]</span>
                    </div>
                  )}

                  {files.length === 0 ? (
                    <div className="text-gray-200 animate-pulse">[ DIRECTORY_EMPTY ]</div>
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
                            <span className="text-gray-100 text-[13px] shrink-0">
                              {file.type === 'file' ? formatBytes(file.size) : '<DIR>'}
                            </span>
                          </div>
                          <button
                            onClick={(e) => { e.stopPropagation(); handleDeleteFile(file); }}
                            className="px-2 py-1 bg-red-500/10 border border-red-500/30 rounded text-[14px] text-red-400 opacity-0 group-hover:opacity-100 hover:bg-red-500/20 transition-all shrink-0"
                          >
                            [DEL]
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* File Stats */}
                <div className="mt-2 flex items-center justify-between text-[13px] text-gray-300">
                  <span>{files.length} items</span>
                  <span>{currentDir || 'root'}</span>
                </div>

                {/* Create Modal */}
                {showCreateModal && (
                  <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 animate-fadeIn">
                    <div className="bg-gray-900 border border-cyan-500/30 rounded-lg p-4 w-80">
                      <div className="text-cyan-400 text-lg font-bold mb-3">
                        :: CREATE_{createType.toUpperCase()} ::
                      </div>
                      <input
                        type="text"
                        value={createName}
                        onChange={(e) => setCreateName(e.target.value)}
                        placeholder={`${createType} name...`}
                        className="w-full bg-black border border-gray-700 rounded p-2 text-[14px] text-gray-300 focus:border-cyan-500 focus:outline-none mb-3"
                        autoFocus
                        onKeyDown={(e) => { if (e.key === 'Enter') handleCreate(); }}
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={handleCreate}
                          className="flex-1 px-3 py-2 bg-blue-500/20 border border-blue-500/30 rounded text-[13px] text-blue-400 hover:bg-blue-500/30 transition-all"
                        >
                          [CREATE]
                        </button>
                        <button
                          onClick={() => { setShowCreateModal(false); setCreateName(''); }}
                          className="flex-1 px-3 py-2 bg-gray-700/20 border border-gray-600/30 rounded text-[13px] text-gray-100 hover:bg-gray-700/30 transition-all"
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
                <div className="text-cyan-400 text-lg font-bold mb-4">:: PERFORMANCE_METRICS ::</div>

                {/* Real-time Graphs */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  {/* CPU History Graph */}
                  <div className="border border-gray-800 bg-black p-3 rounded">
                    <div className="flex justify-between items-center mb-2">
                      <div className="text-gray-300 text-[13px]">CPU_HISTORY (30s)</div>
                      <div className="text-yellow-400 text-lg font-bold">{totalCpu.toFixed(1)}%</div>
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
                      <div className="text-gray-300 text-[13px]">MEMORY_HISTORY (30s)</div>
                      <div className="text-purple-400 text-lg font-bold">{formatBytes(totalMem)}</div>
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
                    <div className="text-gray-200 text-[14px] mb-1">PROCESSES</div>
                    <div className="text-xl font-bold text-cyan-400 group-hover:scale-110 transition-transform">{processes.length}</div>
                  </div>
                  <div className="border border-blue-500/30 p-2 rounded hover:border-blue-500 transition-all group">
                    <div className="text-gray-200 text-[14px] mb-1">ONLINE</div>
                    <div className="text-xl font-bold text-blue-400 group-hover:scale-110 transition-transform">{onlineCount}</div>
                  </div>
                  <div className="border border-yellow-500/30 p-2 rounded hover:border-yellow-500 transition-all group">
                    <div className="text-gray-200 text-[14px] mb-1">AVG_CPU</div>
                    <div className="text-xl font-bold text-yellow-400 group-hover:scale-110 transition-transform">
                      {processes.length > 0 ? (totalCpu / processes.length).toFixed(1) : '0'}%
                    </div>
                  </div>
                  <div className="border border-purple-500/30 p-2 rounded hover:border-purple-500 transition-all group">
                    <div className="text-gray-200 text-[14px] mb-1">TOTAL_MEM</div>
                    <div className="text-xl font-bold text-purple-400 group-hover:scale-110 transition-transform">{formatBytes(totalMem)}</div>
                  </div>
                </div>

                {/* System Health */}
                <div className="border border-gray-800 bg-black p-3 rounded mb-4">
                  <div className="text-gray-300 text-[13px] mb-3">:: SYSTEM_HEALTH ::</div>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="text-center">
                      <div className="text-gray-200 text-[14px] mb-1">UPTIME_RATIO</div>
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
                      <div className="text-gray-200 text-[14px] mb-1">TOTAL_RESTARTS</div>
                      <div className="text-2xl font-bold text-yellow-400">
                        {processes.reduce((sum, p) => sum + p.restarts, 0)}
                      </div>
                      <div className="text-[14px] text-gray-200 mt-2">All processes</div>
                    </div>
                    <div className="text-center">
                      <div className="text-gray-200 text-[14px] mb-1">HELIATH_STATUS</div>
                      <div className={`text-xl font-bold ${onlineCount === processes.length && processes.length > 0 ? 'text-blue-400' : onlineCount > 0 ? 'text-yellow-400' : 'text-red-400'}`}>
                        {onlineCount === processes.length && processes.length > 0 ? 'HEALTHY' : onlineCount > 0 ? 'WARNING' : 'CRITICAL'}
                      </div>
                      <div className="text-[14px] text-gray-200 mt-2">Overall system</div>
                    </div>
                  </div>
                </div>

                {/* Process Details Table */}
                <div className="border border-gray-800 bg-black p-3 rounded mb-4">
                  <div className="text-gray-300 text-[13px] mb-3">:: PROCESS_DETAILS ::</div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-[13px]">
                      <thead>
                        <tr className="text-gray-300 border-b border-gray-800">
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
                              <span className={`px-1.5 py-0.5 rounded text-[14px] font-bold ${
                                p.status === 'online' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'
                              }`}>
                                {p.status.toUpperCase()}
                              </span>
                            </td>
                            <td className="py-2 px-2 text-right text-yellow-400">{p.cpu.toFixed(2)}%</td>
                            <td className="py-2 px-2 text-right text-purple-400">{formatBytes(p.memory)}</td>
                            <td className="py-2 px-2 text-right text-gray-100">{formatUptime(p.uptime)}</td>
                            <td className="py-2 px-2 text-right text-gray-100">{p.restarts}</td>
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
                    <div className="text-gray-300 text-[13px] mb-3">MEMORY_DISTRIBUTION</div>
                    <div className="space-y-3">
                      {processes.map((p) => (
                        <div key={p.id} className="space-y-1">
                          <div className="flex justify-between text-[13px]">
                            <span className="text-gray-100 truncate flex-1">{p.name}</span>
                            <span className="text-purple-400 ml-2">{formatBytes(p.memory)}</span>
                            <span className="text-gray-200 ml-2">{((p.memory / totalMem) * 100 || 0).toFixed(1)}%</span>
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
                    <div className="text-gray-300 text-[13px] mb-3">CPU_DISTRIBUTION</div>
                    <div className="space-y-3">
                      {processes.map((p) => (
                        <div key={p.id} className="space-y-1">
                          <div className="flex justify-between text-[13px]">
                            <span className="text-gray-100 truncate flex-1">{p.name}</span>
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
                  <div className="text-gray-300 text-[13px] mb-3">RESOURCE_UTILIZATION</div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="flex justify-between text-[13px] mb-2">
                        <span className="text-purple-400">MEMORY</span>
                        <span className="text-gray-100">{((totalMem / 4000000000) * 100).toFixed(1)}%</span>
                      </div>
                      <div className="relative h-4 bg-gray-900 rounded-full overflow-hidden">
                        <div
                          className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min((totalMem / 4000000000) * 100, 100)}%` }}
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
                        </div>
                      </div>
                      <div className="text-[14px] text-gray-200 mt-1 text-right">4 GB max</div>
                    </div>
                    <div>
                      <div className="flex justify-between text-[13px] mb-2">
                        <span className="text-yellow-400">CPU</span>
                        <span className="text-gray-100">{totalCpu.toFixed(1)}%</span>
                      </div>
                      <div className="relative h-4 bg-gray-900 rounded-full overflow-hidden">
                        <div
                          className="absolute inset-y-0 left-0 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(totalCpu, 100)}%` }}
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
                        </div>
                      </div>
                      <div className="text-[14px] text-gray-200 mt-1 text-right">{processes.length} cores</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'ad-management' && (
              <div className="animate-fadeIn h-full flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <div className="text-cyan-400 text-lg font-bold">:: AD_MANAGEMENT ::</div>
                    <div className="text-gray-300 text-[14px]">Gulahmed Shop E-commerce Monitor</div>
                  </div>
                  <button
                    onClick={refreshAdData}
                    className="px-3 py-2 bg-cyan-500/20 border border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/30 transition-all text-[14px] font-bold flex items-center gap-2"
                  >
                    <span>⟳</span>
                    REFRESH DATA
                  </button>
                </div>

                {/* Sub-Tabs Navigation */}
                <div className="flex gap-2 mb-4 border-b border-gray-800 pb-2">
                  {(['inventory', 'performance', 'topworst', 'heatmap', 'backinstock'] as const).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setAdSubTab(tab)}
                      className={`px-4 py-2 text-[13px] font-bold transition-all ${
                        adSubTab === tab
                          ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400'
                          : 'bg-gray-900/50 border-gray-700 text-gray-400 hover:border-cyan-500/30'
                      } border rounded`}
                    >
                      {tab === 'inventory' && '🚨 STOCKOUTS'}
                      {tab === 'performance' && '📊 PERFORMANCE'}
                      {tab === 'topworst' && '🏆 TOP/LOW'}
                      {tab === 'heatmap' && '🔥 HEATMAP'}
                      {tab === 'backinstock' && '⚠️ BACK-IN-STOCK'}
                    </button>
                  ))}
                </div>

                {adLoading ? (
                  <div className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                      <div className="text-4xl text-cyan-400 animate-spin inline-block" style={{ animationDuration: '1s' }}>◉</div>
                      <div className="text-cyan-700 mt-4 animate-pulse text-[14px]">LOADING AD DATA...</div>
                    </div>
                  </div>
                ) : (
                  <>
                    {/* STOCKOUT TAB - Only shows out of stock products */}
                    {adSubTab === 'inventory' && (
                      <>
                        {adSummary && (
                          <div className="grid grid-cols-4 gap-3 mb-4">
                            <div className="bg-gray-900/50 border border-cyan-500/30 rounded-lg p-3 hover:border-cyan-400 hover:shadow-[0_0_20px_rgba(6,182,212,0.3)] transition-all group">
                              <div className="text-gray-300 text-[14px] mb-1">TOTAL_PRODUCTS</div>
                              <div className="text-2xl font-bold text-cyan-400 group-hover:scale-110 transition-transform">{adSummary.total}</div>
                            </div>
                            <div className="bg-gray-900/50 border border-red-500/30 rounded-lg p-3 hover:border-red-400 hover:shadow-[0_0_20px_rgba(239,68,68,0.3)] transition-all group">
                              <div className="text-gray-300 text-[14px] mb-1">OUT_OF_STOCK</div>
                              <div className="text-2xl font-bold text-red-400 group-hover:scale-110 transition-transform">{adSummary.out_of_stock}</div>
                            </div>
                            <div className="bg-gray-900/50 border border-yellow-500/30 rounded-lg p-3 hover:border-yellow-400 hover:shadow-[0_0_20px_rgba(250,204,21,0.3)] transition-all group">
                              <div className="text-gray-300 text-[14px] mb-1">REVENUE_IMPACT</div>
                              <div className="text-2xl font-bold text-yellow-400 group-hover:scale-110 transition-transform">PKR {adSummary.total_revenue_impact.toLocaleString()}</div>
                            </div>
                            <div className="bg-gray-900/50 border border-purple-500/30 rounded-lg p-3 hover:border-purple-400 hover:shadow-[0_0_20px_rgba(168,85,247,0.3)] transition-all group">
                              <div className="text-gray-300 text-[14px] mb-1">TOP_SELLING</div>
                              <div className="text-2xl font-bold text-purple-400 group-hover:scale-110 transition-transform">{adSummary.top_selling}</div>
                            </div>
                          </div>
                        )}

                        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4 flex-1 overflow-auto">
                          <div className="flex items-center justify-between mb-3">
                            <h3 className="text-lg font-bold text-gray-300">:: STOCKOUT_ALERTS ::</h3>
                            <div className="text-red-300 text-[14px] font-bold">{adProducts.filter(p => p.status === 'Out of Stock').length} OUT OF STOCK</div>
                          </div>

                          <div className="overflow-x-auto">
                            <table className="w-full text-[13px]">
                              <thead>
                                <tr className="text-gray-300 border-b border-gray-700">
                                  <th className="text-left py-2 px-2">ID</th>
                                  <th className="text-left py-2 px-2">PRODUCT</th>
                                  <th className="text-left py-2 px-2">CATEGORY</th>
                                  <th className="text-right py-2 px-2">PRICE</th>
                                  <th className="text-center py-2 px-2">STATUS</th>
                                  <th className="text-center py-2 px-2">DAYS_OUT</th>
                                  <th className="text-right py-2 px-2">REVENUE_IMPACT</th>
                                  <th className="text-center py-2 px-2">SOURCE</th>
                                </tr>
                              </thead>
                              <tbody>
                                {adProducts
                                  .filter(product => product.status === 'Out of Stock')
                                  .map((product) => (
                                  <tr
                                    key={product.id}
                                    className={`border-b border-gray-800 hover:bg-red-900/20 transition-colors ${
                                      product.is_top_selling ? 'bg-purple-900/10' : ''
                                    }`}
                                  >
                                    <td className="py-2 px-2 text-cyan-300">{product.id}</td>
                                    <td className="py-2 px-2">
                                      <div className="flex items-center gap-2">
                                        {product.is_top_selling && (
                                          <span className="text-purple-400">★</span>
                                        )}
                                        <a
                                          href={product.url}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="text-gray-100 hover:text-cyan-400 transition-colors truncate max-w-xs block"
                                        >
                                          {product.title}
                                        </a>
                                      </div>
                                    </td>
                                    <td className="py-2 px-2 text-gray-300">{product.category}</td>
                                    <td className="py-2 px-2 text-right text-green-400">PKR {product.price.toLocaleString()}</td>
                                    <td className="py-2 px-2 text-center">
                                      <span className="px-2 py-1 rounded text-[14px] font-bold bg-red-500/20 text-red-400">
                                        OUT_OF_STOCK
                                      </span>
                                    </td>
                                    <td className="py-2 px-2 text-center text-yellow-400 font-bold">{product.days_out}</td>
                                    <td className="py-2 px-2 text-right text-orange-400">PKR {product.revenue_impact.toLocaleString()}</td>
                                    <td className="py-2 px-2 text-center">
                                      {(product as any).source === 'playwright_scrape' ? (
                                        <span className="px-2 py-1 rounded text-[11px] font-bold bg-green-500/20 text-green-400">
                                        LIVE
                                        </span>
                                      ) : (product as any).source === 'csv_fallback' ? (
                                        <span className="px-2 py-1 rounded text-[11px] font-bold bg-yellow-500/20 text-yellow-400">
                                        CSV
                                        </span>
                                      ) : (
                                        <span className="text-gray-500 text-[11px]">-</span>
                                      )}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </>
                    )}

                    {/* PERFORMANCE TAB */}
                    {adSubTab === 'performance' && (
                      <>
                        {performanceSummary ? (
                          <>
                            <div className="grid grid-cols-4 gap-3 mb-4">
                              <div className="bg-gray-900/50 border border-cyan-500/30 rounded-lg p-3 hover:border-cyan-400 hover:shadow-[0_0_20px_rgba(6,182,212,0.3)] transition-all group">
                                <div className="text-gray-300 text-[14px] mb-1">TOTAL_AD_SPEND</div>
                                <div className="text-2xl font-bold text-cyan-400 group-hover:scale-110 transition-transform">PKR {performanceSummary.total_ad_spend.toLocaleString()}</div>
                              </div>
                              <div className="bg-gray-900/50 border border-green-500/30 rounded-lg p-3 hover:border-green-400 hover:shadow-[0_0_20px_rgba(34,197,94,0.3)] transition-all group">
                                <div className="text-gray-300 text-[14px] mb-1">TOTAL_REVENUE</div>
                                <div className="text-2xl font-bold text-green-400 group-hover:scale-110 transition-transform">PKR {performanceSummary.total_revenue.toLocaleString()}</div>
                              </div>
                              <div className="bg-gray-900/50 border border-blue-500/30 rounded-lg p-3 hover:border-blue-400 hover:shadow-[0_0_20px_rgba(59,130,246,0.3)] transition-all group">
                                <div className="text-gray-300 text-[14px] mb-1">OVERALL_ROAS</div>
                                <div className="text-2xl font-bold text-blue-400 group-hover:scale-110 transition-transform">{performanceSummary.overall_roas.toFixed(2)}</div>
                              </div>
                              <div className="bg-gray-900/50 border border-red-500/30 rounded-lg p-3 hover:border-red-400 hover:shadow-[0_0_20px_rgba(239,68,68,0.3)] transition-all group">
                                <div className="text-gray-300 text-[14px] mb-1">STOCKOUT_DAYS</div>
                                <div className="text-2xl font-bold text-red-400 group-hover:scale-110 transition-transform">{performanceSummary.total_stockout_days}</div>
                              </div>
                            </div>

                            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4 flex-1 overflow-auto">
                              <h3 className="text-lg font-bold text-gray-300 mb-3">:: PRODUCT_PERFORMANCE ::</h3>
                              <div className="overflow-x-auto">
                                <table className="w-full text-[13px]">
                                  <thead>
                                    <tr className="text-gray-300 border-b border-gray-700">
                                      <th className="text-left py-2 px-2">PRODUCT</th>
                                      <th className="text-right py-2 px-2">AD_SPEND</th>
                                      <th className="text-right py-2 px-2">SALES</th>
                                      <th className="text-right py-2 px-2">REVENUE</th>
                                      <th className="text-right py-2 px-2">ROAS</th>
                                      <th className="text-right py-2 px-2">CONV_RATE</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {performanceData.map((product, index) => (
                                      <tr key={index} className="border-b border-gray-800 hover:bg-cyan-900/10 transition-colors">
                                        <td className="py-2 px-2 text-cyan-300 font-semibold">{product.ad_name}</td>
                                        <td className="py-2 px-2 text-right text-gray-300">PKR {product.ad_spend_actual.toFixed(2)}</td>
                                        <td className="py-2 px-2 text-right text-gray-300">{product.sales_count}</td>
                                        <td className="py-2 px-2 text-right text-green-400 font-bold">PKR {product.revenue.toLocaleString()}</td>
                                        <td className="py-2 px-2 text-right text-blue-400">{product.roas.toFixed(2)}</td>
                                        <td className="py-2 px-2 text-right text-gray-300">{(product.conversion_rate * 100).toFixed(2)}%</td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          </>
                        ) : (
                          <div className="flex-1 flex items-center justify-center">
                            <div className="text-center">
                              <div className="text-4xl text-cyan-400 animate-spin inline-block" style={{ animationDuration: '1s' }}>◉</div>
                              <div className="text-gray-300 mt-4 text-[14px]">Loading performance data from backend...</div>
                              <div className="text-gray-500 mt-2 text-[12px]">Make sure ad-dashboard is running on port 8501</div>
                            </div>
                          </div>
                        )}
                      </>
                    )}

                    {/* TOP/LOW TAB */}
                    {adSubTab === 'topworst' && (
                      <>
                        <div className="flex gap-4 mb-4">
                          <select
                            value={selectedMetric}
                            onChange={(e) => { setSelectedMetric(e.target.value); fetchTopWorstProducts(e.target.value, topWorstCount); }}
                            className="bg-gray-900 border border-gray-700 text-gray-300 px-4 py-2 rounded text-[13px] hover:border-cyan-500/50 transition-all"
                          >
                            <option value="roas">By ROAS (Return on Ad Spend)</option>
                            <option value="revenue">By Revenue</option>
                            <option value="sales_count">By Sales Count</option>
                            <option value="conversion_rate">By Conversion Rate</option>
                            <option value="Product_Price">By Price</option>
                            <option value="total_stockout_days">By Stockout Days</option>
                          </select>
                          <select
                            value={topWorstCount}
                            onChange={(e) => { setTopWorstCount(Number(e.target.value)); fetchTopWorstProducts(selectedMetric, Number(e.target.value)); }}
                            className="bg-gray-900 border border-gray-700 text-gray-300 px-4 py-2 rounded text-[13px] hover:border-cyan-500/50 transition-all"
                          >
                            <option value={5}>Top 5</option>
                            <option value={10}>Top 10</option>
                            <option value={15}>Top 15</option>
                          </select>
                        </div>

                        <div className="grid grid-cols-2 gap-4 flex-1 overflow-auto">
                          {/* Top Products */}
                          <div className="bg-gray-900/50 border border-green-500/30 rounded-lg p-4 overflow-auto">
                            <h3 className="text-lg font-bold text-green-400 mb-3 flex items-center gap-2">
                              <span className="text-2xl">🏆</span>
                              :: TOP_PRODUCTS ::
                            </h3>
                            <div className="space-y-2">
                              {topProducts.map((product, index) => (
                                <div key={index} className="bg-black/50 border border-gray-800 rounded p-3 hover:border-green-500/50 transition-all">
                                  <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                      <div className="w-8 h-8 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center font-bold text-[14px]">
                                        {index + 1}
                                      </div>
                                      <div>
                                        <div className="text-gray-100 font-semibold text-[13px]">{product.ad_name || product.title}</div>
                                        <div className="text-gray-500 text-[11px]">₨{product.price?.toLocaleString() || product.Product_Price?.toLocaleString()}</div>
                                      </div>
                                    </div>
                                    <div className="text-green-400 font-bold text-[15px]">{formatMetricValue(product, selectedMetric)}</div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Low Performers */}
                          <div className="bg-gray-900/50 border border-red-500/30 rounded-lg p-4 overflow-auto">
                            <h3 className="text-lg font-bold text-red-400 mb-3 flex items-center gap-2">
                              <span className="text-2xl">⚠️</span>
                              :: LOW_PERFORMERS ::
                            </h3>
                            <div className="space-y-2">
                              {worstProducts.map((product, index) => (
                                <div key={index} className="bg-black/50 border border-gray-800 rounded p-3 hover:border-red-500/50 transition-all">
                                  <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                      <div className="w-8 h-8 rounded-full bg-red-500/20 text-red-400 flex items-center justify-center font-bold text-[14px]">
                                        {index + 1}
                                      </div>
                                      <div>
                                        <div className="text-gray-100 font-semibold text-[13px]">{product.ad_name || product.title}</div>
                                        <div className="text-gray-500 text-[11px]">₨{product.price?.toLocaleString() || product.Product_Price?.toLocaleString()}</div>
                                      </div>
                                    </div>
                                    <div className="text-red-400 font-bold text-[15px]">{formatMetricValue(product, selectedMetric)}</div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </>
                    )}

                    {/* HEATMAP TAB */}
                    {adSubTab === 'heatmap' && (
                      <>
                        <div className="flex gap-4 mb-4 items-center">
                          <select
                            value={selectedMetric}
                            onChange={(e) => { setSelectedMetric(e.target.value); fetchHeatmapData(e.target.value); }}
                            className="bg-gray-900 border border-gray-700 text-gray-300 px-4 py-2 rounded text-[13px] hover:border-cyan-500/50 transition-all"
                          >
                            <option value="roas">ROAS (Return on Ad Spend)</option>
                            <option value="revenue">Revenue</option>
                            <option value="sales_count">Sales Count</option>
                            <option value="conversion_rate">Conversion Rate</option>
                            <option value="Product_Price">Product Price</option>
                            <option value="total_stockout_days">Stockout Days</option>
                          </select>
                          <div className="text-gray-400 text-[12px] ml-auto">
                            Showing: <span className="text-cyan-400 font-bold">{heatmapData.length} products</span>
                          </div>
                        </div>

                        <div className="bg-gray-900/50 border border-cyan-500/30 rounded-lg p-4 flex-1 overflow-auto">
                          <h3 className="text-lg font-bold text-cyan-400 mb-4 flex items-center gap-2">
                            <span className="text-2xl">🔥</span>
                            :: PERFORMANCE_HEATMAP ::
                          </h3>

                          <div className="bg-black/30 rounded-lg p-4 border border-gray-800">
                            <div className="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-10 lg:grid-cols-12 gap-1.5">
                              {heatmapData.map((item, index) => {
                                const normalized = item.normalized;
                                // Enhanced color scheme with smooth gradients
                                let bgColor, textColor, borderColor;

                                if (normalized < 0.25) {
                                  // Very Low - Deep Red to Red
                                  bgColor = `rgba(239, 68, 68, ${0.3 + normalized * 0.7})`;
                                  textColor = 'text-red-300';
                                  borderColor = 'border-red-900/50';
                                } else if (normalized < 0.5) {
                                  // Low - Orange to Yellow
                                  bgColor = `rgba(251, 146, 60, ${0.4 + (normalized - 0.25) * 0.6})`;
                                  textColor = 'text-orange-200';
                                  borderColor = 'border-orange-900/50';
                                } else if (normalized < 0.75) {
                                  // Medium - Yellow to Light Green
                                  bgColor = `rgba(234, 179, 8, ${0.5 + (normalized - 0.5) * 0.5})`;
                                  textColor = 'text-yellow-200';
                                  borderColor = 'border-yellow-900/50';
                                } else {
                                  // High - Green to Emerald
                                  bgColor = `rgba(16, 185, 129, ${0.6 + (normalized - 0.75) * 0.4})`;
                                  textColor = 'text-emerald-100';
                                  borderColor = 'border-emerald-900/50';
                                }

                                return (
                                  <div
                                    key={index}
                                    className={`rounded-lg p-2 text-center cursor-pointer transition-all duration-300 border ${borderColor} hover:scale-105 hover:shadow-lg hover:shadow-${bgColor.includes('red') ? 'red' : bgColor.includes('orange') ? 'orange' : bgColor.includes('yellow') ? 'yellow' : 'emerald'}-500/20`}
                                    style={{ background: bgColor }}
                                    title={`${item.ad_name}: ${formatMetricValue({ ...item, roas: item.metric_value, price: item.metric_value, sales_count: item.metric_value, conversion_rate: item.metric_value, days_out: item.metric_value }, selectedMetric)}`}
                                  >
                                    <div className={`text-[9px] font-semibold truncate ${textColor} mb-1`} style={{ fontSize: '9px', lineHeight: '1.2' }}>
                                      {item.ad_name.split(' ').slice(0, 2).join(' ')}
                                    </div>
                                    <div className={`text-sm font-bold ${textColor}`}>
                                      {selectedMetric === 'roas' ? item.metric_value.toFixed(1) + 'x' :
                                       selectedMetric === 'revenue' ? '₨' + (item.metric_value / 1000).toFixed(1) + 'k' :
                                       selectedMetric === 'sales_count' ? Math.round(item.metric_value) :
                                       selectedMetric === 'conversion_rate' ? (item.metric_value * 100).toFixed(1) + '%' :
                                       selectedMetric === 'Product_Price' ? '₨' + item.metric_value.toLocaleString() :
                                       selectedMetric === 'total_stockout_days' ? Math.round(item.metric_value) + 'd' :
                                       item.metric_value.toFixed(0)}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>

                            {/* Enhanced Legend */}
                            <div className="mt-4 space-y-2">
                              <div className="flex items-center gap-2 text-[12px] text-gray-400">
                                <span className="font-semibold">PERFORMANCE_SCALE:</span>
                              </div>
                              <div className="flex items-center gap-1 h-6 rounded overflow-hidden border border-gray-700">
                                <div className="flex-1 h-full bg-gradient-to-r from-red-900 via-red-600 to-red-400" title="Very Low (0-25%)"></div>
                                <div className="flex-1 h-full bg-gradient-to-r from-orange-700 via-orange-500 to-yellow-500" title="Low (25-50%)"></div>
                                <div className="flex-1 h-full bg-gradient-to-r from-yellow-600 via-yellow-400 to-lime-400" title="Medium (50-75%)"></div>
                                <div className="flex-1 h-full bg-gradient-to-r from-green-600 via-emerald-500 to-emerald-300" title="High (75-100%)"></div>
                              </div>
                              <div className="flex justify-between text-[10px] text-gray-500 font-mono">
                                <span>LOW (0-25%)</span>
                                <span>MEDIUM-LOW (25-50%)</span>
                                <span>MEDIUM-HIGH (50-75%)</span>
                                <span>HIGH (75-100%)</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </>
                    )}

                    {/* BACK-IN-STOCK TAB */}
                    {adSubTab === 'backinstock' && (
                      <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4 flex-1 overflow-auto">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="text-lg font-bold text-orange-400 flex items-center gap-2">
                            <span className="text-2xl">⚠️</span>
                            :: STOCKOUT_ALERTS ::
                          </h3>
                          <div className="flex items-center gap-2">
                            {lastStockCheck && (
                              <span className="text-gray-500 text-[11px]">
                                Last check: {lastStockCheck.toLocaleTimeString()}
                              </span>
                            )}
                            <button
                              onClick={checkRealStock}
                              disabled={stockCheckLoading}
                              className="bg-orange-500/20 hover:bg-orange-500/30 text-orange-400 px-4 py-2 rounded text-[12px] font-bold border border-orange-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                            >
                              {stockCheckLoading ? (
                                <>
                                  <span className="animate-spin">◉</span>
                                  Checking...
                                </>
                              ) : (
                                <>
                                  <span>🔍</span>
                                  Check Stock (Live)
                                </>
                              )}
                            </button>
                          </div>
                        </div>
                        {realStockData.length > 0 && (
                          <div className="mb-4 p-3 bg-green-500/10 border border-green-500/30 rounded">
                            <div className="text-green-400 text-[12px] font-bold mb-1">
                              ✓ Stock data loaded from {realStockData.length} products
                            </div>
                            <div className="text-gray-400 text-[11px]">
                              Using ad_monitoring skill ({realStockData.filter((d: any) => d.source === 'playwright_scrape').length} live-scraped, {realStockData.filter((d: any) => d.source === 'csv_fallback').length} CSV fallback)
                            </div>
                          </div>
                        )}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                          {performanceData.filter(p => p.total_stockout_days > 0).map((product, index) => (
                            <div key={index} className="bg-black/50 border border-red-500/30 rounded-lg p-4 hover:border-red-500/50 transition-all">
                              <div className="flex items-center justify-between mb-3">
                                <h4 className="font-bold text-gray-100">{product.ad_name}</h4>
                                <span className="px-3 py-1 rounded-full bg-red-500/20 text-red-400 text-[12px] font-bold border border-red-500/50">
                                  {product.total_stockout_days} days OOS
                                </span>
                              </div>
                              <div className="grid grid-cols-2 gap-3 text-[13px] mb-3">
                                <div>
                                  <div className="text-gray-500 text-[11px]">WASTED_AD_SPEND</div>
                                  <div className="text-red-400 font-bold">PKR {product.ad_spend_actual.toFixed(2)}</div>
                                </div>
                                <div>
                                  <div className="text-gray-500 text-[11px]">PRODUCT_PRICE</div>
                                  <div className="text-gray-300 font-bold">PKR {product.price.toLocaleString()}</div>
                                </div>
                                <div>
                                  <div className="text-gray-500 text-[11px]">CONVERSION_RATE</div>
                                  <div className="text-gray-300 font-bold">{(product.conversion_rate * 100).toFixed(2)}%</div>
                                </div>
                                <div>
                                  <div className="text-gray-500 text-[11px]">LOST_REVENUE</div>
                                  <div className="text-orange-400 font-bold">PKR {(product.total_stockout_days * product.price * product.conversion_rate).toFixed(2)}</div>
                                </div>
                              </div>
                              <div className="bg-orange-500/10 border border-orange-500/30 rounded p-3">
                                <div className="text-orange-400 text-[11px] mb-1">RECOMMENDED_ACTION</div>
                                <div className="font-bold text-orange-300 text-[13px]">
                                  {product.total_stockout_days > 10
                                    ? `🚨 URGENT: Pause ads immediately - product has been sold out for ${product.total_stockout_days} days`
                                    : '⚡ Monitor: Consider pausing ads if stockout continues'
                                  }
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN - The Stream (25%) */}
        <div className="w-[25%] border-l border-cyan-900/50 flex flex-col bg-black/95 backdrop-blur-sm">

          {/* Header */}
          <div className="border-b border-cyan-900/50 p-3">
            <div className="text-cyan-400 text-lg font-bold">:: LIVE_FEED ::</div>
            <div className="text-gray-300 text-[14px] mt-1">REAL-TIME_DATA_STREAM</div>
          </div>

          {/* Summary Metrics */}
          <div className="border-b border-cyan-900/50 p-3">
            <div className="grid grid-cols-2 gap-2">
              <div className="border border-gray-800 p-2 rounded hover:border-cyan-500/50 transition-all duration-300 group">
                <div className="text-gray-200 text-[13px]">UPTIME</div>
                <div className="text-cyan-400 text-lg font-bold group-hover:scale-110 transition-transform">99.9%</div>
              </div>
              <div className="border border-gray-800 p-2 rounded hover:border-blue-500/50 transition-all duration-300 group">
                <div className="text-gray-200 text-[13px]">REQS</div>
                <div className="text-blue-400 text-lg font-bold group-hover:scale-110 transition-transform">42K</div>
              </div>
              <div className="border border-gray-800 p-2 rounded hover:border-red-500/50 transition-all duration-300 group">
                <div className="text-gray-200 text-[13px]">ERRORS</div>
                <div className="text-red-400 text-lg font-bold group-hover:scale-110 transition-transform">0</div>
              </div>
              <div className="border border-gray-800 p-2 rounded hover:border-yellow-500/50 transition-all duration-300 group">
                <div className="text-gray-200 text-[13px]">LOAD</div>
                <div className="text-yellow-400 text-lg font-bold group-hover:scale-110 transition-transform">{totalCpu.toFixed(0)}%</div>
              </div>
            </div>
          </div>

          {/* Cognitive Stream */}
          <div className="flex-1 overflow-hidden flex flex-col">
            <div className="p-3 border-b border-cyan-900/50">
              <div className="text-cyan-400 text-[14px]">:: COGNITIVE_STREAM ::</div>
            </div>
            <div className="flex-1 overflow-auto p-3 font-mono text-[13px]">
              {logs.length === 0 ? (
                <div className="text-gray-500 animate-pulse">[ AWAITING_DATA_STREAM ]</div>
              ) : (
                <div className="space-y-2">
                  {logs.slice(0, 15).map((log, i) => (
                    <div
                      key={i}
                      className="mb-2 leading-tight p-1 rounded hover:bg-cyan-900/10 transition-all duration-200 animate-slideIn"
                      style={{ animationDelay: `${i * 30}ms` }}
                    >
                      <span className="text-gray-500">[{log.timestamp}]</span>
                      <span className="text-gray-300 ml-1">{log.message.substring(0, 50)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Production Metrics */}
          <div className="border-t border-cyan-900/50 p-3">
            <div className="text-cyan-400 text-[14px] mb-2">:: PRODUCTION_METRICS ::</div>
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-gray-300 text-[13px] mb-1">
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
                <div className="flex justify-between text-gray-300 text-[13px] mb-1">
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
          <div className="border-t border-cyan-900/50 p-2 text-gray-500 text-[13px]">
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
