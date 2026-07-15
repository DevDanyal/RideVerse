using UnityEngine;

namespace RideVerse.Player
{
    public class ThirdPersonCamera : MonoBehaviour
    {
        [Header("Target")]
        [SerializeField] private Transform _target;

        [Header("Offset")]
        [SerializeField] private float _distance = Core.Constants.Player.CameraDistance;
        [SerializeField] private float _height = Core.Constants.Player.CameraHeight;
        [SerializeField] private float _lookAtHeightOffset = 1.5f;

        [Header("Smoothing")]
        [SerializeField] private float _positionSmoothness = Core.Constants.Player.CameraSmoothness;
        [SerializeField] private float _rotationSmoothness = 8f;

        [Header("Collision")]
        [SerializeField] private float _collisionBuffer = 0.3f;
        [SerializeField] private LayerMask _collisionMask;

        private Vector3 _currentVelocity;
        private float _currentAngle;
        private float _targetAngle;

        private UnityEngine.InputSystem.InputAction _lookAction;
        private float _mouseX;
        private float _mouseY;

        private void Awake()
        {
            var inputActions = new InputActions();
            inputActions.Player.Look.performed += ctx =>
            {
                var delta = ctx.ReadValue<Vector2>();
                _mouseX = delta.x;
                _mouseY = delta.y;
            };
            inputActions.Player.Look.canceled += ctx =>
            {
                _mouseX = 0;
                _mouseY = 0;
            };
            _lookAction = inputActions.Player.Look;
        }

        private void OnEnable()
        {
            _lookAction?.Enable();
        }

        private void OnDisable()
        {
            _lookAction?.Disable();
        }

        private void LateUpdate()
        {
            if (_target == null)
            {
                return;
            }

            _targetAngle += _mouseX * _rotationSmoothness * Time.deltaTime;

            Quaternion rotation = Quaternion.Euler(0f, _targetAngle, 0f);
            Vector3 desiredPosition = _target.position - (rotation * Vector3.forward * _distance) + Vector3.up * _height;

            float actualDistance = _distance;

            if (Physics.Linecast(
                _target.position + Vector3.up * _lookAtHeightOffset,
                desiredPosition,
                out RaycastHit hit,
                _collisionMask,
                QueryTriggerInteraction.Ignore))
            {
                actualDistance = hit.distance - _collisionBuffer;
                actualDistance = Mathf.Max(actualDistance, 0.5f);
                desiredPosition = _target.position - (rotation * Vector3.forward * actualDistance) + Vector3.up * _height;
            }

            transform.position = Vector3.SmoothDamp(
                transform.position, desiredPosition, ref _currentVelocity, 1f / _positionSmoothness);

            Vector3 lookTarget = _target.position + Vector3.up * _lookAtHeightOffset;
            Quaternion lookRotation = Quaternion.LookRotation(lookTarget - transform.position);
            transform.rotation = Quaternion.Slerp(
                transform.rotation, lookRotation, _rotationSmoothness * Time.deltaTime);
        }

        public void SetTarget(Transform target)
        {
            _target = target;
        }

        public void SetDistance(float distance)
        {
            _distance = Mathf.Clamp(distance, 1f, 10f);
        }

        public void ResetCamera()
        {
            _targetAngle = _target != null ? _target.eulerAngles.y : 0f;
            _currentVelocity = Vector3.zero;
        }
    }
}
