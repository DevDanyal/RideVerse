using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionStateMachine
    {
        private MissionData _currentMission;
        private MissionState _previousState;
        private readonly Dictionary<MissionState, Action<MissionData, MissionState>> _onEnterCallbacks;
        private readonly Dictionary<MissionState, Action<MissionData, MissionState>> _onExitCallbacks;

        public MissionData CurrentMission => _currentMission;
        public MissionState CurrentState => _currentMission?.State ?? MissionState.Locked;
        public MissionState PreviousState => _previousState;
        public bool HasMission => _currentMission != null;

        public event Action<MissionData, MissionState, MissionState> OnStateChanged;
        public event Action<MissionData> OnMissionCompleted;
        public event Action<MissionData, FailureReason> OnMissionFailed;
        public event Action<MissionData> OnMissionCancelled;
        public event Action<MissionData> OnMissionAccepted;
        public event Action<MissionData> OnMissionStarted;

        public MissionStateMachine()
        {
            _onEnterCallbacks = new Dictionary<MissionState, Action<MissionData, MissionState>>();
            _onExitCallbacks = new Dictionary<MissionState, Action<MissionData, MissionState>>();

            RegisterDefaultCallbacks();
        }

        private void RegisterDefaultCallbacks()
        {
            OnEnter(MissionState.Available, (mission, prev) =>
            {
                Debug.Log($"[MissionStateMachine] Mission '{mission.MissionName}' is now available");
            });

            OnEnter(MissionState.Accepted, (mission, prev) =>
            {
                mission.AcceptedTime = DateTime.UtcNow;
                Debug.Log($"[MissionStateMachine] Mission '{mission.MissionName}' accepted");
            });

            OnEnter(MissionState.InProgress, (mission, prev) =>
            {
                mission.ElapsedTime = 0f;
                Debug.Log($"[MissionStateMachine] Mission '{mission.MissionName}' in progress");
            });

            OnEnter(MissionState.Paused, (mission, prev) =>
            {
                Debug.Log($"[MissionStateMachine] Mission '{mission.MissionName}' paused");
            });

            OnEnter(MissionState.Completed, (mission, prev) =>
            {
                mission.CompletedTime = DateTime.UtcNow;
                Debug.Log($"[MissionStateMachine] Mission '{mission.MissionName}' completed!");
            });

            OnEnter(MissionState.Failed, (mission, prev) =>
            {
                Debug.Log($"[MissionStateMachine] Mission '{mission.MissionName}' failed");
            });

            OnEnter(MissionState.Cancelled, (mission, prev) =>
            {
                Debug.Log($"[MissionStateMachine] Mission '{mission.MissionName}' cancelled");
            });
        }

        public void SetMission(MissionData mission)
        {
            _currentMission = mission;
            _previousState = mission.State;
        }

        public bool TransitionTo(MissionState newState, FailureReason failureReason = FailureReason.None)
        {
            if (_currentMission == null)
            {
                Debug.LogWarning("[MissionStateMachine] No mission set");
                return false;
            }

            if (!IsValidTransition(_currentMission.State, newState))
            {
                Debug.LogWarning($"[MissionStateMachine] Invalid transition from {_currentMission.State} to {newState} for '{_currentMission.MissionName}'");
                return false;
            }

            _previousState = _currentMission.State;

            if (_onExitCallbacks.TryGetValue(_previousState, out var exitCallback))
            {
                exitCallback.Invoke(_currentMission, newState);
            }

            _currentMission.State = newState;

            if (_onEnterCallbacks.TryGetValue(newState, out var enterCallback))
            {
                enterCallback.Invoke(_currentMission, _previousState);
            }

            OnStateChanged?.Invoke(_currentMission, _previousState, newState);

            switch (newState)
            {
                case MissionState.Accepted:
                    OnMissionAccepted?.Invoke(_currentMission);
                    break;
                case MissionState.InProgress:
                    OnMissionStarted?.Invoke(_currentMission);
                    break;
                case MissionState.Completed:
                    OnMissionCompleted?.Invoke(_currentMission);
                    break;
                case MissionState.Failed:
                    OnMissionFailed?.Invoke(_currentMission, failureReason);
                    break;
                case MissionState.Cancelled:
                    OnMissionCancelled?.Invoke(_currentMission);
                    break;
            }

            return true;
        }

        public bool CanAccept()
        {
            return _currentMission != null && _currentMission.State == MissionState.Available;
        }

        public bool CanStart()
        {
            return _currentMission != null && _currentMission.State == MissionState.Accepted;
        }

        public bool CanPause()
        {
            return _currentMission != null && _currentMission.State == MissionState.InProgress;
        }

        public bool CanResume()
        {
            return _currentMission != null && _currentMission.State == MissionState.Paused;
        }

        public bool CanComplete()
        {
            if (_currentMission == null || _currentMission.State != MissionState.InProgress) return false;
            return _currentMission.AreAllObjectivesComplete();
        }

        public bool CanFail()
        {
            if (_currentMission == null) return false;
            return _currentMission.State == MissionState.InProgress || _currentMission.State == MissionState.Paused;
        }

        public bool CanRetry()
        {
            return _currentMission != null
                && _currentMission.State == MissionState.Failed
                && _currentMission.RetryCount < _currentMission.MaxRetries;
        }

        public bool CanCancel()
        {
            if (_currentMission == null) return false;
            return _currentMission.State == MissionState.Accepted || _currentMission.State == MissionState.InProgress;
        }

        public void OnEnter(MissionState state, Action<MissionData, MissionState> callback)
        {
            if (!_onEnterCallbacks.ContainsKey(state))
                _onEnterCallbacks[state] = null;
            _onEnterCallbacks[state] += callback;
        }

        public void OnExit(MissionState state, Action<MissionData, MissionState> callback)
        {
            if (!_onExitCallbacks.ContainsKey(state))
                _onExitCallbacks[state] = null;
            _onExitCallbacks[state] += callback;
        }

        private bool IsValidTransition(MissionState from, MissionState to)
        {
            switch (from)
            {
                case MissionState.Locked:
                    return to == MissionState.Available;
                case MissionState.Available:
                    return to == MissionState.Accepted || to == MissionState.Cancelled;
                case MissionState.Accepted:
                    return to == MissionState.InProgress || to == MissionState.Cancelled || to == MissionState.Failed;
                case MissionState.InProgress:
                    return to == MissionState.Paused || to == MissionState.Completed || to == MissionState.Failed || to == MissionState.Cancelled;
                case MissionState.Paused:
                    return to == MissionState.InProgress || to == MissionState.Failed || to == MissionState.Cancelled;
                case MissionState.Completed:
                    return false;
                case MissionState.Failed:
                    return to == MissionState.Available || to == MissionState.InProgress;
                case MissionState.Cancelled:
                    return to == MissionState.Available;
                default:
                    return false;
            }
        }

        public MissionState[] GetValidTransitions()
        {
            if (_currentMission == null) return Array.Empty<MissionState>();

            var valid = new List<MissionState>();
            var allStates = (MissionState[])Enum.GetValues(typeof(MissionState));

            foreach (var state in allStates)
            {
                if (IsValidTransition(_currentMission.State, state))
                    valid.Add(state);
            }

            return valid.ToArray();
        }

        public void Reset()
        {
            _currentMission = null;
            _previousState = MissionState.Locked;
        }
    }
}
