using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionRewardSystem
    {
        private readonly MissionConfig _config;

        public event Action<string, List<MissionRewardEntry>> OnRewardsGranted;
        public event Action<string, int> OnCashGranted;
        public event Action<string, int> OnExperienceGranted;

        public MissionRewardSystem(MissionConfig config)
        {
            _config = config;
        }

        public List<MissionRewardEntry> CalculateRewards(MissionData mission)
        {
            if (mission == null) return new List<MissionRewardEntry>();

            var rewards = new List<MissionRewardEntry>();

            int baseCash = mission.RewardCash;
            int baseExp = mission.RewardExperience;

            float difficultyMultiplier = GetDifficultyMultiplier(mission.Difficulty);

            rewards.Add(new MissionRewardEntry
            {
                Type = RewardType.Cash,
                Amount = Mathf.RoundToInt(baseCash * difficultyMultiplier),
                ItemName = "Cash"
            });

            rewards.Add(new MissionRewardEntry
            {
                Type = RewardType.Experience,
                Amount = Mathf.RoundToInt(baseExp * difficultyMultiplier),
                ItemName = "Experience"
            });

            if (mission.BonusRewards != null)
            {
                foreach (var bonus in mission.BonusRewards)
                {
                    rewards.Add(new MissionRewardEntry
                    {
                        Type = bonus.Type,
                        Amount = bonus.Amount,
                        ItemId = bonus.ItemId,
                        ItemName = bonus.ItemName
                    });
                }
            }

            return rewards;
        }

        public List<MissionRewardEntry> CalculateTimeBonus(MissionData mission)
        {
            if (mission == null || !mission.IsTimed) return new List<MissionRewardEntry>();

            var bonuses = new List<MissionRewardEntry>();
            float timeRemaining = mission.GetTimeRemaining();
            float timePercent = timeRemaining / mission.TimeLimit;

            if (timePercent > 0.5f)
            {
                bonuses.Add(new MissionRewardEntry
                {
                    Type = RewardType.Cash,
                    Amount = Mathf.RoundToInt(mission.RewardCash * 0.5f),
                    ItemName = "Speed Bonus"
                });
            }
            else if (timePercent > 0.25f)
            {
                bonuses.Add(new MissionRewardEntry
                {
                    Type = RewardType.Cash,
                    Amount = Mathf.RoundToInt(mission.RewardCash * 0.25f),
                    ItemName = "Time Bonus"
                });
            }

            return bonuses;
        }

        public List<MissionRewardEntry> CalculateDifficultyBonus(MissionData mission)
        {
            if (mission == null) return new List<MissionRewardEntry>();

            var bonuses = new List<MissionRewardEntry>();

            if (mission.Difficulty >= MissionDifficulty.Hard)
            {
                bonuses.Add(new MissionRewardEntry
                {
                    Type = RewardType.Experience,
                    Amount = Mathf.RoundToInt(mission.RewardExperience * 0.25f),
                    ItemName = "Difficulty Bonus"
                });
            }

            return bonuses;
        }

        public List<MissionRewardEntry> CalculateStreakBonus(int currentStreak)
        {
            var bonuses = new List<MissionRewardEntry>();

            if (currentStreak >= 3)
            {
                int streakBonus = currentStreak * _config.dailyStreakBonusMultiplier;
                bonuses.Add(new MissionRewardEntry
                {
                    Type = RewardType.Cash,
                    Amount = streakBonus,
                    ItemName = $"Streak x{currentStreak} Bonus"
                });
            }

            return bonuses;
        }

        public void GrantRewards(string missionId, List<MissionRewardEntry> rewards)
        {
            int totalCash = 0;
            int totalExp = 0;

            foreach (var reward in rewards)
            {
                switch (reward.Type)
                {
                    case RewardType.Cash:
                        totalCash += reward.Amount;
                        break;
                    case RewardType.Experience:
                        totalExp += reward.Amount;
                        break;
                }
            }

            if (totalCash > 0)
                OnCashGranted?.Invoke(missionId, totalCash);
            if (totalExp > 0)
                OnExperienceGranted?.Invoke(missionId, totalExp);

            OnRewardsGranted?.Invoke(missionId, rewards);
            Debug.Log($"[MissionRewards] Granted {rewards.Count} rewards for mission {missionId}");
        }

        private float GetDifficultyMultiplier(MissionDifficulty difficulty)
        {
            if (_config == null) return 1f;

            switch (difficulty)
            {
                case MissionDifficulty.Easy: return _config.easyRewardMultiplier;
                case MissionDifficulty.Normal: return _config.normalRewardMultiplier;
                case MissionDifficulty.Hard: return _config.hardRewardMultiplier;
                case MissionDifficulty.Expert: return _config.expertRewardMultiplier;
                case MissionDifficulty.Legendary: return _config.legendaryRewardMultiplier;
                default: return 1f;
            }
        }

        public int GetBaseExperience(MissionDifficulty difficulty)
        {
            if (_config == null) return 100;

            switch (difficulty)
            {
                case MissionDifficulty.Easy: return _config.baseExpEasy;
                case MissionDifficulty.Normal: return _config.baseExpNormal;
                case MissionDifficulty.Hard: return _config.baseExpHard;
                case MissionDifficulty.Expert: return _config.baseExpExpert;
                case MissionDifficulty.Legendary: return _config.baseExpLegendary;
                default: return 100;
            }
        }

        public float GetTimeMultiplier(MissionDifficulty difficulty)
        {
            if (_config == null) return 1f;

            switch (difficulty)
            {
                case MissionDifficulty.Easy: return _config.easyTimeMultiplier;
                case MissionDifficulty.Normal: return _config.normalTimeMultiplier;
                case MissionDifficulty.Hard: return _config.hardTimeMultiplier;
                case MissionDifficulty.Expert: return _config.expertTimeMultiplier;
                case MissionDifficulty.Legendary: return _config.legendaryTimeMultiplier;
                default: return 1f;
            }
        }
    }
}
