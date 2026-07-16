using System;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionFailureSystem
    {
        private readonly MissionConfig _config;

        public event Action<string, FailureReason> OnMissionFailed;
        public event Action<string> OnRetryStarted;
        public event Action<string> OnRetrySucceeded;
        public event Action<string> OnRetryFailed;
        public event Action<string> OnMaxRetriesReached;

        public MissionFailureSystem(MissionConfig config)
        {
            _config = config;
        }

        public bool CheckTimeExpired(MissionData mission)
        {
            if (mission == null || !mission.IsTimed) return false;

            if (mission.ElapsedTime >= mission.TimeLimit)
            {
                FailMission(mission, FailureReason.TimeExpired);
                return true;
            }
            return false;
        }

        public bool CheckVehicleDestroyed(MissionData mission, bool isVehicleDestroyed)
        {
            if (mission == null || !isVehicleDestroyed) return false;

            FailMission(mission, FailureReason.VehicleDestroyed);
            return true;
        }

        public bool CheckPlayerDefeated(MissionData mission, bool isPlayerDefeated)
        {
            if (mission == null || !isPlayerDefeated) return false;

            FailMission(mission, FailureReason.PlayerDefeated);
            return true;
        }

        public bool CheckLeftMissionArea(MissionData mission, Vector3 playerPosition, float maxRadius)
        {
            if (mission == null) return false;

            foreach (var checkpoint in mission.Checkpoints)
            {
                if (!checkpoint.IsReached)
                {
                    float distance = Vector3.Distance(playerPosition, checkpoint.Position);
                    if (distance <= checkpoint.Radius + maxRadius)
                    {
                        return false;
                    }
                }
            }

            return false;
        }

        public bool CheckObjectiveFailed(MissionData mission)
        {
            if (mission == null) return false;

            if (mission.HasFailedObjectives())
            {
                FailMission(mission, FailureReason.ObjectiveFailed);
                return true;
            }
            return false;
        }

        public void FailMission(MissionData mission, FailureReason reason)
        {
            if (mission == null) return;
            if (mission.State != MissionState.InProgress && mission.State != MissionState.Paused) return;

            mission.State = MissionState.Failed;
            OnMissionFailed?.Invoke(mission.MissionId, reason);
            Debug.Log($"[MissionFailure] Mission '{mission.MissionName}' failed: {reason}");
        }

        public bool AttemptRetry(MissionData mission)
        {
            if (mission == null) return false;

            if (mission.RetryCount >= mission.MaxRetries)
            {
                OnMaxRetriesReached?.Invoke(mission.MissionId);
                Debug.Log($"[MissionFailure] Max retries reached for '{mission.MissionName}'");
                return false;
            }

            mission.RetryCount++;
            mission.State = MissionState.Available;
            mission.ElapsedTime = 0f;

            if (_config != null && _config.retryResetTimer)
            {
                mission.ElapsedTime = 0f;
            }

            foreach (var checkpoint in mission.Checkpoints)
            {
                checkpoint.IsReached = false;
            }

            foreach (var objective in mission.Objectives)
            {
                if (objective.State == ObjectiveState.Failed)
                {
                    objective.State = ObjectiveState.Inactive;
                    objective.CurrentCount = 0;
                }
            }

            OnRetryStarted?.Invoke(mission.MissionId);
            Debug.Log($"[MissionFailure] Retry {mission.RetryCount}/{mission.MaxRetries} for '{mission.MissionName}'");

            return true;
        }

        public void CancelMission(MissionData mission)
        {
            if (mission == null) return;

            mission.State = MissionState.Cancelled;
            OnMissionFailed?.Invoke(mission.MissionId, FailureReason.PlayerCancelled);
            Debug.Log($"[MissionFailure] Mission '{mission.MissionName}' cancelled");
        }

        public bool CanRetry(MissionData mission)
        {
            return mission != null
                && mission.State == MissionState.Failed
                && mission.RetryCount < mission.MaxRetries;
        }

        public float GetRetryCooldown(MissionData mission)
        {
            if (mission == null || _config == null) return 0f;
            return _config.retryCooldown;
        }

        public int GetRemainingRetries(MissionData mission)
        {
            if (mission == null) return 0;
            return mission.MaxRetries - mission.RetryCount;
        }

        public void ResetFailureState(MissionData mission)
        {
            if (mission == null) return;

            foreach (var checkpoint in mission.Checkpoints)
            {
                checkpoint.IsReached = false;
            }

            foreach (var objective in mission.Objectives)
            {
                objective.State = ObjectiveState.Inactive;
                objective.CurrentCount = 0;
            }

            mission.ElapsedTime = 0f;
            mission.State = MissionState.Available;
        }
    }
}
