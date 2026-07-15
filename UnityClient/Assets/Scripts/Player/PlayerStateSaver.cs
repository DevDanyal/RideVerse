using UnityEngine;
using RideVerse.Core;

namespace RideVerse.Player
{
    public class PlayerStateSaver : MonoBehaviour
    {
        [Header("Settings")]
        [SerializeField] private float _saveInterval = Constants.Vehicle.PositionSaveInterval;
        [SerializeField] private float _positionThreshold = 1f;

        private Transform _playerTransform;
        private float _lastSaveTime;
        private Vector3 _lastSavedPosition;

        public bool HasSavedPosition => PlayerPrefs.HasKey(Constants.PlayerPrefs.PlayerPosX);
        public Transform PlayerTransform => _playerTransform;

        private void Update()
        {
            if (_playerTransform == null) return;

            if (Time.time - _lastSaveTime >= _saveInterval)
            {
                float distSinceLastSave = Vector3.Distance(_playerTransform.position, _lastSavedPosition);

                if (distSinceLastSave >= _positionThreshold)
                {
                    SavePosition();
                }

                _lastSaveTime = Time.time;
            }
        }

        public void SetPlayerTransform(Transform player)
        {
            _playerTransform = player;
            _lastSavedPosition = player.position;
        }

        public void SavePosition()
        {
            if (_playerTransform == null) return;

            Vector3 pos = _playerTransform.position;
            float rotY = _playerTransform.eulerAngles.y;

            PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerPosX, pos.x);
            PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerPosY, pos.y);
            PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerPosZ, pos.z);
            PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerRotY, rotY);
            PlayerPrefs.Save();

            _lastSavedPosition = pos;
            Debug.Log($"[PlayerStateSaver] Position saved: {pos}");
        }

        public Vector3 GetSavedPosition()
        {
            if (!HasSavedPosition) return Vector3.zero;

            float x = PlayerPrefs.GetFloat(Constants.PlayerPrefs.PlayerPosX, 0f);
            float y = PlayerPrefs.GetFloat(Constants.PlayerPrefs.PlayerPosY, 0f);
            float z = PlayerPrefs.GetFloat(Constants.PlayerPrefs.PlayerPosZ, 0f);

            return new Vector3(x, y, z);
        }

        public float GetSavedRotationY()
        {
            return PlayerPrefs.GetFloat(Constants.PlayerPrefs.PlayerRotY, 0f);
        }

        public void ClearSavedPosition()
        {
            PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerPosX);
            PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerPosY);
            PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerPosZ);
            PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerRotY);
            PlayerPrefs.Save();
        }

        public void SaveImmediate()
        {
            SavePosition();
        }
    }
}
