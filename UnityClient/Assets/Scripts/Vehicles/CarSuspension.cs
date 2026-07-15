using UnityEngine;

namespace RideVerse.Vehicles
{
    [RequireComponent(typeof(WheelCollider))]
    public class CarSuspension : MonoBehaviour
    {
        [SerializeField] private CarConfig config;
        [SerializeField] private bool isFrontWheel;
        [SerializeField] private bool isLeftWheel;

        private WheelCollider wheelCollider;

        private void Awake()
        {
            wheelCollider = GetComponent<WheelCollider>();
        }

        private void Start()
        {
            if (config != null) SetupSuspension();
        }

        public void SetupSuspension()
        {
            if (config == null || wheelCollider == null) return;

            float springForce = isFrontWheel ? config.frontSpringForce : config.rearSpringForce;
            float damperForce = isFrontWheel ? config.frontDamperForce : config.rearDamperForce;
            float travel = isFrontWheel ? config.frontSuspensionTravel : config.rearSuspensionTravel;
            float wheelRadius = isFrontWheel ? config.frontWheelRadius : config.rearWheelRadius;

            JointSpring jointSpring = wheelCollider.suspensionSpring;
            jointSpring.spring = springForce;
            jointSpring.damper = damperForce;
            jointSpring.targetPosition = 0.5f;
            wheelCollider.suspensionSpring = jointSpring;

            wheelCollider.suspensionDistance = travel;
            wheelCollider.radius = wheelRadius;
        }

        public void SetConfig(CarConfig newConfig)
        {
            config = newConfig;
            SetupSuspension();
        }

        public float GetSuspensionCompression()
        {
            WheelHit hit;
            if (wheelCollider.GetGroundHit(out hit))
                return 1f - (wheelCollider.compressionDistance / wheelCollider.suspensionDistance);
            return 0f;
        }

        public bool IsGrounded() => wheelCollider.isGrounded;

        public float GetContactHeight()
        {
            WheelHit hit;
            if (wheelCollider.GetGroundHit(out hit))
                return hit.point.y;
            return transform.position.y;
        }

        public Vector3 GetContactPoint()
        {
            WheelHit hit;
            if (wheelCollider.GetGroundHit(out hit))
                return hit.point;
            return transform.position;
        }

        public Vector3 GetContactNormal()
        {
            WheelHit hit;
            if (wheelCollider.GetGroundHit(out hit))
                return hit.normal;
            return Vector3.up;
        }

        public float GetSurfaceGrip()
        {
            WheelHit hit;
            if (wheelCollider.GetGroundHit(out hit))
                return hit.force;
            return 0f;
        }

        public float GetForwardSlip()
        {
            WheelHit hit;
            if (wheelCollider.GetGroundHit(out hit))
                return hit.forwardSlip;
            return 0f;
        }

        public float GetSidewaysSlip()
        {
            WheelHit hit;
            if (wheelCollider.GetGroundHit(out hit))
                return hit.sidewaysSlip;
            return 0f;
        }
    }
}
