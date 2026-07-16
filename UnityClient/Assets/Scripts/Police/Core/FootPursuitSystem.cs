using UnityEngine;
using System.Collections.Generic;

namespace RideVerse.Police.Core
{
    public class FootPursuitSystem
    {
        private readonly PoliceConfig _config;
        private readonly Dictionary<string, FootPursuitData> _activePursuits;

        public int ActivePursuitCount => _activePursuits.Count;

        public FootPursuitSystem(PoliceConfig config)
        {
            _config = config;
            _activePursuits = new Dictionary<string, FootPursuitData>();
        }

        public void StartPursuit(string unitId, string targetId, Vector3 unitPosition)
        {
            _activePursuits[unitId] = new FootPursuitData
            {
                TargetId = targetId,
                StartPosition = unitPosition,
                Duration = 0f,
                LostSightTimer = 0f,
                LastKnownTargetPosition = unitPosition,
                IsTaserReady = true,
                TaserCooldown = 0f
            };
        }

        public void Update(float deltaTime, string unitId, Vector3 unitPosition, Vector3 targetPosition, bool canSeeTarget)
        {
            if (!_activePursuits.TryGetValue(unitId, out var data)) return;

            data.Duration += deltaTime;

            if (data.Duration > _config.footPursuitMaxDuration)
            {
                TerminatePursuit(unitId);
                return;
            }

            if (!canSeeTarget)
            {
                data.LostSightTimer += deltaTime;
                if (data.LostSightTimer >= _config.footPursuitLostSightTime)
                {
                    TerminatePursuit(unitId);
                    return;
                }
            }
            else
            {
                data.LostSightTimer = 0f;
                data.LastKnownTargetPosition = targetPosition;
            }

            if (!data.IsTaserReady)
            {
                data.TaserCooldown -= deltaTime;
                if (data.TaserCooldown <= 0f)
                {
                    data.IsTaserReady = true;
                }
            }
        }

        public bool CanTase(string unitId)
        {
            if (!_activePursuits.TryGetValue(unitId, out var data)) return false;
            return data.IsTaserReady;
        }

        public bool Tase(string unitId, Vector3 unitPos, Vector3 targetPos)
        {
            if (!CanTase(unitId)) return false;

            float distance = Vector3.Distance(unitPos, targetPos);
            if (distance > _config.footPursuitTaserRange) return false;

            _activePursuits[unitId].IsTaserReady = false;
            _activePursuits[unitId].TaserCooldown = _config.footPursuitTaserCooldown;
            return true;
        }

        public void TerminatePursuit(string unitId)
        {
            _activePursuits.Remove(unitId);
        }

        public bool IsInPursuit(string unitId)
        {
            return _activePursuits.ContainsKey(unitId);
        }

        public FootPursuitData GetPursuitData(string unitId)
        {
            _activePursuits.TryGetValue(unitId, out var data);
            return data;
        }

        public Vector3 GetLastKnownPosition(string unitId)
        {
            if (_activePursuits.TryGetValue(unitId, out var data))
            {
                return data.LastKnownTargetPosition;
            }
            return Vector3.zero;
        }

        public string GetTargetId(string unitId)
        {
            if (_activePursuits.TryGetValue(unitId, out var data))
            {
                return data.TargetId;
            }
            return null;
        }

        public float CalculatePursuitSpeed(string unitId, bool isTargetRunning)
        {
            if (!isTargetRunning) return _config.footPursuitSpeed;
            return _config.footPursuitSprintSpeed;
        }

        public Vector3 CalculateChaseDirection(Vector3 unitPos, Vector3 targetPos)
        {
            Vector3 dir = (targetPos - unitPos).normalized;
            dir.y = 0f;
            return dir.sqrMagnitude > 0.01f ? dir : Vector3.forward;
        }

        public bool IsWithinCatchDistance(Vector3 unitPos, Vector3 targetPos)
        {
            return Vector3.Distance(unitPos, targetPos) <= _config.footPursuitCatchDistance;
        }

        public bool IsWithinTaserRange(Vector3 unitPos, Vector3 targetPos)
        {
            return Vector3.Distance(unitPos, targetPos) <= _config.footPursuitTaserRange;
        }

        public void ClearAll()
        {
            _activePursuits.Clear();
        }

        public class FootPursuitData
        {
            public string TargetId;
            public Vector3 StartPosition;
            public float Duration;
            public float LostSightTimer;
            public Vector3 LastKnownTargetPosition;
            public bool IsTaserReady;
            public float TaserCooldown;
        }
    }
}
