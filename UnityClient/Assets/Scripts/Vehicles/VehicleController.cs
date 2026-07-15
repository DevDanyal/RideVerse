using UnityEngine;
using UnityEngine.InputSystem;
using RideVerse.Core;

namespace RideVerse.Vehicles
{
    [RequireComponent(typeof(Rigidbody))]
    public class VehicleController : MonoBehaviour
    {
        [Header("Vehicle Settings")]
        [SerializeField] private string _vehicleId = Constants.Vehicle.HondaCG125.VehicleId;
        [SerializeField] private string _displayName = Constants.Vehicle.HondaCG125.DisplayName;

        [Header("Configuration")]
        [SerializeField] private HondaCG125Config config;

        [Header("Wheels")]
        [SerializeField] private WheelCollider frontWheelCollider;
        [SerializeField] private WheelCollider rearWheelCollider;
        [SerializeField] private Transform frontWheelMesh;
        [SerializeField] private Transform rearWheelMesh;

        [Header("Rider")]
        [SerializeField] private Transform _riderSeat;
        [SerializeField] private Transform _riderHandlebarGrip;

        [Header("References")]
        [SerializeField] private MotorcyclePhysics motorcyclePhysics;
        [SerializeField] private VehicleSuspension frontSuspension;
        [SerializeField] private VehicleSuspension rearSuspension;
        [SerializeField] private VehicleLights vehicleLights;
        [SerializeField] private VehicleDamage vehicleDamage;
        [SerializeField] private VehicleEffects vehicleEffects;
        [SerializeField] private MotorcycleAudioManager audioManager;

        private Rigidbody _rb;
        private float _currentSpeed;
        private float _currentFuel;
        private int _currentGear;
        private float _currentRPM;
        private float _clutchAmount;
        private bool _hasRider;
        private bool _isEngineRunning;
        private bool _isBraking;
        private bool _isKickStarting;

        private float _throttleInput;
        private float _steeringInput;
        private bool _brakeInput;
        private bool _frontBrakeInput;
        private bool _clutchInput;

        private float _speedKmh;
        private float _targetLeanAngle;
        private float _currentLeanAngle;

        private InputActions _inputActions;

        public string VehicleId => _vehicleId;
        public string DisplayName => _displayName;
        public float CurrentSpeed => _speedKmh;
        public float MaxSpeed => config.maxSpeedKmh;
        public float CurrentFuel => _currentFuel;
        public float MaxFuel => config.maxFuel;
        public float CurrentHealth => vehicleDamage != null ? vehicleDamage.CurrentHealth : config.maxHealth;
        public float MaxHealth => config.maxHealth;
        public int CurrentGear => _currentGear;
        public float CurrentRPM => _currentRPM;
        public float ClutchAmount => _clutchAmount;
        public bool IsGrounded => motorcyclePhysics != null && motorcyclePhysics.IsGrounded;
        public bool HasRider => _hasRider;
        public bool IsEngineRunning => _isEngineRunning;
        public Transform RiderSeat => _riderSeat;
        public Transform RiderHandlebarGrip => _riderHandlebarGrip;
        public float SpeedPercent => config.maxSpeedKmh > 0 ? _speedKmh / config.maxSpeedKmh : 0f;
        public float FuelPercent => config.maxFuel > 0 ? _currentFuel / config.maxFuel : 0f;
        public float LeanAngle => motorcyclePhysics != null ? motorcyclePhysics.CurrentLeanAngle : 0f;
        public bool IsKickStarting => _isKickStarting;

        public event System.Action<VehicleController> OnEngineStarted;
        public event System.Action<VehicleController> OnEngineStopped;
        public event System.Action<int> OnGearChanged;
        public event System.Action OnKickStarted;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _rb.mass = config.mass;
            _rb.interpolation = RigidbodyInterpolation.Interpolate;
            _rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;

            _currentFuel = config.maxFuel;
            _currentGear = config.neutralGear;

            SetupInput();
        }

        private void SetupInput()
        {
            _inputActions = new InputActions();

            _inputActions.Vehicle.Throttle.performed += ctx => _throttleInput = ctx.ReadValue<float>();
            _inputActions.Vehicle.Throttle.canceled += ctx => _throttleInput = 0f;

            _inputActions.Vehicle.Brake.performed += ctx =>
            {
                _brakeInput = true;
                _frontBrakeInput = true;
            };
            _inputActions.Vehicle.Brake.canceled += ctx =>
            {
                _brakeInput = false;
                _frontBrakeInput = false;
            };

            _inputActions.Vehicle.Steer.performed += ctx => _steeringInput = ctx.ReadValue<float>();
            _inputActions.Vehicle.Steer.canceled += ctx => _steeringInput = 0f;
        }

