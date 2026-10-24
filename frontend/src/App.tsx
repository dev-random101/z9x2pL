import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, AreaChart, Area
} from 'recharts';
import { Calendar, Clock, AlertTriangle, Info, Activity, TrendingDown, TrendingUp } from 'lucide-react';

// --- Types ---
interface DataPoint {
  startTime: string;
  generation: number;
}

interface Metrics {
  mae: number;
  rmse: number;
  bias: number;
  nmae: number;
  p50: number;
  p90: number;
  p95: number;
  coverage: number;
  insight: string;
}

interface HorizonMetric {
  horizon_hours: number;
  mean: number;
  std: number;
  count: number;
}

interface HourMetric {
  hour: number;
  mean: number;
  std: number;
  count: number;
}

// --- Components ---
const StatCard = ({ label, value, unit, icon: Icon, color = "blue" }: {
  label: string, value: any, unit?: string, icon: any, color?: string
}) => {
  const colorMap: any = {
    blue: "bg-blue-50 text-blue-700 border-blue-100",
    green: "bg-green-50 text-green-700 border-green-100",
    red: "bg-red-50 text-red-700 border-red-100",
    amber: "bg-amber-50 text-amber-700 border-amber-100",
  };

  return (
    <div className={`p-4 rounded-xl border ${colorMap[color]} flex items-start gap-4`}>
      <div className="p-2 bg-white rounded-lg shadow-sm">
        <Icon size={20} />
      </div>
      <div className="overflow-hidden">
        <p className="text-xs font-medium uppercase opacity-70 truncate">{label}</p>
        <p className="text-2xl font-bold truncate">
          {typeof value === 'number' ? value.toFixed(2) : value} <span className="text-sm font-normal">{unit}</span>
        </p>
      </div>
    </div>
  );
};

