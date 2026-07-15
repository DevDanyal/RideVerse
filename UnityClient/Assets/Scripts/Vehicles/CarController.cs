using UnityEngine;
using UnityEngine.InputSystem;
using RideVerse.Core;

namespace RideVerse.Vehicles
{
    [RequireComponent(typeof(Rigidbody))]
    public class CarController : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private CarConfig config;

        [Header("Wheel Colliders")]
        [SerializeField] private WheelCollider frontLeftWheel;
        [SerializeField] private WheelCollider frontRightWheel;
        [SerializeField] private WheelCollider rearLeftWheel;
        [SerializeField] private WheelCollider rearRightWheel;

        [Header("Wheel Meshes")]
        [SerializeField] private Transform frontLeftMesh;
        [SerializeField] private Transform frontRightMesh;
        [SerializeField] private Transform rearLeftMesh;
        [SerializeField] private Transform rearRightMesh;

        [Header("Driver")]
        [SerializeField] private Transform driverSeat;
        [SerializeField] private Transform steeringWheel;

        [Header("References")]
        [SerializeField] private CarPhysics carPhysics;
        [SerializeField] private CarDriftController driftController;
        [SerializeField] private CarDamage carDamage;
        [SerializeField] private CarEffects carEffects;
        [SerializeField] private CarLights carLights;
        [SerializeField] private CarAudioManager audioManager;

        private Rigidbody _rb;
        private InputActions _inputActions;

        private float _throttleInput;
        private float _steerInput;
        private bool _brakeInput;
        private bool _handbrakeInput;
        private bool _clutchInput;
        private bool _hasDriver;
        private bool _isEngineRunning;
        private bool _isReversing;

        private int _currentGear = 0;
        private float _currentRPM;
        private float _currentSpeed;
        private float _speedKmh;
        private float _currentFuel;
        private float _lateralGForce;
        private float _longitudinalGForce;

        public string VehicleId => config != null ? config.vehicleId : "";
        public string DisplayName => config != null ? config.displayName : "";
        public float CurrentSpeed => _speedKmh;
        public float MaxSpeed => config != null ? config.maxSpeedKmh : 0f;
        public float CurrentFuel => _currentFuel;
        public float MaxFuel => config != null ? config.maxFuel : 0f;
        public float CurrentHealth => carDamage != null ? carDamage.CurrentHealth : (config != null ? config.maxHealth : 100f);
        public float MaxHealth => config != null ? config.maxHealth : 100f;
        public int CurrentGear => _currentGear;
        public float CurrentRPM => _currentRPM;
        public bool IsGrounded => frontLeftWheel.isGrounded && rearLeftWheel.isGrounded;
        public bool HasDriver => _hasDriver;
        public bool IsEngineRunning => _isEngineRunning;
        public bool IsReversing => _isReversing;
        public Transform DriverSeat => driverSeat;
        public Transform SteeringWheel => steeringWheel;
        public float SpeedPercent => config != null && config.maxSpeedKmh > 0 ? _speedKmh / config.maxSpeedKmh : 0f;
        public float FuelPercent => config != null && config.maxFuel > 0 ? _currentFuel / config.maxFuel : 0f;
        public float LateralGForce => _lateralGForce;
        public float LongitudinalGForce => _longitudinalGForce;
        public bool IsDrifting => driftController != null && driftController.IsDrifting;
        public float DriftAngle => driftController != null ? driftController.DriftAngle : 0f;
        public CarConfig Config => config;

        public event System.Action<CarController> OnEngineStarted;
        public event System.Action<CarController> OnEngineStopped;
        public event System.Action<int> OnGearChanged;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _rb.mass = config.mass;
            _rb.interpolation = RigidbodyInterpolation.Interpolate;
            _rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
            _rb.centerOfMass = config.centerOfMassOffset;

