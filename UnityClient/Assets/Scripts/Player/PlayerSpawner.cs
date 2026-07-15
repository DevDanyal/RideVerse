using System;
using UnityEngine;
using RideVerse.Network;
using RideVerse.Core;

namespace RideVerse.Player
{
    public class PlayerSpawner : MonoBehaviour
    {
        [Header("Prefabs")]
        [SerializeField] private GameObject _playerPrefab;

        [Header("Spawn")]
        [SerializeField] private Transform _defaultSpawnPoint;

        private GameObject _spawnedPlayer;

        public GameObject SpawnedPlayer => _spawnedPlayer;
        public PlayerController Controller => _spawnedPlayer?.GetComponent<PlayerController>();

        public event Action<GameObject> OnPlayerSpawned;
        public event Action OnPlayerDespawned;

        private void Start()
        {
            SpawnPlayer();
        }

        public void SpawnPlayer()
        {
            if (_playerPrefab == null)
            {
                Debug.LogError("[PlayerSpawner] Player prefab is not assigned");
                return;
            }

            Vector3 spawnPos = _defaultSpawnPoint != null
                ? _defaultSpawnPoint.position
                : Vector3.up * 0.5f;

            Quaternion spawnRot = _defaultSpawnPoint != null
                ? _defaultSpawnPoint.rotation
                : Quaternion.identity;

            _spawnedPlayer = Instantiate(_playerPrefab, spawnPos, spawnRot);
            _spawnedPlayer.tag = Constants.Tags.Player;

            SetupCamera();
            SetupNetworkSync();

            OnPlayerSpawned?.Invoke(_spawnedPlayer);
            Debug.Log("[PlayerSpawner] Player spawned");
        }

        public void DespawnPlayer()
        {
            if (_spawnedPlayer != null)
            {
                Destroy(_spawnedPlayer);
                _spawnedPlayer = null;
                OnPlayerDespawned?.Invoke();
                Debug.Log("[PlayerSpawner] Player despawned");
            }
        }

        private void SetupCamera()
        {
            Camera mainCam = Camera.main;
            if (mainCam != null)
            {
                var tpc = mainCam.GetComponent<ThirdPersonCamera>();
                if (tpc != null)
                {
                    tpc.SetTarget(_spawnedPlayer.transform);
                    tpc.ResetCamera();
                }
            }
        }

        private void SetupNetworkSync()
        {
            var controller = _spawnedPlayer.GetComponent<PlayerController>();
            if (controller != null && NetworkManager.Instance != null && NetworkManager.Instance.IsConnected)
            {
                controller.SetInputEnabled(true);
            }
        }

        public void TeleportPlayer(Vector3 position)
        {
            var controller = _spawnedPlayer?.GetComponent<PlayerController>();
            if (controller != null)
            {
                controller.Teleport(position);
            }
        }
    }
}
