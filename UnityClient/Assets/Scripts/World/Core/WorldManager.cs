using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.Core;
using RideVerse.World.Chunks;
using RideVerse.World.Layout;
using RideVerse.World.Buildings;
using RideVerse.World.Environment;
using RideVerse.World.Streaming;
using RideVerse.World.Spawn;
using RideVerse.World.Minimap;
using RideVerse.World.Performance;
using RideVerse.World.Settings;

namespace RideVerse.World.Core
{
    public class WorldManager : Singleton<WorldManager>
    {
        [Header("Configuration")]
        [SerializeField] private WorldConfig _config;
        [SerializeField] private WorldSettings _settings;

        [Header("References")]
        [SerializeField] private ChunkManager _chunkManager;
        [SerializeField] private CityLayoutGenerator _layoutGenerator;
        [SerializeField] private BuildingPlacer _buildingPlacer;
        [SerializeField] private EnvironmentPlacer _environmentPlacer;
        [SerializeField] private WorldStreamer _streamer;
        [SerializeField] private SpawnManager _spawnManager;
        [SerializeField] private MinimapManager _minimapManager;
        [SerializeField] private AndroidOptimizer _optimizer;

        [Header("Spawn")]
        [SerializeField] private Transform _playerSpawnPoint;

        private WorldSaveData _currentSaveData;
        private bool _isWorldLoaded;
        private Transform _worldRoot;

        public WorldConfig Config => _config;
        public bool IsWorldLoaded => _isWorldLoaded;
        public SpawnManager SpawnSystem => _spawnManager;
        public MinimapManager Minimap => _minimapManager;

        public event Action OnWorldLoaded;
        public event Action OnWorldSaved;
        public event Action OnWorldCleared;

        protected override void Awake()
        {
            base.Awake();
            InitializeComponents();
        }

        private void InitializeComponents()
        {
            if (_chunkManager == null)
                _chunkManager = GetComponentInChildren<ChunkManager>();
            if (_layoutGenerator == null)
                _layoutGenerator = GetComponentInChildren<CityLayoutGenerator>();
            if (_buildingPlacer == null)
                _buildingPlacer = GetComponentInChildren<BuildingPlacer>();
            if (_environmentPlacer == null)
                _environmentPlacer = GetComponentInChildren<EnvironmentPlacer>();
            if (_streamer == null)
                _streamer = GetComponentInChildren<WorldStreamer>();
            if (_spawnManager == null)
                _spawnManager = GetComponentInChildren<SpawnManager>();
            if (_minimapManager == null)
                _minimapManager = GetComponentInChildren<MinimapManager>();
            if (_optimizer == null)
                _optimizer = GetComponentInChildren<AndroidOptimizer>();
        }

        public void LoadWorld()
        {
            Debug.Log("[WorldManager] Loading world...");

            if (_config == null)
            {
                Debug.LogError("[WorldManager] WorldConfig is null!");
                return;
            }

            _worldRoot = new GameObject("World_Root").transform;
            _worldRoot.SetParent(transform);

            InitializeAllSystems();
            GenerateWorld();
            RegisterSpawnPoints();
            ApplySettings();
            OptimizeForPlatform();

            _isWorldLoaded = true;
            OnWorldLoaded?.Invoke();
            Debug.Log("[WorldManager] World loaded successfully");
        }

        public void LoadWorld(string savePath)
        {
            Debug.Log($"[WorldManager] Loading world from save: {savePath}");

            if (File.Exists(savePath))
            {
                string json = File.ReadAllText(savePath);
                _currentSaveData = JsonUtility.FromJson<WorldSaveData>(json);

                if (_currentSaveData == null)
                {
                    Debug.LogWarning("[WorldManager] Failed to parse save data, loading fresh world");
                    LoadWorld();
                    return;
                }

                LoadWorld();

                if (_currentSaveData.PlayerData != null && _playerSpawnPoint != null)
                {
                    _playerSpawnPoint.position = _currentSaveData.PlayerData.GetPosition();
                    _playerSpawnPoint.rotation = Quaternion.Euler(0f, _currentSaveData.PlayerData.RotationY, 0f);
                }

                if (_currentSaveData.Settings != null && _settings != null)
                {
                    _settings.LoadFromSaveData(_currentSaveData.Settings);
                    _settings.Apply();
                }
            }
            else
            {
                LoadWorld();
            }
        }

        public void SaveWorld()
        {
            Debug.Log("[WorldManager] Saving world...");

            string saveDir = Path.Combine(Application.persistentDataPath, "saves");
            if (!Directory.Exists(saveDir))
            {
                Directory.CreateDirectory(saveDir);
            }

            _currentSaveData = new WorldSaveData
            {
                WorldId = _config.worldId,
                SaveTimestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
                PlayerData = new PlayerSpawnData(),
                Settings = _settings != null ? _settings.ToSaveData() : new WorldSettingsData()
            };

            if (_playerSpawnPoint != null)
            {
                _currentSaveData.PlayerData.SetPosition(_playerSpawnPoint.position);
                _currentSaveData.PlayerData.RotationY = _playerSpawnPoint.eulerAngles.y;
            }

            if (_buildingPlacer != null)
            {
                foreach (var building in _buildingPlacer.PlacedBuildings)
                {
                    _currentSaveData.PlacedBuildings.Add(new PlacedBuildingData
                    {
                        Id = building.Id,
                        BuildingTypeIndex = (int)building.Type,
                        PositionX = building.Position.x,
                        PositionY = building.Position.y,
                        PositionZ = building.Position.z,
                        RotationY = building.RotationY,
                        ScaleX = building.Scale.x,
                        ScaleY = building.Scale.y,
                        ScaleZ = building.Scale.z
                    });
                }
            }

            string json = JsonUtility.ToJson(_currentSaveData, true);
            string savePath = Path.Combine(saveDir, $"{_config.worldId}_save.json");
            File.WriteAllText(savePath, json);

            OnWorldSaved?.Invoke();
            Debug.Log($"[WorldManager] World saved to: {savePath}");
        }

