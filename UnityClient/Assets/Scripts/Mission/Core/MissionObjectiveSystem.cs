using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionObjectiveSystem
    {
        private readonly MissionConfig _config;
        private readonly Dictionary<string, List<MissionObjectiveData>> _missionObjectives;

        public event Action<string, MissionObjectiveData> OnObjectiveActivated;
        public event Action<string, MissionObjectiveData> OnObjectiveCompleted;
        public event Action<string, MissionObjectiveData> OnObjectiveFailed;
        public event Action<string> OnAllObjectivesCompleted;

        public MissionObjectiveSystem(MissionConfig config)
        {
            _config = config;
            _missionObjectives = new Dictionary<string, List<MissionObjectiveData>>();
        }

        public void InitializeMissionObjectives(MissionData mission)
        {
            if (mission == null) return;

            _missionObjectives[mission.MissionId] = mission.Objectives ?? new List<MissionObjectiveData>();

            for (int i = 0; i < _missionObjectives[mission.MissionId].Count; i++)
            {
                var obj = _missionObjectives[mission.MissionId][i];
                if (!obj.IsOptional)
                {
                    obj.State = ObjectiveState.Active;
                    OnObjectiveActivated?.Invoke(mission.MissionId, obj);
                }
            }
        }

        public void Update(float deltaTime, string activeMissionId, Vector3 playerPosition)
        {
            if (string.IsNullOrEmpty(activeMissionId)) return;
            if (!_missionObjectives.ContainsKey(activeMissionId)) return;

            var objectives = _missionObjectives[activeMissionId];
            bool allRequiredComplete = true;

            foreach (var obj in objectives)
            {
                if (obj.State != ObjectiveState.Active) continue;
                if (obj.IsOptional) continue;

                switch (obj.Type)
                {
                    case ObjectiveType.ReachCheckpoint:
                        CheckReachCheckpoint(obj, playerPosition);
                        break;
                    case ObjectiveType.SurviveTime:
                        CheckSurviveTime(obj, deltaTime);
                        break;
                }

                if (!obj.IsComplete && !obj.IsOptional)
                    allRequiredComplete = false;
            }

            if (allRequiredComplete && objectives.Count > 0)
            {
                bool hasRequired = false;
                foreach (var obj in objectives)
                {
                    if (!obj.IsOptional)
                    {
                        hasRequired = true;
                        break;
                    }
                }

                if (hasRequired)
                {
                    OnAllObjectivesCompleted?.Invoke(activeMissionId);
                }
            }
        }

        private void CheckReachCheckpoint(MissionObjectiveData obj, Vector3 playerPosition)
        {
            float distance = Vector3.Distance(playerPosition, obj.TargetPosition);
            if (distance <= obj.TargetRadius)
            {
                obj.CurrentCount = 1;
                if (obj.IsComplete && obj.State == ObjectiveState.Active)
                {
                    CompleteObjective(obj);
                }
            }
        }

        private void CheckSurviveTime(MissionObjectiveData obj, float deltaTime)
        {
            if (float.TryParse(obj.CustomData.TryGetValue("elapsed", out var elapsed) ? elapsed : "0", out float elapsedVal))
            {
                elapsedVal += deltaTime;
                obj.CustomData["elapsed"] = elapsedVal.ToString();
                obj.CurrentCount = elapsedVal >= obj.RequiredCount ? obj.RequiredCount : (int)elapsedVal;
            }

            if (obj.IsComplete && obj.State == ObjectiveState.Active)
            {
                CompleteObjective(obj);
            }
        }

        public void IncrementObjective(string missionId, string objectiveId, int amount = 1)
        {
            if (!_missionObjectives.ContainsKey(missionId)) return;

            foreach (var obj in _missionObjectives[missionId])
            {
                if (obj.ObjectiveId == objectiveId && obj.State == ObjectiveState.Active)
                {
                    obj.CurrentCount = Mathf.Min(obj.CurrentCount + amount, obj.RequiredCount);

                    if (obj.IsComplete)
                    {
                        CompleteObjective(obj);
                    }
                    break;
                }
            }
        }

        public void IncrementObjectiveByType(string missionId, ObjectiveType type, int amount = 1)
        {
            if (!_missionObjectives.ContainsKey(missionId)) return;

            foreach (var obj in _missionObjectives[missionId])
            {
                if (obj.Type == type && obj.State == ObjectiveState.Active)
                {
                    obj.CurrentCount = Mathf.Min(obj.CurrentCount + amount, obj.RequiredCount);

                    if (obj.IsComplete)
                    {
                        CompleteObjective(obj);
                    }
                    break;
                }
            }
        }

        public void CompleteObjective(MissionObjectiveData obj)
        {
            if (obj.State == ObjectiveState.Completed) return;

            obj.State = ObjectiveState.Completed;
            obj.CurrentCount = obj.RequiredCount;
            OnObjectiveCompleted?.Invoke(null, obj);
            Debug.Log($"[MissionObjectives] Objective completed: {obj.Description}");
        }

        public void FailObjective(string missionId, string objectiveId)
        {
            if (!_missionObjectives.ContainsKey(missionId)) return;

            foreach (var obj in _missionObjectives[missionId])
            {
                if (obj.ObjectiveId == objectiveId && obj.State == ObjectiveState.Active)
                {
                    obj.State = ObjectiveState.Failed;
                    OnObjectiveFailed?.Invoke(missionId, obj);
                    break;
                }
            }
        }

        public void FailAllObjectives(string missionId)
        {
            if (!_missionObjectives.ContainsKey(missionId)) return;

            foreach (var obj in _missionObjectives[missionId])
            {
                if (obj.State == ObjectiveState.Active)
                {
                    obj.State = ObjectiveState.Failed;
                    OnObjectiveFailed?.Invoke(missionId, obj);
                }
            }
        }

        public void ActivateOptionalObjective(string missionId, string objectiveId)
        {
            if (!_missionObjectives.ContainsKey(missionId)) return;

            foreach (var obj in _missionObjectives[missionId])
            {
                if (obj.ObjectiveId == objectiveId && obj.State == ObjectiveState.Inactive)
                {
                    obj.State = ObjectiveState.Active;
                    OnObjectiveActivated?.Invoke(missionId, obj);
                    break;
                }
            }
        }

        public bool AreAllRequiredComplete(string missionId)
        {
            if (!_missionObjectives.ContainsKey(missionId)) return false;

            foreach (var obj in _missionObjectives[missionId])
            {
                if (!obj.IsOptional && obj.State != ObjectiveState.Completed)
                    return false;
            }
            return true;
        }

        public bool HasFailedObjective(string missionId)
        {
            if (!_missionObjectives.ContainsKey(missionId)) return false;

            foreach (var obj in _missionObjectives[missionId])
            {
                if (obj.State == ObjectiveState.Failed) return true;
            }
            return false;
        }

        public List<MissionObjectiveData> GetObjectives(string missionId)
        {
            if (!_missionObjectives.ContainsKey(missionId))
                return new List<MissionObjectiveData>();
            return new List<MissionObjectiveData>(_missionObjectives[missionId]);
        }

        public float GetProgress(string missionId)
        {
            if (!_missionObjectives.ContainsKey(missionId)) return 0f;

            var objectives = _missionObjectives[missionId];
            int requiredCount = 0;
            int completedCount = 0;

            foreach (var obj in objectives)
            {
                if (!obj.IsOptional)
                {
                    requiredCount++;
                    if (obj.State == ObjectiveState.Completed)
                        completedCount++;
                }
            }

            return requiredCount > 0 ? (float)completedCount / requiredCount : 0f;
        }

        public void ResetMissionObjectives(string missionId)
        {
            if (!_missionObjectives.ContainsKey(missionId)) return;

            foreach (var obj in _missionObjectives[missionId])
            {
                obj.State = ObjectiveState.Inactive;
                obj.CurrentCount = 0;
            }
        }

        public void RemoveMission(string missionId)
        {
            _missionObjectives.Remove(missionId);
        }

        public void ClearAll()
        {
            _missionObjectives.Clear();
        }
    }
}
