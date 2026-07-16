using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionCheckpointSystem
    {
        private readonly MissionConfig _config;
        private readonly Dictionary<string, List<MissionCheckpointData>> _missionCheckpoints;
        private readonly Dictionary<string, int> _currentCheckpointIndex;

        public event Action<string, MissionCheckpointData> OnCheckpointReached;
        public event Action<string, MissionCheckpointData> OnCheckpointActivated;
        public event Action<string> OnAllCheckpointsCompleted;

        public MissionCheckpointSystem(MissionConfig config)
        {
            _config = config;
            _missionCheckpoints = new Dictionary<string, List<MissionCheckpointData>>();
            _currentCheckpointIndex = new Dictionary<string, int>();
        }

        public void InitializeMissionCheckpoints(MissionData mission)
        {
            if (mission == null) return;

            _missionCheckpoints[mission.MissionId] = mission.Checkpoints ?? new List<MissionCheckpointData>();
            _currentCheckpointIndex[mission.MissionId] = 0;

            if (_missionCheckpoints[mission.MissionId].Count > 0)
            {
                ActivateCheckpoint(mission.MissionId, 0);
            }
        }

        public void Update(float deltaTime, Vector3 playerPosition, string activeMissionId)
        {
            if (string.IsNullOrEmpty(activeMissionId)) return;
            if (!_missionCheckpoints.ContainsKey(activeMissionId)) return;

            int currentIndex = GetCurrentCheckpointIndex(activeMissionId);
            var checkpoints = _missionCheckpoints[activeMissionId];

            if (currentIndex >= checkpoints.Count) return;

            var checkpoint = checkpoints[currentIndex];
            float distance = Vector3.Distance(playerPosition, checkpoint.Position);

            if (distance <= checkpoint.Radius)
            {
                ReachCheckpoint(activeMissionId, currentIndex);
            }
        }

        public void CheckManualReach(string missionId, Vector3 position)
        {
            if (!_missionCheckpoints.ContainsKey(missionId)) return;

            int currentIndex = GetCurrentCheckpointIndex(missionId);
            var checkpoints = _missionCheckpoints[missionId];

            if (currentIndex >= checkpoints.Count) return;

            var checkpoint = checkpoints[currentIndex];
            float distance = Vector3.Distance(position, checkpoint.Position);

            if (distance <= checkpoint.Radius)
            {
                ReachCheckpoint(missionId, currentIndex);
            }
        }

        private void ReachCheckpoint(string missionId, int index)
        {
            var checkpoints = _missionCheckpoints[missionId];
            var checkpoint = checkpoints[index];

            if (checkpoint.IsReached) return;

            checkpoint.IsReached = true;
            _currentCheckpointIndex[missionId] = index + 1;

            OnCheckpointReached?.Invoke(missionId, checkpoint);
            Debug.Log($"[MissionCheckpoints] Checkpoint {index + 1}/{checkpoints.Count} reached for mission {missionId}");

            if (index + 1 < checkpoints.Count)
            {
                ActivateCheckpoint(missionId, index + 1);
            }
            else
            {
                OnAllCheckpointsCompleted?.Invoke(missionId);
                Debug.Log($"[MissionCheckpoints] All checkpoints completed for mission {missionId}");
            }
        }

        private void ActivateCheckpoint(string missionId, int index)
        {
            var checkpoints = _missionCheckpoints[missionId];
            if (index < checkpoints.Count)
            {
                OnCheckpointActivated?.Invoke(missionId, checkpoints[index]);
                Debug.Log($"[MissionCheckpoints] Checkpoint {index + 1} activated");
            }
        }

        public int GetCurrentCheckpointIndex(string missionId)
        {
            return _currentCheckpointIndex.TryGetValue(missionId, out var idx) ? idx : 0;
        }

        public MissionCheckpointData GetCurrentCheckpoint(string missionId)
        {
            if (!_missionCheckpoints.ContainsKey(missionId)) return null;

            int index = GetCurrentCheckpointIndex(missionId);
            var checkpoints = _missionCheckpoints[missionId];

            if (index < checkpoints.Count)
                return checkpoints[index];
            return null;
        }

        public MissionCheckpointData GetCheckpoint(string missionId, int index)
        {
            if (!_missionCheckpoints.ContainsKey(missionId)) return null;
            var checkpoints = _missionCheckpoints[missionId];
            if (index >= 0 && index < checkpoints.Count)
                return checkpoints[index];
            return null;
        }

        public List<MissionCheckpointData> GetAllCheckpoints(string missionId)
        {
            if (!_missionCheckpoints.ContainsKey(missionId))
                return new List<MissionCheckpointData>();
            return new List<MissionCheckpointData>(_missionCheckpoints[missionId]);
        }

        public int GetTotalCheckpoints(string missionId)
        {
            return _missionCheckpoints.ContainsKey(missionId) ? _missionCheckpoints[missionId].Count : 0;
        }

        public int GetReachedCount(string missionId)
        {
            if (!_missionCheckpoints.ContainsKey(missionId)) return 0;

            int count = 0;
            foreach (var cp in _missionCheckpoints[missionId])
            {
                if (cp.IsReached) count++;
            }
            return count;
        }

        public float GetProgress(string missionId)
        {
            int total = GetTotalCheckpoints(missionId);
            if (total == 0) return 1f;
            return (float)GetReachedCount(missionId) / total;
        }

        public void ResetMissionCheckpoints(string missionId)
        {
            if (_missionCheckpoints.ContainsKey(missionId))
            {
                foreach (var cp in _missionCheckpoints[missionId])
                {
                    cp.IsReached = false;
                }
            }
            _currentCheckpointIndex[missionId] = 0;
        }

        public void RemoveMission(string missionId)
        {
            _missionCheckpoints.Remove(missionId);
            _currentCheckpointIndex.Remove(missionId);
        }

        public bool AreAllCheckpointsReached(string missionId)
        {
            return GetCurrentCheckpointIndex(missionId) >= GetTotalCheckpoints(missionId);
        }

        public void ClearAll()
        {
            _missionCheckpoints.Clear();
            _currentCheckpointIndex.Clear();
        }
    }
}
