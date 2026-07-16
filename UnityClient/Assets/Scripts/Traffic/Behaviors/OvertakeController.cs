using UnityEngine;
using RideVerse.Traffic.Core;

namespace RideVerse.Traffic.Behaviors
{
    public class OvertakeController : MonoBehaviour
    {
        private TrafficConfig _config;
        private bool _isOvertaking;
        private float _overtakeTimer;
        private float _overtakeDistanceTraveled;
        private TrafficVehicle _targetVehicle;

        public bool IsOvertaking => _isOvertaking;
        public TrafficVehicle TargetVehicle => _targetVehicle;

        public void Initialize(TrafficConfig config)
        {
            _config = config;
        }

        public bool ShouldOvertake(TrafficVehicle vehicle)
        {
            if (_isOvertaking) return false;
            if (vehicle.CurrentSpeed < vehicle.MaxSpeed * 0.3f) return false;
            if (vehicle.IsEmergency) return false;

            _targetVehicle = GetVehicleToOvertake(vehicle);
            if (_targetVehicle == null) return false;

            if (_targetVehicle.CurrentSpeed >= vehicle.MaxSpeed * 0.8f) return false;

            if (!IsOvertakeSafe(vehicle, _targetVehicle)) return false;

            StartOvertake();
            return true;
        }

        public bool ExecuteOvertake(TrafficVehicle vehicle, float deltaTime)
        {
            if (!_isOvertaking || _targetVehicle == null)
            {
                CancelOvertake();
                return true;
            }

            _overtakeTimer += deltaTime;
            _overtakeDistanceTraveled += vehicle.CurrentSpeed * deltaTime;

            float overtakeSpeed = Mathf.Min(vehicle.MaxSpeed, _targetVehicle.CurrentSpeed + _config.overtakeSpeedBoost);
            vehicle.SetTargetSpeed(overtakeSpeed);

            Vector3 direction = vehicle.Forward;
            Vector3 right = Vector3.Cross(Vector3.up, direction);

            float lateralOffset = GetOvertakeLateralOffset(vehicle, deltaTime);
            Vector3 targetPos = vehicle.Position + direction * vehicle.CurrentSpeed * deltaTime + right * lateralOffset;
            Vector3 moveDir = (targetPos - vehicle.Position).normalized;
            moveDir.y = 0f;

            vehicle.ApplyMovement(moveDir, vehicle.CurrentSpeed, deltaTime);

            if (_overtakeDistanceTraveled >= _config.overtakeReturnDistance ||
                _overtakeTimer >= _config.overtakeMaxDuration)
            {
                CancelOvertake();
                return true;
            }

            if (_targetVehicle.DistanceAlongForward(vehicle.Position) < -5f)
            {
                CancelOvertake();
                return true;
            }

            return false;
        }

        private void StartOvertake()
        {
            _isOvertaking = true;
            _overtakeTimer = 0f;
            _overtakeDistanceTraveled = 0f;
        }

        private void CancelOvertake()
        {
            _isOvertaking = false;
            _overtakeTimer = 0f;
            _overtakeDistanceTraveled = 0f;
            _targetVehicle = null;
        }

        private float GetOvertakeLateralOffset(TrafficVehicle vehicle, float deltaTime)
        {
            float progress = Mathf.Clamp01(_overtakeDistanceTraveled / _config.overtakeReturnDistance);
            float lateralTarget = _config.laneWidth;

            if (progress < 0.3f)
            {
                lateralTarget = Mathf.Lerp(0f, _config.laneWidth, progress / 0.3f);
            }
            else if (progress > 0.7f)
            {
                lateralTarget = Mathf.Lerp(_config.laneWidth, 0f, (progress - 0.7f) / 0.3f);
            }

            return lateralTarget * deltaTime * 2f;
        }

        private TrafficVehicle GetVehicleToOvertake(TrafficVehicle vehicle)
        {
            TrafficVehicle closest = null;
            float closestDist = _config.overtakeDetectionRange;

            Collider[] hits = Physics.OverlapBox(
                vehicle.Position + vehicle.Forward * (_config.overtakeDetectionRange * 0.5f),
                new Vector3(_config.laneWidth, 1.5f, _config.overtakeDetectionRange * 0.5f),
                vehicle.transform.rotation);

            foreach (var hit in hits)
            {
                if (hit.gameObject == vehicle.gameObject) continue;

                var otherVehicle = hit.GetComponent<TrafficVehicle>();
                if (otherVehicle == null || otherVehicle.IsEmergency) continue;

                float forwardDist = vehicle.DistanceAlongForward(otherVehicle.Position);
                float lateralDist = Mathf.Abs(vehicle.LateralDistanceTo(otherVehicle.Position));

                if (forwardDist > 0f && forwardDist < closestDist && lateralDist < _config.laneWidth * 1.5f)
                {
                    closestDist = forwardDist;
                    closest = otherVehicle;
                }
            }

            return closest;
        }

        private bool IsOvertakeSafe(TrafficVehicle vehicle, TrafficVehicle target)
        {
            Vector3 right = Vector3.Cross(Vector3.up, vehicle.Forward);
            Vector3 overtakePos = vehicle.Position + right * _config.laneWidth;

            Collider[] hits = Physics.OverlapSphere(overtakePos, _config.laneWidth);

            foreach (var hit in hits)
            {
                if (hit.gameObject == vehicle.gameObject || hit.gameObject == target.gameObject) continue;

                var nearbyVehicle = hit.GetComponent<TrafficVehicle>();
                if (nearbyVehicle != null)
                {
                    float dist = Vector3.Distance(overtakePos, nearbyVehicle.Position);
                    if (dist < _config.laneWidth * 2f)
                        return false;
                }
            }

            return true;
        }
    }
}
