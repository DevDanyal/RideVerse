using UnityEngine;
using RideVerse.Traffic.Core;

namespace RideVerse.Traffic.Behaviors
{
    public class CollisionAvoidance : MonoBehaviour
    {
        private TrafficConfig _config;
        private bool _isEmergencyBraking;
        private bool _isFollowing;
        private float _followDistance;
        private TrafficVehicle _vehicleAhead;

        public bool IsEmergencyBrakingState => _isEmergencyBraking;
        public bool IsFollowingState => _isFollowing;
        public TrafficVehicle VehicleAhead => _vehicleAhead;

        public void Initialize(TrafficConfig config)
        {
            _config = config;
        }

        public bool IsEmergencyBraking(TrafficVehicle vehicle)
        {
            _vehicleAhead = DetectVehicleAhead(vehicle);

            if (_vehicleAhead == null)
            {
                _isEmergencyBraking = false;
                return false;
            }

            _followDistance = vehicle.DistanceAlongForward(_vehicleAhead.Position);

            if (_followDistance < _config.emergencyStopDistance && vehicle.CurrentSpeed > 5f)
            {
                _isEmergencyBraking = true;
                return true;
            }

            _isEmergencyBraking = false;
            return false;
        }

        public bool IsFollowingVehicle(TrafficVehicle vehicle)
        {
            if (_vehicleAhead == null)
            {
                _vehicleAhead = DetectVehicleAhead(vehicle);
            }

            if (_vehicleAhead == null)
            {
                _isFollowing = false;
                return false;
            }

            _followDistance = vehicle.DistanceAlongForward(_vehicleAhead.Position);

            if (_followDistance < _config.frontDetectionRange && _followDistance > _config.emergencyStopDistance)
            {
                _isFollowing = true;
                return true;
            }

            _isFollowing = false;
            return false;
        }

        public float GetSafeFollowSpeed(TrafficVehicle vehicle)
        {
            if (_vehicleAhead == null || _followDistance <= 0f)
                return vehicle.MaxSpeed;

            float safeSpeed = _vehicleAhead.CurrentSpeed;
            float distanceRatio = _followDistance / _config.frontDetectionRange;

            if (_followDistance < _config.minFollowDistance)
            {
                safeSpeed = Mathf.Min(safeSpeed, _vehicleAhead.CurrentSpeed * 0.5f);
            }
            else if (distanceRatio < 0.5f)
            {
                safeSpeed = Mathf.Lerp(_vehicleAhead.CurrentSpeed * 0.7f, _vehicleAhead.CurrentSpeed, distanceRatio);
            }

            return Mathf.Clamp(safeSpeed, 0f, vehicle.MaxSpeed);
        }

        public bool IsPedestrianAhead(TrafficVehicle vehicle)
        {
            RaycastHit hit;
            if (Physics.SphereCast(vehicle.Position + Vector3.up * 0.5f, 0.5f, vehicle.Forward, out hit, _config.pedestrianDetectionRange))
            {
                if (hit.collider.CompareTag("Player") || hit.collider.GetComponent<CharacterController>() != null)
                {
                    float lateralDist = Mathf.Abs(vehicle.LateralDistanceTo(hit.point));
                    if (lateralDist < _config.laneWidth)
                        return true;
                }
            }

            return false;
        }

        public bool IsRoadBlocked(TrafficVehicle vehicle)
        {
            RaycastHit hit;
            if (Physics.Raycast(vehicle.Position + Vector3.up * 0.3f, vehicle.Forward, out hit, _config.frontDetectionRange))
            {
                if (hit.collider.GetComponent<TrafficVehicle>() != null &&
                    hit.collider.gameObject != vehicle.gameObject)
                {
                    return true;
                }

                if (hit.collider.isTrigger == false &&
                    hit.collider.GetComponent<TrafficVehicle>() == null)
                {
                    float lateralDist = Mathf.Abs(vehicle.LateralDistanceTo(hit.point));
                    if (lateralDist < vehicle.Width * 0.5f)
                        return true;
                }
            }

            return false;
        }

        public TrafficVehicle DetectVehicleAhead(TrafficVehicle vehicle)
        {
            TrafficVehicle closest = null;
            float closestDist = _config.frontDetectionRange;

            Collider[] hits = Physics.OverlapBox(
                vehicle.Position + vehicle.Forward * (_config.frontDetectionRange * 0.5f),
                new Vector3(vehicle.Width, 1.5f, _config.frontDetectionRange * 0.5f),
                vehicle.transform.rotation);

            foreach (var hit in hits)
            {
                if (hit.gameObject == vehicle.gameObject) continue;

                var otherVehicle = hit.GetComponent<TrafficVehicle>();
                if (otherVehicle == null) continue;

                float forwardDist = vehicle.DistanceAlongForward(otherVehicle.Position);
                float lateralDist = Mathf.Abs(vehicle.LateralDistanceTo(otherVehicle.Position));

                if (forwardDist > 0f && forwardDist < closestDist && lateralDist < _config.laneWidth)
                {
                    closestDist = forwardDist;
                    closest = otherVehicle;
                }
            }

            return closest;
        }

        public TrafficVehicle DetectVehicleBehind(TrafficVehicle vehicle)
        {
            TrafficVehicle closest = null;
            float closestDist = _config.rearDetectionRange;

            Collider[] hits = Physics.OverlapBox(
                vehicle.Position - vehicle.Forward * (_config.rearDetectionRange * 0.5f),
                new Vector3(vehicle.Width, 1.5f, _config.rearDetectionRange * 0.5f),
                vehicle.transform.rotation);

            foreach (var hit in hits)
            {
                if (hit.gameObject == vehicle.gameObject) continue;

                var otherVehicle = hit.GetComponent<TrafficVehicle>();
                if (otherVehicle == null) continue;

                float rearDist = -vehicle.DistanceAlongForward(otherVehicle.Position);
                float lateralDist = Mathf.Abs(vehicle.LateralDistanceTo(otherVehicle.Position));

                if (rearDist > 0f && rearDist < closestDist && lateralDist < _config.laneWidth)
                {
                    closestDist = rearDist;
                    closest = otherVehicle;
                }
            }

            return closest;
        }

        public bool IsVehicleAlongside(TrafficVehicle vehicle, float range)
        {
            Collider[] hits = Physics.OverlapSphere(vehicle.Position, range);

            foreach (var hit in hits)
            {
                if (hit.gameObject == vehicle.gameObject) continue;

                var otherVehicle = hit.GetComponent<TrafficVehicle>();
                if (otherVehicle == null) continue;

                float forwardDist = Mathf.Abs(vehicle.DistanceAlongForward(otherVehicle.Position));
                float lateralDist = Mathf.Abs(vehicle.LateralDistanceTo(otherVehicle.Position));

                if (forwardDist < vehicle.Length && lateralDist < _config.laneWidth * 2f && lateralDist > vehicle.Width * 0.5f)
                    return true;
            }

            return false;
        }
    }
}
