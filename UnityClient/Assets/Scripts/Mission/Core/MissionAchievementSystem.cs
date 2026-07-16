using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionAchievementSystem
    {
        private readonly MissionConfig _config;
        private readonly Dictionary<string, AchievementDefinition> _achievements;
        private readonly Dictionary<string, int> _progressValues;

        public int TotalAchievements => _achievements.Count;
        public int UnlockedCount
        {
            get
            {
                int count = 0;
                foreach (var a in _achievements.Values) if (a.IsUnlocked) count++;
                return count;
            }
        }

        public event Action<AchievementDefinition> OnAchievementUnlocked;
        public event Action<string, int, int> OnAchievementProgressUpdated;

        public MissionAchievementSystem(MissionConfig config)
        {
            _config = config;
            _achievements = new Dictionary<string, AchievementDefinition>();
            _progressValues = new Dictionary<string, int>();
        }

        public void RegisterAchievement(AchievementDefinition achievement)
        {
            if (achievement == null) return;
            _achievements[achievement.AchievementId] = achievement;
            if (!_progressValues.ContainsKey(achievement.AchievementId))
            {
                _progressValues[achievement.AchievementId] = 0;
            }
        }

        public void OnMissionCompleted(MissionData mission)
        {
            if (mission == null) return;

            foreach (var achievement in _achievements.Values)
            {
                if (achievement.IsUnlocked) continue;

                switch (achievement.TriggerType)
                {
                    case AchievementTriggerType.MissionCompleted:
                        IncrementProgress(achievement.AchievementId, 1);
                        break;

                    case AchievementTriggerType.MissionsCompletedCount:
                        IncrementProgress(achievement.AchievementId, 1);
                        break;

                    case AchievementTriggerType.StoryProgress:
                        if (mission.Type == MissionType.Story && mission.IsRequiredForStory)
                        {
                            IncrementProgress(achievement.AchievementId, 1);
                        }
                        break;

                    case AchievementTriggerType.DailyMissionCompleted:
                        if (mission.Type == MissionType.Daily)
                        {
                            IncrementProgress(achievement.AchievementId, 1);
                        }
                        break;

                    case AchievementTriggerType.SideMissionCompleted:
                        if (mission.Type == MissionType.Side)
                        {
                            IncrementProgress(achievement.AchievementId, 1);
                        }
                        break;
                }
            }
        }

        public void OnCashEarned(int amount)
        {
            foreach (var achievement in _achievements.Values)
            {
                if (achievement.IsUnlocked) continue;

                if (achievement.TriggerType == AchievementTriggerType.TotalCashEarned)
                {
                    IncrementProgress(achievement.AchievementId, amount);
                }
            }
        }

        public void OnDistanceTraveled(float distance)
        {
            foreach (var achievement in _achievements.Values)
            {
                if (achievement.IsUnlocked) continue;

                if (achievement.TriggerType == AchievementTriggerType.TotalDistanceTraveled)
                {
                    IncrementProgress(achievement.AchievementId, Mathf.RoundToInt(distance));
                }
            }
        }

        public void OnTimePlayed(float seconds)
        {
            foreach (var achievement in _achievements.Values)
            {
                if (achievement.IsUnlocked) continue;

                if (achievement.TriggerType == AchievementTriggerType.TimePlayed)
                {
                    IncrementProgress(achievement.AchievementId, Mathf.RoundToInt(seconds));
                }
            }
        }

        public void OnStreakDay(int streakDay)
        {
            foreach (var achievement in _achievements.Values)
            {
                if (achievement.IsUnlocked) continue;

                if (achievement.TriggerType == AchievementTriggerType.StreakDays)
                {
                    IncrementProgress(achievement.AchievementId, 1);
                }
            }
        }

        private void IncrementProgress(string achievementId, int amount)
        {
            if (!_achievements.ContainsKey(achievementId)) return;
            if (_achievements[achievementId].IsUnlocked) return;

            if (!_progressValues.ContainsKey(achievementId))
                _progressValues[achievementId] = 0;

            _progressValues[achievementId] += amount;

            var achievement = _achievements[achievementId];
            OnAchievementProgressUpdated?.Invoke(achievementId, _progressValues[achievementId], achievement.RequiredValue);

            if (_progressValues[achievementId] >= achievement.RequiredValue)
            {
                achievement.IsUnlocked = true;
                OnAchievementUnlocked?.Invoke(achievement);
                Debug.Log($"[MissionAchievement] Unlocked: {achievement.Name}");
            }
        }

        public AchievementDefinition GetAchievement(string achievementId)
        {
            _achievements.TryGetValue(achievementId, out var achievement);
            return achievement;
        }

        public int GetProgress(string achievementId)
        {
            return _progressValues.TryGetValue(achievementId, out var val) ? val : 0;
        }

        public List<AchievementDefinition> GetAllAchievements()
        {
            return new List<AchievementDefinition>(_achievements.Values);
        }

        public List<AchievementDefinition> GetUnlockedAchievements()
        {
            var unlocked = new List<AchievementDefinition>();
            foreach (var a in _achievements.Values)
            {
                if (a.IsUnlocked) unlocked.Add(a);
            }
            return unlocked;
        }

        public List<AchievementDefinition> GetLockedAchievements()
        {
            var locked = new List<AchievementDefinition>();
            foreach (var a in _achievements.Values)
            {
                if (!a.IsUnlocked) locked.Add(a);
            }
            return locked;
        }

        public float GetCompletionRate()
        {
            if (_achievements.Count == 0) return 0f;
            return (float)UnlockedCount / _achievements.Count * 100f;
        }

        public void ClearAll()
        {
            _achievements.Clear();
            _progressValues.Clear();
        }
    }
}
