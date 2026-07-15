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

        [Header("Movement")]
        [SerializeField] private float _maxSpeed = Constants.Vehicle.HondaCG125.MaxSpeed;
        [SerializeField] private float _acceleration = Constants.Vehicle.HondaCG125.Acceleration;
        [SerializeField] private float _brakingForce = Constants.Vehicle.HondaCG125.BrakingForce;
        [SerializeField] private float _steeringSpeed = Constants.Vehicle.HondaCG125.SteeringSpeed;
        [SerializeField] private float _maxLeanAngle = Constants.Vehicle.HondaCG125.MaxLeanAngle;
        [SerializeField] private float _leanSpeed = Constants.Vehicle.HondaCG125.LeanSpeed;

        [Header("Wheels")]
        [SerializeField] private Transform _frontWheel;
        [SerializeField] private Transform _rearWheel;

        [Header("Rider")]
        [SerializeField] private Transform _riderSeat;
        [SerializeField] private Transform _riderHandlebarGrip;

        [Header("Ground Check")]
        [SerializeField] private float _groundCheckDistance = 0.5f;
        [SerializeField] private LayerMask _groundMask;

        [Header("Fuel")]
        [SerializeField] private float _maxFuel = Constants.Vehicle.HondaCG125.MaxFuel;
        [SerializeField] private float _fuelConsumptionRate = Constants.Vehicle.HondaCG125.FuelConsumptionRate;

        [Header("Health")]
        [SerializeField] private float _maxHealth = Constants.Vehicle.HondaCG125.MaxHealth;

        private Rigidbody _rb;
        private float _currentSpeed;
        private float _currentFuel;
        private float _currentHealth;
        private int _currentGear;
        private float _currentLeanAngle;
        private bool _isGrounded;
        private bool _hasRider;

        private float _throttleInput;
        private float _steeringInput;
        private bool _brakeInput;
        private bool _isEngineRunning;

        private InputActions _inputActions;

        public string VehicleId => _vehicleId;
        public string DisplayName => _displayName;
        public float CurrentSpeed => _currentSpeed;
        public float MaxSpeed => _maxSpeed;
        public float CurrentFuel => _currentFuel;
        public float MaxFuel => _maxFuel;
        public float CurrentHealth => _currentHealth;
        public float MaxHealth => _maxHealth;
        public int CurrentGear => _currentGear;
        public bool IsGrounded => _isGrounded;
        public bool HasRider => _hasRider;
        public bool IsEngineRunning => _isEngineRunning;
        public Transform RiderSeat => _riderSeat;
        public Transform RiderHandlebarGrip => _riderHandlebarGrip;
        public float SpeedPercent => _maxSpeed > 0 ? Mathf.Abs(_currentSpeed) / _maxSpeed : 0f;
        public float FuelPercent => _maxFuel > 0 ? _currentFuel / _maxFuel : 0f;

        public event System.Action<VehicleController> OnEngineStarted;
        public event System.Action<VehicleController> OnEngineStopped;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _rb.mass = Constants.Vehicle.HondaCG125.Mass;
            _rb.interpolation = RigidbodyInterpolation.Interpolate;
            _rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;

            _currentFuel = _maxFuel;
            _currentHealth = _maxHealth;

            SetupInput();
        }

        private void SetupInput()
        {
            _inputActions = new InputActions();

            _inputActions.Vehicle.Throttle.performed += ctx => _throttleInput = ctx.ReadValue<float>();
            _inputActions.Vehicle.Throttle.canceled += ctx => _throttleInput = 0f;

            _inputActions.Vehicle.Brake.performed += ctx => _brakeInput = true;
            _inputActions.Vehicle.Brake.canceled += ctx => _brakeInput = false;

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
            if (!_hasRider || !_isEngineRunning) return;

            CheckGround();
            HandleAcceleration();
            HandleBraking();
            HandleSteering();
            HandleLean();
            ApplyMovement();
            HandleFuelConsumption();
            UpdateWheelRotation();
        }

        private void CheckGround()
        {
            _isGrounded = Physics.Raycast(
                transform.position + Vector3.up * 0.1f,
                Vector3.down,
                _groundCheckDistance + 0.1f,
                _groundMask,
                QueryTriggerInteraction.Ignore);
        }

        private void HandleAcceleration()
        {
            if (_throttleInput > 0f && _currentFuel > 0f)
            {
                float gearRatio = Constants.Vehicle.HondaCG125.GearRatios[_currentGear];
                float gearMaxSpeed = _maxSpeed * gearRatio;

                if (Mathf.Abs(_currentSpeed) < gearMaxSpeed)
                {
                    _rb.AddForce(transform.forward * (_acceleration * _throttleInput), ForceMode.Acceleration);
                }

                AutoShiftGear();
            }
        }

        private void HandleBraking()
        {
            if (_brakeInput)
            {
                Vector3 velocity = _rb.linearVelocity;
                velocity.x *= (1f - _brakingForce * Time.fixedDeltaTime);
                velocity.z *= (1f - _brakingForce * Time.fixedDeltaTime);
                _rb.linearVelocity = velocity;

                if (Mathf.Abs(_currentSpeed) < 0.5f)
                {
                    _rb.linearVelocity = new Vector3(0f, _rb.linearVelocity.y, 0f);
                }
            }
        }

        private void HandleSteering()
        {
            if (Mathf.Abs(_steeringInput) > 0.01f && Mathf.Abs(_currentSpeed) > 0.1f)
            {
                float steerAmount = _steeringInput * _steeringSpeed * Time.fixedDeltaTime;
                float speedFactor = Mathf.InverseLerp(0f, _maxSpeed * 0.5f, Mathf.Abs(_currentSpeed));
                steerAmount *= Mathf.Lerp(1f, 0.3f, speedFactor);

                transform.Rotate(Vector3.up, steerAmount);
            }
        }

        private void HandleLean()
        {
            float targetLean = -_steeringInput * _maxLeanAngle * Mathf.InverseLerp(0f, _maxSpeed * 0.5f, Mathf.Abs(_currentSpeed));
            _currentLeanAngle = Mathf.Lerp(_currentLeanAngle, targetLean, _leanSpeed * Time.fixedDeltaTime);

            Vector3 currentEuler = transform.localEulerAngles;
            transform.localRotation = Quaternion.Euler(currentEuler.x, currentEuler.y, _currentLeanAngle);
        }

        private void ApplyMovement()
        {
            _currentSpeed = Vector3.Dot(_rb.linearVelocity, transform.forward);

            if (_isGrounded && !_brakeInput && _throttleInput <= 0f)
            {
                Vector3 velocity = _rb.linearVelocity;
                float dampFactor = 1f - 3f * Time.fixedDeltaTime;
                velocity.x *= dampFactor;
                velocity.z *= dampFactor;
                _rb.linearVelocity = velocity;
            }
        }

        private void HandleFuelConsumption()
        {
            if (_throttleInput > 0f && _currentFuel > 0f)
            {
                _currentFuel -= _fuelConsumptionRate * _throttleInput * Time.fixedDeltaTime;
                _currentFuel = Mathf.Max(0f, _currentFuel);

                if (_currentFuel <= 0f)
                {
                    StopEngine();
                }
            }
        }

        private void AutoShiftGear()
        {
            float speedPercent = Mathf.Abs(_currentSpeed) / _maxSpeed;

            int targetGear = 1;
            if (speedPercent > 0.75f) targetGear = 4;
            else if (speedPercent > 0.5f) targetGear = 3;
            else if (speedPercent > 0.25f) targetGear = 2;

            if (targetGear != _currentGear)
            {
                _currentGear = targetGear;
            }
        }

        private void UpdateWheelRotation()
        {
            if (_frontWheel != null)
            {
                _frontWheel.Rotate(Vector3.right, _currentSpeed * 360f * Time.fixedDeltaTime);
            }

            if (_rearWheel != null)
            {
                _rearWheel.Rotate(Vector3.right, _currentSpeed * 360f * Time.fixedDeltaTime);
            }
        }

        public void StartEngine()
        {
            if (_currentFuel <= 0f) return;

            _isEngineRunning = true;
            OnEngineStarted?.Invoke(this);
            Debug.Log($"[Vehicle] {DisplayName} engine started");
        }

        public void StopEngine()
        {
            _isEngineRunning = false;
            _throttleInput = 0f;
            _brakeInput = false;
            _steeringInput = 0f;
            _currentGear = 0;
            OnEngineStopped?.Invoke(this);
            Debug.Log($"[Vehicle] {DisplayName} engine stopped");
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
            Debug.Log($"[Vehicle] Rider dismounted from {DisplayName}");
        }

        public void Refuel(float amount)
        {
            _currentFuel = Mathf.Min(_currentFuel + amount, _maxFuel);
        }

        public void TakeDamage(float amount)
        {
            _currentHealth = Mathf.Max(0f, _currentHealth - amount);
        }

        public void Repair(float amount)
        {
            _currentHealth = Mathf.Min(_currentHealth + amount, _maxHealth);
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
    }
}
