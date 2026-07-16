using UnityEngine;
using RideVerse.Core;
using RideVerse.Player;
using RideVerse.Vehicles;
using RideVerse.Network;
using RideVerse.UI;

namespace RideVerse.Game
{
    public class GameManager : MonoBehaviour
    {
        [Header("Player")]
        [SerializeField] private PlayerSpawner _playerSpawner;
        [SerializeField] private VehicleInteraction _vehicleInteraction;

        [Header("Map")]
        [SerializeField] private TestMapGenerator _mapGenerator;

        [Header("Vehicles")]
        [SerializeField] private VehicleController[] _spawnedVehicles;

        [Header("Network")]
        [SerializeField] private PlayerPositionSync _positionSync;

        [Header("UI")]
        [SerializeField] private HUDUI _hud;

        private bool _isGameActive;
        private PlayerStateSaver _stateSaver;

        private void Start()
        {
            InitializeGame();
        }

        private void InitializeGame()
        {
            Debug.Log("[GameManager] Initializing game...");

            if (_mapGenerator != null)
            {
                _mapGenerator.GenerateMap();
            }

            SpawnPlayer();

            if (_hud != null)
            {
                _hud.SetHUDVisible(true);
                _hud.UpdateHealth(100, 100);
                _hud.UpdateStamina(100, 100);
                _hud.UpdateMoney(500, 1000);
            }

            ConnectToNetwork();

            _isGameActive = true;
            Debug.Log("[GameManager] Game initialized");
        }

        private void SpawnPlayer()
        {
            if (_playerSpawner == null) return;

            _playerSpawner.SpawnPlayer();

            var player = _playerSpawner.SpawnedPlayer;
            if (player != null)
            {
                var controller = player.GetComponent<PlayerController>();
                _stateSaver = player.GetComponent<PlayerStateSaver>();

                if (_stateSaver != null && _stateSaver.HasSavedPosition)
                {
                    Vector3 savedPos = _stateSaver.GetSavedPosition();
                    float savedRot = _stateSaver.GetSavedRotationY();

                    if (savedPos != Vector3.zero)
                    {
                        controller?.Teleport(savedPos);
                        player.transform.rotation = Quaternion.Euler(0f, savedRot, 0f);
                        Debug.Log($"[GameManager] Player loaded from saved position: {savedPos}");
                    }
                }

                if (_stateSaver != null)
                {
                    _stateSaver.SetPlayerTransform(player.transform);
                }

                if (_vehicleInteraction != null)
                {
                    _vehicleInteraction.OnEnteredVehicle += HandleEnteredVehicle;
                    _vehicleInteraction.OnExitedVehicle += HandleExitedVehicle;
                }

                if (_positionSync != null)
                {
                    _positionSync.SetPlayerTransform(player.transform);
                }
            }
        }

        private void ConnectToNetwork()
        {
            if (NetworkManager.Instance != null && !NetworkManager.Instance.IsConnected)
            {
                NetworkManager.Instance.Connect();
            }
        }

        private void HandleEnteredVehicle(VehicleController vehicle)
        {
            Debug.Log($"[GameManager] Player entered {vehicle.DisplayName}");

            if (_positionSync != null)
            {
                _positionSync.SetVehicleController(vehicle);
            }

            if (_hud != null)
            {
                _hud.UpdateFuel(vehicle.CurrentFuel, vehicle.MaxFuel);
            }
        }

        private void HandleExitedVehicle(VehicleController vehicle)
        {
            Debug.Log($"[GameManager] Player exited {vehicle.DisplayName}");

            if (_positionSync != null)
            {
                _positionSync.SetVehicleController(null);
            }
        }

        private void Update()
        {
            if (!_isGameActive) return;

            UpdateHUD();
            HandleAutoSave();
        }

        private void UpdateHUD()
        {
            if (_hud == null) return;

            if (_vehicleInteraction != null && _vehicleInteraction.IsRiding)
            {
                var vehicle = _vehicleInteraction.CurrentVehicle;
                if (vehicle != null)
                {
                    _hud.UpdateFuel(vehicle.CurrentFuel, vehicle.MaxFuel);
                }
            }
        }

        private void HandleAutoSave()
        {
            if (_stateSaver != null && _playerSpawner != null && _playerSpawner.SpawnedPlayer != null)
            {
                if (_stateSaver.PlayerTransform == null)
                {
                    _stateSaver.SetPlayerTransform(_playerSpawner.SpawnedPlayer.transform);
                }
            }
        }

        private void OnDestroy()
        {
            if (_vehicleInteraction != null)
            {
                _vehicleInteraction.OnEnteredVehicle -= HandleEnteredVehicle;
                _vehicleInteraction.OnExitedVehicle -= HandleExitedVehicle;
            }

            if (_stateSaver != null)
            {
                _stateSaver.SaveImmediate();
            }
        }

        private void OnApplicationPause(bool paused)
        {
            if (paused && _stateSaver != null)
            {
                _stateSaver.SaveImmediate();
            }
        }

        private void OnApplicationQuit()
        {
            if (_stateSaver != null)
            {
                _stateSaver.SaveImmediate();
            }
        }

        public void PauseGame()
        {
            Time.timeScale = 0f;
            _isGameActive = false;
        }

        public void ResumeGame()
        {
            Time.timeScale = 1f;
            _isGameActive = true;
        }

        public void RestartGame()
        {
            _isGameActive = false;
            Time.timeScale = 1f;
            AppManager.Instance?.LoadScene(Constants.Scenes.Game);
        }

        public void ReturnToMainMenu()
        {
            _isGameActive = false;
            Time.timeScale = 1f;
            NetworkManager.Instance?.Disconnect();
            AppManager.Instance?.LoadScene(Constants.Scenes.MainMenu);
        }
    }
}