        private void OnEnable()
        {
            _inputActions?.Vehicle.Enable();
        }

        private void OnDisable()
        {
            _inputActions?.Vehicle.Disable();
        }

        private void FixedUpdate()
        {
            if (!_hasRider) return;

            if (motorcyclePhysics != null)
                motorcyclePhysics.CheckGround();

            if (_isEngineRunning)
            {
                UpdateEngine();
                HandleTransmission();
                HandleThrottle();
                HandleBraking();
                HandleSteering();
                HandleLean();
                ApplyEngineBraking();
                HandleFuelConsumption();
            }

            if (vehicleEffects != null)
                vehicleEffects.UpdateExhaust(_currentRPM, _throttleInput);

            UpdateWheelMeshes();
        }

        private void UpdateEngine()
        {
            float wheelRPM = rearWheelCollider != null ? Mathf.Abs(rearWheelCollider.rpm) : 0f;
            float gearRatio = _currentGear > 0 ? config.gearRatios[_currentGear] : 1f;
            float driveRPM = wheelRPM * gearRatio * config.finalDriveRatio;

            if (_throttleInput > 0.1f)
            {
                float targetRPM = config.idleRPM + _throttleInput * (config.maxRPM - config.idleRPM);
                _currentRPM = Mathf.Lerp(_currentRPM, targetRPM, Time.fixedDeltaTime * 5f);
            }
            else
            {
                _currentRPM = Mathf.Lerp(_currentRPM, config.idleRPM, Time.fixedDeltaTime * 3f);
            }

            _currentRPM = Mathf.Clamp(_currentRPM, config.idleRPM, config.maxRPM);

            if (audioManager != null)
                audioManager.UpdateEngineSound(_currentRPM, _throttleInput);
        }

        private void HandleTransmission()
        {
            float wheelRPM = rearWheelCollider != null ? Mathf.Abs(rearWheelCollider.rpm) : 0f;
            float normalizedRPM = _currentRPM / config.maxRPM;

            if (_currentGear > 0)
            {
                float gearMaxRPM = config.maxRPM * 0.85f;
                if (_currentRPM > gearMaxRPM && _currentGear < config.totalGears)
                {
                    ShiftUp();
                }
                else if (_currentRPM < config.clutchEngageRPM && _currentGear > 1)
                {
                    ShiftDown();
                }
            }
        }

        public void ShiftUp()
        {
            if (_currentGear < config.totalGears)
            {
                _currentGear++;
                OnGearChanged?.Invoke(_currentGear);
                if (audioManager != null)
                    audioManager.PlayGearShift(_currentGear);
            }
        }

        public void ShiftDown()
        {
            if (_currentGear > config.neutralGear)
            {
                _currentGear--;
                OnGearChanged?.Invoke(_currentGear);
                if (audioManager != null)
                    audioManager.PlayGearShift(_currentGear);
            }
        }

        private void HandleThrottle()
        {
            if (_throttleInput <= 0f || _currentFuel <= 0f || _currentGear == config.neutralGear) return;

            float gearRatio = config.gearRatios[_currentGear];
            float gearMaxSpeed = config.maxSpeedKmh / config.finalDriveRatio * gearRatio;
            float speedFactor = Mathf.InverseLerp(0f, gearMaxSpeed, _speedKmh);

            float torqueMultiplier = (1f - speedFactor) * gearRatio;
            float torque = config.maxTorque * torqueMultiplier * _throttleInput * config.finalDriveRatio;

            if (rearWheelCollider != null)
            {
                rearWheelCollider.motorTorque = torque;
            }
        }

        private void HandleBraking()
        {
            if (!_brakeInput)
            {
                if (vehicleLights != null)
                    vehicleLights.SetBrake(false);
                return;
            }

            if (vehicleLights != null)
                vehicleLights.SetBrake(true);

            if (_frontBrakeInput && frontWheelCollider != null)
            {
                frontWheelCollider.brakeTorque = config.frontBrakeForce;
            }

            if (rearWheelCollider != null)
            {
                rearWheelCollider.brakeTorque = config.rearBrakeForce;
            }
        }

