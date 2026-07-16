using UnityEngine;
using RideVerse.Traffic.Core;

namespace RideVerse.Traffic.Behaviors
{
    public class SpeedController : MonoBehaviour
    {
        private TrafficConfig _config;
        private float _currentTargetSpeed;

        public float CurrentTargetSpeed => _currentTargetSpeed;

        public void Initialize(TrafficConfig config)
        {
            _config = config;
        }

        public void SmoothAccelerate(TrafficVehicle vehicle, float targetSpeed, float deltaTime)
        {
            _currentTargetSpeed = Mathf.Clamp(targetSpeed, 0f, vehicle.MaxSpeed);
            float currentSpeed = vehicle.CurrentSpeed;

            if (currentSpeed < _currentTargetSpeed)
            {
                float newSpeed = Mathf.MoveTowards(currentSpeed, _currentTargetSpeed, _config.smoothAcceleration * deltaTime);
                vehicle.SetCurrentSpeed(newSpeed);
            }
            else if (currentSpeed > _currentTargetSpeed)
            {
                SmoothDecelerate(vehicle, _currentTargetSpeed, deltaTime);
            }

            Vector3 direction = vehicle.Forward;
            vehicle.ApplyMovement(direction, vehicle.CurrentSpeed, deltaTime);
        }

        public void SmoothDecelerate(TrafficVehicle vehicle, float targetSpeed, float deltaTime)
        {
            _currentTargetSpeed = Mathf.Clamp(targetSpeed, 0f, vehicle.MaxSpeed);
            float currentSpeed = vehicle.CurrentSpeed;

            if (currentSpeed > _currentTargetSpeed)
            {
                float deceleration = _config.normalDeceleration;
                if (_currentTargetSpeed < 1f)
                    deceleration = _config.normalDeceleration * 1.5f;

                vehicle.ApplyBrake(deceleration, deltaTime);
            }
            else
            {
                vehicle.SetCurrentSpeed(_currentTargetSpeed);
            }
        }

        public void HardBrake(TrafficVehicle vehicle, float deltaTime)
        {
            vehicle.ApplyBrake(_config.emergencyBrakeDeceleration, deltaTime);
            _currentTargetSpeed = 0f;
        }

        public float CalculateApproachSpeed(TrafficVehicle vehicle, float distanceToTarget, float targetSpeed)
        {
            if (distanceToTarget <= 0f) return 0f;

            float requiredDeceleration = (vehicle.CurrentSpeed * vehicle.CurrentSpeed) / (2f * Mathf.Max(0.1f, distanceToTarget));
            float approachSpeed = vehicle.CurrentSpeed - requiredDeceleration * 0.8f;

            return Mathf.Clamp(approachSpeed, targetSpeed, vehicle.MaxSpeed);
        }

        public float CalculateSafeSpeedForWeather(TrafficVehicle vehicle, WeatherCondition weather)
        {
            float multiplier = 1f;

            switch (weather)
            {
                case WeatherCondition.Rain:
                    multiplier = 0.75f;
                    break;
                case WeatherCondition.HeavyRain:
                    multiplier = 0.55f;
                    break;
                case WeatherCondition.Fog:
                    multiplier = 0.6f;
                    break;
                case WeatherCondition.Storm:
                    multiplier = 0.4f;
                    break;
                case WeatherCondition.Snow:
                    multiplier = 0.45f;
                    break;
            }

            return vehicle.MaxSpeed * multiplier;
        }

        public float CalculateSafeSpeedForCurve(float curvature, float baseSpeed)
        {
            float curveFactor = Mathf.Clamp01(1f - curvature * 0.5f);
            return baseSpeed * curveFactor;
        }

        public float GetSpeedDifference(TrafficVehicle vehicle, TrafficVehicle other)
        {
            return vehicle.CurrentSpeed - other.CurrentSpeed;
        }

        public bool IsSpeedSafe(TrafficVehicle vehicle, float minSpeed, float maxSpeed)
        {
            return vehicle.CurrentSpeed >= minSpeed && vehicle.CurrentSpeed <= maxSpeed;
        }
    }
}
