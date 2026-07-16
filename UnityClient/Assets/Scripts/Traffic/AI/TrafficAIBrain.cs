using System;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.Traffic.Core;
using RideVerse.Traffic.Navigation;
using RideVerse.Traffic.Behaviors;
using RideVerse.Traffic.Rules;
using RideVerse.Traffic.Parking;
using RideVerse.Traffic.Emergency;

namespace RideVerse.Traffic.AI
{
    [RequireComponent(typeof(TrafficVehicle))]
    public class TrafficAIBrain : MonoBehaviour
    {
        private TrafficVehicle _vehicle;
        private TrafficConfig _config;
        private LaneController _laneController;
        private OvertakeController _overtakeController;
        private CollisionAvoidance _collisionAvoidance;
        private SpeedController _speedController;
        private TrafficRuleSystem _ruleSystem;
        private ParkingSystem _parkingSystem;
        private EmergencySystem _emergencySystem;
        private RoadNetwork _roadNetwork;
        private TrafficPathfinder _pathfinder;

        private TrafficAIBehaviorState _currentState;
        private TrafficAIBehaviorState _previousState;
        private List<Vector3> _currentPath;
        private int _currentPathIndex;
        private float _stateTimer;
        private float _decisionTimer;
        private float _decisionInterval = 0.5f;
        private bool _isInitialized;
        private bool _shouldPark;

        public TrafficVehicle Vehicle => _vehicle;
        public TrafficAIBehaviorState CurrentState => _currentState;
        public TrafficAIBehaviorState PreviousState => _previousState;
        public bool IsInitialized => _isInitialized;

        public event Action<TrafficAIBrain, TrafficAIBehaviorState> OnStateChanged;

        public void Initialize(TrafficConfig config, RoadNetwork roadNetwork)
        {
            _vehicle = GetComponent<TrafficVehicle>();
            _config = config;
            _roadNetwork = roadNetwork;
            _pathfinder = new TrafficPathfinder(roadNetwork);

            _laneController = gameObject.AddComponent<LaneController>();
            _laneController.Initialize(_config);

            _overtakeController = gameObject.AddComponent<OvertakeController>();
            _overtakeController.Initialize(_config);

            _collisionAvoidance = gameObject.AddComponent<CollisionAvoidance>();
            _collisionAvoidance.Initialize(_config);

            _speedController = gameObject.AddComponent<SpeedController>();
            _speedController.Initialize(_config);

            _ruleSystem = GetComponent<TrafficRuleSystem>();
            if (_ruleSystem == null)
                _ruleSystem = gameObject.AddComponent<TrafficRuleSystem>();
            _ruleSystem.Initialize(_config);

            _parkingSystem = GetComponent<ParkingSystem>();
            if (_parkingSystem == null)
                _parkingSystem = gameObject.AddComponent<ParkingSystem>();
            _parkingSystem.Initialize(_config);

            _emergencySystem = GetComponent<EmergencySystem>();
            if (_emergencySystem == null)
                _emergencySystem = gameObject.AddComponent<EmergencySystem>();
            _emergencySystem.Initialize(_config);

            _isInitialized = true;
            ChangeState(TrafficAIBehaviorState.FollowingLane);
        }

        private void Update()
        {
            if (!_isInitialized || !_vehicle.IsActive) return;

            _stateTimer += Time.deltaTime;
            _decisionTimer += Time.deltaTime;

            if (_decisionTimer >= _decisionInterval)
            {
                _decisionTimer = 0f;
                EvaluateBehavior();
            }

            ExecuteState();
        }

        private void EvaluateBehavior()
        {
            if (_vehicle.IsEmergency)
            {
                if (_emergencySystem != null && _emergencySystem.ShouldYield(_vehicle))
                {
                    ChangeState(TrafficAIBehaviorState.YieldingToEmergency);
                    return;
                }
            }

            var avoidanceState = CheckCollisionAvoidance();
            if (avoidanceState.HasValue)
            {
                ChangeState(avoidanceState.Value);
                return;
            }

            if (_vehicle.IsEmergency)
            {
                _vehicle.SetTargetSpeed(_config.emergencyVehicleSpeed);
                ChangeState(TrafficAIBehaviorState.Cruising);
                return;
            }

            if (_ruleSystem != null)
            {
                var ruleState = _ruleSystem.CheckRules(_vehicle);
                if (ruleState.HasValue)
                {
                    ChangeState(ruleState.Value);
                    return;
                }
            }

            if (_parkingSystem != null && _parkingSystem.ShouldPark(_vehicle))
            {
                ChangeState(TrafficAIBehaviorState.Parking);
                return;
            }

            if (_overtakeController != null && _overtakeController.ShouldOvertake(_vehicle))
            {
                ChangeState(TrafficAIBehaviorState.Overtaking);
                return;
            }

            if (_laneController != null && _laneController.ShouldChangeLane(_vehicle))
            {
                ChangeState(TrafficAIBehaviorState.LaneChanging);
                return;
            }

            if (_currentState != TrafficAIBehaviorState.FollowingLane &&
                _currentState != TrafficAIBehaviorState.Cruising)
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
            }
        }

