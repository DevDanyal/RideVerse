using UnityEngine;

namespace RideVerse.Vehicles
{
    public class CarPhysics : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private Rigidbody carRigidbody;
        [SerializeField] private CarConfig config;

        [Header("Wheel Colliders")]
        [SerializeField] private WheelCollider frontLeftWheel;
        [SerializeField] private WheelCollider frontRightWheel;
        [SerializeField] private WheelCollider rearLeftWheel;
        [SerializeField] private WheelCollider rearRightWheel;

        [Header("Anti-Roll")]
        [SerializeField] private float antiRollForce = 8000f;

        private float _previousSteerAngle;
        private bool _isGrounded;

        public bool IsGrounded => _isGrounded;
        public float WeightTransferFront { get; private set; }
        public float WeightTransferRear { get; private set; }

        private void Awake()
        {
            if (carRigidbody == null) carRigidbody = GetComponent<Rigidbody>();
        }

        private void FixedUpdate()
        {
            UpdateGroundStatus();
            ApplyWeightTransfer();
            ApplyAntiRollBars();
            ApplyStabilityControl();
        }

        private void UpdateGroundStatus()
        {
            _isGrounded = frontLeftWheel.isGrounded || frontRightWheel.isGrounded ||
                           rearLeftWheel.isGrounded || rearRightWheel.isGrounded;
        }

        public void ApplyDownforce(float speedKmh)
        {
            if (config == null) return;

            float speedMs = speedKmh / 3.6f;
            float downforce = config.downforceCoefficient * speedMs * speedMs * config.frontalArea;
            carRigidbody.AddForce(-transform.up * downforce, ForceMode.Force);
        }

        private void ApplyWeightTransfer()
        {
            if (config == null) return;

            Vector3 localVelocity = transform.InverseTransformDirection(carRigidbody.linearVelocity);
            float longitudinalAccel = localVelocity.z / (Time.fixedDeltaTime + 0.001f);
            float lateralAccel = localVelocity.x / (Time.fixedDeltaTime + 0.001f);

            float weightTransferFront = (longitudinalAccel * config.mass * config.centerOfMassOffset.y) / config.wheelBase;
            float weightTransferRear = -weightTransferFront;

            WeightTransferFront = weightTransferFront;
            WeightTransferRear = weightTransferRear;

            float lateralTransfer = (lateralAccel * config.mass * config.centerOfMassOffset.y) / config.trackWidth;

            ApplySuspensionLoad(frontLeftWheel, weightTransferFront - lateralTransfer);
            ApplySuspensionLoad(frontRightWheel, weightTransferFront + lateralTransfer);
            ApplySuspensionLoad(rearLeftWheel, weightTransferRear - lateralTransfer);
            ApplySuspensionLoad(rearRightWheel, weightTransferRear + lateralTransfer);
        }

        private void ApplySuspensionLoad(WheelCollider wheel, float loadOffset)
        {
            if (wheel == null) return;

            JointSpring spring = wheel.suspensionSpring;
            spring.targetPosition = Mathf.Clamp01(0.5f + loadOffset / (spring.spring * 2f));
            wheel.suspensionSpring = spring;
        }

        private void ApplyAntiRollBars()
        {
            if (config == null || frontLeftWheel == null) return;

            ApplySingleAntiRoll(frontLeftWheel, frontRightWheel);
            ApplySingleAntiRoll(rearLeftWheel, rearRightWheel);
        }

        private void ApplySingleAntiRoll(WheelCollider leftWheel, WheelCollider rightWheel)
        {
            if (leftWheel == null || rightWheel == null) return;

            WheelHit leftHit, rightHit;
            bool leftGrounded = leftWheel.GetGroundHit(out leftHit);
            bool rightGrounded = rightWheel.GetGroundHit(out rightHit);

            float leftCompression = leftGrounded ? leftWheel.compressionDistance / leftWheel.suspensionDistance : 1f;
            float rightCompression = rightGrounded ? rightWheel.compressionDistance / rightWheel.suspensionDistance : 1f;

            float antiRollDelta = (leftCompression - rightCompression) * antiRollForce;

            if (leftGrounded)
                carRigidbody.AddForceAtPosition(leftHit.normal * -antiRollDelta, leftWheel.transform.position);
            if (rightGrounded)
                carRigidbody.AddForceAtPosition(rightHit.normal * antiRollDelta, rightWheel.transform.position);
        }

        private void ApplyStabilityControl()
        {
            Vector3 localVelocity = transform.InverseTransformDirection(carRigidbody.linearVelocity);
            float lateralSpeed = localVelocity.x;

            if (Mathf.Abs(lateralSpeed) > 2f)
            {
                float correctionTorque = -lateralSpeed * 0.5f;
                carRigidbody.AddRelativeTorque(0f, correctionTorque, 0f, ForceMode.Acceleration);
            }
        }

        public void ApplyTractionControl(float throttle, float speedKmh)
        {
            if (config == null) return;

            float speedFactor = Mathf.Clamp01(speedKmh / config.maxSpeedKmh);
            float tractionLossChance = speedFactor * Mathf.Abs(throttle);

            if (tractionLossChance > 0.8f)
            {
                rearLeftWheel.motorTorque *= 0.9f;
                rearRightWheel.motorTorque *= 0.9f;
            }
        }

        public float GetWheelSlip(WheelCollider wheel)
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

        public void UpdateCenterOfMass(Vector3 offset)
        {
            if (carRigidbody != null)
                carRigidbody.centerOfMass = offset;
        }

        public void SetConfig(CarConfig newConfig)
        {
            config = newConfig;
            if (carRigidbody != null)
                carRigidbody.mass = config.mass;
        }
    }
}
