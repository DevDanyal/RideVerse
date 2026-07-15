using UnityEngine;
using RideVerse.Core;

namespace RideVerse.Vehicles
{
    public class MotorcyclePhysics : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private Rigidbody bikeRigidbody;
        [SerializeField] private Transform centerOfMassPoint;

        [Header("Configuration")]
        [SerializeField] private HondaCG125Config config;

        private float currentLeanAngle;
        private float targetLeanAngle;
        private bool isGrounded;

        public float CurrentLeanAngle => currentLeanAngle;
        public bool IsGrounded => isGrounded;

        private void Awake()
        {
            if (bikeRigidbody == null)
                bikeRigidbody = GetComponent<Rigidbody>();

            if (config == null)
                config = Resources.Load<HondaCG125Config>("HondaCG125Config");
        }

        private void Start()
        {
            SetupCenterOfMass();
        }

        private void SetupCenterOfMass()
        {
            if (centerOfMassPoint != null)
                bikeRigidbody.centerOfMass = centerOfMassPoint.localPosition;
            else
                bikeRigidbody.centerOfMass = config.centerOfMassOffset;
        }

        public void UpdateLean(float steerInput, float speed)
        {
            float speedFactor = Mathf.Clamp01(speed / (config.maxSpeedKmh / 3.6f));
            float maxLean = Mathf.Lerp(config.lowSpeedLeanLimit, config.maxLeanAngle, speedFactor);

            targetLeanAngle = steerInput * maxLean;
            targetLeanAngle = Mathf.Clamp(targetLeanAngle, -maxLean, maxLean);

            currentLeanAngle = Mathf.Lerp(currentLeanAngle, targetLeanAngle,
                Time.deltaTime * (config.leanSpeed * 0.1f));

            ApplyLeanRotation();
        }

        private void ApplyLeanRotation()
        {
            bikeRigidbody.MoveRotation(
                bikeRigidbody.rotation * Quaternion.Euler(0f, 0f, -currentLeanAngle * config.leanToSteerRatio));
        }

        public void UpdateSuspension(float throttle, float brake, float speed)
        {
            float speedFactor = Mathf.Clamp01(speed / (config.maxSpeedKmh / 3.6f));
            float frontCompression = throttle * config.frontSuspensionTravel * (1f - speedFactor);
            float rearCompression = brake * config.rearSuspensionTravel * (1f - speedFactor);
            ApplySuspensionForce(frontCompression, rearCompression);
        }

        private void ApplySuspensionForce(float frontCompression, float rearCompression)
        {
            Vector3 forwardForce = transform.forward * (frontCompression - rearCompression) * config.frontSpringForce;
            bikeRigidbody.AddForceAtPosition(forwardForce,
                transform.position + transform.forward * (config.wheelBase * 0.5f));
        }

        public void UpdateCenterOfMass(float speed)
        {
            float speedFactor = Mathf.Clamp01(speed / (config.maxSpeedKmh / 3.6f));
            Vector3 dynamicCoM = config.centerOfMassOffset + Vector3.back * (speedFactor * 0.05f);
            bikeRigidbody.centerOfMass = dynamicCoM;
        }

        public void ApplyDownforce(float speed)
        {
            float speedFactor = Mathf.Clamp01(speed / (config.maxSpeedKmh / 3.6f));
            float downforce = speedFactor * config.mass * 0.1f;
            bikeRigidbody.AddForce(Vector3.down * downforce, ForceMode.Acceleration);
        }

        public void ApplyAntiGravityStabilizer()
        {
            if (!isGrounded)
                bikeRigidbody.AddForce(Vector3.up * Physics.gravity.magnitude * 0.5f, ForceMode.Acceleration);
        }

        public void CheckGrounded()
        {
            isGrounded = Physics.Raycast(transform.position + Vector3.up * 0.1f, Vector3.down, 0.5f);
        }

        public float CalculateSpeedKmh()
        {
            return bikeRigidbody.linearVelocity.magnitude * 3.6f;
        }

        public float CalculateWheelRPM(WheelCollider wheel)
        {
            return wheel.rpm;
        }

        public float CalculateAcceleration()
        {
            return bikeRigidbody.linearAcceleration.magnitude;
        }

        public Vector3 GetLeanDirection()
        {
            return Quaternion.Euler(0f, 0f, currentLeanAngle) * transform.forward;
        }

        public Quaternion GetLeanRotation()
        {
            return Quaternion.Euler(0f, 0f, -currentLeanAngle * config.leanToSteerRatio);
        }
    }
}
