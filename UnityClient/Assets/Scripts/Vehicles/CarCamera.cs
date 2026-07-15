using UnityEngine;

namespace RideVerse.Vehicles
{
    public enum CameraMode
    {
        ThirdPerson,
        FirstPerson,
        Hood,
        Orbit
    }

    public class CarCamera : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private Transform carTransform;
        [SerializeField] private Transform driverSeat;
        [SerializeField] private Transform hoodMount;

        [Header("Third Person Settings")]
        [SerializeField] private float thirdPersonDistance = 6f;
        [SerializeField] private float thirdPersonHeight = 2.5f;
        [SerializeField] private float thirdPersonLookAhead = 2f;
        [SerializeField] private float thirdPersonSmoothing = 8f;

        [Header("First Person Settings")]
        [SerializeField] private float firstPersonFOV = 75f;

        [Header("Hood Settings")]
        [SerializeField] private float hoodFOV = 85f;

        [Header("Orbit Settings")]
        [SerializeField] private float orbitDistance = 5f;
        [SerializeField] private float orbitHeight = 2f;
        [SerializeField] private float orbitSensitivity = 3f;
        [SerializeField] private float orbitMinAngle = -20f;
        [SerializeField] private float orbitMaxAngle = 60f;

        [Header("General")]
        [SerializeField] private float collisionBuffer = 0.3f;
        [SerializeField] private LayerMask collisionMask;

        private Camera _camera;
        private CameraMode _currentMode = CameraMode.ThirdPerson;
        private float _orbitYaw;
        private float _orbitPitch = 15f;
        private Vector3 _currentVelocity;
        private bool _isFollowing;

        public CameraMode CurrentMode => _currentMode;

        private void Awake()
        {
            _camera = GetComponent<Camera>();
            if (_camera == null) _camera = GetComponentInChildren<Camera>();
        }

        private void LateUpdate()
        {
            if (carTransform == null || !_isFollowing) return;

            switch (_currentMode)
            {
                case CameraMode.ThirdPerson:
                    UpdateThirdPerson();
                    break;
                case CameraMode.FirstPerson:
                    UpdateFirstPerson();
                    break;
                case CameraMode.Hood:
                    UpdateHood();
                    break;
                case CameraMode.Orbit:
                    UpdateOrbit();
                    break;
            }
        }

        private void UpdateThirdPerson()
        {
            if (_camera == null) return;

            Vector3 targetPosition = carTransform.position +
                carTransform.up * thirdPersonHeight -
                carTransform.forward * thirdPersonDistance;

            targetPosition += carTransform.forward * thirdPersonLookAhead;

            transform.position = Vector3.SmoothDamp(
                transform.position, targetPosition, ref _currentVelocity, 1f / thirdPersonSmoothing);

            transform.LookAt(carTransform.position + carTransform.forward * 2f + carTransform.up * 1f);
            _camera.fieldOfView = 60f;
        }

        private void UpdateFirstPerson()
        {
            if (driverSeat == null || _camera == null) return;

            transform.position = driverSeat.position + Vector3.up * 0.3f;
            transform.rotation = carTransform.rotation;
            _camera.fieldOfView = firstPersonFOV;
        }

        private void UpdateHood()
        {
            if (hoodMount == null || _camera == null) return;

            transform.position = hoodMount.position;
            transform.rotation = carTransform.rotation;
            _camera.fieldOfView = hoodFOV;
        }

        private void UpdateOrbit()
        {
            if (_camera == null) return;

            if (Input.GetMouseButton(1))
            {
                _orbitYaw += Input.GetAxis("Mouse X") * orbitSensitivity;
                _orbitPitch -= Input.GetAxis("Mouse Y") * orbitSensitivity;
                _orbitPitch = Mathf.Clamp(_orbitPitch, orbitMinAngle, orbitMaxAngle);
            }

            Quaternion rotation = Quaternion.Euler(_orbitPitch, _orbitYaw, 0f);
            Vector3 offset = rotation * new Vector3(0f, 0f, -orbitDistance) + Vector3.up * orbitHeight;

            Vector3 targetPos = carTransform.position + offset;

            if (Physics.Raycast(carTransform.position, offset.normalized, out RaycastHit hit, offset.magnitude + collisionBuffer, collisionMask))
                targetPos = hit.point - offset.normalized * collisionBuffer;

            transform.position = Vector3.Lerp(transform.position, targetPos, Time.deltaTime * 5f);
            transform.LookAt(carTransform.position + Vector3.up * 1f);
            _camera.fieldOfView = 60f;
        }

        public void SetTarget(Transform car, Transform seat = null, Transform hood = null)
        {
            carTransform = car;
            driverSeat = seat;
            hoodMount = hood;
            _isFollowing = car != null;

            if (_isFollowing && _camera != null)
            {
                transform.SetParent(null);
                _camera.enabled = true;
            }
        }

        public void SetMode(CameraMode mode)
        {
            _currentMode = mode;
        }

        public void CycleCameraMode()
        {
            _currentMode = (CameraMode)(((int)_currentMode + 1) % 4);
        }

        public void StartFollowing()
        {
            _isFollowing = true;
        }

        public void StopFollowing()
        {
            _isFollowing = false;
        }

        public void SetFollowEnabled(bool enabled)
        {
            _isFollowing = enabled;
        }
    }
}
