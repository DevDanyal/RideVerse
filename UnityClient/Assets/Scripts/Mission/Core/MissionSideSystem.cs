using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionSideSystem
    {
        private readonly MissionConfig _config;
        private readonly Dictionary<string, MissionData> _sideMissions;
        private readonly List<string> _completedSideMissions;
        private readonly List<string> _activeSideMissions;
        private float _cooldownTimer;

        public int ActiveCount => _activeSideMissions.Count;
        public int CompletedCount => _completedSideMissions.Count;
        public bool IsOnCooldown => _cooldownTimer > 0f;

        public event Action<MissionData> OnSideMissionStarted;
        public event Action<MissionData> OnSideMissionCompleted;
        public event Action<MissionData> OnSideMissionFailed;
        public event Action<float> OnCooldownUpdated;

        public MissionSideSystem(MissionConfig config)
        {
            _config = config;
            _sideMissions = new Dictionary<string, MissionData>();
            _completedSideMissions = new List<string>();
            _activeSideMissions = new List<string>();
        }

        public void RegisterSideMission(MissionData mission)
        {
            if (mission == null) return;
            mission.Type = MissionType.Side;
            _sideMissions[mission.MissionId] = mission;
        }

        public void Update(float deltaTime)
        {
            if (_cooldownTimer > 0f)
            {
                _cooldownTimer -= deltaTime;
                OnCooldownUpdated?.Invoke(_cooldownTimer);
            }
        }

        public bool CanStartSideMission()
        {
            if (_config != null && _activeSideMissions.Count >= _config.maxSideMissionsPerDay) return false;
            if (_cooldownTimer > 0f) return false;
            return true;
        }

        public MissionData StartSideMission(string missionId)
        {
            if (!CanStartSideMission())
            {
                Debug.LogWarning("[MissionSide] Cannot start side mission");
                return null;
            }

            if (!_sideMissions.TryGetValue(missionId, out var mission))
            {
                Debug.LogWarning($"[MissionSide] Mission {missionId} not found");
                return null;
            }

            if (_completedSideMissions.Contains(missionId))
            {
                Debug.LogWarning($"[MissionSide] Mission {missionId} already completed");
                return null;
            }

            _activeSideMissions.Add(missionId);
            mission.State = MissionState.InProgress;

            OnSideMissionStarted?.Invoke(mission);
            Debug.Log($"[MissionSide] Side mission started: {mission.MissionName}");
            return mission;
        }

        public void CompleteSideMission(string missionId)
        {
            if (!_activeSideMissions.Contains(missionId)) return;

            _activeSideMissions.Remove(missionId);
            _completedSideMissions.Add(missionId);

            if (_sideMissions.TryGetValue(missionId, out var mission))
            {
                mission.State = MissionState.Completed;
                OnSideMissionCompleted?.Invoke(mission);
            }

            StartCooldown();
            Debug.Log($"[MissionSide] Side mission completed: {missionId}");
        }

        public void FailSideMission(string missionId)
        {
            if (!_activeSideMissions.Contains(missionId)) return;

            _activeSideMissions.Remove(missionId);

            if (_sideMissions.TryGetValue(missionId, out var mission))
            {
                mission.State = MissionState.Failed;
                OnSideMissionFailed?.Invoke(mission);
            }

            Debug.Log($"[MissionSide] Side mission failed: {missionId}");
        }

        private void StartCooldown()
        {
            if (_config == null) return;
            _cooldownTimer = _config.sideMissionCooldown;
        }

        public float GetCooldownProgress()
        {
            if (_config == null || _config.sideMissionCooldown <= 0f) return 1f;
            return 1f - (_cooldownTimer / _config.sideMissionCooldown);
        }

        public List<MissionData> GetAvailableSideMissions()
        {
            var available = new List<MissionData>();
            foreach (var kvp in _sideMissions)
            {
                if (kvp.Value.State == MissionState.Available && !_completedSideMissions.Contains(kvp.Key))
                {
                    available.Add(kvp.Value);
                }
            }
            return available;
        }

        public List<MissionData> GetActiveSideMissions()
        {
            var active = new List<MissionData>();
            foreach (var id in _activeSideMissions)
            {
                if (_sideMissions.TryGetValue(id, out var mission))
                {
                    active.Add(mission);
                }
            }
            return active;
        }

        public void ResetDaily()
        {
            _activeSideMissions.Clear();
            _cooldownTimer = 0f;
        }

        public void ClearAll()
        {
            _sideMissions.Clear();
            _completedSideMissions.Clear();
            _activeSideMissions.Clear();
            _cooldownTimer = 0f;
        }
    }
}
