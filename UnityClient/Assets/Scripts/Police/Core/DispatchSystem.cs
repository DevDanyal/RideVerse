using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class DispatchSystem
    {
        private readonly PoliceConfig _config;
        private readonly List<DispatchCall> _activeCalls;
        private readonly Dictionary<string, PoliceUnitState> _unitStates;
        private float _dispatchTimer;

        public int ActiveCallCount => _activeCalls.Count;
        public IReadOnlyList<DispatchCall> ActiveCalls => _activeCalls;

        public event Action<DispatchCall> OnDispatchCreated;
        public event Action<DispatchCall, string> OnUnitAssigned;
        public event Action<DispatchCall> OnDispatchCompleted;

        public DispatchSystem(PoliceConfig config)
        {
            _config = config;
            _activeCalls = new List<DispatchCall>();
            _unitStates = new Dictionary<string, PoliceUnitState>();
        }

        public void RegisterUnit(string unitId)
        {
            if (!_unitStates.ContainsKey(unitId))
            {
                _unitStates[unitId] = new PoliceUnitState(unitId);
            }
        }

        public void UnregisterUnit(string unitId)
        {
            _unitStates.Remove(unitId);
        }

        public void Update(float deltaTime)
        {
            _dispatchTimer += deltaTime;
            if (_dispatchTimer < 0.5f) return;
            _dispatchTimer = 0f;

            CleanupExpiredCalls();
            ProcessPendingAssignments();
        }

        public DispatchCall CreateDispatchCall(string crimeId, CrimeType type, Vector3 position, DispatchPriority priority, int requiredUnits = 1)
        {
            if (_activeCalls.Count >= _config.maxActiveDispatchCalls)
            {
                var lowest = GetLowestPriorityCall();
                if (lowest != null && priority > lowest.Priority)
                {
                    CancelDispatch(lowest.CallId);
                }
                else
                {
                    return null;
                }
            }

            var call = new DispatchCall(crimeId, type, position, priority);
            call.ExpiryTime = _config.dispatchCallExpiryTime;
            call.RequiredUnits = requiredUnits;
            _activeCalls.Add(call);

            OnDispatchCreated?.Invoke(call);
            return call;
        }

        public bool AssignUnit(string callId, string unitId)
        {
            var call = FindCallById(callId);
            if (call == null || !call.IsActive) return false;

            if (!_unitStates.TryGetValue(unitId, out var state)) return false;
            if (!state.IsAvailable) return false;

            call.IsAssigned = true;
            call.AssignedUnitId = unitId;
            state.IsAvailable = false;
            state.CurrentDispatchCallId = callId;

            OnUnitAssigned?.Invoke(call, unitId);
            return true;
        }

        public void CompleteDispatch(string callId)
        {
            var call = FindCallById(callId);
            if (call == null) return;

            call.IsActive = false;

            if (!string.IsNullOrEmpty(call.AssignedUnitId) && _unitStates.TryGetValue(call.AssignedUnitId, out var state))
            {
                state.IsAvailable = true;
                state.CurrentDispatchCallId = null;
                state.CurrentState = PoliceState.ReturningToStation;
            }

            OnDispatchCompleted?.Invoke(call);
        }

        public void CancelDispatch(string callId)
        {
            var call = FindCallById(callId);
            if (call == null) return;

            call.IsActive = false;

            if (!string.IsNullOrEmpty(call.AssignedUnitId) && _unitStates.TryGetValue(call.AssignedUnitId, out var state))
            {
                state.IsAvailable = true;
                state.CurrentDispatchCallId = null;
            }
        }

        public DispatchCall GetBestCallForUnit(string unitId, Vector3 unitPosition)
        {
            DispatchCall bestCall = null;
            float bestScore = float.MinValue;

            for (int i = 0; i < _activeCalls.Count; i++)
            {
                var call = _activeCalls[i];
                if (!call.IsActive || call.IsAssigned) continue;

                float distance = Vector3.Distance(unitPosition, call.Position);
                float maxRadius = GetRadiusForPriority(call.Priority);

                if (distance > maxRadius) continue;

                float score = call.GetPriorityScore() * 10f - distance * 0.01f;
                if (score > bestScore)
                {
                    bestScore = score;
                    bestCall = call;
                }
            }

            return bestCall;
        }

        public DispatchCall GetCallById(string callId)
        {
            return FindCallById(callId);
        }

        public bool IsUnitAvailable(string unitId)
        {
            if (_unitStates.TryGetValue(unitId, out var state))
            {
                return state.IsAvailable;
            }
            return false;
        }

        public PoliceUnitState GetUnitState(string unitId)
        {
            _unitStates.TryGetValue(unitId, out var state);
            return state;
        }

        public void SetUnitState(string unitId, PoliceState newState)
        {
            if (_unitStates.TryGetValue(unitId, out var state))
            {
                state.CurrentState = newState;
            }
        }

        private void ProcessPendingAssignments()
        {
            for (int i = 0; i < _activeCalls.Count; i++)
            {
                var call = _activeCalls[i];
                if (!call.IsActive || call.IsAssigned) continue;
            }
        }

        private DispatchCall GetLowestPriorityCall()
        {
            DispatchCall lowest = null;
            for (int i = 0; i < _activeCalls.Count; i++)
            {
                if (!_activeCalls[i].IsAssigned)
                {
                    if (lowest == null || _activeCalls[i].Priority < lowest.Priority)
                    {
                        lowest = _activeCalls[i];
                    }
                }
            }
            return lowest;
        }

        private float GetRadiusForPriority(DispatchPriority priority)
        {
            return priority switch
            {
                DispatchPriority.Low => _config.dispatchRadiusLowPriority,
                DispatchPriority.Medium => _config.dispatchRadiusLowPriority * 0.8f,
                DispatchPriority.High => _config.dispatchRadiusHighPriority,
                DispatchPriority.Critical => _config.dispatchRadiusCritical,
                _ => _config.dispatchRadiusLowPriority
            };
        }

        private void CleanupExpiredCalls()
        {
            for (int i = _activeCalls.Count - 1; i >= 0; i--)
            {
                if (_activeCalls[i].IsExpired(Time.time))
                {
                    if (_activeCalls[i].IsAssigned && !string.IsNullOrEmpty(_activeCalls[i].AssignedUnitId))
                    {
                        if (_unitStates.TryGetValue(_activeCalls[i].AssignedUnitId, out var state))
                        {
                            state.IsAvailable = true;
                            state.CurrentDispatchCallId = null;
                        }
                    }
                    _activeCalls.RemoveAt(i);
                }
            }
        }

        private DispatchCall FindCallById(string callId)
        {
            for (int i = 0; i < _activeCalls.Count; i++)
            {
                if (_activeCalls[i].CallId == callId)
                    return _activeCalls[i];
            }
            return null;
        }

        public void ClearAll()
        {
            foreach (var kvp in _unitStates)
            {
                kvp.Value.IsAvailable = true;
                kvp.Value.CurrentDispatchCallId = null;
            }
            _activeCalls.Clear();
        }
    }
}
