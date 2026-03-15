import React, { useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Canvas } from '@react-three/fiber';
import { HextechCrystal } from '../components/HextechCrystal';
import TiltMotionCard from '../components/TiltMotionCard';
import {
  predictMatchOutcomeEarly,
  predictProgression,
  predictRank,
  predictSmurf,
} from '../services/api';

type ModelKey = 'match' | 'rank' | 'progression' | 'smurf';

const SAMPLE_PAYLOADS: Record<ModelKey, Record<string, number>> = {
  match: {
    lane_cs_10m: 78,
    jungle_cs_10m: 62,
    total_cs_10m: 140,
    takedowns_early: 6,
    aces_before_15m: 0,
    first_turret_kills: 1,
    first_turret_time_sec: 740,
    earliest_dragon_time_sec: 610,
    earliest_baron_time_sec: 1400,
    early_laning_advantage: 1,
    control_wards_placed: 8,
    avg_kill_participation: 0.58,
    total_gold_earned: 52300,
    total_xp: 61200,
    avg_champion_level: 13.7,
  },
  rank: {
    avg_kda: 3.2,
    avg_cs_per_min: 6.5,
    avg_gold_per_min: 430,
    avg_damage_per_min: 610,
    avg_vision: 25,
    avg_vision_per_min: 1.2,
    avg_kill_participation: 0.58,
    team_first_blood_rate: 0.52,
    team_first_tower_rate: 0.49,
    team_first_dragon_rate: 0.47,
    player_first_blood_rate: 0.11,
    win_rate: 0.54,
    champ_pool_size: 18,
    recent_form_30: 0.53,
    recent_form_10: 0.56,
    kda_consistency: 0.71,
    champion_pool: 20,
    role_focus_pct: 0.74,
    gold_std: 95,
    damage_std: 110,
    goldPerMinute: 430,
    damagePerMinute: 610,
    visionScorePerMinute: 1.2,
    skillshotAccuracy: 0.48,
    killParticipation: 0.58,
    controlWardsPlaced: 3,
    wardTakedowns: 5,
    soloKills: 1,
    deathTimeRatio: 0.82,
    earlyCS: 70,
    turretPlates: 2,
    killsNearTurret: 1,
    epicMonsterSteals: 0,
    objectivesStolen: 0,
    bountyGold: 120,
    champion_pool_size: 18,
    role_consistency: 0.77,
    total_games: 240,
    matches_analyzed: 80,
    wins_in_matches: 44,
  },
  progression: {
    delta_kda: 0.25,
    delta_cs: 0.8,
    delta_gold: 36,
    delta_damage: 48,
    delta_vision: 0.3,
    delta_kill_participation: 0.04,
    delta_team_first_blood: 0.03,
    delta_team_first_tower: 0.02,
    delta_team_first_dragon: 0.01,
    delta_player_first_blood: 0.01,
    win_streak: 3,
    delta_goldPerMinute: 24,
    delta_damagePerMinute: 41,
    delta_visionScorePerMinute: 0.08,
    delta_skillshotAccuracy: 0.03,
    champion_pool_growth: 2,
    total_matches_analyzed: 60,
  },
  smurf: {
    winrate_zscore: 3.2,
    kda_zscore: 2.8,
    dmg_share: 0.42,
    gold_share: 0.38,
    avg_game_time: 28.2,
    champ_mastery_entropy: 0.5,
    avg_kill_participation: 0.78,
    avg_gold_per_min: 520,
    avg_damage_per_min: 680,
    avg_vision_per_min: 1.8,
    team_first_blood_rate: 0.72,
    team_first_tower_rate: 0.68,
    team_first_dragon_rate: 0.65,
    player_first_blood_rate: 0.35,
    current_win_streak: 15,
    current_loss_streak: 0,
    longest_win_streak_20: 17,
    longest_loss_streak_20: 2,
    recent_winrate_5: 0.95,
    recent_winrate_10: 0.88,
    winrate_trend_10: 0.25,
    recent_kda_5: 5.2,
    recent_kda_10: 4.8,
    kda_trend_10: 0.35,
    kda_volatility_10: 0.4,
  },
};

const MODEL_LABELS: Record<ModelKey, string> = {
  match: 'Match Outcome (Early)',
  rank: 'Rank Classification',
  progression: 'Progression Predictor',
  smurf: 'Smurf Detection',
};

const isModelKey = (value: string | null): value is ModelKey => {
  return value === 'match' || value === 'rank' || value === 'progression' || value === 'smurf';
};

const modelGridVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.07,
      delayChildren: 0.05,
    },
  },
};

const modelItemVariants = {
  hidden: { opacity: 0, y: 14 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: 'easeOut' },
  },
};

