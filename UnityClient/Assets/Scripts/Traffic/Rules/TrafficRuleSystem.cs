using System.Collections.Generic;
using UnityEngine;
using RideVerse.Traffic.Core;
using RideVerse.Traffic.Behaviors;
using RideVerse.World.Environment;

namespace RideVerse.Traffic.Rules
{
    public class TrafficRuleSystem : MonoBehaviour
    {
        private TrafficConfig _config;
        private float _stopTimer;
        private bool _hasStoppedAtSign;
        private float _roundaboutTimer;
        private int _roundaboutEntryCount;

        public void Initialize(TrafficConfig config)
        {
            _config = config;
        }

        public TrafficAIBehaviorState? CheckRules(TrafficVehicle vehicle)
        {
            var lightState = CheckTrafficLights(vehicle);
            if (lightState.HasValue) return lightState.Value;

            var stopState = CheckStopSigns(vehicle);
            if (stopState.HasValue) return stopState.Value;

            var roundaboutState = CheckRoundabouts(vehicle);
            if (roundaboutState.HasValue) return roundaboutState.Value;

            return null;
        }

        private TrafficAIBehaviorState? CheckTrafficLights(TrafficVehicle vehicle)
        {
            TrafficLight nearestLight = FindNearestTrafficLight(vehicle);

            if (nearestLight == null) return null;

            float distance = Vector3.Distance(vehicle.Position, nearestLight.transform.position);

            if (distance > _config.trafficLightDetectRange) return null;

            if (nearestLight.IsGreen)
            {
                return TrafficAIBehaviorState.FollowingLane;
            }

            if (nearestLight.IsYellow)
            {
                if (vehicle.CurrentSpeed > _config.yellowLightDecisionSpeed)
                {
                    float stoppingDistance = (vehicle.CurrentSpeed * vehicle.CurrentSpeed) / (2f * _config.normalDeceleration);
                    if (distance > stoppingDistance + _config.stopAtLightBuffer)
                    {
                        return TrafficAIBehaviorState.StoppingAtLight;
                    }
                    else
                    {
                        return TrafficAIBehaviorState.FollowingLane;
                    }
                }
                return TrafficAIBehaviorState.StoppingAtLight;
            }

            if (nearestLight.IsRed)
            {
                if (distance < _config.stopAtLightBuffer + vehicle.Length)
                {
                    return TrafficAIBehaviorState.WaitingAtLight;
                }
                return TrafficAIBehaviorState.StoppingAtLight;
            }

            return null;
        }

        private TrafficAIBehaviorState? CheckStopSigns(TrafficVehicle vehicle)
        {
            if (vehicle.CurrentSpeed < 1f && _hasStoppedAtSign)
            {
                _stopTimer += Time.deltaTime;
                if (_stopTimer >= _config.stopDuration)
                {
                    _stopTimer = 0f;
                    _hasStoppedAtSign = false;
                    return TrafficAIBehaviorState.FollowingLane;
                }
                return TrafficAIBehaviorState.StoppedAtStopSign;
            }

            float distToStopSign = FindDistanceToStopSign(vehicle);
            if (distToStopSign < 0f) return null;

            if (distToStopSign <= _config.stopSignDetectRange)
            {
                if (distToStopSign <= _config.stopAtLightBuffer + vehicle.Length * 0.5f)
                {
                    _hasStoppedAtSign = true;
                    _stopTimer = 0f;
                    return TrafficAIBehaviorState.StoppedAtStopSign;
                }

                return TrafficAIBehaviorState.ApproachingStopSign;
            }

            return null;
        }

        private TrafficAIBehaviorState? CheckRoundabouts(TrafficVehicle vehicle)
        {
            float distToRoundabout = FindDistanceToRoundabout(vehicle);
            if (distToRoundabout < 0f) return null;

            if (distToRoundabout <= _config.roundaboutYieldRange)
            {
                if (!IsRoundaboutClear(vehicle))
                {
                    return TrafficAIBehaviorState.ApproachingRoundabout;
                }
            }

            if (distToRoundabout < _config.roundaboutYieldRange * 2f)
            {
                return TrafficAIBehaviorState.ApproachingRoundabout;
            }

            return null;
        }

