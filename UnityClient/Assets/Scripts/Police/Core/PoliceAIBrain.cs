using UnityEngine;
using System.Collections.Generic;

namespace RideVerse.Police.Core
{
    [RequireComponent(typeof(CharacterController))]
    public class PoliceAIBrain : MonoBehaviour
    {
        [SerializeField] private PoliceConfig _config;

        private PoliceUnitData _unitData;
        private PoliceUnitState _state;
        private PolicePatrolRoute _patrolRoute;
        private float _aiTimer;
        private float _decisionTimer;
        private float _stateTimer;
        private bool _isInitialized;
        private CharacterController _characterController;
        private Vector3 _homeStationPosition;
        private float _currentSpeed;
        private bool _isInVehicle;
        private string _assignedCallId;
        private string _pursuitTargetId;
        private Vector3 _investigationTarget;
        private float _investigationTimer;
        private int _crimeCount;

        public PoliceUnitData UnitData => _unitData;
        public PoliceUnitState State => _state;
        public PoliceState CurrentState => _state.CurrentState;
        public bool IsInitialized => _isInitialized;
        public bool IsInVehicle => _isInVehicle;
        public Vector3 HomeStation => _homeStationPosition;
        public float CurrentSpeed => _currentSpeed;
        public string PursuitTargetId => _pursuitTargetId;

        public void Initialize(PoliceConfig config, PoliceUnitData data, Vector3 homePosition)
        {
            _config = config;
            _unitData = data;
            _homeStationPosition = homePosition;
            _characterController = GetComponent<CharacterController>();
            _patrolRoute = new PolicePatrolRoute(config);
            _state = new PoliceUnitState(data.UnitId);
            _isInVehicle = true;
            _currentSpeed = 0f;

            transform.position = data.SpawnPosition;
            transform.rotation = Quaternion.Euler(0f, data.SpawnRotation, 0f);

            _isInitialized = true;
            ChangeState(PoliceState.Patrolling);
        }

        private void Update()
        {
            if (!_isInitialized) return;

            _aiTimer += Time.deltaTime;
            _decisionTimer += Time.deltaTime;
            _stateTimer += Time.deltaTime;

            if (_decisionTimer >= _config.aiUpdateInterval)
            {
                _decisionTimer = 0f;
                EvaluateBehavior();
            }

            ExecuteState();
        }

        private void EvaluateBehavior()
        {
            switch (_state.CurrentState)
            {
                case PoliceState.Patrolling:
                    EvaluatePatrol();
                    break;
                case PoliceState.RespondingToCall:
                    EvaluateResponse();
                    break;
                case PoliceState.PursuingVehicle:
                    EvaluateVehiclePursuit();
                    break;
                case PoliceState.PursuingOnFoot:
                    EvaluateFootPursuit();
                    break;
                case PoliceState.Investigating:
                    EvaluateInvestigation();
                    break;
                case PoliceState.AttemptingArrest:
                    EvaluateArrest();
                    break;
                case PoliceState.ReturningToStation:
                    EvaluateReturnToStation();
                    break;
            }
        }

        private void EvaluatePatrol()
        {
            if (_patrolRoute == null || !_patrolRoute.HasRoute)
            {
                _patrolRoute.GeneratePatrolRoute(transform.position);
            }

            if (_patrolRoute.HasReachedCurrentWaypoint(transform.position))
            {
                _patrolRoute.AdvanceToNextWaypoint();
            }

            if (_patrolRoute.ShouldRegenerate())
            {
                _patrolRoute.GeneratePatrolRoute(transform.position);
            }
        }

        private void EvaluateResponse()
        {
            if (string.IsNullOrEmpty(_assignedCallId)) return;
        }

        private void EvaluateVehiclePursuit()
        {
        }

        private void EvaluateFootPursuit()
        {
        }

        private void EvaluateInvestigation()
        {
            _investigationTimer += _config.aiUpdateInterval;
            if (_investigationTimer >= _config.aiInvestigationDuration)
            {
                ChangeState(PoliceState.ReturningToStation);
            }
        }

        private void EvaluateArrest()
        {
            if (_stateTimer >= _config.arrestHandcuffTime)
            {
                ChangeState(PoliceState.EscortingToJail);
            }
        }

        private void EvaluateReturnToStation()
        {
            float distance = Vector3.Distance(transform.position, _homeStationPosition);
            if (distance <= _config.patrolWaypointReachDistance)
            {
                ChangeState(PoliceState.Patrolling);
            }
        }