        private void InitializeAllSystems()
        {
            _chunkManager?.Initialize(_config);
            _layoutGenerator?.Initialize(_config);
            _buildingPlacer?.Initialize(_config);
            _environmentPlacer?.Initialize(_config);
            _streamer?.Initialize(_config, _chunkManager);
            _spawnManager?.Initialize();

            if (_minimapManager != null)
            {
                var minimapCam = GetComponentInChildren<Camera>();
                _minimapManager.Initialize(minimapCam, null);
            }
        }

        private void GenerateWorld()
        {
            if (_layoutGenerator != null)
            {
                _layoutGenerator.GenerateCityLayout(_worldRoot);
            }

            if (_layoutGenerator != null && _buildingPlacer != null)
            {
                foreach (var district in _layoutGenerator.Districts)
                {
                    _buildingPlacer.GenerateBuildingsForDistrict(district, _worldRoot);
                }
            }

            if (_environmentPlacer != null && _config != null)
            {
                Vector3 center = _config.WorldCenter;
                float radius = Mathf.Max(_config.worldSizeX, _config.worldSizeZ) * 0.5f;
                _environmentPlacer.GenerateEnvironment(center, radius, _worldRoot);
            }

            GenerateNearbyChunks();
        }

        private void GenerateNearbyChunks()
        {
            if (_chunkManager == null || _config == null) return;

            Vector3 center = _config.WorldCenter;
            ChunkCoord centerChunk = ChunkCoord.FromWorldPosition(center, _config.chunkSize);

            int initialRadius = 2;
            for (int x = -initialRadius; x <= initialRadius; x++)
            {
                for (int z = -initialRadius; z <= initialRadius; z++)
                {
                    ChunkCoord coord = new ChunkCoord(centerChunk.X + x, centerChunk.Z + z);
                    _chunkManager.UpdatePlayerPosition(coord.ToWorldPosition(_config.chunkSize));
                }
            }
        }

        private void RegisterSpawnPoints()
        {
            if (_spawnManager == null || _config == null) return;

            Vector3 center = _config.WorldCenter;
            _spawnManager.RegisterSpawnPoint(SpawnType.Player, center + new Vector3(0f, 1f, 0f));
            _spawnManager.RegisterSpawnPoint(SpawnType.Player, center + new Vector3(50f, 1f, 0f));
            _spawnManager.RegisterSpawnPoint(SpawnType.Player, center + new Vector3(-50f, 1f, 0f));

            _spawnManager.RegisterSpawnPoint(SpawnType.Vehicle, center + new Vector3(10f, 0.1f, 10f), 0f);
            _spawnManager.RegisterSpawnPoint(SpawnType.Vehicle, center + new Vector3(-10f, 0.1f, 10f), 90f);
            _spawnManager.RegisterSpawnPoint(SpawnType.Vehicle, center + new Vector3(10f, 0.1f, -10f), 180f);
            _spawnManager.RegisterSpawnPoint(SpawnType.Vehicle, center + new Vector3(-10f, 0.1f, -10f), 270f);

            _spawnManager.RegisterSpawnPoint(SpawnType.NPC, center + new Vector3(20f, 0f, 20f));
            _spawnManager.RegisterSpawnPoint(SpawnType.NPC, center + new Vector3(-20f, 0f, 20f));
            _spawnManager.RegisterSpawnPoint(SpawnType.NPC, center + new Vector3(20f, 0f, -20f));

            Debug.Log($"[WorldManager] Registered {_spawnManager.TotalSpawnPoints} spawn points");
        }

        private void ApplySettings()
        {
            if (_settings != null)
            {
                _settings.Apply();
            }
        }

        private void OptimizeForPlatform()
        {
            if (_optimizer != null)
            {
                _optimizer.Initialize();
            }
        }

        public void SetPlayerForStreaming(Transform player)
        {
            if (_streamer != null)
            {
                _streamer.SetPlayerTransform(player);
            }

            if (_chunkManager != null)
            {
                _chunkManager.UpdatePlayerPosition(player.position);
            }

            if (_minimapManager != null)
            {
                _minimapManager.SetPlayerTransform(player);
            }
        }

        public void ClearWorld()
        {
            Debug.Log("[WorldManager] Clearing world...");

            _buildingPlacer?.ClearBuildings();
            _environmentPlacer?.ClearEnvironment();
            _layoutGenerator?.ClearLayout();
            _chunkManager?.ClearAllChunks();
            _spawnManager?.Initialize();
            _minimapManager?.ClearIcons();

            if (_worldRoot != null)
            {
                Destroy(_worldRoot.gameObject);
            }

            _isWorldLoaded = false;
            OnWorldCleared?.Invoke();
            Debug.Log("[WorldManager] World cleared");
        }

        public WorldSaveData GetCurrentSaveData()
        {
            return _currentSaveData;
        }

        public string GetSavePath()
        {
            return Path.Combine(Application.persistentDataPath, "saves", $"{_config.worldId}_save.json");
        }

        public bool HasSaveData()
        {
            return File.Exists(GetSavePath());
        }
    }
}
