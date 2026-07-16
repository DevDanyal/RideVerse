using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionDailySystem
    {
        private readonly MissionConfig _config;
        private readonly List<DailyMissionTemplate> _templates;
        private readonly List<MissionData> _currentDailyMissions;
        private int _currentStreak;
        private string _lastResetDate;
        private bool _isInitialized;

        public int StreakCount => _currentStreak;
        public int ActiveMissionsCount => _currentDailyMissions.Count;
        public bool IsInitialized => _isInitialized;
        public IReadOnlyList<MissionData> CurrentDailyMissions => _currentDailyMissions;

        public event Action<List<MissionData>> OnDailyMissionsGenerated;
        public event Action<MissionData> OnDailyMissionCompleted;
        public event Action<int> OnStreakUpdated;
        public event Action OnDailyReset;

        public MissionDailySystem(MissionConfig config)
        {
            _config = config;
            _templates = new List<DailyMissionTemplate>();
            _currentDailyMissions = new List<MissionData>();
        }

        public void Initialize(int savedStreak, string lastResetDate)
        {
            _currentStreak = savedStreak;
            _lastResetDate = lastResetDate;
            _isInitialized = true;

            if (ShouldResetDaily())
            {
                PerformDailyReset();
            }
        }

        public void Update(float deltaTime)
        {
            if (!_isInitialized) return;

            if (ShouldResetDaily())
            {
                PerformDailyReset();
            }
        }

        public void RegisterTemplate(DailyMissionTemplate template)
        {
            if (template == null) return;
            _templates.Add(template);
        }

        public List<MissionData> GenerateDailyMissions()
        {
            _currentDailyMissions.Clear();

            int count = _config != null ? _config.dailyMissionCount : 3;

            if (_templates.Count == 0)
            {
                for (int i = 0; i < count; i++)
                {
                    var mission = CreateRandomDailyMission(i);
                    _currentDailyMissions.Add(mission);
                }
            }
            else
            {
                var available = new List<DailyMissionTemplate>(_templates);
                for (int i = 0; i < count && available.Count > 0; i++)
                {
                    int idx = UnityEngine.Random.Range(0, available.Count);
                    var template = available[idx];
                    available.RemoveAt(idx);

                    var mission = CreateMissionFromTemplate(template);
                    _currentDailyMissions.Add(mission);
                }
            }

            OnDailyMissionsGenerated?.Invoke(_currentDailyMissions);
            Debug.Log($"[MissionDaily] Generated {_currentDailyMissions.Count} daily missions");
            return _currentDailyMissions;
        }

        private MissionData CreateRandomDailyMission(int index)
        {
            string[] names = { "Quick Delivery", "Speed Race", "Patrol Route", "Package Pickup", "City Tour" };
            string[] descriptions = {
                "Deliver a package across the city",
                "Race to the destination before time runs out",
                "Patrol the city streets",
                "Pick up and deliver an important package",
                "Explore the city and visit checkpoints"
            };

            MissionType[] types = { MissionType.Delivery, MissionType.Racing, MissionType.Side, MissionType.Delivery, MissionType.Side };
            MissionDifficulty[] difficulties = { MissionDifficulty.Easy, MissionDifficulty.Normal, MissionDifficulty.Normal, MissionDifficulty.Easy, MissionDifficulty.Hard };

            int idx = index % names.Length;

            var mission = new MissionData(
                $"daily_{DateTime.UtcNow:yyyyMMdd}_{index}",
                names[idx],
                types[idx],
                difficulties[idx]);

            mission.MissionDescription = descriptions[idx];
            mission.RewardCash = 200 + (int)(difficulties[idx]) * 100;
            mission.RewardExperience = 50 + (int)(difficulties[idx]) * 50;
            mission.TimeLimit = 300f;
            mission.MaxRetries = 3;
            mission.State = MissionState.Available;

            mission.Objectives.Add(new MissionObjectiveData(
                descriptions[idx], ObjectiveType.ReachCheckpoint,
                new Vector3(UnityEngine.Random.Range(-80f, 80f), 0f, UnityEngine.Random.Range(-80f, 80f)), 1));

            return mission;
        }

        private MissionData CreateMissionFromTemplate(DailyMissionTemplate template)
        {
            var mission = new MissionData(
                $"daily_{DateTime.UtcNow:yyyyMMdd}_{template.TemplateId}",
                template.MissionName,
                template.Type,
                template.Difficulty);

            mission.MissionDescription = template.Description;
            mission.RewardCash = template.RewardCash;
            mission.RewardExperience = template.RewardExperience;
            mission.TimeLimit = template.TimeLimit;
            mission.MaxRetries = 3;
            mission.State = MissionState.Available;
            mission.Objectives = new List<MissionObjectiveData>(template.Objectives);

            return mission;
        }

        public void CompleteDailyMission(string missionId)
        {
            for (int i = _currentDailyMissions.Count - 1; i >= 0; i--)
            {
                if (_currentDailyMissions[i].MissionId == missionId)
                {
                    var mission = _currentDailyMissions[i];
                    mission.State = MissionState.Completed;
                    _currentDailyMissions.RemoveAt(i);

                    _currentStreak++;
                    OnStreakUpdated?.Invoke(_currentStreak);
                    OnDailyMissionCompleted?.Invoke(mission);
                    break;
                }
            }
        }

        public void FailDailyMission(string missionId)
        {
            for (int i = _currentDailyMissions.Count - 1; i >= 0; i--)
            {
                if (_currentDailyMissions[i].MissionId == missionId)
                {
                    _currentDailyMissions[i].State = MissionState.Failed;
                    _currentDailyMissions.RemoveAt(i);
                    _currentStreak = 0;
                    OnStreakUpdated?.Invoke(_currentStreak);
                    break;
                }
            }
        }

        private bool ShouldResetDaily()
        {
            if (string.IsNullOrEmpty(_lastResetDate)) return true;
            return DateTime.UtcNow.Date.ToString("yyyy-MM-dd") != _lastResetDate;
        }

        private void PerformDailyReset()
        {
            _lastResetDate = DateTime.UtcNow.Date.ToString("yyyy-MM-dd");
            GenerateDailyMissions();
            OnDailyReset?.Invoke();
            Debug.Log("[MissionDaily] Daily reset performed");
        }

        public int GetStreakBonus()
        {
            if (_config == null || _currentStreak < 3) return 0;
            return _currentStreak * _config.dailyStreakBonusMultiplier;
        }

        public void SetStreak(int streak)
        {
            _currentStreak = Mathf.Max(0, streak);
            OnStreakUpdated?.Invoke(_currentStreak);
        }

        public void ClearAll()
        {
            _templates.Clear();
            _currentDailyMissions.Clear();
            _currentStreak = 0;
            _isInitialized = false;
        }
    }
}
