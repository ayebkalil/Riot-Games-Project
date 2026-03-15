import React, { useState, useEffect, useMemo } from 'react';
import { AreaChart, Area, ResponsiveContainer, XAxis, Tooltip, CartesianGrid } from 'recharts';
import { motion, useMotionValue, useSpring } from 'framer-motion';
import { Canvas } from '@react-three/fiber';
import { HextechCrystal } from '../components/HextechCrystal';
import { predictMatchOutcomeEarly, predictMatchOutcomeFromSummary, predictProgression, predictRank, predictSmurf, getSummonerPredictions, getRiotHealth, type SummonerProfile, type MatchSummary } from '../services/api';
import { sampleMatchPayload, sampleProgressionPayload, sampleRankPayload, sampleSmurfPayload } from '../services/samplePayloads';

const progressionData = [
  { game: 'Game 1', gain: 10 },
  { game: 'Game 2', gain: 25 },
  { game: 'Game 3', gain: 20 },
  { game: 'Game 4', gain: 45 },
  { game: 'Game 5', gain: 30 },
  { game: 'Game 6', gain: 60 },
  { game: 'Game 7', gain: 55 },
  { game: 'Game 8', gain: 80 },
  { game: 'Game 9', gain: 65 },
  { game: 'Game 10', gain: 95 },
  { game: 'Game 11', gain: 85 },
  { game: 'Game 12', gain: 110 },
  { game: 'Game 13', gain: 90 },
  { game: 'Game 14', gain: 125 },
  { game: 'Game 15', gain: 115 },
];

type DetectionFactor = {
  label: string;
  value: string;
  color: string;
  icon: string;
  context: string;
};

type WhyReason = {
  title: string;
  value: string;
  note: string;
  icon: string;
  color: string;
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#0a1428] border border-primary/30 p-2 rounded shadow-lg backdrop-blur-md">
        <p className="text-[10px] font-black text-primary uppercase tracking-widest mb-1">{label}</p>
        <p className="text-sm font-bold text-white">
          Gain: <span className="text-hextech-blue">+{payload[0].value} LP</span>
        </p>
      </div>
    );
  }
  return null;
};

const matchListVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.08,
    },
  },
};

const matchItemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.45,
      ease: 'easeOut',
    },
  },
};

type TiltMotionCardProps = React.ComponentProps<typeof motion.div> & {
  tiltStrength?: number;
};

const TiltMotionCard: React.FC<TiltMotionCardProps> = ({ tiltStrength = 8, style, onMouseMove, onMouseLeave, ...props }) => {
  const rotateXTarget = useMotionValue(0);
  const rotateYTarget = useMotionValue(0);
  const rotateX = useSpring(rotateXTarget, { stiffness: 260, damping: 28, mass: 0.6 });
  const rotateY = useSpring(rotateYTarget, { stiffness: 260, damping: 28, mass: 0.6 });

  return (
    <motion.div
      {...props}
      style={{
        ...style,
        rotateX,
        rotateY,
        transformPerspective: 1100,
        transformStyle: 'preserve-3d',
        willChange: 'transform',
      }}
      onMouseMove={(event) => {
        const bounds = event.currentTarget.getBoundingClientRect();
        const relativeX = (event.clientX - bounds.left) / bounds.width;
        const relativeY = (event.clientY - bounds.top) / bounds.height;
        const centeredX = relativeX - 0.5;
        const centeredY = relativeY - 0.5;

        rotateXTarget.set(-centeredY * tiltStrength);
        rotateYTarget.set(centeredX * tiltStrength);

        if (onMouseMove) {
          onMouseMove(event);
        }
      }}
      onMouseLeave={(event) => {
        rotateXTarget.set(0);
        rotateYTarget.set(0);
        if (onMouseLeave) {
          onMouseLeave(event);
        }
      }}
    />
  );
};