        private TrafficAIBehaviorState? CheckCollisionAvoidance()
        {
            if (_collisionAvoidance == null) return null;

            if (_collisionAvoidance.IsEmergencyBraking(_vehicle))
                return TrafficAIBehaviorState.EmergencyBraking;

            if (_collisionAvoidance.IsFollowingVehicle(_vehicle))
                return TrafficAIBehaviorState.FollowingTraffic;

            return null;
        }

        private void ExecuteState()
        {
            switch (_currentState)
            {
                case TrafficAIBehaviorState.Idle:
                    ExecuteIdle();
                    break;
                case TrafficAIBehaviorState.FollowingLane:
                    ExecuteFollowingLane();
                    break;
                case TrafficAIBehaviorState.ApproachingLight:
                case TrafficAIBehaviorState.StoppingAtLight:
                case TrafficAIBehaviorState.WaitingAtLight:
                    ExecuteTrafficLight();
                    break;
                case TrafficAIBehaviorState.ApproachingStopSign:
                case TrafficAIBehaviorState.StoppedAtStopSign:
                    ExecuteStopSign();
                    break;
                case TrafficAIBehaviorState.LaneChanging:
                    ExecuteLaneChange();
                    break;
                case TrafficAIBehaviorState.Overtaking:
                    ExecuteOvertake();
                    break;
                case TrafficAIBehaviorState.EmergencyBraking:
                    ExecuteEmergencyBrake();
                    break;
                case TrafficAIBehaviorState.FollowingTraffic:
                    ExecuteFollowTraffic();
                    break;
                case TrafficAIBehaviorState.Parking:
                    ExecuteParking();
                    break;
                case TrafficAIBehaviorState.Unparking:
                    ExecuteUnparking();
                    break;
                case TrafficAIBehaviorState.YieldingToEmergency:
                    ExecuteYieldEmergency();
                    break;
                case TrafficAIBehaviorState.Cruising:
                    ExecuteCruising();
                    break;
                case TrafficAIBehaviorState.ApproachingRoundabout:
                case TrafficAIBehaviorState.NavigatingRoundabout:
                    ExecuteRoundabout();
                    break;
            }
        }

        private void ExecuteIdle()
        {
            _vehicle.SetTargetSpeed(0f);
            _vehicle.ApplyBrake(_config.normalDeceleration, Time.deltaTime);
        }

        private void ExecuteFollowingLane()
        {
            float targetSpeed = _vehicle.MaxSpeed;
            if (_laneController != null)
                targetSpeed = Mathf.Min(targetSpeed, _laneController.GetLaneTargetSpeed(_vehicle));

            _vehicle.SetTargetSpeed(targetSpeed);
            _speedController?.SmoothAccelerate(_vehicle, targetSpeed, Time.deltaTime);

            Vector3 lanePosition = _laneController != null
                ? _laneController.GetDesiredPosition(_vehicle)
                : transform.position + transform.forward * 5f;

            Vector3 direction = (lanePosition - transform.position).normalized;
            direction.y = 0f;

            if (direction.sqrMagnitude > 0.01f)
            {
                _vehicle.ApplyMovement(direction, _vehicle.CurrentSpeed, Time.deltaTime);
            }
        }

        private void ExecuteTrafficLight()
        {
            if (_ruleSystem == null) return;

            switch (_currentState)
            {
                case TrafficAIBehaviorState.ApproachingLight:
                    float approachSpeed = _ruleSystem.GetApproachSpeed(_vehicle);
                    _vehicle.SetTargetSpeed(approachSpeed);
                    _speedController?.SmoothDecelerate(_vehicle, approachSpeed, Time.deltaTime);
                    break;

                case TrafficAIBehaviorState.StoppingAtLight:
                    _vehicle.SetTargetSpeed(0f);
                    _vehicle.ApplyBrake(_config.normalDeceleration, Time.deltaTime);
                    break;

                case TrafficAIBehaviorState.WaitingAtLight:
                    _vehicle.Stop();
                    break;
            }
        }

