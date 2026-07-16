using System;
using UnityEngine;

namespace RideVerse.Traffic.Core
{
    public class TrafficVehicle : MonoBehaviour
    {
        [Header("Vehicle Data")]
        [SerializeField] private string _vehicleId;
        [SerializeField] private TrafficVehicleType _vehicleType;

        [Header("Physics")]
        [SerializeField] private float _mass = 1500f;
        [SerializeField] private float _length = 4.5f;
        [SerializeField] private float _width = 1.8f;
        [SerializeField] private float _maxSpeed = 50f;

        private float _currentSpeed;
        private float _currentAcceleration;
        private float _targetSpeed;
        private int _currentLaneIndex;
        private float _laneOffset;
        private bool _isActive;
        private bool _isEmergency;
        private EmergencyType _emergencyType;
        private TrafficAIBehaviorState _behaviorState;
        private TrafficVehicleLOD _lodLevel;

        private Rigidbody _rb;
        private Vector3 _velocity;

        public string VehicleId => _vehicleId;
        public TrafficVehicleType VehicleType => _vehicleType;
        public float Mass => _mass;
        public float Length => _length;
        public float Width => _width;
        public float MaxSpeed => _maxSpeed;
        public float CurrentSpeed => _currentSpeed;
        public float CurrentAcceleration => _currentAcceleration;
        public float TargetSpeed => _targetSpeed;
        public int CurrentLaneIndex => _currentLaneIndex;
        public float LaneOffset => _laneOffset;
        public bool IsActive => _isActive;
        public bool IsEmergency => _isEmergency;
        public EmergencyType EmergencyType => _emergencyType;
        public TrafficAIBehaviorState BehaviorState => _behaviorState;
        public TrafficVehicleLOD LODLevel => _lodLevel;
        public Rigidbody Rb => _rb;
        public Vector3 Forward => transform.forward;
        public Vector3 Position => transform.position;

        public event Action<TrafficVehicle> OnVehicleDespawned;

        private void Awake()
        {
            _rb = gameObject.AddComponent<Rigidbody>();
            _rb.mass = _mass;
            _rb.interpolation = RigidbodyInterpolation.Interpolate;
            _rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
            _rb.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;

            gameObject.layer = LayerMask.NameToLayer("Default");
        }

        public void Initialize(string id, TrafficVehicleType type, Vector3 position, float rotationY, float maxSpeed)
        {
            _vehicleId = id;
            _vehicleType = type;
            _maxSpeed = maxSpeed;
            _currentSpeed = 0f;
            _targetSpeed = maxSpeed;
            _isActive = true;
            _isEmergency = false;
            _emergencyType = EmergencyType.None;
            _behaviorState = TrafficAIBehaviorState.Idle;
            _lodLevel = TrafficVehicleLOD.Full;
            _currentLaneIndex = 0;
            _laneOffset = 0f;

            transform.position = position;
            transform.rotation = Quaternion.Euler(0f, rotationY, 0f);

            ApplyVehicleDimensions();
        }

