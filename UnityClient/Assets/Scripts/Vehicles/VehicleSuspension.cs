using UnityEngine;

namespace RideVerse.Vehicles
{
    [RequireComponent(typeof(WheelCollider))]
    public class VehicleSuspension : MonoBehaviour
    {
        [SerializeField] private HondaCG125Config config;
        [SerializeField] private bool isFrontWheel;

        private WheelCollider wheelCollider;

        private void Awake()
        {
            wheelCollider = GetComponent<WheelCollider>();
        }

        private void Start()
        {
            if (config == null)
                config = Resources.Load<HondaCG125Config>("HondaCG125Config");

            SetupSuspension();
        }

        private void SetupSuspension()
        {
            float springForce = isFrontWheel ? config.frontSpringForce : config.rearSpringForce;
            float damperForce = isFrontWheel ? config.frontDamperForce : config.rearDamperForce;
            float travel = isFrontWheel ? config.frontSuspensionTravel : config.rearSuspensionTravel;

            JointSpring jointSpring = wheelCollider.suspensionSpring;
            jointSpring.spring = springForce;
            jointSpring.damper = damperForce;
            jointSpring.targetPosition = 0.5f;
            wheelCollider.suspensionSpring = jointSpring;

            wheelCollider.suspensionDistance = travel;
        }

        public float GetSuspensionCompression()
        {
            WheelHit hit;
            if (wheelCollider.GetGroundHit(out hit))
            {
                return 1f - (hit.forwardFriction.extremumSlip + hit.sidewaysFriction.extremumSlip);
            }
            return 0f;
        }

        public bool IsGrounded()
        {
            return wheelCollider.isGrounded;
        }

        public float GetContactHeight()
        {
            WheelHit hit;
            if (wheelCollider.GetGroundHit(out hit))
            {
                return hit.point.y;
            }
            return transform.position.y;
        }

        public Vector3 GetContactPoint()
        {
            WheelHit hit;
            if (wheelCollider.GetGroundHit(out hit))
            {
                return hit.point;
            }
            return transform.position;
        }

        public Vector3 GetContactNormal()
        {
            WheelHit hit;
            if (wheelCollider.GetGroundHit(out hit))
            {
                return hit.normal;
            }
            return Vector3.up;
        }

        public float GetSurfaceGrip()
        {
            WheelHit hit;
            if (wheelCollider.GetGroundHit(out hit))
            {
                return hit.force;
            }
            return 0f;
        }
    }
}
