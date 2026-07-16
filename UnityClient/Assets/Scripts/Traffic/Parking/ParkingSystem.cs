using UnityEngine;
using RideVerse.Traffic.Core;
using RideVerse.Traffic.Behaviors;

namespace RideVerse.Traffic.Parking
{
    public class ParkingSystem : MonoBehaviour
    {
        private TrafficConfig _config;
        private ParkingState _parkingState;
        private Vector3 _parkingSpotPosition;
        private float _parkingSpotRotation;
        private float _parkingTimer;
        private float _unparkTimer;
        private float _parkedDuration;
        private float _maxParkedDuration;

        public ParkingState State => _parkingState;
        public Vector3 ParkingSpotPosition => _parkingSpotPosition;

        public void Initialize(TrafficConfig config)
        {
            _config = config;
            _parkingState = ParkingState.None;
            _maxParkedDuration = Random.Range(30f, 120f);
        }

        public bool ShouldPark(TrafficVehicle vehicle)
        {
            if (_parkingState != ParkingState.None) return false;
            if (vehicle.IsEmergency) return false;
            if (vehicle.CurrentSpeed > 5f) return false;

            if (Random.value > _config.incidentSpawnChance * 0.5f) return false;

            Vector3 spot;
            float rotation;
            if (FindParkingSpot(vehicle, out spot, out rotation))
            {
                _parkingSpotPosition = spot;
                _parkingSpotRotation = rotation;
                _parkingState = ParkingState.Searching;
                _parkingTimer = 0f;
                return true;
            }

            return false;
        }

        public bool ExecuteParkingManeuver(TrafficVehicle vehicle, float deltaTime)
        {
            _parkingTimer += deltaTime;

            switch (_parkingState)
            {
                case ParkingState.Searching:
                    return ExecuteSearch(vehicle, deltaTime);
                case ParkingState.Approaching:
                    return ExecuteApproach(vehicle, deltaTime);
                case ParkingState.Maneuvering:
                    return ExecuteManeuver(vehicle, deltaTime);
                case ParkingState.Parked:
                    return ExecuteParked(vehicle, deltaTime);
                default:
                    return true;
            }
        }

        public bool ExecuteUnpark(TrafficVehicle vehicle, float deltaTime)
        {
            _unparkTimer += deltaTime;

            Vector3 exitDir = -(_parkingSpotPosition - vehicle.Position).normalized;
            exitDir.y = 0f;

            float exitSpeed = Mathf.Lerp(0f, _config.parkingSpeed, _unparkTimer / 3f);
            vehicle.SetTargetSpeed(exitSpeed);
            vehicle.ApplyMovement(exitDir, exitSpeed, deltaTime);

            if (_unparkTimer >= 3f)
            {
                _unparkTimer = 0f;
                _parkingState = ParkingState.None;
                return true;
            }

            return false;
        }

        private bool ExecuteSearch(TrafficVehicle vehicle, float deltaTime)
        {
            float dist = Vector3.Distance(vehicle.Position, _parkingSpotPosition);

            if (dist < 10f)
            {
                _parkingState = ParkingState.Approaching;
                return false;
            }

            Vector3 direction = (_parkingSpotPosition - vehicle.Position).normalized;
            direction.y = 0f;

            vehicle.SetTargetSpeed(_config.parkingApproachSpeed);
            vehicle.ApplyMovement(direction, vehicle.CurrentSpeed, deltaTime);

            return false;
        }

        private bool ExecuteApproach(TrafficVehicle vehicle, float deltaTime)
        {
            float dist = Vector3.Distance(vehicle.Position, _parkingSpotPosition);

            if (dist < 2f)
            {
                _parkingState = ParkingState.Maneuvering;
                _parkingTimer = 0f;
                return false;
            }

            Vector3 direction = (_parkingSpotPosition - vehicle.Position).normalized;
            direction.y = 0f;

            float approachSpeed = Mathf.Lerp(_config.parkingManeuverSpeed, _config.parkingApproachSpeed, dist / 10f);
            vehicle.SetTargetSpeed(approachSpeed);
            vehicle.ApplyMovement(direction, vehicle.CurrentSpeed, deltaTime);

            Quaternion targetRot = Quaternion.Euler(0f, _parkingSpotRotation, 0f);
            vehicle.transform.rotation = Quaternion.Slerp(vehicle.transform.rotation, targetRot, deltaTime * 3f);

            return false;
        }

        private bool ExecuteManeuver(TrafficVehicle vehicle, float deltaTime)
        {
            _parkingTimer += deltaTime;

            vehicle.SetTargetSpeed(_config.parkingManeuverSpeed);

            Quaternion targetRot = Quaternion.Euler(0f, _parkingSpotRotation, 0f);
            vehicle.transform.rotation = Quaternion.Slerp(vehicle.transform.rotation, targetRot, deltaTime * 5f);

            Vector3 direction = (_parkingSpotPosition - vehicle.Position).normalized;
            direction.y = 0f;

            float dist = Vector3.Distance(vehicle.Position, _parkingSpotPosition);
            if (dist > 0.5f)
            {
                vehicle.ApplyMovement(direction, _config.parkingManeuverSpeed, deltaTime);
            }
            else
            {
                vehicle.Stop();
                _parkingState = ParkingState.Parked;
                _parkingTimer = 0f;
                _maxParkedDuration = Random.Range(30f, 120f);
            }

            if (_parkingTimer > 10f)
            {
                vehicle.Stop();
                _parkingState = ParkingState.Parked;
                _parkingTimer = 0f;
            }

            return false;
        }

        private bool ExecuteParked(TrafficVehicle vehicle, float deltaTime)
        {
            _parkedDuration += deltaTime;

            if (_parkedDuration >= _maxParkedDuration)
            {
                _parkedDuration = 0f;
                _parkingState = ParkingState.Exiting;
                _unparkTimer = 0f;
                return false;
            }

            vehicle.Stop();
            return false;
        }

        private bool FindParkingSpot(TrafficVehicle vehicle, out Vector3 spot, out float rotation)
        {
            Vector3[] directions = {
                vehicle.Forward,
                -vehicle.Forward,
                vehicle.transform.right,
                -vehicle.transform.right
            };

            foreach (var dir in directions)
            {
                for (float dist = 5f; dist <= _config.parkingDetectRange; dist += 5f)
                {
                    Vector3 checkPos = vehicle.Position + dir * dist;

                    if (IsParkingSpotValid(checkPos))
                    {
                        spot = checkPos;
                        rotation = Quaternion.LookRotation(-dir).eulerAngles.y;
                        return true;
                    }
                }
            }

            spot = Vector3.zero;
            rotation = 0f;
            return false;
        }

        private bool IsParkingSpotValid(Vector3 position)
        {
            Collider[] overlaps = Physics.OverlapBox(
                position,
                new Vector3(_config.parkingSpotWidth * 0.5f, 1f, _config.parkingSpotDepth * 0.5f));

            foreach (var overlap in overlaps)
            {
                if (overlap.GetComponent<TrafficVehicle>() != null)
                    return false;
            }

            return true;
        }

        public void ResetState()
        {
            _parkingState = ParkingState.None;
            _parkingTimer = 0f;
            _unparkTimer = 0f;
            _parkedDuration = 0f;
        }
    }
}
