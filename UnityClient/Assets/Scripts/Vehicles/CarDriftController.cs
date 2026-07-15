using UnityEngine;

namespace RideVerse.Vehicles
{
    public class CarDriftController : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private Rigidbody carRigidbody;
        [SerializeField] private CarConfig config;
        [SerializeField] private WheelCollider rearLeftWheel;
        [SerializeField] private WheelCollider rearRightWheel;
        [SerializeField] private WheelCollider frontLeftWheel;
        [SerializeField] private WheelCollider frontRightWheel;

        [Header("Drift Settings")]
        [SerializeField] private float driftAngleThreshold = 10f;
        [SerializeField] private float counterSteerAssist = 0.4f;
        [SerializeField] private float driftThrottleBoost = 1.2f;

        private float _driftAngle;
        private float _previousDriftAngle;
        private bool _isDrifting;
        private float _driftScore;
        private float _driftTime;

        public float DriftAngle => _driftAngle;
        public bool IsDrifting => _isDrifting;
        public float DriftScore => _driftScore;
        public float DriftTime => _driftTime;

        public event System.Action<float> OnDriftStarted;
        public event System.Action<float> OnDriftEnded;

        private void Awake()
        {
            if (carRigidbody == null) carRigidbody = GetComponent<Rigidbody>();
        }

        public void UpdateDrift(float steerInput, float throttle, float speedKmh, float rpm)
        {
            if (config == null) return;

            _driftAngle = CalculateDriftAngle();

            bool wasDrifting = _isDrifting;
            _isDrifting = Mathf.Abs(_driftAngle) > driftAngleThreshold && speedKmh > 20f;

            if (_isDrifting && !wasDrifting)
            {
                _driftTime = 0f;
                _driftScore = 0f;
                OnDriftStarted?.Invoke(_driftAngle);
            }
            else if (!_isDrifting && wasDrifting)
            {
                OnDriftEnded?.Invoke(_driftScore);
            }

            if (_isDrifting)
            {
                _driftTime += Time.fixedDeltaTime;
                _driftScore += Mathf.Abs(_driftAngle) * speedKmh * Time.fixedDeltaTime * 0.01f;

                ApplyCounterSteer(steerInput, speedKmh);
                ApplyThrottleBoost(throttle, speedKmh);
            }

            _previousDriftAngle = _driftAngle;
        }

        private float CalculateDriftAngle()
        {
            Vector3 localVelocity = transform.InverseTransformDirection(carRigidbody.linearVelocity);
            float forwardSpeed = localVelocity.z;
            float lateralSpeed = localVelocity.x;

            if (Mathf.Abs(forwardSpeed) < 1f) return 0f;

            float angle = Mathf.Atan2(lateralSpeed, Mathf.Abs(forwardSpeed)) * Mathf.Rad2Deg;
            return Mathf.Clamp(angle, -45f, 45f);
        }

        private void ApplyCounterSteer(float steerInput, float speedKmh)
        {
            if (frontLeftWheel == null || frontRightWheel == null) return;

            float speedFactor = Mathf.Clamp01(speedKmh / config.maxSpeedKmh);
            float counterSteerAmount = -Mathf.Sign(_driftAngle) * counterSteerAssist * speedFactor;

            float targetAngle = steerInput * config.maxSteerAngle + counterSteerAmount * config.maxSteerAngle;
            targetAngle = Mathf.Clamp(targetAngle, -config.maxSteerAngle, config.maxSteerAngle);

            frontLeftWheel.steerAngle = Mathf.Lerp(frontLeftWheel.steerAngle, targetAngle, Time.fixedDeltaTime * config.steeringSpeed);
            frontRightWheel.steerAngle = frontLeftWheel.steerAngle;
        }

        private void ApplyThrottleBoost(float throttle, float speedKmh)
        {
            if (rearLeftWheel == null || rearRightWheel == null) return;

            if (throttle > 0.3f && speedKmh > 15f)
            {
                float boost = config.maxTorque * driftThrottleBoost * throttle;
                rearLeftWheel.motorTorque += boost;
                rearRightWheel.motorTorque += boost;
            }
        }

        public void ApplyHandbrake(float handbrakeForce)
        {
            if (rearLeftWheel == null || rearRightWheel == null) return;

            rearLeftWheel.brakeTorque = handbrakeForce;
            rearRightWheel.brakeTorque = handbrakeForce;
        }

        public void ReleaseHandbrake()
        {
            if (rearLeftWheel == null || rearRightWheel == null) return;

            rearLeftWheel.brakeTorque = 0f;
            rearRightWheel.brakeTorque = 0f;
        }

        public float GetTireSlip(WheelCollider wheel)
        {
            WheelHit hit;
            if (wheel.GetGroundHit(out hit))
                return hit.forwardSlip;
            return 0f;
        }

        public float GetLateralSlip(WheelCollider wheel)
        {
            WheelHit hit;
            if (wheel.GetGroundHit(out hit))
                return hit.sidewaysSlip;
            return 0f;
        }

        public bool IsTireSlipping(WheelCollider wheel, float threshold = 0.3f)
        {
            return Mathf.Abs(GetTireSlip(wheel)) > threshold || Mathf.Abs(GetLateralSlip(wheel)) > threshold;
        }

        public void ResetDrift()
        {
            _isDrifting = false;
            _driftAngle = 0f;
            _driftScore = 0f;
            _driftTime = 0f;
        }

        public void SetConfig(CarConfig newConfig)
        {
            config = newConfig;
            if (newConfig != null)
                driftAngleThreshold = newConfig.driftAngleThreshold;
        }
    }
}