        private void ExecuteStopSign()
        {
            if (_ruleSystem == null) return;

            switch (_currentState)
            {
                case TrafficAIBehaviorState.ApproachingStopSign:
                    _vehicle.SetTargetSpeed(_config.stopSignApproachSpeed);
                    _speedController?.SmoothDecelerate(_vehicle, _config.stopSignApproachSpeed, Time.deltaTime);
                    break;

                case TrafficAIBehaviorState.StoppedAtStopSign:
                    _vehicle.Stop();
                    if (_ruleSystem.CanProceedFromStopSign(_vehicle))
                    {
                        ChangeState(TrafficAIBehaviorState.FollowingLane);
                    }
                    break;
            }
        }

        private void ExecuteLaneChange()
        {
            if (_laneController == null)
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
                return;
            }

            bool complete = _laneController.ExecuteLaneChange(_vehicle, Time.deltaTime);
            if (complete)
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
            }
        }

        private void ExecuteOvertake()
        {
            if (_overtakeController == null)
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
                return;
            }

            bool complete = _overtakeController.ExecuteOvertake(_vehicle, Time.deltaTime);
            if (complete)
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
            }
        }

        private void ExecuteEmergencyBrake()
        {
            _vehicle.SetTargetSpeed(0f);
            _vehicle.ApplyBrake(_config.emergencyBrakeDeceleration, Time.deltaTime);

            if (_collisionAvoidance != null && !_collisionAvoidance.IsEmergencyBraking(_vehicle))
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
            }
        }

        private void ExecuteFollowTraffic()
        {
            if (_collisionAvoidance == null)
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
                return;
            }

            float safeSpeed = _collisionAvoidance.GetSafeFollowSpeed(_vehicle);
            _vehicle.SetTargetSpeed(safeSpeed);
            _speedController?.SmoothDecelerate(_vehicle, safeSpeed, Time.deltaTime);

            Vector3 direction = transform.forward;
            _vehicle.ApplyMovement(direction, _vehicle.CurrentSpeed, Time.deltaTime);

            if (!_collisionAvoidance.IsFollowingVehicle(_vehicle))
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
            }
        }

        private void ExecuteParking()
        {
            if (_parkingSystem == null)
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
                return;
            }

            bool complete = _parkingSystem.ExecuteParkingManeuver(_vehicle, Time.deltaTime);
            if (complete)
            {
                if (_vehicle.CurrentSpeed < 0.1f)
                    ChangeState(TrafficAIBehaviorState.Idle);
                else
                    ChangeState(TrafficAIBehaviorState.FollowingLane);
            }
        }

        private void ExecuteUnparking()
        {
            if (_parkingSystem == null)
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
                return;
            }

            bool complete = _parkingSystem.ExecuteUnpark(_vehicle, Time.deltaTime);
            if (complete)
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
            }
        }

        private void ExecuteYieldEmergency()
        {
            _vehicle.SetTargetSpeed(0f);
            _vehicle.ApplyBrake(_config.normalDeceleration, Time.deltaTime);

            if (_emergencySystem != null && !_emergencySystem.IsEmergencyNearby(_vehicle))
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
            }
        }

        private void ExecuteCruising()
        {
            _speedController?.SmoothAccelerate(_vehicle, _vehicle.TargetSpeed, Time.deltaTime);

            Vector3 direction = transform.forward;
            _vehicle.ApplyMovement(direction, _vehicle.CurrentSpeed, Time.deltaTime);
        }

        private void ExecuteRoundabout()
        {
            if (_ruleSystem == null)
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
                return;
            }

            bool complete = _ruleSystem.ExecuteRoundabout(_vehicle, Time.deltaTime);
            if (complete)
            {
                ChangeState(TrafficAIBehaviorState.FollowingLane);
            }
        }

        private void ChangeState(TrafficAIBehaviorState newState)
        {
            if (newState == _currentState) return;

            _previousState = _currentState;
            _currentState = newState;
            _stateTimer = 0f;
            _vehicle.SetBehaviorState(newState);

            OnStateChanged?.Invoke(this, newState);
        }

        public void SetPath(List<Vector3> path)
        {
            _currentPath = path;
            _currentPathIndex = 0;
        }

        public void ForceState(TrafficAIBehaviorState state)
        {
            ChangeState(state);
        }
    }
}
