using UnityEngine;
using UnityEngine.InputSystem;
using RideVerse.Core;
using RideVerse.Player;

namespace RideVerse.Vehicles
{
    public class VehicleInteraction : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private PlayerController _playerController;

        [Header("Settings")]
        [SerializeField] private float _interactionRange = Constants.Vehicle.InteractionRange;

        private VehicleController _nearestVehicle;
        private VehicleController _currentVehicle;
        private bool _isRiding;
        private InputActions _inputActions;

        public bool IsRiding => _isRiding;
        public VehicleController CurrentVehicle => _currentVehicle;

        public event System.Action<VehicleController> OnEnteredVehicle;
        public event System.Action<VehicleController> OnExitedVehicle;

        private void Awake()
        {
            _inputActions = new InputActions();
            _inputActions.Player.Interact.performed += ctx => OnInteract();
        }

        private void OnEnable()
        {
            _inputActions?.Player.Enable();
        }

        private void OnDisable()
        {
            _inputActions?.Player.Disable();
        }

        private void Update()
        {
            if (!_isRiding)
            {
                FindNearestVehicle();
            }
        }

        private void FindNearestVehicle()
        {
            _nearestVehicle = null;
            float closestDist = _interactionRange;

            var vehicles = FindObjectsByType<VehicleController>(FindObjectsSortMode.None);

            foreach (var vehicle in vehicles)
            {
                float dist = Vector3.Distance(transform.position, vehicle.transform.position);
                if (dist < closestDist)
                {
                    closestDist = dist;
                    _nearestVehicle = vehicle;
                }
            }
        }

        private void OnInteract()
        {
            if (_isRiding)
            {
                ExitVehicle();
            }
            else if (_nearestVehicle != null)
            {
                EnterVehicle(_nearestVehicle);
            }
        }

        public void EnterVehicle(VehicleController vehicle)
        {
            if (vehicle == null || _isRiding) return;

            _currentVehicle = vehicle;
            _isRiding = true;

            if (_playerController != null)
            {
                _playerController.SetInputEnabled(false);
                _playerController.SetRiding(true);
                _playerController.gameObject.SetActive(false);
            }

            vehicle.MountRider(transform);

            if (vehicle.IsEngineRunning)
            {
                vehicle.SetInputEnabled(true);
            }
            else
            {
                vehicle.StartKickStart();
                vehicle.SetInputEnabled(true);
            }

            OnEnteredVehicle?.Invoke(vehicle);
            Debug.Log($"[VehicleInteraction] Entered {vehicle.DisplayName}");
        }

        public void ExitVehicle()
        {
            if (!_isRiding || _currentVehicle == null) return;

            VehicleController vehicle = _currentVehicle;
            vehicle.SetInputEnabled(false);
            vehicle.DismountRider(out Vector3 exitPosition);

            transform.SetParent(null);
            transform.position = exitPosition;
            transform.rotation = Quaternion.Euler(0f, vehicle.transform.eulerAngles.y, 0f);

            if (_playerController != null)
            {
                _playerController.gameObject.SetActive(true);
                _playerController.Teleport(exitPosition);
                _playerController.SetRiding(false);
                _playerController.SetInputEnabled(true);
            }

            _isRiding = false;
            _currentVehicle = null;

            OnExitedVehicle?.Invoke(vehicle);
            Debug.Log($"[VehicleInteraction] Exited {vehicle.DisplayName}");
        }

        public VehicleController GetNearestVehicle()
        {
            return _nearestVehicle;
        }

        public bool IsNearVehicle()
        {
            return _nearestVehicle != null;
        }
    }
}
