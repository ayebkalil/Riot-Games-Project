import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getHealth,
  listMatchOutcomeModels,
  predictMatchOutcomeEarly,
  predictProgression,
  predictRank,
  predictSmurf,
} from '../services/api';
import {
  sampleMatchPayload,
  sampleProgressionPayload,
  sampleRankPayload,
  sampleSmurfPayload,
} from '../services/samplePayloads';

const ModelDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [backendUp, setBackendUp] = useState<boolean>(false);
  const [availableModels, setAvailableModels] = useState<number>(0);
  const [matchWinProb, setMatchWinProb] = useState<number | null>(null);
  const [rankTier, setRankTier] = useState<string>('...');
  const [progressDelta, setProgressDelta] = useState<number | null>(null);
  const [smurfLabel, setSmurfLabel] = useState<string>('...');

  useEffect(() => {
    const load = async () => {
      try {
        const [health, models, match, rank, progression, smurf] = await Promise.all([
          getHealth(),
          listMatchOutcomeModels(),
          predictMatchOutcomeEarly(sampleMatchPayload),
          predictRank(sampleRankPayload),
          predictProgression(sampleProgressionPayload),
          predictSmurf(sampleSmurfPayload),
        ]);

        setBackendUp(health.status === 'ok' || health.status === 'healthy');
        setAvailableModels(models.models.length);
        setMatchWinProb(match.win_probability);
        setRankTier(rank.predicted_tier);
        setProgressDelta(progression.predicted_delta_winrate);
        setSmurfLabel(smurf.is_smurf_anomaly ? 'Anomaly' : 'Normal');
      } catch {
        setBackendUp(false);
      }
    };

    load();
  }, []);

  const models = useMemo(
    () => [
      {
        title: 'Match Outcome Prediction',
        key: 'match',
        value: matchWinProb == null ? '--' : `${Math.round(matchWinProb * 100)}%`,
        metric: 'Win Probability',
        desc: 'Live output from /match-outcome/predict/early using sample match features.',
        icon: 'videogame_asset',
      },
      {
        title: 'Rank Classification',
        key: 'rank',
        value: rankTier,
        metric: 'Predicted Tier',
        desc: 'Live output from /rank/predict using validated ranked player profile.',
        icon: 'military_tech',
      },
      {
        title: 'Player Progression',
        key: 'progression',
        value: progressDelta == null ? '--' : `${progressDelta.toFixed(3)}`,
        metric: 'Delta Winrate',
        desc: 'Live output from /progression/predict based on progression delta features.',
        icon: 'insights',
      },
      {
        title: 'Smurf Detection',
        key: 'smurf',
        value: smurfLabel,
        metric: 'Anomaly State',
        desc: 'Live output from /smurf/predict using high-signal smurf-like profile.',
        icon: 'security',
      },
    ],
    [matchWinProb, progressDelta, rankTier, smurfLabel],
  );

  return (
    <div className="p-8 space-y-12 max-w-[1600px] mx-auto">
      <header>
        <h1 className="text-4xl font-black text-white mb-2">MODEL DASHBOARD</h1>
        <p className="text-white/50">Real-time machine learning analytics and competitive performance tracking.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          {models.map((model, i) => (
            <div key={i} className="glass-panel p-6 rounded-xl hover:border-primary/50 transition-all group flex flex-col">
              <div className="flex justify-between items-start mb-6">
                <div className="size-12 rounded bg-white/5 flex items-center justify-center text-primary border border-white/10">
                  <span className="material-symbols-outlined">{model.icon}</span>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-black text-white">{model.value}</p>
                  <p className="text-[10px] font-bold text-white/40 uppercase tracking-widest">{model.metric}</p>
                </div>
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{model.title}</h3>
              <p className="text-sm text-white/50 mb-6 flex-1">{model.desc}</p>
              <button
                onClick={() => navigate(`/predictions?model=${model.key}`)}
                className="w-full py-2.5 bg-white/5 group-hover:bg-primary group-hover:text-background-dark rounded font-bold text-sm transition-all flex items-center justify-center gap-2"
              >
                <span className="material-symbols-outlined text-sm">rocket_launch</span>
                Open Prediction
              </button>
            </div>
          ))}
        </div>

        <div className="lg:col-span-4 space-y-6">
          <div className="glass-panel p-6 rounded-xl">
            <h3 className="text-white font-bold mb-6 flex items-center gap-2 uppercase tracking-widest text-sm">
              <span className="material-symbols-outlined text-primary">analytics</span>
              System Health
            </h3>
            <div className="space-y-6">
              {[
                {
                  label: 'Backend API',
                  status: backendUp ? 'ONLINE' : 'OFFLINE',
                  color: backendUp ? 'text-green-500' : 'text-red-500',
                  bar: backendUp ? 100 : 15,
                },
                {
                  label: 'Match Model Registry',
                  status: `${availableModels} AVAILABLE`,
                  color: 'text-green-500',
                  bar: Math.min(100, availableModels * 20),
                },
                {
                  label: 'Smurf Detection Service',
                  status: smurfLabel.toUpperCase(),
                  color: smurfLabel === 'Anomaly' ? 'text-yellow-500' : 'text-green-500',
                  bar: smurfLabel === 'Anomaly' ? 70 : 95,
                },
                {
                  label: 'Prediction Pipeline',
                  status: backendUp ? 'ACTIVE' : 'WAITING',
                  color: backendUp ? 'text-green-500' : 'text-yellow-500',
                  bar: backendUp ? 90 : 30,
                },
              ].map((sys, i) => (
                <div key={i}>
                  <div className="flex justify-between items-center mb-2">
                    <p className="text-xs font-bold text-white/60">{sys.label}</p>
                    <p className={`text-[10px] font-black ${sys.color}`}>{sys.status}</p>
                  </div>
                  <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${sys.color === 'text-yellow-500' ? 'bg-yellow-500' : sys.color === 'text-red-500' ? 'bg-red-500' : 'bg-green-500'} transition-all`}
                      style={{ width: `${sys.bar}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-6 rounded-xl bg-primary/10 border border-primary/20 relative overflow-hidden group">
            <div className="absolute -top-10 -right-10 size-40 bg-primary/5 blur-[40px] rounded-full group-hover:bg-primary/10 transition-all"></div>
            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-primary">auto_awesome</span>
                <p className="text-sm font-black text-white">Live Integration</p>
              </div>
              <p className="text-xs text-white/60 leading-relaxed mb-4">
                This dashboard now reads live backend outputs for health, model list, rank classification, progression regression, smurf anomaly, and match outcome probability.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelDashboard;
