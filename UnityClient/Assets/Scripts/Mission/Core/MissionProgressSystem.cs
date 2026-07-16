using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionProgressSystem
    {
        private readonly MissionConfig _config;
        private readonly Dictionary<string, MissionProgressSnapshot> _progressSnapshots;
        private readonly List<MissionStats> _allStats;
        private MissionStats _currentSessionStats;

        public MissionStats CurrentStats => _currentSessionStats;
        public IReadOnlyList<MissionStats> AllStats => _allStats;

        public event Action<string, MissionProgressSnapshot> OnProgressUpdated;
        public event Action<MissionStats> OnStatsUpdated;

        public MissionProgressSystem(MissionConfig config)
        {
            _config = config;
            _progressSnapshots = new Dictionary<string, MissionProgressSnapshot>();
            _allStats = new List<MissionStats>();
            _currentSessionStats = new MissionStats();
        }

        public void Initialize()
        {
            _currentSessionStats = new MissionStats();
        }

        public void TrackMissionStart(MissionData mission)
        {
            if (mission == null) return;

            var snapshot = new MissionProgressSnapshot
            {
                MissionId = mission.MissionId,
                State = mission.State,
                ElapsedTime = 0f,
                CompletedObjectives = 0,
                TotalObjectives = mission.Objectives?.Count ?? 0,
                CurrentCheckpoint = 0,
                TotalCheckpoints = mission.Checkpoints?.Count ?? 0,
                RetryCount = mission.RetryCount,
                Timestamp = DateTime.UtcNow
            };

            _progressSnapshots[mission.MissionId] = snapshot;
            _currentSessionStats.TotalMissionsStarted++;

            OnProgressUpdated?.Invoke(mission.MissionId, snapshot);
            Debug.Log($"[MissionProgress] Tracking mission: {mission.MissionName}");
        }

        public void UpdateProgress(MissionData mission)
        {
            if (mission == null || !_progressSnapshots.ContainsKey(mission.MissionId)) return;

            var snapshot = _progressSnapshots[mission.MissionId];
            snapshot.State = mission.State;
            snapshot.ElapsedTime = mission.ElapsedTime;
            snapshot.CompletedObjectives = mission.CompletedObjectiveCount();
            snapshot.RetryCount = mission.RetryCount;
            snapshot.Timestamp = DateTime.UtcNow;

            _progressSnapshots[mission.MissionId] = snapshot;
            OnProgressUpdated?.Invoke(mission.MissionId, snapshot);
        }

        public void RecordMissionCompletion(MissionData mission)
        {
            if (mission == null) return;

            _currentSessionStats.TotalMissionsCompleted++;
            _currentSessionStats.TotalTimeSpent += mission.ElapsedTime;
            _currentSessionStats.CurrentStreak++;

            if (_currentSessionStats.CurrentStreak > _currentSessionStats.LongestMissionStreak)
            {
                _currentSessionStats.LongestMissionStreak = _currentSessionStats.CurrentStreak;
            }

            if (_progressSnapshots.ContainsKey(mission.MissionId))
            {
                var snapshot = _progressSnapshots[mission.MissionId];
                _currentSessionStats.TotalCheckpointsReached += snapshot.TotalCheckpoints;
                _currentSessionStats.TotalObjectivesCompleted += snapshot.TotalObjectives;
            }

            OnStatsUpdated?.Invoke(_currentSessionStats);
        }

        public void RecordMissionFailure(MissionData mission)
        {
            if (mission == null) return;

            _currentSessionStats.TotalMissionsFailed++;
            _currentSessionStats.TotalTimeSpent += mission.ElapsedTime;
            _currentSessionStats.TotalRetriesUsed += mission.RetryCount;
            _currentSessionStats.CurrentStreak = 0;

            OnStatsUpdated?.Invoke(_currentSessionStats);
        }

        public void RecordMissionCancellation(MissionData mission)
        {
            if (mission == null) return;

            _currentSessionStats.TotalMissionsCancelled++;
            _currentSessionStats.CurrentStreak = 0;

            OnStatsUpdated?.Invoke(_currentSessionStats);
        }

        public MissionProgressSnapshot GetProgress(string missionId)
        {
            _progressSnapshots.TryGetValue(missionId, out var snapshot);
            return snapshot;
        }

        public float GetCompletionPercentage(string missionId)
        {
            if (_progressSnapshots.TryGetValue(missionId, out var snapshot))
            {
                return snapshot.CompletionPercentage;
            }
            return 0f;
        }

        public bool IsMissionTracked(string missionId)
        {
            return _progressSnapshots.ContainsKey(missionId);
        }

        public void RemoveMission(string missionId)
        {
            _progressSnapshots.Remove(missionId);
        }

        public void ClearAll()
        {
            _progressSnapshots.Clear();
            _allStats.Clear();
            _currentSessionStats = new MissionStats();
        }

        public void SaveStats(MissionSaveData saveData)
        {
            if (saveData == null) return;

            saveData.TotalMissionsCompleted = _currentSessionStats.TotalMissionsCompleted;
            saveData.TotalMissionsFailed = _currentSessionStats.TotalMissionsFailed;
        }

        public string GetFormattedStats()
        {
            var s = _currentSessionStats;
            return $"Started: {s.TotalMissionsStarted} | Completed: {s.TotalMissionsCompleted} | " +
                   $"Failed: {s.TotalMissionsFailed} | Streak: {s.CurrentStreak} | " +
                   $"Rate: {s.CompletionRate:F1}%";
        }
    }
}