        public float GetApproachSpeed(TrafficVehicle vehicle)
        {
            TrafficLight light = FindNearestTrafficLight(vehicle);
            if (light == null) return vehicle.MaxSpeed;

            float distance = Vector3.Distance(vehicle.Position, light.transform.position);
            return Mathf.Clamp(distance * 2f, 0f, vehicle.MaxSpeed);
        }

        public bool CanProceedFromStopSign(TrafficVehicle vehicle)
        {
            return _stopTimer >= _config.stopDuration;
        }

        public bool ExecuteRoundabout(TrafficVehicle vehicle, float deltaTime)
        {
            _roundaboutTimer += deltaTime;

            vehicle.SetTargetSpeed(_config.roundaboutCirculatingSpeed);

            Vector3 direction = vehicle.Forward;
            Vector3 right = Vector3.Cross(Vector3.up, direction);
            Vector3 roundaboutCenter = FindNearestRoundaboutCenter(vehicle);

            if (roundaboutCenter.sqrMagnitude > 0.01f)
            {
                Vector3 toCenter = (roundaboutCenter - vehicle.Position).normalized;
                toCenter.y = 0f;
                direction = Vector3.Cross(Vector3.up, toCenter);
            }

            vehicle.ApplyMovement(direction, vehicle.CurrentSpeed, deltaTime);

            if (_roundaboutTimer >= 5f)
            {
                _roundaboutTimer = 0f;
                return true;
            }

            return false;
        }

        private TrafficLight FindNearestTrafficLight(TrafficVehicle vehicle)
        {
            TrafficLight nearest = null;
            float nearestDist = _config.trafficLightDetectRange;

            Collider[] hits = Physics.OverlapSphere(vehicle.Position, _config.trafficLightDetectRange);

            foreach (var hit in hits)
            {
                var light = hit.GetComponent<TrafficLight>();
                if (light != null && light.IsActive)
                {
                    float dist = Vector3.Distance(vehicle.Position, hit.transform.position);
                    if (dist < nearestDist)
                    {
                        float dot = Vector3.Dot(vehicle.Forward, (hit.transform.position - vehicle.Position).normalized);
                        if (dot > 0.3f)
                        {
                            nearestDist = dist;
                            nearest = light;
                        }
                    }
                }
            }

            return nearest;
        }

        private float FindDistanceToStopSign(TrafficVehicle vehicle)
        {
            Collider[] hits = Physics.OverlapSphere(vehicle.Position, _config.stopSignDetectRange);

            foreach (var hit in hits)
            {
                if (hit.CompareTag("StopSign"))
                {
                    float dist = Vector3.Distance(vehicle.Position, hit.transform.position);
                    float dot = Vector3.Dot(vehicle.Forward, (hit.transform.position - vehicle.Position).normalized);

                    if (dot > 0.5f)
                        return dist;
                }
            }

            return -1f;
        }

        private float FindDistanceToRoundabout(TrafficVehicle vehicle)
        {
            Collider[] hits = Physics.OverlapSphere(vehicle.Position, _config.roundaboutYieldRange * 3f);

            foreach (var hit in hits)
            {
                if (hit.CompareTag("Roundabout"))
                {
                    return Vector3.Distance(vehicle.Position, hit.transform.position);
                }
            }

            return -1f;
        }

        private bool IsRoundaboutClear(TrafficVehicle vehicle)
        {
            Collider[] hits = Physics.OverlapSphere(vehicle.Position, _config.roundaboutYieldRange);

            foreach (var hit in hits)
            {
                if (hit.gameObject == vehicle.gameObject) continue;

                var otherVehicle = hit.GetComponent<TrafficVehicle>();
                if (otherVehicle != null)
                {
                    float dist = Vector3.Distance(vehicle.Position, otherVehicle.Position);
                    if (dist < _config.roundaboutYieldRange)
                        return false;
                }
            }

            return true;
        }

        private Vector3 FindNearestRoundaboutCenter(TrafficVehicle vehicle)
        {
            Collider[] hits = Physics.OverlapSphere(vehicle.Position, _config.roundaboutYieldRange * 3f);

            foreach (var hit in hits)
            {
                if (hit.CompareTag("Roundabout"))
                {
                    return hit.transform.position;
                }
            }

            return Vector3.zero;
        }

        public void ResetState()
        {
            _stopTimer = 0f;
            _hasStoppedAtSign = false;
            _roundaboutTimer = 0f;
            _roundaboutEntryCount = 0;
        }
    }
}