        private void ApplyVehicleDimensions()
        {
            switch (_vehicleType)
            {
                case TrafficVehicleType.Motorcycle:
                case TrafficVehicleType.Scooter:
                    _mass = Random.Range(100f, 250f);
                    _length = Random.Range(1.8f, 2.2f);
                    _width = Random.Range(0.7f, 0.9f);
                    break;
                case TrafficVehicleType.Sedan:
                    _mass = Random.Range(1200f, 1600f);
                    _length = Random.Range(4.2f, 4.8f);
                    _width = Random.Range(1.7f, 1.9f);
                    break;
                case TrafficVehicleType.SUV:
                    _mass = Random.Range(1800f, 2400f);
                    _length = Random.Range(4.5f, 5.2f);
                    _width = Random.Range(1.8f, 2.0f);
                    break;
                case TrafficVehicleType.PickupTruck:
                    _mass = Random.Range(1800f, 2600f);
                    _length = Random.Range(5.0f, 5.8f);
                    _width = Random.Range(1.8f, 2.0f);
                    break;
                case TrafficVehicleType.SportsCar:
                    _mass = Random.Range(1300f, 1600f);
                    _length = Random.Range(4.2f, 4.6f);
                    _width = Random.Range(1.8f, 2.0f);
                    break;
                case TrafficVehicleType.Bus:
                    _mass = Random.Range(8000f, 14000f);
                    _length = Random.Range(10f, 12f);
                    _width = Random.Range(2.4f, 2.6f);
                    break;
                case TrafficVehicleType.DeliveryVan:
                    _mass = Random.Range(2000f, 3500f);
                    _length = Random.Range(5.0f, 6.5f);
                    _width = Random.Range(2.0f, 2.3f);
                    break;
                case TrafficVehicleType.CargoTruck:
                case TrafficVehicleType.FuelTanker:
                    _mass = Random.Range(8000f, 18000f);
                    _length = Random.Range(8f, 14f);
                    _width = Random.Range(2.4f, 2.8f);
                    break;
                default:
                    _mass = Random.Range(1200f, 2000f);
                    _length = Random.Range(4.0f, 5.0f);
                    _width = Random.Range(1.7f, 2.0f);
                    break;
            }

            if (_rb != null)
                _rb.mass = _mass;
        }

        public void SetTargetSpeed(float speed)
        {
            _targetSpeed = Mathf.Clamp(speed, 0f, _maxSpeed);
        }

        public void SetCurrentSpeed(float speed)
        {
            _currentSpeed = Mathf.Max(0f, speed);
        }

        public void SetCurrentLane(int laneIndex)
        {
            _currentLaneIndex = laneIndex;
        }

        public void SetLaneOffset(float offset)
        {
            _laneOffset = offset;
        }

        public void SetBehaviorState(TrafficAIBehaviorState state)
        {
            _behaviorState = state;
        }

        public void SetLODLevel(TrafficVehicleLOD lod)
        {
            _lodLevel = lod;
        }

        public void SetEmergency(bool isEmergency, EmergencyType type = EmergencyType.None)
        {
            _isEmergency = isEmergency;
            _emergencyType = type;
        }

        public void ApplyMovement(Vector3 direction, float speed, float deltaTime)
        {
            if (!_isActive || _rb == null) return;

            _currentSpeed = Mathf.Lerp(_currentSpeed, speed, deltaTime * 5f);
            _velocity = direction * _currentSpeed;
            _rb.MovePosition(_rb.position + _velocity * deltaTime);

            if (direction.sqrMagnitude > 0.01f)
            {
                Quaternion targetRot = Quaternion.LookRotation(direction, Vector3.up);
                _rb.MoveRotation(Quaternion.Slerp(_rb.rotation, targetRot, deltaTime * 8f));
            }
        }

        public void ApplyBrake(float deceleration, float deltaTime)
        {
            if (_rb == null) return;

            _currentSpeed = Mathf.Max(0f, _currentSpeed - deceleration * deltaTime);
            _velocity = transform.forward * _currentSpeed;
            _rb.MovePosition(_rb.position + _velocity * deltaTime);
        }

        public void Stop()
        {
            _currentSpeed = 0f;
            _targetSpeed = 0f;
            _velocity = Vector3.zero;
        }

        public float DistanceTo(Vector3 position)
        {
            return Vector3.Distance(transform.position, position);
        }

        public float DistanceAlongForward(Vector3 position)
        {
            return Vector3.Dot(position - transform.position, transform.forward);
        }

        public float LateralDistanceTo(Vector3 position)
        {
            return Vector3.Dot(position - transform.position, transform.right);
        }

        public bool HasVehicleAhead(float range)
        {
            return Physics.Raycast(transform.position + Vector3.up * 0.5f, transform.forward, range, LayerMask.GetMask("Default"));
        }

        public void SetActive(bool active)
        {
            _isActive = active;
            gameObject.SetActive(active);
        }

        public void Despawn()
        {
            _isActive = false;
            OnVehicleDespawned?.Invoke(this);
            Destroy(gameObject);
        }
    }
}
