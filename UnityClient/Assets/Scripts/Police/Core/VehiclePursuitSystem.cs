using UnityEngine;
using System.Collections.Generic;

namespace RideVerse.Police.Core
{
    public class VehiclePursuitSystem
    {
        private readonly PoliceConfig _config;
        private readonly Dictionary<string, PursuitState> _pursuits;
        private readonly Dictionary<string, float> _pursuitTimers;
        private readonly Dictionary<string, float> _lostSightTimers;
        private readonly Dictionary<string, Vector3> _lastKnownPositions;

        public int ActivePursuitCount => _pursuits.Count;

        public VehiclePursuitSystem(PoliceConfig config)
        {
            _config = config;
            _pursuits = new Dictionary<string, PursuitState>();
            _pursuitTimers = new Dictionary<string, float>();
            _lostSightTimers = new Dictionary<string, float>();
            _lastKnownPositions = new Dictionary<string, Vector3>();
        }

        public void StartPursuit(string unitId, string targetId)
        {
            _pursuits[unitId] = PursuitState.Initiating;
            _pursuitTimers[unitId] = 0f;
            _lostSightTimers[unitId] = 0f;
            _lastKnownPositions[unitId] = Vector3.zero;

            _ = TimerTransition(unitId, PursuitState.Initiating, PursuitState.ActiveVehicleChase, 1f);
        }

        public void Update(float deltaTime, string unitId, Vector3 unitPosition, Vector3 targetPosition, float targetSpeed)
        {
            if (!_pursuits.ContainsKey(unitId)) return;

            _pursuitTimers[unitId] += deltaTime;

            var state = _pursuits[unitId];
            _lastKnownPositions[unitId] = targetPosition;

            if (IsPursuitExpired(unitId))
            {
                TerminatePursuit(unitId);
                return;
            }

            switch (state)
            {
                case PursuitState.ActiveVehicleChase:
                    UpdateVehicleChase(deltaTime, unitId, unitPosition, targetPosition, targetSpeed);
                    break;
                case PursuitState.LostSight:
                    UpdateLostSight(deltaTime, unitId, unitPosition);
                    break;
            }
        }

        private void UpdateVehicleChase(float deltaTime, string unitId, Vector3 unitPos, Vector3 targetPos, float targetSpeed)
        {
            float distance = Vector3.Distance(unitPos, targetPos);

            if (distance > _config.pursuitLostSightTime * targetSpeed)
            {
                _lostSightTimers[unitId] += deltaTime;
                if (_lostSightTimers[unitId] >= _config.pursuitLostSightTime)
                {
                    _pursuits[unitId] = PursuitState.LostSight;
                    _lostSightTimers[unitId] = 0f;
                }
            }
            else
            {
                _lostSightTimers[unitId] = 0f;
            }
        }

        private void UpdateLostSight(float deltaTime, string unitId, Vector3 unitPos)
        {
            _lostSightTimers[unitId] += deltaTime;

            if (_lostSightTimers[unitId] >= _config.pursuitLostSightTime)
            {
                TerminatePursuit(unitId);
            }
        }

        public void TerminatePursuit(string unitId)
        {
            if (_pursuits.ContainsKey(unitId))
            {
                _pursuits[unitId] = PursuitState.PursuitTerminated;
                _pursuits.Remove(unitId);
                _pursuitTimers.Remove(unitId);
                _lostSightTimers.Remove(unitId);
                _lastKnownPositions.Remove(unitId);
            }
        }

        public void TargetArrested(string unitId)
        {
            if (_pursuits.ContainsKey(unitId))
            {
                _pursuits[unitId] = PursuitState.TargetArrested;
                _pursuits.Remove(unitId);
            }
        }

        public PursuitState GetPursuitState(string unitId)
        {
            _pursuits.TryGetValue(unitId, out var state);
            return state;
        }

        public bool IsInPursuit(string unitId)
        {
            return _pursuits.ContainsKey(unitId) &&
                   _pursuits[unitId] != PursuitState.PursuitTerminated &&
                   _pursuits[unitId] != PursuitState.TargetArrested;
        }

        public Vector3 GetLastKnownPosition(string unitId)
        {
            _lastKnownPositions.TryGetValue(unitId, out var pos);
            return pos;
        }

        public float GetPursuitDuration(string unitId)
        {
            _pursuitTimers.TryGetValue(unitId, out float timer);
            return timer;
        }

        public float GetPursuitSpeedMultiplier(string unitId, float wantedLevelStars)
        {
            float baseMultiplier = 1f;
            float starsBonus = wantedLevelStars * 0.1f;
            float timerPenalty = GetPursuitDuration(unitId) * 0.005f;
            return Mathf.Clamp(baseMultiplier + starsBonus - timerPenalty, 0.7f, 1.5f);
        }

        public Vector3 CalculateInterceptPosition(Vector3 unitPos, Vector3 targetPos, Vector3 targetVelocity, float unitSpeed)
        {
            Vector3 toTarget = targetPos - unitPos;
            float distance = toTarget.magnitude;
            float timeToReach = distance / Mathf.Max(unitSpeed, 1f);
            Vector3 predictedPos = targetPos + targetVelocity * timeToReach;
            return predictedPos;
        }

        public Vector3 CalculateRamDirection(Vector3 unitPos, Vector3 unitForward, Vector3 targetPos)
        {
            Vector3 toTarget = (targetPos - unitPos).normalized;
            return Vector3.Lerp(unitForward, toTarget, 0.7f).normalized;
        }

        public bool ShouldUsePITManeuver(string unitId, float unitSpeed, float targetSpeed)
        {
            if (!IsInPursuit(unitId)) return false;

            float speedDiff = Mathf.Abs(unitSpeed - targetSpeed);
            return speedDiff < 10f &&
                   unitSpeed > _config.pursuitPITManeuverMinSpeed &&
                   unitSpeed < _config.pursuitPITManeuverMaxSpeed;
        }

        private bool IsPursuitExpired(string unitId)
        {
            _pursuitTimers.TryGetValue(unitId, out float timer);
            return timer > _config.pursuitMaxDuration;
        }

        private bool TimerTransition(string unitId, PursuitState from, PursuitState to, float delay)
        {
            if (!_pursuits.ContainsKey(unitId) || _pursuits[unitId] != from) return false;
            _pursuits[unitId] = to;
            return true;
        }

        public void ClearAll()
        {
            _pursuits.Clear();
            _pursuitTimers.Clear();
            _lostSightTimers.Clear();
            _lastKnownPositions.Clear();
        }
    }
}
