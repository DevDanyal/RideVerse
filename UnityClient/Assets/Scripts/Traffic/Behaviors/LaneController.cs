using UnityEngine;
using RideVerse.Traffic.Core;

namespace RideVerse.Traffic.Behaviors
{
    public class LaneController : MonoBehaviour
    {
        private TrafficConfig _config;
        private int _targetLaneIndex;
        private int _currentLaneIndex;
        private float _laneChangeProgress;
        private bool _isChangingLane;
        private float _laneChangeStartOffset;
        private float _laneChangeTargetOffset;

        public int CurrentLaneIndex => _currentLaneIndex;
        public int TargetLaneIndex => _targetLaneIndex;
        public bool IsChangingLane => _isChangingLane;

        public void Initialize(TrafficConfig config)
        {
            _config = config;
            _currentLaneIndex = 1;
            _targetLaneIndex = 1;
        }

        public Vector3 GetDesiredPosition(TrafficVehicle vehicle)
        {
            Vector3 forward = vehicle.Forward;
            Vector3 right = Vector3.Cross(Vector3.up, forward);
            float laneOffset = (_currentLaneIndex - 1) * _config.laneWidth;

            if (_isChangingLane)
            {
                float t = _laneChangeProgress / _config.laneChangeDuration;
                t = Mathf.SmoothStep(0f, 1f, t);
                float currentOffset = Mathf.Lerp(_laneChangeStartOffset, _laneChangeTargetOffset, t);
                laneOffset = currentOffset;
            }

            return vehicle.Position + forward * 10f + right * laneOffset;
        }

        public float GetLaneTargetSpeed(TrafficVehicle vehicle)
        {
            return vehicle.MaxSpeed;
        }

        public bool ShouldChangeLane(TrafficVehicle vehicle)
        {
            if (_isChangingLane) return false;
            if (vehicle.CurrentSpeed < 5f) return false;

            if (vehicle.DistanceAlongForward(vehicle.Position + vehicle.Forward * _config.laneChangeMinGap) < _config.laneChangeMinGap)
            {
                int preferredLane = GetPreferredLane(vehicle);
                if (preferredLane != _currentLaneIndex && IsLaneSafe(vehicle, preferredLane))
                {
                    StartLaneChange(preferredLane);
                    return true;
                }
            }

            return false;
        }

        public bool ExecuteLaneChange(TrafficVehicle vehicle, float deltaTime)
        {
            if (!_isChangingLane) return true;

            _laneChangeProgress += deltaTime;

            if (_laneChangeProgress >= _config.laneChangeDuration)
            {
                _currentLaneIndex = _targetLaneIndex;
                _isChangingLane = false;
                _laneChangeProgress = 0f;
                vehicle.SetCurrentLane(_currentLaneIndex);
                return true;
            }

            float t = _laneChangeProgress / _config.laneChangeDuration;
            t = Mathf.SmoothStep(0f, 1f, t);

            Vector3 forward = vehicle.Forward;
            Vector3 right = Vector3.Cross(Vector3.up, forward);
            float currentOffset = Mathf.Lerp(_laneChangeStartOffset, _laneChangeTargetOffset, t);

            Vector3 desiredPos = vehicle.Position + forward * vehicle.CurrentSpeed * deltaTime + right * currentOffset * deltaTime;
            Vector3 direction = (desiredPos - vehicle.Position).normalized;
            direction.y = 0f;

            vehicle.ApplyMovement(direction, vehicle.CurrentSpeed, deltaTime);
            vehicle.SetLaneOffset(currentOffset);

            return false;
        }

        private int GetPreferredLane(TrafficVehicle vehicle)
        {
            if (_currentLaneIndex > 0) return _currentLaneIndex - 1;
            if (_currentLaneIndex < 2) return _currentLaneIndex + 1;
            return _currentLaneIndex;
        }

        private bool IsLaneSafe(TrafficVehicle vehicle, int targetLane)
        {
            float offset = (targetLane - _currentLaneIndex) * _config.laneWidth;
            Vector3 right = Vector3.Cross(Vector3.up, vehicle.Forward);
            Vector3 targetPos = vehicle.Position + right * offset;

            Collider[] hits = Physics.OverlapBox(
                targetPos + vehicle.Forward * (_config.laneChangeMinGap * 0.5f),
                new Vector3(_config.laneWidth * 0.4f, 1f, _config.laneChangeMinGap * 0.5f),
                vehicle.transform.rotation);

            foreach (var hit in hits)
            {
                if (hit.gameObject == vehicle.gameObject) continue;

                var otherVehicle = hit.GetComponent<TrafficVehicle>();
                if (otherVehicle != null)
                {
                    float lateralDist = Mathf.Abs(vehicle.LateralDistanceTo(otherVehicle.Position));
                    float forwardDist = vehicle.DistanceAlongForward(otherVehicle.Position);

                    if (lateralDist < _config.laneWidth && Mathf.Abs(forwardDist) < _config.laneChangeMinGap)
                        return false;
                }
            }

            return true;
        }

        private void StartLaneChange(int targetLane)
        {
            _targetLaneIndex = targetLane;
            _laneChangeStartOffset = (_currentLaneIndex - 1) * _config.laneWidth;
            _laneChangeTargetOffset = (targetLane - 1) * _config.laneWidth;
            _laneChangeProgress = 0f;
            _isChangingLane = true;
        }

        public void SetLane(int laneIndex)
        {
            _currentLaneIndex = Mathf.Clamp(laneIndex, 0, 2);
            _targetLaneIndex = _currentLaneIndex;
            _isChangingLane = false;
        }
    }
}