const App = () => {
  const [startDate, setStartDate] = useState('2026-01-01');
  const [endDate, setEndDate] = useState('2026-01-31');
  const [cutoffHour, setCutoffHour] = useState(9);
  const [horizonHours, setHorizonHours] = useState<number | 'null'>('null');
  const [mode, setMode] = useState<'cutoff' | 'horizon'>('cutoff');

  const [actuals, setActuals] = useState<DataPoint[]>([]);
  const [forecasts, setForecasts] = useState<DataPoint[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [hourMetrics, setHourMetrics] = useState<HourMetric[]>([]);
  const [horizonMetrics, setHorizonMetrics] = useState<HorizonMetric[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const hParam = horizonHours === 'null' ? '' : `&horizon_hours=${horizonHours}`;
      const cParam = mode === 'cutoff' ? `&cutoff_hour=${cutoffHour}` : '';

      const [resAct, resFc, resMet, resHour, resHoriz] = await Promise.all([
        fetch(`/api/actuals?start=${startDate}&end=${endDate}`).then(r => r.json()),
        fetch(`/api/forecast?start=${startDate}&end=${endDate}${cParam}${hParam}`).then(r => r.json()),
        fetch(`/api/metrics?start=${startDate}&end=${endDate}${cParam}${hParam}`).then(r => r.json()),
        fetch(`/api/metrics/by-hour?start=${startDate}&end=${endDate}${cParam}${hParam}`).then(r => r.json()),
        fetch(`/api/metrics/by-horizon?start=${startDate}&end=${endDate}`).then(r => r.json()),
      ]);

      setActuals(resAct);
      setForecasts(resFc);
      setMetrics(resMet);
      setHourMetrics(resHour);
      setHorizonMetrics(resHoriz);
    } catch (e) {
      setError("Failed to fetch data from API. Please ensure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [startDate, endDate, cutoffHour, horizonHours, mode]);

  const chartData = actuals.map((a, i) => {
    const f = forecasts.find(f => f.startTime === a.startTime);
    return {
      time: a.startTime.replace('T', ' ').substring(0, 16),
      actual: a.generation,
      forecast: f ? f.generation : null,
    };
  });

  if (error) return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-red-50 text-red-700 p-6 rounded-2xl border border-red-100 flex flex-col items-center text-center max-w-md">
        <AlertTriangle size={48} className="mb-4" />
        <h2 className="text-xl font-bold mb-2">Connection Error</h2>
        <p className="mb-6">{error}</p>
        <button onClick={fetchData} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
          Retry Connection
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen p-4 md:p-8 max-w-7xl mx-auto space-y-8">
      {/* Header & Controls */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div className="flex-shrink-0">
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Activity className="text-blue-600" />
            UK Wind Forecast Analysis
          </h1>
          <p className="text-slate-500 text-sm">January 2026 Day-Ahead Market Analysis</p>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-lg">
            <button
              onClick={() => setMode('cutoff')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${mode === 'cutoff' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-700'}`}
            >
              Cutoff Mode
            </button>
            <button
              onClick={() => setMode('horizon')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${mode === 'horizon' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-700'}`}
            >
              Horizon Mode
            </button>
          </div>

          <div className="flex items-center gap-3">
            {mode === 'cutoff' ? (
              <div className="flex items-center gap-2 bg-white border border-slate-200 px-3 py-1.5 rounded-lg">
                <Clock size={14} className="text-slate-400" />
                <span className="text-xs text-slate-500 font-medium">Cutoff:</span>
                <input
                  type="number"
                  value={cutoffHour}
                  onChange={e => setCutoffHour(parseInt(e.target.value))}
                  className="w-12 text-xs font-bold text-center outline-none"
                  min="0" max="23"
                />
                <span className="text-xs text-slate-400">UTC</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 bg-white border border-slate-200 px-3 py-1.5 rounded-lg">
                <TrendingDown size={14} className="text-slate-400" />
                <span className="text-xs text-slate-500 font-medium">Horizon:</span>
                <input
                  type="number"
                  value={horizonHours === 'null' ? '' : horizonHours}
                  onChange={e => setHorizonHours(parseInt(e.target.value))}
                  className="w-12 text-xs font-bold text-center outline-none"
                  min="1"
                />
                <span className="text-xs text-slate-400">hrs</span>
              </div>
            )}

            <div className="flex items-center gap-2 bg-white border border-slate-200 px-3 py-1.5 rounded-lg">
              <Calendar size={14} className="text-slate-400" />
              <input
                type="date"
                value={startDate}
                onChange={e => setStartDate(e.target.value)}
                className="text-xs font-medium outline-none"
              />
              <span className="text-xs text-slate-400">to</span>
              <input
                type="date"
                value={endDate}
                onChange={e => setEndDate(e.target.value)}
                className="text-xs font-medium outline-none"
              />
            </div>
          </div>
        </div>
      </header>

      {loading && (
        <div className="fixed inset-0 bg-white/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="MAE" value={metrics?.mae} unit="MW" icon={Activity} color="blue" />
        <StatCard label="RMSE" value={metrics?.rmse} unit="MW" icon={TrendingUp} color="blue" />
        <StatCard label="Bias" value={metrics?.bias} unit="MW" icon={TrendingDown} color={metrics && metrics.bias > 0 ? "red" : "green"} />
        <StatCard label="P90 Error" value={metrics?.p90} unit="MW" icon={Info} color="amber" />
      </div>

      {/* Insights Panel */}
      <div className="bg-blue-600 text-white p-6 rounded-2xl shadow-lg flex items-center gap-6 relative overflow-hidden">
        <div className="relative z-10 flex-1">
          <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
            <Info size={20} />
            Buying Insight
          </h3>
          <p className="text-blue-100 text-lg leading-relaxed">
            {metrics?.insight || "Loading analysis..."}
          </p>
        </div>
        <div className="hidden lg:block opacity-20 absolute -right-10 -bottom-10 transform rotate-12">
          <Activity size={160} />
        </div>
      </div>

      {/* Main Chart */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <h3 className="text-lg font-bold mb-6 text-slate-800">Actual vs Decision-Time Forecast</h3>
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis
                dataKey="time"
                tick={{fontSize: 12}}
                tickMargin={10}
                minTickGap={30}
              />
              <YAxis
                tick={{fontSize: 12}}
                unit="MW"
                domain={['auto', 'auto']}
              />
              <Tooltip
                contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'}}
              />
              <Legend verticalAlign="top" height={36} />
              <Line
                type="monotone"
                dataKey="actual"
                name="Actual Generation"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="forecast"
                name="Decision-Time Forecast"
                stroke="#f97316"
                strokeWidth={2}
                dot={false}
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Secondary Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Error by Hour */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
          <h3 className="text-lg font-bold mb-6 text-slate-800">Bias by Hour of Day</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hourMetrics}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="hour" tick={{fontSize: 12}} />
                <YAxis tick={{fontSize: 12}} unit="MW" />
                <Tooltip
                  contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'}}
                />
                <Bar dataKey="mean" name="Mean Bias" fill="#64748b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Error by Horizon */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
          <h3 className="text-lg font-bold mb-6 text-slate-800">Accuracy vs Horizon</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={horizonMetrics}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis
                  dataKey="horizon_hours"
                  tick={{fontSize: 12}}
                  label={{ value: 'Hours before target', position: 'insideBottom', offset: -5 }}
                />
                <YAxis tick={{fontSize: 12}} unit="MW" />
                <Tooltip
                  contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'}}
                />
                <Area type="monotone" dataKey="std" name="Error Std Dev" stroke="#3b82f6" fill="#dbeafe" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <footer className="text-center text-slate-400 text-xs py-8">
        <p>© 2026 Energy Utility Analysis Tool • Data source: Elexon BMRS</p>
      </footer>
    </div>
  );
};

export default App;
