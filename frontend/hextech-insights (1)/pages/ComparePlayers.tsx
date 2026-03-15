import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Canvas } from '@react-three/fiber';
import { HextechCrystal } from '../components/HextechCrystal';
import TiltMotionCard from '../components/TiltMotionCard';
import { getSummonerPredictions, type SummonerProfile } from '../services/api';

type CompareCardProps = {
  title: string;
  leftValue: string;
  rightValue: string;
};

const CompareCard: React.FC<CompareCardProps> = ({ title, leftValue, rightValue }) => (
  <TiltMotionCard tiltStrength={6} whileHover={{ scale: 1.01 }} transition={{ type: 'spring', stiffness: 280, damping: 22 }} className="glass-panel p-4 rounded-lg border border-primary/20">
    <p className="text-[11px] uppercase tracking-widest text-slate-400 font-bold mb-3">{title}</p>
    <div className="grid grid-cols-2 gap-4">
      <p className="text-white font-bold text-lg">{leftValue}</p>
      <p className="text-hextech-blue font-bold text-lg text-right">{rightValue}</p>
    </div>
  </TiltMotionCard>
);

const ComparePlayers: React.FC = () => {
  const [leftName, setLeftName] = useState('');
  const [leftRegion, setLeftRegion] = useState('euw1');
  const [rightName, setRightName] = useState('');
  const [rightRegion, setRightRegion] = useState('euw1');
  const [leftProfile, setLeftProfile] = useState<SummonerProfile | null>(null);
  const [rightProfile, setRightProfile] = useState<SummonerProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const withTimeout = async <T,>(promise: Promise<T>, timeoutMs = 45000): Promise<T> => {
    let timeoutId: ReturnType<typeof setTimeout> | undefined;
    const timeoutPromise = new Promise<never>((_, reject) => {
      timeoutId = setTimeout(() => reject(new Error('Comparison timed out. Please try again in a few seconds.')), timeoutMs);
    });

    try {
      return await Promise.race([promise, timeoutPromise]);
    } finally {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    }
  };

  const fetchBoth = async () => {
    const normalizedLeft = leftName.replace(/\s*#\s*/g, '#').trim();
    const normalizedRight = rightName.replace(/\s*#\s*/g, '#').trim();

    if (!normalizedLeft || !normalizedRight) {
      setError('Enter both summoner names to compare.');
      return;
    }

    if (!normalizedLeft.includes('#') || !normalizedRight.includes('#')) {
      setError('Use Riot ID format for both players: Name#Tag');
      return;
    }

    setLoading(true);
    setError(null);
    setLeftName(normalizedLeft);
    setRightName(normalizedRight);

    try {
      const [leftRes, rightRes] = await withTimeout(Promise.all([
        getSummonerPredictions({ summoner_name: normalizedLeft, region: leftRegion, match_count: 20 }),
        getSummonerPredictions({ summoner_name: normalizedRight, region: rightRegion, match_count: 20 }),
      ]));

      if (!leftRes.success || !leftRes.profile) {
        throw new Error(leftRes.error || 'Left player fetch failed');
      }
      if (!rightRes.success || !rightRes.profile) {
        throw new Error(rightRes.error || 'Right player fetch failed');
      }

      setLeftProfile(leftRes.profile);
      setRightProfile(rightRes.profile);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Comparison failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const regions = [
    ['na1', 'NA'],
    ['euw1', 'EUW'],
    ['eun1', 'EUNE'],
    ['kr', 'KR'],
    ['br1', 'BR'],
    ['jp1', 'JP'],
    ['la1', 'LAN'],
    ['la2', 'LAS'],
    ['oc1', 'OCE'],
    ['tr1', 'TR'],
    ['ru', 'RU'],
  ] as const;

  return (
    <div className="p-8 max-w-[1500px] mx-auto space-y-6">
      <motion.header
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      >
        <h1 className="text-4xl font-black text-white">COMPARE PLAYERS</h1>
        <p className="text-white/50 mt-2">Search two summoners and compare live model outputs side-by-side.</p>
      </motion.header>

      <motion.section
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.7, ease: 'easeOut' }}
        className="relative w-full h-[220px] rounded-xl overflow-hidden glass-panel border border-primary/20"
      >
        <div className="absolute inset-0 z-0">
          <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
            <ambientLight intensity={0.45} />
            <pointLight position={[3, 2, 4]} intensity={1.1} color="#c8aa6f" />
            <directionalLight position={[-5, 6, 3]} intensity={0.6} color="#00bcda" />
            <HextechCrystal />
          </Canvas>
        </div>
        <div className="relative z-10 h-full flex flex-col items-center justify-end pb-8 pointer-events-none">
          <p className="text-xs uppercase tracking-[0.3em] text-primary font-bold mb-2">Dual Profile Analysis</p>
          <h2 className="text-3xl font-black text-white tracking-wide">Head-to-Head Intelligence</h2>
        </div>
      </motion.section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: '-50px' }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className="glass-panel p-5 rounded-xl space-y-3"
        >
          <p className="text-xs uppercase tracking-widest text-slate-400 font-bold">Player A</p>
          <input
            value={leftName}
            onChange={(e) => setLeftName(e.target.value)}
            placeholder="Summoner or Riot ID"
            className="w-full px-4 py-3 bg-background-dark border border-primary/30 rounded-lg text-white"
          />
          <select
            value={leftRegion}
            onChange={(e) => setLeftRegion(e.target.value)}
            className="w-full px-4 py-3 bg-background-dark border border-primary/30 rounded-lg text-white"
          >
            {regions.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: '-50px' }}
          transition={{ duration: 0.5, ease: 'easeOut', delay: 0.05 }}
          className="glass-panel p-5 rounded-xl space-y-3"
        >
          <p className="text-xs uppercase tracking-widest text-slate-400 font-bold">Player B</p>
          <input
            value={rightName}
            onChange={(e) => setRightName(e.target.value)}
            placeholder="Summoner or Riot ID"
            className="w-full px-4 py-3 bg-background-dark border border-primary/30 rounded-lg text-white"
          />
          <select
            value={rightRegion}
            onChange={(e) => setRightRegion(e.target.value)}
            className="w-full px-4 py-3 bg-background-dark border border-primary/30 rounded-lg text-white"
          >
            {regions.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </motion.div>
      </section>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45 }}
        className="flex items-center gap-3"
      >
        <button
          onClick={fetchBoth}
          disabled={loading}
          className="px-8 py-3 bg-primary text-background-dark font-bold rounded-lg disabled:opacity-50"
        >
          {loading ? 'Comparing...' : 'Compare Now'}
        </button>
        {loading ? <p className="text-primary text-sm font-medium">Fetching both profiles...</p> : null}
        {error ? <p className="text-red-400 text-sm font-medium">{error}</p> : null}
      </motion.div>

      {leftProfile && rightProfile ? (
        <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <CompareCard title="Summoner" leftValue={`${leftProfile.summoner_name} (${leftProfile.region.toUpperCase()})`} rightValue={`${rightProfile.summoner_name} (${rightProfile.region.toUpperCase()})`} />
          <CompareCard title="Rank" leftValue={`${leftProfile.ranked_tier ?? leftProfile.predicted_rank_tier}`} rightValue={`${rightProfile.ranked_tier ?? rightProfile.predicted_rank_tier}`} />
          <CompareCard title="Win Rate" leftValue={`${Math.round(leftProfile.overall_winrate * 100)}%`} rightValue={`${Math.round(rightProfile.overall_winrate * 100)}%`} />
          <CompareCard title="Avg KDA" leftValue={leftProfile.avg_kda.toFixed(2)} rightValue={rightProfile.avg_kda.toFixed(2)} />
          <CompareCard title="CS / Min" leftValue={leftProfile.avg_cs_per_min.toFixed(2)} rightValue={rightProfile.avg_cs_per_min.toFixed(2)} />
          <CompareCard title="Gold / Min" leftValue={leftProfile.avg_gold_per_min.toFixed(1)} rightValue={rightProfile.avg_gold_per_min.toFixed(1)} />
          <CompareCard title="Smurf Risk" leftValue={leftProfile.smurf_is_anomaly ? 'Anomaly' : 'Normal'} rightValue={rightProfile.smurf_is_anomaly ? 'Anomaly' : 'Normal'} />
          <CompareCard title="Smurf Score" leftValue={leftProfile.smurf_anomaly_score.toFixed(3)} rightValue={rightProfile.smurf_anomaly_score.toFixed(3)} />
          <CompareCard title="Champion Pool" leftValue={`${leftProfile.champion_pool_size}`} rightValue={`${rightProfile.champion_pool_size}`} />
        </section>
      ) : (
        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
          className="glass-panel p-6 rounded-xl border border-primary/20"
        >
          <p className="text-white/60 text-sm">Run a comparison to see side-by-side stats and model outputs.</p>
        </motion.section>
      )}
    </div>
  );
};

export default ComparePlayers;
