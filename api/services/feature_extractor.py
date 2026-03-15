"""Feature extraction service to convert Riot API match data into ML model features."""
import numpy as np
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
from datetime import datetime


class FeatureExtractor:
    """Extract ML features from Riot API match data."""
    
    @staticmethod
    def extract_participant_stats(match_data: Dict[str, Any], puuid: str) -> Optional[Dict[str, Any]]:
        """Extract stats for a specific participant from match data.
        
        Args:
            match_data: Match data from Riot API
            puuid: Player PUUID to find
            
        Returns:
            Participant stats dict or None if not found
        """
        try:
            participants = match_data['info']['participants']
            for participant in participants:
                if participant['puuid'] == puuid:
                    return participant
            return None
        except KeyError:
            return None
    
    @staticmethod
    def calculate_rank_features(matches: List[Dict[str, Any]], puuid: str) -> Dict[str, float]:
        """Calculate rank classification features from match history.
        
        Args:
            matches: List of match data dicts from Riot API
            puuid: Player PUUID
            
        Returns:
            Dict of features for rank classification model
        """
        if not matches:
            raise ValueError("No matches provided")
        
        stats_list = []
        wins = 0
        total_games = len(matches)
        champion_counts = Counter()
        role_counts = Counter()
        
        for match in matches:
            participant = FeatureExtractor.extract_participant_stats(match, puuid)
            if not participant:
                continue
            
            # Extract basic stats
            kills = participant.get('kills', 0)
            deaths = max(participant.get('deaths', 1), 1)  # Avoid division by zero
            assists = participant.get('assists', 0)
            kda = (kills + assists) / deaths
            
            game_duration = match['info'].get('gameDuration', 1) / 60  # Convert to minutes
            
            # Per-minute stats
            cs = participant.get('totalMinionsKilled', 0) + participant.get('neutralMinionsKilled', 0)
            cs_per_min = cs / game_duration if game_duration > 0 else 0
            
            gold = participant.get('goldEarned', 0)
            gold_per_min = gold / game_duration if game_duration > 0 else 0
            
            damage = participant.get('totalDamageDealtToChampions', 0)
            damage_per_min = damage / game_duration if game_duration > 0 else 0
            
            vision = participant.get('visionScore', 0)
            vision_per_min = vision / game_duration if game_duration > 0 else 0
            
            # Team stats
            team_id = participant.get('teamId', 100)
            teams = match['info'].get('teams', [])
            team_data = next((t for t in teams if t['teamId'] == team_id), {})
            objectives = team_data.get('objectives', {})
            
            first_blood = objectives.get('champion', {}).get('first', False)
            first_tower = objectives.get('tower', {}).get('first', False)
            first_dragon = objectives.get('dragon', {}).get('first', False)
            
            # Calculate team totals for participation
            team_participants = [p for p in match['info']['participants'] if p['teamId'] == team_id]
            team_kills = sum(p.get('kills', 0) for p in team_participants)
            kill_participation = (kills + assists) / team_kills if team_kills > 0 else 0
            
            # Win/loss
            won = participant.get('win', False)
            if won:
                wins += 1
            
            # Champion and role
            champion_counts[participant.get('championName', 'Unknown')] += 1
            role_counts[participant.get('teamPosition', 'UTILITY')] += 1
            
            # Challenges (new fields)
            challenges = participant.get('challenges', {})
            skillshot_accuracy = challenges.get('skillshotsDodged', 0) / max(challenges.get('skillshotsHit', 1) + challenges.get('skillshotsDodged', 1), 1)
            control_wards = participant.get('visionWardsBoughtInGame', 0)
            ward_takedowns = participant.get('wardsKilled', 0)
            solo_kills = challenges.get('soloKills', 0)
            
            # Store stats
            stats_list.append({
                'kda': kda,
                'cs_per_min': cs_per_min,
                'gold_per_min': gold_per_min,
                'damage_per_min': damage_per_min,
                'vision': vision,
                'vision_per_min': vision_per_min,
                'kill_participation': kill_participation,
                'first_blood': first_blood,
                'first_tower': first_tower,
                'first_dragon': first_dragon,
                'player_first_blood': participant.get('firstBloodKill', False),
                'won': won,
                'gold': gold,
                'damage': damage,
                'skillshot_accuracy': skillshot_accuracy,
                'control_wards': control_wards,
                'ward_takedowns': ward_takedowns,
                'solo_kills': solo_kills,
                'death_time': participant.get('totalTimeSpentDead', 0),
                'game_duration': game_duration * 60,  # Back to seconds
                'early_cs': participant.get('totalMinionsKilled', 0),  # Approximation
                'turret_plates': participant.get('turretPlatesTaken', 0),
                'kills_near_turret': 0,  # Not available in API
                'epic_monster_steals': challenges.get('baronTakedowns', 0),
                'objectives_stolen': challenges.get('dragonTakedowns', 0),
                'bounty_gold': participant.get('bountyGold', 0),
            })
        
        if not stats_list:
            raise ValueError("Could not extract stats from any match")
        
        # Calculate aggregated features
        avg_kda = np.mean([s['kda'] for s in stats_list])
        avg_cs_per_min = np.mean([s['cs_per_min'] for s in stats_list])
        avg_gold_per_min = np.mean([s['gold_per_min'] for s in stats_list])
        avg_damage_per_min = np.mean([s['damage_per_min'] for s in stats_list])
        avg_vision = np.mean([s['vision'] for s in stats_list])
        avg_vision_per_min = np.mean([s['vision_per_min'] for s in stats_list])
        avg_kill_participation = np.mean([s['kill_participation'] for s in stats_list])
        
        team_first_blood_rate = np.mean([s['first_blood'] for s in stats_list])
        team_first_tower_rate = np.mean([s['first_tower'] for s in stats_list])
        team_first_dragon_rate = np.mean([s['first_dragon'] for s in stats_list])
        player_first_blood_rate = np.mean([s['player_first_blood'] for s in stats_list])
        
        win_rate = wins / total_games
        
        # Recent form
        recent_30_wins = sum(1 for s in stats_list[-30:] if s['won'])
        recent_form_30 = recent_30_wins / min(len(stats_list), 30)
        
        recent_10_wins = sum(1 for s in stats_list[-10:] if s['won'])
        recent_form_10 = recent_10_wins / min(len(stats_list), 10)
        
        # KDA consistency (inverse of coefficient of variation)
        kda_values = [s['kda'] for s in stats_list]
        kda_std = np.std(kda_values)
        kda_mean = np.mean(kda_values)
        kda_consistency = 1 / (1 + (kda_std / kda_mean if kda_mean > 0 else 1))
        
        # Champion pool
        champ_pool_size = len(champion_counts)
        champion_pool = champ_pool_size
        champion_pool_size_feature = float(champ_pool_size)
        
        # Role focus
        most_common_role_count = role_counts.most_common(1)[0][1] if role_counts else 0
        role_focus_pct = most_common_role_count / total_games
        role_consistency = role_focus_pct
        
        # Gold and damage standard deviations
        gold_std = np.std([s['gold'] for s in stats_list])
        damage_std = np.std([s['damage'] for s in stats_list])
        
        # Additional features from challenges
        avg_skillshot_accuracy = np.mean([s['skillshot_accuracy'] for s in stats_list])
        avg_control_wards = np.mean([s['control_wards'] for s in stats_list])
        avg_ward_takedowns = np.mean([s['ward_takedowns'] for s in stats_list])
        avg_solo_kills = np.mean([s['solo_kills'] for s in stats_list])
        
        # Death time ratio
        total_death_time = sum(s['death_time'] for s in stats_list)
        total_game_time = sum(s['game_duration'] for s in stats_list)
        death_time_ratio = total_death_time / total_game_time if total_game_time > 0 else 0
        
        # Early CS (approximation - using total CS as proxy)
        avg_early_cs = np.mean([s['early_cs'] for s in stats_list])
        
        # Objective features
        avg_turret_plates = np.mean([s['turret_plates'] for s in stats_list])
        avg_kills_near_turret = np.mean([s['kills_near_turret'] for s in stats_list])
        avg_epic_monster_steals = np.mean([s['epic_monster_steals'] for s in stats_list])
        avg_objectives_stolen = np.mean([s['objectives_stolen'] for s in stats_list])
        avg_bounty_gold = np.mean([s['bounty_gold'] for s in stats_list])
        
        return {
            'avg_kda': avg_kda,
            'avg_cs_per_min': avg_cs_per_min,
            'avg_gold_per_min': avg_gold_per_min,
            'avg_damage_per_min': avg_damage_per_min,
            'avg_vision': avg_vision,
            'avg_vision_per_min': avg_vision_per_min,
            'avg_kill_participation': avg_kill_participation,
            'team_first_blood_rate': team_first_blood_rate,
            'team_first_tower_rate': team_first_tower_rate,
            'team_first_dragon_rate': team_first_dragon_rate,
            'player_first_blood_rate': player_first_blood_rate,
            'win_rate': win_rate,
            'champ_pool_size': champ_pool_size,
            'recent_form_30': recent_form_30,
            'recent_form_10': recent_form_10,
            'kda_consistency': kda_consistency,
            'champion_pool': champion_pool,
            'role_focus_pct': role_focus_pct,
            'gold_std': gold_std,
            'damage_std': damage_std,
            'goldPerMinute': avg_gold_per_min,
            'damagePerMinute': avg_damage_per_min,
            'visionScorePerMinute': avg_vision_per_min,
            'skillshotAccuracy': avg_skillshot_accuracy,
            'killParticipation': avg_kill_participation,
            'controlWardsPlaced': avg_control_wards,
            'wardTakedowns': avg_ward_takedowns,
            'soloKills': avg_solo_kills,
            'deathTimeRatio': death_time_ratio,
            'earlyCS': avg_early_cs,
            'turretPlates': avg_turret_plates,
            'killsNearTurret': avg_kills_near_turret,
            'epicMonsterSteals': avg_epic_monster_steals,
            'objectivesStolen': avg_objectives_stolen,
            'bountyGold': avg_bounty_gold,
            'champion_pool_size': champion_pool_size_feature,
            'role_consistency': role_consistency,
            'total_games': float(total_games),
            'matches_analyzed': float(len(stats_list)),
            'wins_in_matches': float(wins),
        }
    
    @staticmethod
    def calculate_smurf_features(matches: List[Dict[str, Any]], puuid: str) -> Dict[str, float]:
        """Calculate smurf detection features from match history.
        
        Args:
            matches: List of match data dicts from Riot API
            puuid: Player PUUID
            
        Returns:
            Dict of features for smurf detection model
        """
        if not matches:
            raise ValueError("No matches provided")
        
        stats_list = []
        champion_counts = Counter()
        
        for match in matches:
            participant = FeatureExtractor.extract_participant_stats(match, puuid)
            if not participant:
                continue
            
            kills = participant.get('kills', 0)
            deaths = max(participant.get('deaths', 1), 1)
            assists = participant.get('assists', 0)
            kda = (kills + assists) / deaths
            
            game_duration = match['info'].get('gameDuration', 1) / 60
            
            gold = participant.get('goldEarned', 0)
            gold_per_min = gold / game_duration if game_duration > 0 else 0
            
            damage = participant.get('totalDamageDealtToChampions', 0)
            damage_per_min = damage / game_duration if game_duration > 0 else 0
            
            vision = participant.get('visionScore', 0)
            vision_per_min = vision / game_duration if game_duration > 0 else 0
            
            team_id = participant.get('teamId', 100)
            team_participants = [p for p in match['info']['participants'] if p['teamId'] == team_id]
            team_kills = sum(p.get('kills', 0) for p in team_participants)
            team_gold = sum(p.get('goldEarned', 0) for p in team_participants)
            team_damage = sum(p.get('totalDamageDealtToChampions', 0) for p in team_participants)
            
            kill_participation = (kills + assists) / team_kills if team_kills > 0 else 0
            gold_share = gold / team_gold if team_gold > 0 else 0
            dmg_share = damage / team_damage if team_damage > 0 else 0
            
            teams = match['info'].get('teams', [])
            team_data = next((t for t in teams if t['teamId'] == team_id), {})
            objectives = team_data.get('objectives', {})
            
            won = participant.get('win', False)
            champion_counts[participant.get('championName', 'Unknown')] += 1
            
            stats_list.append({
                'kda': kda,
                'gold_per_min': gold_per_min,
                'damage_per_min': damage_per_min,
                'vision_per_min': vision_per_min,
                'kill_participation': kill_participation,
                'gold_share': gold_share,
                'dmg_share': dmg_share,
                'game_time': game_duration,
                'first_blood': objectives.get('champion', {}).get('first', False),
                'first_tower': objectives.get('tower', {}).get('first', False),
                'first_dragon': objectives.get('dragon', {}).get('first', False),
                'player_first_blood': participant.get('firstBloodKill', False),
                'won': won,
            })
        
        if not stats_list:
            raise ValueError("Could not extract stats from any match")
        
        # Calculate z-scores
        kda_values = [s['kda'] for s in stats_list]
        kda_mean = np.mean(kda_values)
        kda_std = np.std(kda_values)
        kda_zscore = (kda_values[-1] - kda_mean) / kda_std if kda_std > 0 else 0
        
        winrate = sum(1 for s in stats_list if s['won']) / len(stats_list)
        winrate_zscore = (winrate - 0.5) / 0.1  # Normalized against expected 50% winrate
        
        # Average shares
        avg_dmg_share = np.mean([s['dmg_share'] for s in stats_list])
        avg_gold_share = np.mean([s['gold_share'] for s in stats_list])
        avg_game_time = np.mean([s['game_time'] for s in stats_list])
        
        # Champion mastery entropy
        total_games = len(stats_list)
        probabilities = [count / total_games for count in champion_counts.values()]
        champ_mastery_entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        
        # Average stats
        avg_kill_participation = np.mean([s['kill_participation'] for s in stats_list])
        avg_gold_per_min = np.mean([s['gold_per_min'] for s in stats_list])
        avg_damage_per_min = np.mean([s['damage_per_min'] for s in stats_list])
        avg_vision_per_min = np.mean([s['vision_per_min'] for s in stats_list])
        
        team_first_blood_rate = np.mean([s['first_blood'] for s in stats_list])
        team_first_tower_rate = np.mean([s['first_tower'] for s in stats_list])
        team_first_dragon_rate = np.mean([s['first_dragon'] for s in stats_list])
        player_first_blood_rate = np.mean([s['player_first_blood'] for s in stats_list])
        
        # Win/loss streaks
        current_win_streak = 0
        current_loss_streak = 0
        longest_win_streak = 0
        longest_loss_streak = 0
        temp_win_streak = 0
        temp_loss_streak = 0
        
        for s in reversed(stats_list):
            if s['won']:
                if current_win_streak == 0 and current_loss_streak == 0:
                    current_win_streak = 1
                elif current_win_streak > 0:
                    current_win_streak += 1
                else:
                    break
            else:
                if current_loss_streak == 0 and current_win_streak == 0:
                    current_loss_streak = 1
                elif current_loss_streak > 0:
                    current_loss_streak += 1
                else:
                    break
        
        for s in stats_list[-20:]:
            if s['won']:
                temp_win_streak += 1
                temp_loss_streak = 0
                longest_win_streak = max(longest_win_streak, temp_win_streak)
            else:
                temp_loss_streak += 1
                temp_win_streak = 0
                longest_loss_streak = max(longest_loss_streak, temp_loss_streak)
        
        # Recent winrates
        recent_5 = stats_list[-5:]
        recent_10 = stats_list[-10:]
        recent_winrate_5 = sum(1 for s in recent_5 if s['won']) / len(recent_5) if recent_5 else 0
        recent_winrate_10 = sum(1 for s in recent_10 if s['won']) / len(recent_10) if recent_10 else 0
        
        # Winrate trend (last 10 vs previous 10)
        last_10 = stats_list[-10:]
        prev_10 = stats_list[-20:-10] if len(stats_list) >= 20 else stats_list[:-10]
        last_10_wr = sum(1 for s in last_10 if s['won']) / len(last_10) if last_10 else 0
        prev_10_wr = sum(1 for s in prev_10 if s['won']) / len(prev_10) if prev_10 else 0
        winrate_trend_10 = last_10_wr - prev_10_wr
        
        # Recent KDA
        recent_kda_5 = np.mean([s['kda'] for s in recent_5]) if recent_5 else 0
        recent_kda_10 = np.mean([s['kda'] for s in recent_10]) if recent_10 else 0
        
        # KDA trend
        last_10_kda = np.mean([s['kda'] for s in last_10]) if last_10 else 0
        prev_10_kda = np.mean([s['kda'] for s in prev_10]) if prev_10 else 0
        kda_trend_10 = last_10_kda - prev_10_kda
        
        # KDA volatility
        kda_volatility_10 = np.std([s['kda'] for s in recent_10]) if recent_10 else 0
        
        return {
            'winrate_zscore': winrate_zscore,
            'kda_zscore': kda_zscore,
            'dmg_share': avg_dmg_share,
            'gold_share': avg_gold_share,
            'avg_game_time': avg_game_time,
            'champ_mastery_entropy': champ_mastery_entropy,
            'avg_kill_participation': avg_kill_participation,
            'avg_gold_per_min': avg_gold_per_min,
            'avg_damage_per_min': avg_damage_per_min,
            'avg_vision_per_min': avg_vision_per_min,
            'team_first_blood_rate': team_first_blood_rate,
            'team_first_tower_rate': team_first_tower_rate,
            'team_first_dragon_rate': team_first_dragon_rate,
            'player_first_blood_rate': player_first_blood_rate,
            'current_win_streak': float(current_win_streak),
            'current_loss_streak': float(current_loss_streak),
            'longest_win_streak_20': float(longest_win_streak),
            'longest_loss_streak_20': float(longest_loss_streak),
            'recent_winrate_5': recent_winrate_5,
            'recent_winrate_10': recent_winrate_10,
            'winrate_trend_10': winrate_trend_10,
            'recent_kda_5': recent_kda_5,
            'recent_kda_10': recent_kda_10,
            'kda_trend_10': kda_trend_10,
            'kda_volatility_10': kda_volatility_10,
        }