        private void HandleSteering()
        {
            if (Mathf.Abs(_steeringInput) < 0.01f) return;

            float speedKmh = _speedKmh;
            float speedFactor = Mathf.Clamp01(speedKmh / (config.maxSpeedKmh * 0.5f));
            float steerAngle = _steeringInput * config.steeringAngle * (1f - speedFactor * config.speedDependentSteerFactor);

            if (frontWheelCollider != null)
            {
                frontWheelCollider.steerAngle = steerAngle;
            }
        }

        private void HandleLean()
        {
            if (motorcyclePhysics == null) return;

            float steerInput = frontWheelCollider != null ? frontWheelCollider.steerAngle / config.steeringAngle : _steeringInput;
            motorcyclePhysics.UpdateLean(steerInput, _speedKmh);
        }

        private void ApplyEngineBraking()
        {
            if (_throttleInput > 0.1f || _brakeInput) return;

            if (rearWheelCollider != null && _currentGear > config.neutralGear)
            {
                float engineBrake = config.engineBrakeForce * (1f - _currentRPM / config.maxRPM);
                rearWheelCollider.brakeTorque = engineBrake;
            }
        }

        private void HandleFuelConsumption()
        {
            if (_throttleInput <= 0f || _currentFuel <= 0f) return;

            float rpmFactor = _currentRPM / config.maxRPM;
            float consumption = config.fuelConsumptionRate * _throttleInput * (0.5f + rpmFactor * 0.5f);
            _currentFuel -= consumption * Time.fixedDeltaTime;
            _currentFuel = Mathf.Max(0f, _currentFuel);

            if (_currentFuel <= 0f)
                StopEngine();
        }

        private void UpdateWheelMeshes()
        {
            UpdateWheelMesh(frontWheelCollider, frontWheelMesh);
            UpdateWheelMesh(rearWheelCollider, rearWheelMesh);
        }

        private void UpdateWheelMesh(WheelCollider collider, Transform mesh)
        {
            if (collider == null || mesh == null) return;

            collider.GetWorldPose(out Vector3 position, out Quaternion rotation);
            mesh.position = position;
            mesh.rotation = rotation;
        }

        public void StartEngine()
        {
            if (_isEngineRunning || _currentFuel <= 0f) return;

            _isEngineRunning = true;
            _currentRPM = config.idleRPM;

            if (audioManager != null)
                audioManager.StartEngine();

            OnEngineStarted?.Invoke(this);
        }

        public void StartKickStart()
        {
            if (_isEngineRunning) return;

            _isKickStarting = true;
            OnKickStarted?.Invoke();

            float successChance = _currentFuel > 0f ? 0.8f : 0f;
            if (Random.value < successChance)
            {
                StartEngine();
            }

            _isKickStarting = false;
        }

        public void StopEngine()
        {
            _isEngineRunning = false;
            _throttleInput = 0f;
            _brakeInput = false;
            _frontBrakeInput = false;
            _steeringInput = 0f;
            _currentGear = config.neutralGear;
            _currentRPM = 0f;

            if (audioManager != null)
                audioManager.StopEngine();

            if (rearWheelCollider != null)
                rearWheelCollider.motorTorque = 0f;

            OnEngineStopped?.Invoke(this);
        }

        public void MountRider(Transform rider)
        {
            if (rider == null) return;

            _hasRider = true;
            rider.SetParent(_riderSeat != null ? _riderSeat : transform);
            rider.localPosition = Vector3.zero;
            rider.localRotation = Quaternion.identity;
        }

        public void DismountRider(out Vector3 exitPosition)
        {
            _hasRider = false;
            exitPosition = transform.position + transform.right * -2f + Vector3.up * 0.1f;
            StopEngine();
        }

        public void Refuel(float amount)
        {
            _currentFuel = Mathf.Min(_currentFuel + amount, config.maxFuel);
        }

        public void SetInputEnabled(bool enabled)
        {
            if (enabled)
                _inputActions?.Vehicle.Enable();
            else
                _inputActions?.Vehicle.Disable();
        }

        public void SetRiderReferences(Transform seat, Transform grip)
        {
            _riderSeat = seat;
            _riderHandlebarGrip = grip;
        }

        public float GetSpeedKmh()
        {
            return _rb != null ? _rb.linearVelocity.magnitude * 3.6f : 0f;
        }

        public float GetRPM()
        {
            return _currentRPM;
        }

        public int GetGear()
        {
            return _currentGear;
        }

        public bool IsInNeutral()
        {
            return _currentGear == config.neutralGear;
        }

        public bool IsRedlining()
        {
            return _currentRPM >= config.redlineRPM;
        }
    }
}