const Profile: React.FC = () => {
  const [pulse, setPulse] = useState(false);
  const [summonerProfile, setSummonerProfile] = useState<SummonerProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [riotAccess, setRiotAccess] = useState<string>('checking');
  const [retryCooldown, setRetryCooldown] = useState<number>(0);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string>('Never');
  const [showSkeletons, setShowSkeletons] = useState<boolean>(false);
  const [cacheInfo, setCacheInfo] = useState<string | null>(null);
  const [searchName, setSearchName] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('na1');

  // Prediction states for match history items
  const [predictingMatches, setPredictingMatches] = useState<Record<string, boolean>>({});
  const [matchPredictions, setMatchPredictions] = useState<Record<string, number>>({});

  const handlePredictMatch = async (match: MatchSummary | any, matchIndex: string) => {
    setPredictingMatches(prev => ({ ...prev, [matchIndex]: true }));
    try {
      // Create a payload that satisfies MatchSummary fields whether it's real API data or mock frontend data
      const payload = match.match_id ? match : {
        kills: parseInt(match.kda.split(' / ')[0]),
        deaths: parseInt(match.kda.split(' / ')[1]),
        assists: parseInt(match.kda.split(' / ')[2]),
        win: match.res === 'Victory',
        game_duration: 1500,
        champion: match.champ
      } as MatchSummary;

      const response = await predictMatchOutcomeFromSummary(payload);
      setMatchPredictions(prev => ({ ...prev, [matchIndex]: response.win_probability }));
    } catch (err) {
      console.error("Prediction failed:", err);
    } finally {
      setPredictingMatches(prev => ({ ...prev, [matchIndex]: false }));
    }
  };

  // Fallback states for when no summoner is loaded
  const [smurfConfidence, setSmurfConfidence] = useState<number>(85);
  const [smurfMatchLabel, setSmurfMatchLabel] = useState<string>('Critical Match');
  const [progressionGain, setProgressionGain] = useState<string>('+15% Gain');
  const [predictedRankTier, setPredictedRankTier] = useState<string>('Loading');
  const [liveWinRate, setLiveWinRate] = useState<string>('...');
  const [detectionFactors, setDetectionFactors] = useState<DetectionFactor[]>([
    {
      label: 'Mechanical Outlier',
      value: 'High',
      color: 'text-primary',
      icon: 'bolt',
      context: 'Skillshots land 42% more often than league average.',
    },
    {
      label: 'APM Consistency',
      value: '380+',
      color: 'text-hextech-blue',
      icon: 'speed',
      context: 'Input variance is < 2ms, typical of Pro-level hardware/mechanics.',
    },
    {
      label: 'Pathing Efficiency',
      value: '98%',
      color: 'text-green-400',
      icon: 'map',
      context: 'Jungle route optimization matches Diamond+ patterns.',
    },
    {
      label: 'Itemization Speed',
      value: 'Critical',
      color: 'text-red-400',
      icon: 'shopping_cart',
      context: 'Recall-to-buy window is 1.4s (Tier 1 speed).',
    },
  ]);
  const [verdictText, setVerdictText] = useState<string>(
    'Account exhibits patterns typical of alternate identity play. Combat effectiveness is in the 99th percentile for current bracket.',
  );

  const handleSummonerSearch = async () => {
    const normalizedSearch = searchName.replace(/\s*#\s*/g, '#').trim();

    if (!normalizedSearch) {
      setError('Please enter a summoner name');
      return;
    }

    setLoading(true);
    setShowSkeletons(true);
    setError(null);
    setCacheInfo(null);

    try {
      const response = await getSummonerPredictions({
        summoner_name: normalizedSearch,
        region: selectedRegion,
        match_count: 20,
      });

      setSearchName(normalizedSearch);

      if (response.success && response.profile) {
        setSummonerProfile(response.profile);
        updateUIWithProfile(response.profile);
        if (response.from_cache) {
          setCacheInfo(`Showing cached data (${response.cache_age_seconds ?? 0}s old)`);
        }
        setLastUpdatedAt(new Date().toLocaleTimeString());
      } else {
        setError(response.error || 'Failed to fetch summoner data');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch summoner data');
    } finally {
      setLoading(false);
      setShowSkeletons(false);
    }
  };

  const openRiotPortal = () => {
    window.open('https://developer.riotgames.com/', '_blank', 'noopener,noreferrer');
  };

  const startRetryCooldown = () => {
    setRetryCooldown(30);
  };

  const updateUIWithProfile = (profile: SummonerProfile) => {
    // Update smurf detection
    const confidence = Math.max(0, Math.min(99, Math.round(Math.abs(profile.smurf_anomaly_score) * 100)));
    setSmurfConfidence(confidence);
    setSmurfMatchLabel(profile.smurf_is_anomaly ? 'Critical Match' : 'Normal Match');

    // Update rank
    setPredictedRankTier(profile.predicted_rank_tier);

    // Update win rate
    setLiveWinRate(`${Math.round(profile.overall_winrate * 100)}%`);

    // Update detection factors with real data
    setDetectionFactors([
      {
        label: 'Smurf Detection',
        value: profile.smurf_is_anomaly ? 'Anomaly' : 'Normal',
        color: profile.smurf_is_anomaly ? 'text-red-400' : 'text-green-400',
        icon: 'shield',
        context: `Anomaly score: ${profile.smurf_anomaly_score.toFixed(4)}`,
      },
      {
        label: 'Predicted Rank',
        value: profile.predicted_rank_tier,
        color: 'text-hextech-blue',
        icon: 'military_tech',
        context: 'ML prediction from ranked features',
      },
      {
        label: 'Champion Pool',
        value: `${profile.champion_pool_size} champs`,
        color: 'text-primary',
        icon: 'groups',
        context: `${profile.matches_analyzed} matches analyzed`,
      },
      {
        label: 'Performance',
        value: `${profile.avg_kda.toFixed(2)} KDA`,
        color: 'text-hextech-blue',
        icon: 'trending_up',
        context: `${profile.avg_cs_per_min.toFixed(1)} CS/min avg`,
      },
    ]);

    // Update verdict
    if (profile.smurf_is_anomaly) {
      setVerdictText(`${profile.summoner_name} exhibits anomalous behavior patterns. Performance metrics significantly deviate from expected baseline for ${profile.ranked_tier || 'current rank'}.`);
    } else {
      setVerdictText(`${profile.summoner_name} shows consistent performance patterns. Behavioral metrics align with ${profile.ranked_tier || profile.predicted_rank_tier} skill level.`);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => setPulse(p => !p), 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (retryCooldown <= 0) return;

    const timer = setInterval(() => {
      setRetryCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [retryCooldown]);

  useEffect(() => {
    const loadRiotStatus = async () => {
      try {
        const status = await getRiotHealth();
        setRiotAccess(status.riot?.api_access ?? 'unreachable');
      } catch {
        setRiotAccess('unreachable');
      }
    };

    loadRiotStatus();

    const loadLiveSignals = async () => {
      try {
        const [smurf, progression, rank, match] = await Promise.all([
          predictSmurf(sampleSmurfPayload),
          predictProgression(sampleProgressionPayload),
          predictRank(sampleRankPayload),
          predictMatchOutcomeEarly(sampleMatchPayload),
        ]);

        const confidence = Math.max(0, Math.min(99, Math.round(Math.abs(smurf.anomaly_score) * 500)));
        setSmurfConfidence(confidence);
        setSmurfMatchLabel(smurf.is_smurf_anomaly ? 'Critical Match' : 'Normal Match');
        setPredictedRankTier(rank.predicted_tier);
        setLiveWinRate(`${Math.round(match.win_probability * 100)}%`);

        const gainPct = (progression.predicted_delta_winrate * 100).toFixed(1);
        const prefix = progression.predicted_delta_winrate >= 0 ? '+' : '';
        setProgressionGain(`${prefix}${gainPct}% Gain`);

        if (smurf.is_smurf_anomaly) {
          setVerdictText('Live model flags this profile as anomalous. Performance pattern is highly inconsistent with baseline account behavior.');
        } else {
          setVerdictText('Live model classifies this profile as normal. Current behavior remains consistent with historical account distribution.');
        }

        setDetectionFactors([
          {
            label: 'Mechanical Outlier',
            value: smurf.is_smurf_anomaly ? 'High' : 'Normal',
            color: smurf.is_smurf_anomaly ? 'text-primary' : 'text-hextech-blue',
            icon: 'bolt',
            context: `Anomaly score: ${smurf.anomaly_score.toFixed(4)} from smurf detector.`,
          },
          {
            label: 'Predicted Rank',
            value: rank.predicted_tier,
            color: 'text-hextech-blue',
            icon: 'military_tech',
            context: 'Live output from rank classification endpoint.',
          },
          {
            label: 'Win Probability',
            value: `${Math.round(match.win_probability * 100)}%`,
            color: 'text-green-400',
            icon: 'bar_chart',
            context: 'Live output from match outcome early prediction endpoint.',
          },
          {
            label: 'Progression Delta',
            value: `${progression.predicted_delta_winrate >= 0 ? '+' : ''}${(progression.predicted_delta_winrate * 100).toFixed(1)}%`,
            color: progression.predicted_delta_winrate >= 0 ? 'text-green-400' : 'text-red-400',
            icon: 'trending_up',
            context: 'Live output from progression regression endpoint.',
          },
        ]);
        setLastUpdatedAt(new Date().toLocaleTimeString());
      } catch {
        setVerdictText('Live backend signal unavailable. Displaying cached profile analysis.');
      }
    };

    loadLiveSignals();
  }, []);

  const whyReasons = useMemo<WhyReason[]>(() => {
    if (!summonerProfile) {
      return [
        {
          title: 'Rank Model Signal',
          value: predictedRankTier,
          note: 'Predicted from performance features including KDA, CS/min, gold/min, vision, and objective rates.',
          icon: 'military_tech',
          color: 'text-primary',
        },
        {
          title: 'Smurf Risk Signal',
          value: smurfMatchLabel,
          note: 'Based on anomaly score and behavioral consistency from recent games.',
          icon: 'radar',
          color: smurfMatchLabel === 'Critical Match' ? 'text-red-400' : 'text-hextech-blue',
        },
      ];
    }

    return [
      {
        title: 'Rank Prediction Driver',
        value: `${summonerProfile.predicted_rank_tier}`,
        note: `Avg KDA ${summonerProfile.avg_kda.toFixed(2)}, CS/min ${summonerProfile.avg_cs_per_min.toFixed(1)}, Gold/min ${summonerProfile.avg_gold_per_min.toFixed(0)} across ${summonerProfile.matches_analyzed} matches.`,
        icon: 'insights',
        color: 'text-primary',
      },
      {
        title: 'Winrate Influence',
        value: `${Math.round(summonerProfile.overall_winrate * 100)}%`,
        note: summonerProfile.overall_winrate >= 0.55
          ? 'High sustained winrate boosts rank and consistency confidence.'
          : 'Moderate/low winrate lowers confidence in upward rank projection.',
        icon: 'bar_chart',
        color: summonerProfile.overall_winrate >= 0.55 ? 'text-green-400' : 'text-yellow-400',
      },
      {
        title: 'Smurf Detector Driver',
        value: summonerProfile.smurf_is_anomaly ? 'Anomaly' : 'Normal',
        note: `Anomaly score ${summonerProfile.smurf_anomaly_score.toFixed(3)} with champion pool size ${summonerProfile.champion_pool_size}.`,
        icon: 'shield',
        color: summonerProfile.smurf_is_anomaly ? 'text-red-400' : 'text-hextech-blue',
      },
      {
        title: 'Champion Pool Impact',
        value: `${summonerProfile.champion_pool_size} champions`,
        note: summonerProfile.champion_pool_size <= 5
          ? 'Small pool usually means higher specialization and stronger role consistency.'
          : 'Wide pool indicates flexibility but can reduce specialization consistency.',
        icon: 'groups',
        color: 'text-hextech-blue',
      },
    ];
  }, [summonerProfile, predictedRankTier, smurfMatchLabel]);

  const riotStatusLabel = useMemo(() => {
    if (riotAccess === 'active') return 'Active';
    if (riotAccess === 'expired') return 'Expired';
    if (riotAccess === 'rate_limited') return 'Rate Limited';
    if (riotAccess === 'checking') return 'Checking';
    if (riotAccess === 'not_configured') return 'Not Configured';
    return 'Unreachable';
  }, [riotAccess]);

  const riotStatusClass = useMemo(() => {
    if (riotAccess === 'active') return 'text-green-400 border-green-400/40 bg-green-500/10';
    if (riotAccess === 'expired') return 'text-red-400 border-red-400/40 bg-red-500/10';
    if (riotAccess === 'rate_limited') return 'text-yellow-400 border-yellow-400/40 bg-yellow-500/10';
    return 'text-slate-400 border-slate-400/30 bg-white/5';
  }, [riotAccess]);

  return (
    <div className="p-8 max-w-[1400px] mx-auto space-y-8">
      {/* 3D Intro Scene */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.5, ease: "easeOut" }}
        className="relative w-full h-[300px] rounded-xl overflow-hidden glass-panel border border-primary/20 mb-8 flex flex-col items-center justify-center"
      >
        <div className="absolute inset-0 z-0">
          <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
            <ambientLight intensity={0.5} />
            <directionalLight position={[10, 10, 5]} intensity={1} />
            <HextechCrystal />
          </Canvas>
        </div>
        <div className="relative z-10 text-center pointer-events-none mt-32">
          <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-b from-white to-primary/80 drop-shadow-lg tracking-widest uppercase">
            Hextech Insights
          </h1>
          <p className="text-primary font-bold tracking-[0.3em] text-sm mt-2">Neural Prediction Engine</p>
        </div>
      </motion.div>

      {/* Summoner Search */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="glass-panel p-6 rounded-xl"
      >
        <div className="mb-4 flex items-center justify-between">
          <p className="text-xs uppercase tracking-widest text-slate-400 font-bold">Riot API</p>
          <span className={`text-[10px] px-2 py-1 rounded border font-bold uppercase ${riotStatusClass}`}>
            {riotStatusLabel}
          </span>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 items-end">
          <div className="lg:col-span-2 flex items-end gap-4">
            <div className="flex-1">
            <label className="block text-xs text-slate-400 font-bold uppercase tracking-wider mb-2">
              Summoner Name
            </label>
            <input
              type="text"
              value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSummonerSearch()}
              placeholder="Enter summoner name..."
              className="w-full px-4 py-3 bg-background-dark border border-primary/30 rounded-lg text-white font-medium focus:outline-none focus:border-primary transition-colors"
              disabled={loading}
            />
            </div>
            <div className="w-48">
            <label className="block text-xs text-slate-400 font-bold uppercase tracking-wider mb-2">
              Region
            </label>
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="w-full px-4 py-3 bg-background-dark border border-primary/30 rounded-lg text-white font-medium focus:outline-none focus:border-primary transition-colors"
              disabled={loading}
            >
              <option value="na1">NA</option>
              <option value="euw1">EUW</option>
              <option value="eun1">EUNE</option>
              <option value="kr">KR</option>
              <option value="br1">BR</option>
              <option value="jp1">JP</option>
              <option value="la1">LAN</option>
              <option value="la2">LAS</option>
              <option value="oc1">OCE</option>
              <option value="tr1">TR</option>
              <option value="ru">RU</option>
            </select>
            </div>
            <button
              onClick={handleSummonerSearch}
              disabled={loading}
              className="mt-7 flex items-center justify-center rounded-lg h-12 px-8 bg-primary text-background-dark hover:bg-white transition-all text-sm font-bold uppercase tracking-widest shadow-[0_0_20px_rgba(200,170,111,0.4)] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <span className="material-symbols-outlined mr-2 text-sm animate-spin">sync</span>
                  Loading...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined mr-2 text-sm">search</span>
                  Search
                </>
              )}
            </button>
          </div>

        </div>
        {error && (
          <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg space-y-3">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-red-400">error</span>
              <p className="text-red-400 text-sm font-medium">{error}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={openRiotPortal}
                className="px-3 py-1.5 border border-primary/30 rounded text-primary text-xs font-bold hover:bg-primary/10"
              >
                Refresh Key
              </button>
              <button
                disabled={retryCooldown > 0}
                onClick={() => {
                  handleSummonerSearch();
                  startRetryCooldown();
                }}
                className="px-3 py-1.5 border border-red-400/30 rounded text-red-300 text-xs font-bold hover:bg-red-500/10 disabled:opacity-50"
              >
                {retryCooldown > 0 ? `Try again in ${retryCooldown}s` : 'Try again in 30s'}
              </button>
            </div>
          </div>
        )}
        {cacheInfo && (
          <div className="mt-4 p-4 bg-yellow-500/10 border border-yellow-400/30 rounded-lg flex items-center gap-3">
            <span className="material-symbols-outlined text-yellow-300">history</span>
            <p className="text-yellow-200 text-sm font-medium">{cacheInfo}</p>
          </div>
        )}
        {summonerProfile && (
          <div className="mt-4 p-4 bg-primary/10 border border-primary/30 rounded-lg flex items-center gap-3">
            <span className="material-symbols-outlined text-primary">check_circle</span>
            <p className="text-primary text-sm font-medium">
              Loaded {summonerProfile.summoner_name} - {summonerProfile.matches_analyzed} matches analyzed
            </p>
          </div>
        )}
      </motion.section>

      {/* Profile Header */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-50px" }}
        transition={{ duration: 0.6 }}
        className="glass-panel p-6 rounded-xl flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-64 h-full bg-gradient-to-l from-primary/5 to-transparent pointer-events-none"></div>
        <div className="flex gap-6 items-center z-10">
          <div className="relative">
            <div
              className="size-32 rounded-xl border-2 border-primary shadow-[0_0_15px_rgba(200,170,111,0.3)] bg-cover bg-center"
              style={{ backgroundImage: `url('https://picsum.photos/seed/profile/200')` }}
            ></div>
            <span className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-background-dark border border-primary text-primary text-[10px] px-2 py-0.5 font-bold rounded">LVL 342</span>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <h1 className="text-white text-3xl font-black tracking-tight">
                {summonerProfile ? summonerProfile.summoner_name : 'Hide on bush'}
                <span className="text-slate-500 font-medium ml-2">
                  #{summonerProfile ? summonerProfile.region.toUpperCase() : 'KR1'}
                </span>
              </h1>
              {summonerProfile && <span className="material-symbols-outlined text-primary text-xl animate-pulse">verified</span>}
            </div>
            <div className="flex items-center gap-4 mt-1">
              <p className="text-primary font-bold text-lg">
                {summonerProfile?.ranked_tier || predictedRankTier} {summonerProfile?.ranked_division || ''}
                <span className="text-slate-400 font-normal ml-1">
                  {summonerProfile?.ranked_tier ? 'Current Rank' : 'Predicted Rank'}
                </span>
              </p>
              <div className="w-1 h-1 bg-slate-600 rounded-full"></div>
              <p className="text-slate-400 text-sm uppercase tracking-wider font-semibold">
                {summonerProfile ? `Level ${summonerProfile.summoner_level}` : 'Ranked Solo'}
              </p>
            </div>
            <div className="flex items-center gap-4 mt-3">
              <div className="flex flex-col">
                <span className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Win Rate</span>
                <span className="text-hextech-blue font-bold text-lg">{liveWinRate}</span>
              </div>
              <div className="w-px h-8 bg-slate-700"></div>
              <div className="flex flex-col">
                <span className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">W / L</span>
                <span className="text-slate-300 font-medium text-lg">
                  {summonerProfile?.ranked_wins || 120}W
                  <span className="text-slate-500"> / </span>
                  {summonerProfile?.ranked_losses || 64}L
                </span>
              </div>
            </div>
          </div>
        </div>
        <div className="flex gap-3 z-10">
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider self-center mr-2">Updated {lastUpdatedAt}</p>
          <button className="flex min-w-[140px] items-center justify-center rounded-lg h-12 px-6 bg-white/5 border border-primary/40 text-primary hover:bg-primary/20 transition-all text-sm font-bold uppercase tracking-widest">
            <span className="material-symbols-outlined mr-2 text-sm">refresh</span> Update
          </button>
          <button className="flex min-w-[140px] items-center justify-center rounded-lg h-12 px-6 bg-primary text-background-dark hover:bg-white transition-all text-sm font-bold uppercase tracking-widest shadow-[0_0_20px_rgba(200,170,111,0.4)]">
            Live Game
          </button>
        </div>
      </motion.section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sidebar Analytics */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.6 }}
          className="space-y-6"
        >
          {/* REFINED: Advanced Smurf Probability Visualization */}
          <div className="glass-panel p-6 rounded-xl flex flex-col relative overflow-hidden group">
            {showSkeletons && (
              <div className="absolute inset-0 bg-background-dark/80 backdrop-blur-sm z-20 p-6 space-y-3">
                <div className="h-4 w-40 bg-white/10 rounded animate-pulse"></div>
                <div className="h-48 w-48 mx-auto rounded-full bg-white/10 animate-pulse"></div>
                <div className="h-3 w-full bg-white/10 rounded animate-pulse"></div>
                <div className="h-3 w-5/6 bg-white/10 rounded animate-pulse"></div>
              </div>
            )}
            {/* Ambient Background Elements */}
            <div className={`absolute top-0 right-0 p-4 transition-opacity duration-1000 ${pulse ? 'opacity-10' : 'opacity-30'}`}>
              <span className="material-symbols-outlined text-primary text-6xl select-none">radar</span>
            </div>
            <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent pointer-events-none"></div>

            <header className="flex justify-between items-start mb-6 relative z-10">
              <div>
                <h3 className="text-slate-200 text-sm font-black uppercase tracking-widest">Smurf Confidence</h3>
                <p className="text-[10px] text-primary/60 font-bold uppercase">Algorithm: V3.2-NEURAL</p>
              </div>
              <div className="size-2 bg-red-500 rounded-full animate-ping"></div>
            </header>

            <div className="relative size-56 self-center flex items-center justify-center mb-8">
              {/* Background Glow */}
              <div className="absolute inset-0 bg-primary/10 rounded-full blur-[40px] opacity-50 group-hover:opacity-80 transition-opacity"></div>

              {/* Advanced Multi-layered Arc Meter */}
              <svg className="size-full -rotate-180 relative z-10" viewBox="0 0 100 100">
                {/* Track */}
                <path d="M 20 80 A 40 40 0 1 1 80 80" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="6" strokeLinecap="round" />
                {/* Shimmer Effect */}
                <path
                  d="M 20 80 A 40 40 0 1 1 80 80"
                  fill="none"
                  stroke="rgba(200, 170, 111, 0.1)"
                  strokeWidth="6"
                  strokeDasharray="188"
                  strokeDashoffset="28" // 85%
                  strokeLinecap="round"
                />
                {/* Main Progress Arc */}
                <path
                  d="M 20 80 A 40 40 0 1 1 80 80"
                  fill="none"
                  stroke="url(#arcGradient)"
                  strokeWidth="8"
                  strokeDasharray="188"
                  strokeDashoffset="28" // 85%
                  strokeLinecap="round"
                  className="transition-all duration-[2000ms] ease-out drop-shadow-[0_0_12px_#c8aa6f]"
                />
                <defs>
                  <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#c8aa6f" />
                    <stop offset="100%" stopColor="#00f0ff" />
                  </linearGradient>
                </defs>
              </svg>

              <div className="absolute flex flex-col items-center mt-4">
                <span className="text-5xl font-black text-white leading-none">{smurfConfidence}<span className="text-primary text-2xl">%</span></span>
                <span className="text-[10px] text-white/40 font-black uppercase tracking-[0.2em] mt-2">{smurfMatchLabel}</span>
              </div>
            </div>

            {/* CONTEXTUAL FACTORS: Detail-rich list */}
            <div className="space-y-4 relative z-10">
              <div className="flex items-center justify-between mb-2">
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest border-b border-white/5 pb-2 flex-1">Neural Detection Insight</p>
                <span className="material-symbols-outlined text-slate-500 text-xs ml-2 cursor-help">info</span>
              </div>

              {detectionFactors.map((f, i) => (
                <div key={i} className="flex flex-col gap-1 group/factor cursor-help">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={`material-symbols-outlined text-sm ${f.color}`}>{f.icon}</span>
                      <span className="text-xs text-slate-300 font-bold group-hover/factor:text-white transition-colors">{f.label}</span>
                    </div>
                    <span className={`text-[10px] font-black uppercase bg-white/5 px-1.5 py-0.5 rounded ${f.color}`}>{f.value}</span>
                  </div>
                  <p className="text-[9px] text-slate-500 font-medium ml-6 leading-tight group-hover/factor:text-slate-400 transition-colors">
                    {f.context}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-8 p-4 rounded-lg bg-primary/10 border border-primary/20 relative group-hover:bg-primary/20 transition-all">
              <div className="flex gap-3">
                <span className="material-symbols-outlined text-primary text-xl">psychology</span>
                <div>
                  <p className="text-[11px] font-bold text-primary uppercase mb-1">AI Analyst Verdict</p>
                  <p className="text-[10px] text-white/80 leading-relaxed">
                    {verdictText}
                    <span className="block mt-2 text-primary/60 underline decoration-dotted underline-offset-4 cursor-pointer">Export full behavioral report</span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-xl">
            <div className="flex justify-between items-center mb-4">
              <p className="text-slate-400 text-xs font-bold uppercase tracking-[0.2em]">Progression Analysis</p>
              <span className="text-hextech-blue text-xs font-bold">{progressionGain}</span>
            </div>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-3">Updated {lastUpdatedAt}</p>
            <div className="h-40 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={progressionData}>
                  <defs>
                    <linearGradient id="colorGain" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#c8aa6f" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#c8aa6f" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="game" hide />
                  <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(200, 170, 111, 0.2)', strokeWidth: 1 }} />
                  <Area
                    type="monotone"
                    dataKey="gain"
                    stroke="#c8aa6f"
                    fill="url(#colorGain)"
                    strokeWidth={3}
                    activeDot={{ r: 6, fill: '#c8aa6f', stroke: '#0a0e13', strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
              <div className="flex justify-between px-2 text-[10px] font-bold text-slate-500 mt-2">
                <span>START</span>
                <span>RECENT SESSIONS</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Match History */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.6 }}
          className="lg:col-span-2 space-y-4"
        >
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="material-symbols-outlined text-primary">history</span> Match History
            </h2>
            <div className="flex gap-2">
              <span className="px-3 py-1 bg-primary text-background-dark text-[10px] font-bold rounded uppercase cursor-pointer">All</span>
              <span className="px-3 py-1 bg-white/5 text-slate-400 text-[10px] font-bold rounded uppercase cursor-pointer hover:text-primary transition-colors">Ranked</span>
            </div>
          </div>

          {summonerProfile && summonerProfile.recent_matches.length === 0 ? (
            <div className="glass-panel p-6 rounded-lg border border-white/10">
              <p className="text-white/70 text-sm font-medium">No ranked matches available for this player in the selected window.</p>
            </div>
          ) : (
            <motion.div
              variants={matchListVariants}
              initial="hidden"
              animate="show"
              className="space-y-3"
            >
            {(summonerProfile?.recent_matches || [
              { res: 'Victory', color: 'win-accent', bg: 'bg-win', champ: 'Lee Sin', kda: '12 / 2 / 8', score: '10.00', rank: 'MVP', scoreVal: 9.8 },
              { res: 'Defeat', color: 'red-500', bg: 'bg-loss', champ: 'Ahri', kda: '4 / 7 / 12', score: '2.28', rank: 'ACE', scoreVal: 6.2 },
              { res: 'Victory', color: 'win-accent', bg: 'bg-win', champ: 'Yasuo', kda: '9 / 1 / 4', score: '13.00', rank: 'S+', scoreVal: 9.9 },
            ] as any[]).map((match: any, i: number) => {
              // Check if this is real match data from API or fallback mock data
              const isRealMatch = match.match_id !== undefined;

              if (isRealMatch) {
                const m = match as MatchSummary;
                const kda = m.deaths > 0 ? ((m.kills + m.assists) / m.deaths).toFixed(2) : (m.kills + m.assists).toFixed(2);
                const gameDuration = Math.floor(m.game_duration / 60);
                const gameMinutes = m.game_duration % 60;

                return (
                  <TiltMotionCard
                    variants={matchItemVariants}
                    whileHover={{ scale: 1.02 }}
                    transition={{ type: 'spring', stiffness: 280, damping: 20 }}
                    key={m.match_id}
                    className={`${m.win ? 'bg-win' : 'bg-loss'} border-l-4 border-${m.win ? 'hextech-blue' : 'red-500'} rounded-lg overflow-hidden flex items-center p-4 cursor-pointer group/item shadow-lg hover:shadow-primary/20 hover:border-primary/50 perspective-1000`}
                  >
                    <div className="flex flex-col items-center w-24 border-r border-slate-700/50 pr-4">
                      <span className={`text-xs font-bold ${m.win ? 'text-hextech-blue' : 'text-red-500'} uppercase tracking-wider`}>
                        {m.win ? 'Victory' : 'Defeat'}
                      </span>
                      <span className="text-[10px] text-slate-400 font-medium">{m.role || 'Ranked'}</span>
                      <span className="text-[10px] text-slate-500 mt-2">{gameDuration}:{gameMinutes.toString().padStart(2, '0')}</span>
                    </div>
                    <div className="flex items-center gap-4 px-4 flex-1">
                      <div className="relative size-14">
                        <div className="size-full rounded-lg border border-primary/40 bg-background-dark flex items-center justify-center overflow-hidden">
                          <img
                            src={`/img/champion/${m.champion.replace(/\s+/g, '')}_0.jpg`}
                            alt={m.champion}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                              e.currentTarget.parentElement!.innerHTML = `<span class="text-primary text-[10px] font-bold text-center">${m.champion}</span>`;
                            }}
                          />
                        </div>
                      </div>
                      <div className="flex flex-col items-center flex-1">
                        <p className="text-xl font-black text-slate-100 tabular-nums group-hover/item:text-primary transition-colors">
                          {m.kills} / {m.deaths} / {m.assists}
                        </p>
                        <p className="text-xs text-slate-400 font-bold">{kda} <span className="text-primary">KDA</span></p>
                      </div>
                    </div>

                    {/* Predict Outcome Section */}
                    <div className="flex flex-col items-center gap-2 px-4 border-l border-slate-700/50 min-w-[120px]">
                      {matchPredictions[m.match_id] !== undefined ? (
                        <div className="flex flex-col items-center">
                          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">Win Prob</span>
                          <div className="size-12 rounded-full border-2 border-primary flex items-center justify-center bg-background-dark shadow-[0_0_15px_rgba(200,170,111,0.3)]">
                            <span className={`${matchPredictions[m.match_id] >= 0.5 ? 'text-green-400' : 'text-red-400'} font-black text-sm`}>
                              {Math.round(matchPredictions[m.match_id] * 100)}%
                            </span>
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={(e) => { e.stopPropagation(); handlePredictMatch(m, m.match_id); }}
                          disabled={predictingMatches[m.match_id]}
                          className="px-3 py-2 bg-primary/10 border border-primary/30 text-primary hover:bg-primary hover:text-background-dark rounded text-[10px] font-bold uppercase tracking-wider transition-all disabled:opacity-50 flex items-center gap-1"
                        >
                          {predictingMatches[m.match_id] ? (
                            <><span className="material-symbols-outlined text-[10px] animate-spin">sync</span> Calc...</>
                          ) : (
                            <><span className="material-symbols-outlined text-[10px]">auto_awesome</span> Predict</>
                          )}
                        </button>
                      )}
                    </div>
                  </TiltMotionCard>
                );
              } else {
                // Render mock data as before
                return (
                  <TiltMotionCard
                    variants={matchItemVariants}
                    whileHover={{ scale: 1.02 }}
                    transition={{ type: 'spring', stiffness: 280, damping: 20 }}
                    key={i}
                    className={`${match.bg} border-l-4 border-${match.color === 'win-accent' ? 'hextech-blue' : 'red-500'} rounded-lg overflow-hidden flex items-center p-4 cursor-pointer group/item shadow-lg hover:shadow-primary/20 hover:border-primary/50 perspective-1000`}
                  >
                    <div className="flex flex-col items-center w-24 border-r border-slate-700/50 pr-4">
                      <span className={`text-xs font-bold ${match.color === 'win-accent' ? 'text-hextech-blue' : 'text-red-500'} uppercase tracking-wider`}>{match.res}</span>
                      <span className="text-[10px] text-slate-400 font-medium">Ranked Solo</span>
                      <span className="text-[10px] text-slate-500 mt-2">24:12</span>
                    </div>
                    <div className="flex items-center gap-4 px-4 flex-1">
                      <div className="relative size-14">
                        <div className="size-full rounded-lg border border-primary/40 bg-background-dark flex items-center justify-center overflow-hidden">
                          <img
                            src={`/img/champion/${match.champ.replace(/\s+/g, '')}_0.jpg`}
                            alt={match.champ}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                              e.currentTarget.parentElement!.innerHTML = `<span class="text-primary text-[10px] font-bold text-center">${match.champ}</span>`;
                            }}
                          />
                        </div>
                      </div>
                      <div className="flex flex-col items-center flex-1">
                        <p className="text-xl font-black text-slate-100 tabular-nums group-hover/item:text-primary transition-colors">{match.kda}</p>
                        <p className="text-xs text-slate-400 font-bold">{match.score} <span className="text-primary">KDA</span></p>
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        <div className="flex gap-1">
                          {[1, 2, 3, 4, 5].map(x => <div key={x} className="size-6 bg-slate-800 border border-slate-700 rounded-sm"></div>)}
                        </div>
                        <div className="text-[10px] text-slate-500 font-medium">CS 245 (9.2)</div>
                      </div>
                    </div>

                    {/* Predict Outcome Section (Mock Card) */}
                    <div className="flex flex-col items-center gap-2 px-4 border-l border-slate-700/50 min-w-[120px]">
                      {matchPredictions[`mock-${i}`] !== undefined ? (
                        <div className="flex flex-col items-center">
                          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">Win Prob</span>
                          <div className="size-12 rounded-full border-2 border-primary flex items-center justify-center bg-background-dark shadow-[0_0_15px_rgba(200,170,111,0.3)]">
                            <span className={`${matchPredictions[`mock-${i}`] >= 0.5 ? 'text-green-400' : 'text-red-400'} font-black text-sm`}>
                              {Math.round(matchPredictions[`mock-${i}`] * 100)}%
                            </span>
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={(e) => { e.stopPropagation(); handlePredictMatch(match, `mock-${i}`); }}
                          disabled={predictingMatches[`mock-${i}`]}
                          className="px-3 py-2 bg-primary/10 border border-primary/30 text-primary hover:bg-primary hover:text-background-dark rounded text-[10px] font-bold uppercase tracking-wider transition-all disabled:opacity-50 flex items-center gap-1"
                        >
                          {predictingMatches[`mock-${i}`] ? (
                            <><span className="material-symbols-outlined text-[10px] animate-spin">sync</span> Calc...</>
                          ) : (
                            <><span className="material-symbols-outlined text-[10px]">auto_awesome</span> Predict</>
                          )}
                        </button>
                      )}
                    </div>
                  </TiltMotionCard>
                );
              }
            })}
            </motion.div>
          )}
        </motion.div>
      </div>

      <motion.section
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-50px" }}
        transition={{ duration: 0.6 }}
        className="glass-panel p-6 rounded-xl border border-primary/20"
      >
        <header className="flex items-center justify-between mb-5">
          <h2 className="text-white text-lg font-black flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">psychology_alt</span>
            Why This Prediction
          </h2>
          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Explainability</span>
        </header>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {whyReasons.map((reason, index) => (
            <TiltMotionCard key={index} tiltStrength={6} className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-primary/40 transition-colors">
              <div className="flex items-center justify-between mb-2">
                <p className="text-[11px] uppercase tracking-widest text-slate-400 font-bold">{reason.title}</p>
                <span className={`material-symbols-outlined text-sm ${reason.color}`}>{reason.icon}</span>
              </div>
              <p className={`text-xl font-black mb-1 ${reason.color}`}>{reason.value}</p>
              <p className="text-xs text-slate-400 leading-relaxed">{reason.note}</p>
            </TiltMotionCard>
          ))}
        </div>
      </motion.section>

      {/* Strategy Insights Section */}
      <motion.section
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="mt-12 pt-8 border-t border-primary/20"
      >
        <header className="flex items-center justify-between mb-8">
          <h2 className="text-white text-xl font-black flex items-center gap-3">
            <span className="material-symbols-outlined text-primary text-3xl">lightbulb</span>
            AI STRATEGY INSIGHTS
          </h2>
          <span className="text-[10px] text-primary bg-primary/10 border border-primary/20 px-3 py-1 rounded-full font-bold uppercase tracking-widest">v14.2 Optimized</span>
        </header>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { title: 'Win Condition', desc: 'Focus on early dragons. You have an 82% win rate when taking the first 2 drakes.', icon: 'trophy' },
            { title: 'Weakness Detected', desc: 'Vision score drops significantly between 15-20 minutes. Consider buying more Control Wards.', icon: 'visibility_off' },
            { title: 'Strongest Synergy', desc: 'You perform best when paired with aggressive junglers like Nidalee or Jarvan IV.', icon: 'handshake' },
          ].map((insight, i) => (
            <TiltMotionCard key={i} tiltStrength={7} className="p-6 rounded-lg bg-white/5 border border-primary/10 hover:border-primary/40 hover:bg-primary/5 transition-all cursor-default group/insight">
              <div className="flex items-center gap-3 mb-3">
                <span className="material-symbols-outlined text-primary group-hover/insight:scale-110 transition-transform">{insight.icon}</span>
                <span className="text-primary font-black text-xs uppercase tracking-widest">{insight.title}</span>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed">{insight.desc}</p>
            </TiltMotionCard>
          ))}
        </div>
      </motion.section>

      <footer className="mt-12 py-12 border-t border-primary/10 text-center flex flex-col items-center gap-4">
        <div className="flex gap-4 opacity-30 hover:opacity-100 transition-opacity">
          <span className="material-symbols-outlined text-white cursor-pointer hover:text-primary">share</span>
          <span className="material-symbols-outlined text-white cursor-pointer hover:text-primary">download</span>
          <span className="material-symbols-outlined text-white cursor-pointer hover:text-primary">bookmark</span>
        </div>
        <p className="text-slate-500 text-[10px] uppercase font-bold tracking-[0.3em]">Hextech Insights &bull; Neural Analytics System &bull; 2024</p>
        <p className="text-slate-600 text-[9px] max-w-2xl italic">Hextech Insights isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends.</p>
      </footer>
    </div>
  );
};

export default Profile;