            _currentFuel = config.maxFuel;
            SetupInput();
        }

        private void SetupInput()
        {
            _inputActions = new InputActions();

            _inputActions.Vehicle.Throttle.performed += ctx => _throttleInput = ctx.ReadValue<float>();
            _inputActions.Vehicle.Throttle.canceled += ctx => _throttleInput = 0f;

            _inputActions.Vehicle.Brake.performed += ctx => _brakeInput = true;
            _inputActions.Vehicle.Brake.canceled += ctx => _brakeInput = false;

            _inputActions.Vehicle.Steer.performed += ctx => _steerInput = ctx.ReadValue<float>();
            _inputActions.Vehicle.Steer.canceled += ctx => _steerInput = 0f;
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
            if (!_hasDriver || !_isEngineRunning) return;

            UpdateSpeed();
            UpdateEngine();
            HandleTransmission();
            HandleMotor();
            HandleBraking();
            HandleSteering();
            HandleDrift();
            ApplyDownforce();
            HandleFuelConsumption();
            UpdateGForces();
            UpdateWheelMeshes();
            UpdateEffects();
        }

        private void UpdateSpeed()
        {
            _speedKmh = _rb.linearVelocity.magnitude * 3.6f;
            _currentSpeed = Vector3.Dot(_rb.linearVelocity, transform.forward);
        }

        private void UpdateEngine()
        {
            float avgWheelRPM = (Mathf.Abs(rearLeftWheel.rpm) + Mathf.Abs(rearRightWheel.rpm)) * 0.5f;
            int gearIndex = Mathf.Clamp(_currentGear + 1, 0, config.gearRatios.Length - 1);
            float gearRatio = Mathf.Abs(config.gearRatios[gearIndex]);
            float driveRPM = avgWheelRPM * gearRatio * config.finalDriveRatio;

            _currentRPM = Mathf.Clamp(driveRPM, config.idleRPM, config.maxRPM);

            if (Mathf.Abs(_throttleInput) > 0.1f)
            {
                float targetRPM = config.idleRPM + Mathf.Abs(_throttleInput) * (config.maxRPM - config.idleRPM);
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
            float normalizedRPM = _currentRPM / config.maxRPM;

            if (_currentGear > 0)
            {
                if (normalizedRPM > 0.9f && _currentGear < config.totalGears)
                    ShiftUp();
                else if (normalizedRPM < 0.25f && _currentGear > 1)
                    ShiftDown();
            }
        }

        public void ShiftUp()
        {
            if (_currentGear < config.totalGears)
            {
                _currentGear++;
                OnGearChanged?.Invoke(_currentGear);
                if (audioManager != null) audioManager.PlayGearShift(_currentGear);
            }
        }

        public void ShiftDown()
        {
            if (_currentGear > config.reverseGear)
            {
                _currentGear--;
                if (_currentGear < 0) _isReversing = true;
                OnGearChanged?.Invoke(_currentGear);
                if (audioManager != null) audioManager.PlayGearShift(_currentGear);
            }
        }

        private void HandleMotor()
        {
            if (_throttleInput <= 0f || _currentFuel <= 0f || _currentGear == config.neutralGear) return;

            int gearIndex = Mathf.Clamp(_currentGear + 1, 0, config.gearRatios.Length - 1);
            float gearRatio = Mathf.Abs(config.gearRatios[gearIndex]);
            float speedFactor = Mathf.InverseLerp(0f, config.maxSpeedKmh, _speedKmh);
            float torqueMultiplier = (1f - speedFactor) * gearRatio;
            float torque = config.maxTorque * torqueMultiplier * _throttleInput * config.finalDriveRatio;

            bool isReverse = _currentGear == config.reverseGear;
            float direction = isReverse ? -1f : 1f;

            rearLeftWheel.motorTorque = torque * direction;
            rearRightWheel.motorTorque = torque * direction;
        }

        private void HandleBraking()
        {
            if (!_brakeInput)
            {
                if (carLights != null) carLights.SetBrake(false);
                rearLeftWheel.brakeTorque = 0f;
                rearRightWheel.brakeTorque = 0f;
                frontLeftWheel.brakeTorque = 0f;
                frontRightWheel.brakeTorque = 0f;
                return;
            }

            if (carLights != null) carLights.SetBrake(true);

            frontLeftWheel.brakeTorque = config.frontBrakeForce;
            frontRightWheel.brakeTorque = config.frontBrakeForce;
            rearLeftWheel.brakeTorque = config.rearBrakeForce;
            rearRightWheel.brakeTorque = config.rearBrakeForce;
        }

        private void HandleSteering()
        {
            if (Mathf.Abs(_steerInput) < 0.01f)
            {
                frontLeftWheel.steerAngle = Mathf.Lerp(frontLeftWheel.steerAngle, 0f, Time.fixedDeltaTime * config.steeringSpeed);
                frontRightWheel.steerAngle = frontLeftWheel.steerAngle;
                return;
            }

            float speedFactor = Mathf.Clamp01(_speedKmh / (config.maxSpeedKmh * 0.5f));
            float targetAngle = _steerInput * config.maxSteerAngle * (1f - speedFactor * config.speedDependentSteerFactor);

            frontLeftWheel.steerAngle = Mathf.Lerp(frontLeftWheel.steerAngle, targetAngle, Time.fixedDeltaTime * config.steeringSpeed);
            frontRightWheel.steerAngle = AckermannAngle(frontLeftWheel.steerAngle, targetAngle);
        }

        private float AckermannAngle(float insideWheelAngle, float steerAngle)
        {
            if (Mathf.Abs(steerAngle) < 0.01f) return insideWheelAngle;

            float sign = Mathf.Sign(steerAngle);
            float radInside = Mathf.Deg2Rad * insideWheelAngle;
            float turnRadius = config.wheelBase / Mathf.Tan(Mathf.Abs(radInside));

            float outerRadius = turnRadius + (sign * config.trackWidth * 0.5f);
            float radOutside = Mathf.Atan(config.wheelBase / outerRadius);

            return sign * Mathf.Rad2Deg * radOutside;
        }

        private void HandleDrift()
        {
            if (driftController != null)
                driftController.UpdateDrift(_steerInput, _throttleInput, _speedKmh, _currentRPM);
        }

        private void ApplyDownforce()
        {
            if (carPhysics != null)
                carPhysics.ApplyDownforce(_speedKmh);
        }

        private void HandleFuelConsumption()
        {
            if (_throttleInput <= 0f || _currentFuel <= 0f) return;

            float rpmFactor = _currentRPM / config.maxRPM;
            float consumption = config.fuelConsumptionRate * Mathf.Abs(_throttleInput) * (0.5f + rpmFactor * 0.5f);
            _currentFuel -= consumption * Time.fixedDeltaTime;
            _currentFuel = Mathf.Max(0f, _currentFuel);

            if (_currentFuel <= 0f) StopEngine();
        }

        private void UpdateGForces()
        {
            Vector3 localVelocity = transform.InverseTransformDirection(_rb.linearVelocity);
            _longitudinalGForce = localVelocity.z / (config.maxSpeedKmh / 3.6f + 0.01f);
            _lateralGForce = localVelocity.x / (config.maxSpeedKmh / 3.6f + 0.01f);
        }

        private void UpdateWheelMeshes()
        {
            UpdateWheelMesh(frontLeftWheel, frontLeftMesh);
            UpdateWheelMesh(frontRightWheel, frontRightMesh);
            UpdateWheelMesh(rearLeftWheel, rearLeftMesh);
            UpdateWheelMesh(rearRightWheel, rearRightMesh);
        }

        private void UpdateWheelMesh(WheelCollider collider, Transform mesh)
        {
            if (collider == null || mesh == null) return;
            collider.GetWorldPose(out Vector3 position, out Quaternion rotation);
            mesh.position = position;
            mesh.rotation = rotation;
        }

        private void UpdateEffects()
        {
            if (carEffects == null) return;

            carEffects.UpdateExhaust(_currentRPM, _throttleInput);

            bool isSkidding = Mathf.Abs(_lateralGForce) > 0.3f || (_brakeInput && _speedKmh > 20f);
            if (isSkidding) carEffects.PlaySkidEffect();
            else carEffects.StopSkidEffect();

            if (_handbrakeInput && _speedKmh > 5f) carEffects.PlayBurnoutSmoke();
            else carEffects.StopBurnoutSmoke();
        }

        public void StartEngine()
        {
            if (_isEngineRunning || _currentFuel <= 0f) return;

            _isEngineRunning = true;
            _currentRPM = config.idleRPM;

            if (audioManager != null) audioManager.StartEngine();
            OnEngineStarted?.Invoke(this);
        }

        public void StopEngine()
        {
            _isEngineRunning = false;
            _throttleInput = 0f;
            _brakeInput = false;
            _steerInput = 0f;
            _currentGear = config.neutralGear;
            _currentRPM = 0f;
            _isReversing = false;

            rearLeftWheel.motorTorque = 0f;
            rearRightWheel.motorTorque = 0f;

            if (audioManager != null) audioManager.StopEngine();
            OnEngineStopped?.Invoke(this);
        }

        public void MountDriver(Transform driver)
        {
            if (driver == null) return;
            _hasDriver = true;
            driver.SetParent(driverSeat != null ? driverSeat : transform);
            driver.localPosition = Vector3.zero;
            driver.localRotation = Quaternion.identity;
        }

        public void DismountDriver(out Vector3 exitPosition)
        {
            _hasDriver = false;
            exitPosition = transform.position + transform.right * 2f + Vector3.up * 0.1f;
            StopEngine();
        }

        public void Refuel(float amount)
        {
            _currentFuel = Mathf.Min(_currentFuel + amount, config.maxFuel);
        }

        public void SetInputEnabled(bool enabled)
        {
            if (enabled) _inputActions?.Vehicle.Enable();
            else _inputActions?.Vehicle.Disable();
        }

        public void SetDriverReferences(Transform seat, Transform wheel)
        {
            driverSeat = seat;
            steeringWheel = wheel;
        }

        public float GetSpeedKmh() => _speedKmh;
        public float GetRPM() => _currentRPM;
        public int GetGear() => _currentGear;
        public bool IsInNeutral() => _currentGear == config.neutralGear;
        public bool IsRedlining() => _currentRPM >= config.redlineRPM;
    }
}