        private void ExecuteState()
        {
            switch (_state.CurrentState)
            {
                case PoliceState.Patrolling:
                    ExecutePatrol();
                    break;
                case PoliceState.RespondingToCall:
                    ExecuteResponse();
                    break;
                case PoliceState.PursuingVehicle:
                    ExecuteVehiclePursuit();
                    break;
                case PoliceState.PursuingOnFoot:
                    ExecuteFootPursuit();
                    break;
                case PoliceState.Investigating:
                    ExecuteInvestigation();
                    break;
                case PoliceState.AttemptingArrest:
                    ExecuteArrest();
                    break;
                case PoliceState.ReturningToStation:
                    ExecuteReturnToStation();
                    break;
                case PoliceState.Idle:
                    ExecuteIdle();
                    break;
            }
        }

        private void ExecutePatrol()
        {
            if (!_patrolRoute.HasRoute) return;

            Vector3 targetWaypoint = _patrolRoute.GetCurrentWaypoint();
            Vector3 direction = (targetWaypoint - transform.position).normalized;
            direction.y = 0f;

            float speed = _isInVehicle ? _config.patrolSpeed : _config.patrolSpeed * 0.5f;
            _currentSpeed = speed;

            if (_characterController != null && !_isInVehicle)
            {
                _characterController.Move(direction * speed * Time.deltaTime);
            }
            else
            {
                transform.position += direction * speed * Time.deltaTime;
            }

            if (direction.sqrMagnitude > 0.01f)
            {
                Quaternion targetRot = Quaternion.LookRotation(direction);
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, Time.deltaTime * 5f);
            }
        }

        private void ExecuteResponse()
        {
            if (string.IsNullOrEmpty(_assignedCallId)) return;
        }

        private void ExecuteVehiclePursuit()
        {
            if (string.IsNullOrEmpty(_pursuitTargetId)) return;
            float speed = _config.pursuitMaxSpeed;
            transform.position += transform.forward * speed * Time.deltaTime;
        }

        private void ExecuteFootPursuit()
        {
            if (string.IsNullOrEmpty(_pursuitTargetId)) return;
            float speed = _config.footPursuitSprintSpeed;
            transform.position += transform.forward * speed * Time.deltaTime;
        }

        private void ExecuteInvestigation()
        {
            Vector3 dir = (_investigationTarget - transform.position).normalized;
            dir.y = 0f;
            float speed = _config.patrolSpeed * 0.3f;
            transform.position += dir * speed * Time.deltaTime;
        }

        private void ExecuteArrest()
        {
            _currentSpeed = 0f;
        }

        private void ExecuteReturnToStation()
        {
            Vector3 direction = (_homeStationPosition - transform.position).normalized;
            direction.y = 0f;
            float speed = _isInVehicle ? _config.patrolSpeed : _config.patrolSpeed * 0.6f;
            _currentSpeed = speed;
            transform.position += direction * speed * Time.deltaTime;
        }

        private void ExecuteIdle()
        {
            _currentSpeed = 0f;
        }

        public void ChangeState(PoliceState newState)
        {
            if (_state.CurrentState == newState) return;

            PoliceState oldState = _state.CurrentState;
            _state.CurrentState = newState;
            _stateTimer = 0f;
        }

        public void SetInVehicle(bool inVehicle)
        {
            _isInVehicle = inVehicle;
        }

        public void AssignDispatch(string callId)
        {
            _assignedCallId = callId;
            ChangeState(PoliceState.RespondingToCall);
        }

        public void StartVehiclePursuit(string targetId)
        {
            _pursuitTargetId = targetId;
            ChangeState(PoliceState.PursuingVehicle);
        }

        public void StartFootPursuit(string targetId)
        {
            _pursuitTargetId = targetId;
            _isInVehicle = false;
            ChangeState(PoliceState.PursuingOnFoot);
        }

        public void StartInvestigation(Vector3 targetPosition)
        {
            _investigationTarget = targetPosition;
            _investigationTimer = 0f;
            ChangeState(PoliceState.Investigating);
        }

        public void StartArrest()
        {
            ChangeState(PoliceState.AttemptingArrest);
        }

        public void ReturnToStation()
        {
            _pursuitTargetId = null;
            _assignedCallId = null;
            ChangeState(PoliceState.ReturningToStation);
        }

        public void GoIdle()
        {
            _pursuitTargetId = null;
            _assignedCallId = null;
            ChangeState(PoliceState.Idle);
        }

        public float GetDistanceToTarget(Vector3 targetPosition)
        {
            return Vector3.Distance(transform.position, targetPosition);
        }

        public Vector3 GetDirectionToTarget(Vector3 targetPosition)
        {
            Vector3 dir = (targetPosition - transform.position).normalized;
            dir.y = 0f;
            return dir;
        }

        public void FaceTarget(Vector3 targetPosition)
        {
            Vector3 dir = (targetPosition - transform.position).normalized;
            dir.y = 0f;
            if (dir.sqrMagnitude > 0.01f)
            {
                transform.rotation = Quaternion.LookRotation(dir);
            }
        }
    }
}
