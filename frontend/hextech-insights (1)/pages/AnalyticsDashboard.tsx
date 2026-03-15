import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, Tooltip, Cell } from 'recharts';
import { motion } from 'framer-motion';
import {
  getHealth,
  listMatchOutcomeModels,
  predictMatchOutcomeEarly,
  predictRank,
  predictSmurf,
} from '../services/api';
import { sampleMatchPayload, sampleRankPayload, sampleSmurfPayload } from '../services/samplePayloads';

type RankDistributionPoint = {
  rank: string;
  percentage: number;
  color: string;
};

const tierDistributionData: RankDistributionPoint[] = [
  { rank: 'Iron', percentage: 2.2, color: '#475569' },
  { rank: 'Bronze', percentage: 17.0, color: '#64748b' },
  { rank: 'Silver', percentage: 24.0, color: '#94a3b8' },
  { rank: 'Gold', percentage: 25.0, color: '#c8aa6f' },
  { rank: 'Platinum', percentage: 17.0, color: '#00bcda' },
  { rank: 'Emerald', percentage: 9.6, color: '#10b981' },
  { rank: 'Diamond', percentage: 3.7, color: '#60a5fa' },
  { rank: 'Master', percentage: 1.0, color: '#a78bfa' },
  { rank: 'GrandMaster', percentage: 0.09, color: '#f43f5e' },
  { rank: 'Challenger', percentage: 0.038, color: '#f59e0b' },
];

const divisionDistributionData: RankDistributionPoint[] = [
  { rank: 'Challenger', percentage: 0.038, color: '#f59e0b' },
  { rank: 'GrandMaster', percentage: 0.09, color: '#f43f5e' },
  { rank: 'Master', percentage: 1.0, color: '#a78bfa' },
  { rank: 'Diamond I', percentage: 0.56, color: '#60a5fa' },
  { rank: 'Diamond II', percentage: 0.56, color: '#60a5fa' },
  { rank: 'Diamond III', percentage: 0.81, color: '#60a5fa' },
  { rank: 'Diamond IV', percentage: 1.8, color: '#60a5fa' },
  { rank: 'Emerald I', percentage: 1.3, color: '#10b981' },
  { rank: 'Emerald II', percentage: 1.7, color: '#10b981' },
  { rank: 'Emerald III', percentage: 2.4, color: '#10b981' },
  { rank: 'Emerald IV', percentage: 4.2, color: '#10b981' },
  { rank: 'Platinum I', percentage: 2.4, color: '#00bcda' },
  { rank: 'Platinum II', percentage: 3.6, color: '#00bcda' },
  { rank: 'Platinum III', percentage: 4.5, color: '#00bcda' },
  { rank: 'Platinum IV', percentage: 7.0, color: '#00bcda' },
  { rank: 'Gold I', percentage: 4.0, color: '#c8aa6f' },
  { rank: 'Gold II', percentage: 5.6, color: '#c8aa6f' },
  { rank: 'Gold III', percentage: 6.3, color: '#c8aa6f' },
  { rank: 'Gold IV', percentage: 8.6, color: '#c8aa6f' },
  { rank: 'Silver I', percentage: 4.8, color: '#94a3b8' },
  { rank: 'Silver II', percentage: 6.0, color: '#94a3b8' },
  { rank: 'Silver III', percentage: 6.1, color: '#94a3b8' },
  { rank: 'Silver IV', percentage: 7.1, color: '#94a3b8' },
  { rank: 'Bronze I', percentage: 4.3, color: '#64748b' },
  { rank: 'Bronze II', percentage: 4.4, color: '#64748b' },
  { rank: 'Bronze III', percentage: 4.0, color: '#64748b' },
  { rank: 'Bronze IV', percentage: 4.7, color: '#64748b' },
  { rank: 'Iron I', percentage: 1.4, color: '#475569' },
  { rank: 'Iron II', percentage: 0.54, color: '#475569' },
  { rank: 'Iron III', percentage: 0.19, color: '#475569' },
  { rank: 'Iron IV', percentage: 0.12, color: '#475569' },
];