const Predictions: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialModel = isModelKey(searchParams.get('model')) ? searchParams.get('model') : 'rank';
  const [selectedModel, setSelectedModel] = useState<ModelKey>(initialModel);
  const [payloadText, setPayloadText] = useState<string>(JSON.stringify(SAMPLE_PAYLOADS[initialModel], null, 2));
  const [resultText, setResultText] = useState<string>('');
  const [errorText, setErrorText] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const prettyEndpoint = useMemo(() => {
    if (selectedModel === 'match') return '/match-outcome/predict/early';
    if (selectedModel === 'rank') return '/rank/predict';
    if (selectedModel === 'progression') return '/progression/predict';
    return '/smurf/predict';
  }, [selectedModel]);

  const applySample = (model: ModelKey) => {
    setSelectedModel(model);
    setPayloadText(JSON.stringify(SAMPLE_PAYLOADS[model], null, 2));
    setResultText('');
    setErrorText('');
  };

  const runPrediction = async () => {
    setIsLoading(true);
    setResultText('');
    setErrorText('');

    try {
      const payload = JSON.parse(payloadText) as Record<string, unknown>;

      let result: unknown;
      if (selectedModel === 'match') {
        result = await predictMatchOutcomeEarly(payload);
      } else if (selectedModel === 'rank') {
        result = await predictRank(payload);
      } else if (selectedModel === 'progression') {
        result = await predictProgression(payload);
      } else {
        result = await predictSmurf(payload);
      }

      setResultText(JSON.stringify(result, null, 2));
    } catch (error) {
      if (error instanceof SyntaxError) {
        setErrorText('Invalid JSON in payload editor.');
      } else if (error instanceof Error) {
        setErrorText(error.message);
      } else {
        setErrorText('Unknown error occurred.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-6">
      <motion.header
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      >
        <h1 className="text-white text-4xl font-black tracking-tight">Live Model Predictions</h1>
        <p className="text-white/50 text-sm mt-2">Paste payloads, run predictions, and verify backend responses directly from the frontend.</p>
      </motion.header>

      <motion.section
        initial={{ opacity: 0, scale: 0.97 }}
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
          <p className="text-xs uppercase tracking-[0.3em] text-primary font-bold mb-2">Inference Workbench</p>
          <h2 className="text-3xl font-black text-white tracking-wide">Premium Prediction Console</h2>
        </div>
      </motion.section>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-40px' }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="glass-panel p-6 rounded-xl space-y-4"
      >
        <p className="text-xs uppercase tracking-widest text-white/50 font-bold">Select Model</p>
        <motion.div
          variants={modelGridVariants}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-60px' }}
          className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3"
        >
          {(Object.keys(MODEL_LABELS) as ModelKey[]).map((model) => (
            <motion.div key={model} variants={modelItemVariants}>
              <TiltMotionCard
                tiltStrength={6}
                whileHover={{ scale: 1.015 }}
                transition={{ type: 'spring', stiffness: 260, damping: 22 }}
              >
                <button
                  onClick={() => applySample(model)}
                  className={`w-full px-4 py-3 rounded-lg text-sm font-bold border transition-all ${
                    selectedModel === model
                      ? 'bg-primary text-background-dark border-primary'
                      : 'bg-white/5 text-white border-white/10 hover:border-primary/40'
                  }`}
                >
                  {MODEL_LABELS[model]}
                </button>
              </TiltMotionCard>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <TiltMotionCard
          tiltStrength={4}
          initial={{ opacity: 0, x: -18 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.55, ease: 'easeOut' }}
          className="glass-panel p-6 rounded-xl space-y-4"
        >
          <div className="flex items-center justify-between">
            <p className="text-sm font-bold text-white">Request Payload</p>
            <span className="text-[11px] text-primary font-bold">{prettyEndpoint}</span>
          </div>

          <textarea
            value={payloadText}
            onChange={(event) => setPayloadText(event.target.value)}
            className="w-full min-h-[460px] bg-white/5 border border-white/10 rounded-lg p-4 text-xs text-white font-mono focus:outline-none focus:border-primary/40"
            spellCheck={false}
          />

          <div className="flex gap-3">
            <TiltMotionCard tiltStrength={5} whileHover={{ scale: 1.02 }}>
              <button
                onClick={runPrediction}
                disabled={isLoading}
                className="px-6 py-2.5 bg-primary hover:bg-primary/90 text-background-dark rounded-lg font-bold text-sm disabled:opacity-60"
              >
                {isLoading ? 'Running...' : 'Run Prediction'}
              </button>
            </TiltMotionCard>
            <TiltMotionCard tiltStrength={5} whileHover={{ scale: 1.02 }}>
              <button
                onClick={() => applySample(selectedModel)}
                className="px-6 py-2.5 bg-white/5 hover:bg-white/10 text-white rounded-lg font-bold text-sm border border-white/10"
              >
                Reset Sample
              </button>
            </TiltMotionCard>
          </div>
        </TiltMotionCard>

        <TiltMotionCard
          tiltStrength={4}
          initial={{ opacity: 0, x: 18 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.55, ease: 'easeOut', delay: 0.05 }}
          className="glass-panel p-6 rounded-xl space-y-4"
        >
          <p className="text-sm font-bold text-white">Response</p>

          {errorText ? (
            <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
              {errorText}
            </div>
          ) : null}

          <pre className="min-h-[460px] bg-white/5 border border-white/10 rounded-lg p-4 text-xs text-white font-mono overflow-auto">
            {resultText || 'Run a prediction to see the backend response here.'}
          </pre>
        </TiltMotionCard>
      </div>
    </div>
  );
};

export default Predictions;
