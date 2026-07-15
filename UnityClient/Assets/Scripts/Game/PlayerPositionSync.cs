using UnityEngine;
using RideVerse.Core;
using RideVerse.Network;
using RideVerse.Player;
using RideVerse.Vehicles;

namespace RideVerse.Game
{
    public class PlayerPositionSync : MonoBehaviour
    {
        [Header("Settings")]
        [SerializeField] private float _syncInterval = 1f / Constants.Network.SendRate;
        [SerializeField] private float _positionThreshold = 0.01f;
        [SerializeField] private float _rotationThreshold = 1f;

        private Transform _playerTransform;
        private VehicleController _vehicleController;
        private float _lastSyncTime;
        private Vector3 _lastSyncedPosition;
        private float _lastSyncedRotationY;

        public bool IsSyncing { get; private set; }

        public void SetPlayerTransform(Transform player)
        {
            _playerTransform = player;
            _lastSyncedPosition = player != null ? player.position : Vector3.zero;
            _lastSyncedRotationY = player != null ? player.eulerAngles.y : 0f;
        }

        public void SetVehicleController(VehicleController vehicle)
        {
            _vehicleController = vehicle;
        }

        private void Update()
        {
            if (_playerTransform == null) return;
            if (NetworkManager.Instance == null || !NetworkManager.Instance.IsConnected) return;

            if (Time.time - _lastSyncTime >= _syncInterval)
            {
                SyncPosition();
                _lastSyncTime = Time.time;
            }
        }

        private void SyncPosition()
        {
            Vector3 currentPosition;
            float currentRotationY;
            float currentSpeed;
            bool isInVehicle;
            string vehicleId = null;

            if (_vehicleController != null && _vehicleController.HasRider)
            {
                currentPosition = _vehicleController.transform.position;
                currentRotationY = _vehicleController.transform.eulerAngles.y;
                currentSpeed = Mathf.Abs(_vehicleController.CurrentSpeed);
                isInVehicle = true;
                vehicleId = _vehicleController.VehicleId;
            }
            else
            {
                currentPosition = _playerTransform.position;
                currentRotationY = _playerTransform.eulerAngles.y;
                currentSpeed = _playerTransform.GetComponent<PlayerController>()?.CurrentSpeed ?? 0f;
                isInVehicle = false;
            }

            float posDist = Vector3.Distance(currentPosition, _lastSyncedPosition);
            float rotDiff = Mathf.Abs(Mathf.DeltaAngle(currentRotationY, _lastSyncedRotationY));

            if (posDist < _positionThreshold && rotDiff < _rotationThreshold)
            {
                return;
            }

            var positionUpdate = new WsPositionUpdate
            {
                PositionX = currentPosition.x,
                PositionY = currentPosition.y,
                PositionZ = currentPosition.z,
                RotationX = 0f,
                RotationY = currentRotationY,
                RotationZ = 0f,
                VelocityX = 0f,
                VelocityY = 0f,
                VelocityZ = 0f,
                Speed = currentSpeed,
                IsInVehicle = isInVehicle,
                VehicleId = vehicleId
            };

            NetworkManager.Instance.SendPosition(positionUpdate);

            _lastSyncedPosition = currentPosition;
            _lastSyncedRotationY = currentRotationY;
            IsSyncing = true;
        }

        public void ForceSync()
        {
            _lastSyncTime = 0f;
        }
    }
}