const AnalyticsDashboard: React.FC = () => {
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [modelsCount, setModelsCount] = useState<number>(0);
  const [rankTier, setRankTier] = useState<string>('Loading...');
  const [matchWinRate, setMatchWinRate] = useState<string>('...');
  const [smurfAnomaly, setSmurfAnomaly] = useState<string>('...');
  const [smurfScore, setSmurfScore] = useState<string>('...');
  const [distributionView, setDistributionView] = useState<'tier' | 'division'>('tier');

  const chartData = distributionView === 'tier' ? tierDistributionData : divisionDistributionData;
  const chartWidth = Math.max(900, chartData.length * 56);

  useEffect(() => {
    const load = async () => {
      try {
        const [health, models, match, rank, smurf] = await Promise.all([
          getHealth(),
          listMatchOutcomeModels(),
          predictMatchOutcomeEarly(sampleMatchPayload),
          predictRank(sampleRankPayload),
          predictSmurf(sampleSmurfPayload),
        ]);

        setBackendOnline(health.status === 'ok' || health.status === 'healthy');
        setModelsCount(models.models.length);
        setRankTier(rank.predicted_tier);
        setMatchWinRate(`${Math.round(match.win_probability * 100)}%`);
        setSmurfAnomaly(smurf.is_smurf_anomaly ? 'Critical' : 'Normal');
        setSmurfScore(`${Math.round(Math.abs(smurf.anomaly_score) * 100)}%`);
      } catch {
        setBackendOnline(false);
        setRankTier('Offline');
      }
    };

    load();
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-[1600px] mx-auto">
      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {[
          { label: 'API Status', value: backendOnline ? 'ONLINE' : 'OFFLINE', trend: backendOnline ? 'Connected to FastAPI' : 'Backend unreachable', trendUp: backendOnline, icon: 'hub' },
          { label: 'Live Match Win Rate', value: matchWinRate, trend: 'From match-outcome early endpoint', trendUp: true, icon: 'insights' },
          { label: 'Rank Prediction', value: rankTier, sub: 'From rank classifier endpoint', icon: 'military_tech', image: 'https://picsum.photos/seed/kaisa/64' },
          { label: 'Smurf Alerts', value: smurfAnomaly, trend: `${modelsCount} match models available`, trendUp: smurfAnomaly === 'Critical', icon: 'radar', isBlue: true },
        ].map((stat, i) => (
          <div key={i} className="relative p-6 rounded-lg border border-primary/30 bg-[#1e1a14] overflow-hidden">
            <div className="flex justify-between items-start mb-2 relative z-10">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{stat.label}</p>
              <span className={`material-symbols-outlined ${stat.isBlue ? 'text-hextech-blue' : 'text-primary'} text-xl`}>{stat.icon}</span>
            </div>
            {stat.image ? (
              <div className="flex items-center gap-3">
                <div className="size-9 rounded bg-slate-800 border border-primary/40 bg-cover bg-center" style={{ backgroundImage: `url(${stat.image})` }}></div>
                <div>
                  <p className="text-xl font-extrabold text-white">{stat.value}</p>
                  <p className="text-xs text-slate-500">{stat.sub}</p>
                </div>
              </div>
            ) : (
              <p className="text-3xl font-extrabold text-white">{stat.value}</p>
            )}
            {stat.trend && (
              <div className="flex items-center gap-1 mt-2 relative z-10">
                {!stat.isBlue && <span className={`material-symbols-outlined text-xs ${stat.trendUp ? 'text-green-500' : 'text-red-500'}`}>{stat.trendUp ? 'trending_up' : 'trending_down'}</span>}
                <p className={`text-xs font-bold ${stat.isBlue ? 'text-hextech-blue' : (stat.trendUp ? 'text-green-500' : 'text-red-500')}`}>{stat.trend}</p>
              </div>
            )}
            {stat.isBlue && <div className="absolute -bottom-4 -right-4 size-24 bg-hextech-blue/10 blur-3xl rounded-full"></div>}
          </div>
        ))}
      </motion.section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.55, ease: 'easeOut' }}
          className="lg:col-span-2 glass-panel rounded-lg p-6"
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">bar_chart</span>
                Global Rank Distribution
              </h2>
              <p className="text-xs text-slate-500">
                {distributionView === 'tier'
                  ? 'Real Solo Queue tier distribution snapshot (tier-level aggregate)'
                  : 'Real Solo Queue division distribution snapshot (I/II/III/IV breakdown)'}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setDistributionView('tier')}
                className={`px-3 py-1.5 rounded text-[11px] font-bold uppercase tracking-wider border transition-colors ${
                  distributionView === 'tier'
                    ? 'bg-primary text-background-dark border-primary'
                    : 'bg-white/5 text-slate-300 border-white/10 hover:border-primary/40'
                }`}
              >
                Tier View
              </button>
              <button
                onClick={() => setDistributionView('division')}
                className={`px-3 py-1.5 rounded text-[11px] font-bold uppercase tracking-wider border transition-colors ${
                  distributionView === 'division'
                    ? 'bg-primary text-background-dark border-primary'
                    : 'bg-white/5 text-slate-300 border-white/10 hover:border-primary/40'
                }`}
              >
                Division View
              </button>
            </div>
          </div>

          <div className="h-72 w-full overflow-x-auto custom-scrollbar">
            <BarChart width={chartWidth} height={280} data={chartData}>
              <XAxis
                dataKey="rank"
                axisLine={false}
                tickLine={false}
                interval={0}
                tick={{ fill: '#64748b', fontSize: 10, fontWeight: 'bold' }}
                angle={distributionView === 'division' ? -30 : 0}
                textAnchor={distributionView === 'division' ? 'end' : 'middle'}
                height={distributionView === 'division' ? 70 : 40}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#0a1428', border: '1px solid rgba(200, 170, 111, 0.3)', borderRadius: '8px' }}
                itemStyle={{ color: '#c8aa6f' }}
                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                formatter={(value: number) => [`${value}%`, 'Players']}
              />
              <Bar dataKey="percentage" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 24 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.6, ease: 'easeOut', delay: 0.1 }}
          className="glass-panel rounded-lg p-6 flex flex-col"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span className="material-symbols-outlined text-hextech-blue">shutter_speed</span>
              Smurf Watch
            </h2>
            <span className="text-[10px] font-bold text-hextech-blue bg-hextech-blue/10 px-2 py-1 rounded">LIVE FEED</span>
          </div>

          <div className="space-y-4 flex-1">
            {[
              { name: 'Sample Smurf Profile', wr: smurfScore, rank: 'Smurf endpoint probe', status: smurfAnomaly, color: smurfAnomaly === 'Critical' ? 'text-primary' : 'text-hextech-blue' },
              { name: 'Rank Endpoint Status', wr: rankTier, rank: 'Classifier output', status: backendOnline ? 'Online' : 'Offline', color: backendOnline ? 'text-hextech-blue' : 'text-red-500' },
              { name: 'Match Model Count', wr: `${modelsCount}`, rank: 'Registered models', status: modelsCount > 0 ? 'Healthy' : 'Unknown', color: 'text-primary' },
            ].map((smurf, i) => (
              <div key={i} className="p-3 rounded border border-white/5 bg-white/5 hover:border-hextech-blue/30 transition-all cursor-pointer group">
                <div className="flex justify-between items-start mb-1">
                  <p className="text-sm font-bold text-white group-hover:text-hextech-blue transition-colors">{smurf.name}</p>
                  <p className="text-[10px] font-bold text-green-500">{smurf.wr}</p>
                </div>
                <div className="flex items-center justify-between">
                  <p className="text-[10px] text-slate-500">{smurf.rank}</p>
                  <div className="flex gap-1 items-center">
                    <span className={`size-1.5 rounded-full ${smurf.color === 'text-primary' ? 'bg-primary animate-pulse' : smurf.color === 'text-red-500' ? 'bg-red-500' : 'bg-hextech-blue'}`}></span>
                    <p className={`text-[9px] font-bold ${smurf.color} uppercase`}>{smurf.status}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </section>
    </div>
  );
};

export default AnalyticsDashboard;
