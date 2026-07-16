using System;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.Core;

namespace RideVerse.Traffic.Core
{
    public class TrafficManager : Singleton<TrafficManager>
    {
        [Header("Configuration")]
        [SerializeField] private TrafficConfig _config;

        [Header("References")]
        [SerializeField] private Transform _playerTransform;

        private Dictionary<string, TrafficVehicle> _activeVehicles = new Dictionary<string, TrafficVehicle>();
        private List<string> _vehicleIdPool = new List<string>();
        private readonly List<string> _despawnBuffer = new List<string>();
        private readonly Dictionary<Color, Material> _materialCache = new Dictionary<Color, Material>();
        private Material _baseMaterial;
        private float _spawnTimer;
        private float _updateTimer;
        private bool _isInitialized;
        private int _nextVehicleIndex;

        public TrafficConfig Config => _config;
        public int ActiveVehicleCount => _activeVehicles.Count;
        public bool IsInitialized => _isInitialized;

        public event Action<TrafficVehicle> OnVehicleSpawned;
        public event Action<TrafficVehicle> OnVehicleDespawned;

        protected override void Awake()
        {
            base.Awake();
        }

        public void Initialize(TrafficConfig config)
        {
            _config = config;
            _isInitialized = true;
            _nextVehicleIndex = 0;
            Debug.Log($"[TrafficManager] Initialized with max {_config.maxTrafficVehicles} vehicles");
        }

        public void SetPlayerTransform(Transform player)
        {
            _playerTransform = player;
        }

        private void Update()
        {
            if (!_isInitialized || _playerTransform == null) return;

            _updateTimer += Time.deltaTime;
            _spawnTimer += Time.deltaTime;

            if (_spawnTimer >= 1f)
            {
                _spawnTimer = 0f;
                UpdateSpawning();
                UpdateDespawning();
            }
        }

        private void UpdateSpawning()
        {
            if (_activeVehicles.Count >= _config.maxTrafficVehicles) return;

            int toSpawn = Mathf.Min(3, _config.maxTrafficVehicles - _activeVehicles.Count);
            for (int i = 0; i < toSpawn; i++)
            {
                SpawnVehicleNearPlayer();
            }
        }

        private void UpdateDespawning()
        {
            _despawnBuffer.Clear();

            foreach (var kvp in _activeVehicles)
            {
                if (kvp.Value == null)
                {
                    _despawnBuffer.Add(kvp.Key);
                    continue;
                }

                float distance = Vector3.Distance(_playerTransform.position, kvp.Value.transform.position);
                if (distance > _config.despawnRadius)
                {
                    _despawnBuffer.Add(kvp.Key);
                }
            }

            foreach (var id in _despawnBuffer)
            {
                if (_activeVehicles.TryGetValue(id, out var vehicle))
                {
                    OnVehicleDespawned?.Invoke(vehicle);
                    _activeVehicles.Remove(id);
                    Destroy(vehicle.gameObject);
                }
            }
        }

        private void SpawnVehicleNearPlayer()
        {
            Vector3 spawnPos = GetSpawnPosition();
            float rotation = GetSpawnRotation(spawnPos);
            TrafficVehicleType type = GetRandomVehicleType();
            float maxSpeed = GetMaxSpeedForType(type);

            TrafficVehicle vehicle = SpawnVehicle(type, spawnPos, rotation, maxSpeed);
            if (vehicle != null)
            {
                OnVehicleSpawned?.Invoke(vehicle);
            }
        }

        public TrafficVehicle SpawnVehicle(TrafficVehicleType type, Vector3 position, float rotationY, float maxSpeed)
        {
            string id = GenerateVehicleId();
            GameObject go = CreateVehicleObject(type, position, rotationY);
            TrafficVehicle vehicle = go.GetComponent<TrafficVehicle>();
            if (vehicle == null)
                vehicle = go.AddComponent<TrafficVehicle>();

            vehicle.Initialize(id, type, position, rotationY, maxSpeed);
            _activeVehicles[id] = vehicle;
            return vehicle;
        }

        public void DespawnVehicle(string vehicleId)
        {
            if (_activeVehicles.TryGetValue(vehicleId, out var vehicle))
            {
                OnVehicleDespawned?.Invoke(vehicle);
                _activeVehicles.Remove(vehicleId);
                if (vehicle != null)
                    Destroy(vehicle.gameObject);
            }
        }

        public void DespawnAllVehicles()
        {
            foreach (var kvp in _activeVehicles)
            {
                if (kvp.Value != null)
                {
                    OnVehicleDespawned?.Invoke(kvp.Value);
                    Destroy(kvp.Value.gameObject);
                }
            }
            _activeVehicles.Clear();
        }

        private GameObject CreateVehicleObject(TrafficVehicleType type, Vector3 position, float rotationY)
        {
            var go = new GameObject($"Traffic_{type}_{_nextVehicleIndex++}");
            go.transform.position = position;
            go.transform.rotation = Quaternion.Euler(0f, rotationY, 0f);

            var collider = go.AddComponent<BoxCollider>();
            ApplyVehicleColliderSize(collider, type);

            ApplyVehicleVisual(go, type);

            return go;
        }

        private void ApplyVehicleColliderSize(BoxCollider collider, TrafficVehicleType type)
        {
            switch (type)
            {
                case TrafficVehicleType.Motorcycle:
                case TrafficVehicleType.Scooter:
                    collider.size = new Vector3(0.8f, 1.2f, 2.0f);
                    collider.center = new Vector3(0f, 0.6f, 0f);
                    break;
                case TrafficVehicleType.Bus:
                    collider.size = new Vector3(2.5f, 3.0f, 11f);
                    collider.center = new Vector3(0f, 1.5f, 0f);
                    break;
                case TrafficVehicleType.CargoTruck:
                case TrafficVehicleType.FuelTanker:
                    collider.size = new Vector3(2.6f, 3.5f, 12f);
                    collider.center = new Vector3(0f, 1.75f, 0f);
                    break;
                default:
                    collider.size = new Vector3(1.8f, 1.5f, 4.5f);
                    collider.center = new Vector3(0f, 0.75f, 0f);
                    break;
            }
        }

        private void ApplyVehicleVisual(GameObject go, TrafficVehicleType type)
        {
            var renderer = go.AddComponent<MeshFilter>();
            var meshRenderer = go.AddComponent<MeshRenderer>();

            Vector3 scale;
            Color color = GetRandomVehicleColor(type);

            switch (type)
            {
                case TrafficVehicleType.Motorcycle:
                case TrafficVehicleType.Scooter:
                    scale = new Vector3(0.7f, 1.0f, 1.8f);
                    break;
                case TrafficVehicleType.Bus:
                    scale = new Vector3(2.4f, 2.8f, 10f);
                    color = new Color(0.2f, 0.5f, 0.8f);
                    break;
                case TrafficVehicleType.DeliveryVan:
                    scale = new Vector3(2.0f, 2.2f, 5.5f);
                    color = new Color(0.9f, 0.9f, 0.9f);
                    break;
                case TrafficVehicleType.CargoTruck:
                case TrafficVehicleType.FuelTanker:
                    scale = new Vector3(2.5f, 3.0f, 11f);
                    color = new Color(0.3f, 0.3f, 0.3f);
                    break;
                default:
                    scale = new Vector3(1.7f, 1.3f, 4.2f);
                    break;
            }

            go.transform.localScale = scale;

            meshRenderer.material = GetOrCreateMaterial(color);
        }

        private Material GetOrCreateMaterial(Color color)
        {
            if (_materialCache.TryGetValue(color, out var cached))
                return cached;

            if (_baseMaterial == null)
                _baseMaterial = new Material(Shader.Find("Universal Render Pipeline/Lit"));

            var mat = new Material(_baseMaterial);
            mat.color = color;
            _materialCache[color] = mat;
            return mat;
        }

        private Color GetRandomVehicleColor(TrafficVehicleType type)
        {
            if (type == TrafficVehicleType.Bus)
                return new Color(0.2f, 0.5f, 0.8f);
            if (type == TrafficVehicleType.Taxi)
                return new Color(1f, 0.9f, 0.1f);

            Color[] carColors = {
                new Color(0.9f, 0.9f, 0.9f),
                new Color(0.15f, 0.15f, 0.15f),
                new Color(0.7f, 0.1f, 0.1f),
                new Color(0.1f, 0.2f, 0.6f),
                new Color(0.5f, 0.5f, 0.5f),
                new Color(0.9f, 0.8f, 0.1f),
                new Color(0.1f, 0.5f, 0.2f),
                new Color(0.8f, 0.4f, 0.1f)
            };

            return carColors[UnityEngine.Random.Range(0, carColors.Length)];
        }

        private Vector3 GetSpawnPosition()
        {
            if (_playerTransform == null) return Vector3.zero;

            float angle = UnityEngine.Random.Range(0f, 360f) * Mathf.Deg2Rad;
            float distance = UnityEngine.Random.Range(_config.playerSpawnBuffer, _config.spawnRadius);

            Vector3 pos = _playerTransform.position + new Vector3(
                Mathf.Cos(angle) * distance,
                0f,
                Mathf.Sin(angle) * distance
            );
            pos.y = 0f;

            return pos;
        }

        private float GetSpawnRotation(Vector3 spawnPos)
        {
            if (_playerTransform == null) return 0f;
            Vector3 dir = (_playerTransform.position - spawnPos).normalized;
            dir.y = 0f;
            if (dir.sqrMagnitude < 0.01f) return UnityEngine.Random.Range(0f, 360f);
            return Quaternion.LookRotation(dir).eulerAngles.y;
        }

        private TrafficVehicleType GetRandomVehicleType()
        {
            float roll = UnityEngine.Random.value;
            if (roll < 0.25f) return TrafficVehicleType.Sedan;
            if (roll < 0.40f) return TrafficVehicleType.SUV;
            if (roll < 0.50f) return TrafficVehicleType.Motorcycle;
            if (roll < 0.60f) return TrafficVehicleType.PickupTruck;
            if (roll < 0.68f) return TrafficVehicleType.SportsCar;
            if (roll < 0.75f) return TrafficVehicleType.DeliveryVan;
            if (roll < 0.82f) return TrafficVehicleType.LuxuryCar;
            if (roll < 0.88f) return TrafficVehicleType.Bus;
            if (roll < 0.93f) return TrafficVehicleType.CargoTruck;
            if (roll < 0.97f) return TrafficVehicleType.Taxi;
            return TrafficVehicleType.Scooter;
        }

        private float GetMaxSpeedForType(TrafficVehicleType type)
        {
            switch (type)
            {
                case TrafficVehicleType.Motorcycle:
                case TrafficVehicleType.Scooter:
                    return 45f;
                case TrafficVehicleType.SportsCar:
                case TrafficVehicleType.Supercar:
                    return 80f;
                case TrafficVehicleType.LuxuryCar:
                    return 65f;
                case TrafficVehicleType.Sedan:
                    return 55f;
                case TrafficVehicleType.SUV:
                case TrafficVehicleType.PickupTruck:
                    return 50f;
                case TrafficVehicleType.Bus:
                    return 40f;
                case TrafficVehicleType.DeliveryVan:
                    return 45f;
                case TrafficVehicleType.CargoTruck:
                case TrafficVehicleType.FuelTanker:
                    return 35f;
                case TrafficVehicleType.Taxi:
                    return 55f;
                case TrafficVehicleType.Police:
                    return 65f;
                default:
                    return _config.defaultMaxSpeed;
            }
        }

        private string GenerateVehicleId()
        {
            return $"TV_{DateTime.UtcNow.Ticks % 10000000}_{_nextVehicleIndex++}";
        }

        public TrafficVehicle GetVehicle(string id)
        {
            _activeVehicles.TryGetValue(id, out var vehicle);
            return vehicle;
        }

        public List<TrafficVehicle> GetAllVehicles()
        {
            return new List<TrafficVehicle>(_activeVehicles.Values);
        }

        public List<TrafficVehicle> GetVehiclesInRadius(Vector3 center, float radius)
        {
            var result = new List<TrafficVehicle>();
            float radiusSq = radius * radius;

            foreach (var vehicle in _activeVehicles.Values)
            {
                if (vehicle == null) continue;
                if ((vehicle.transform.position - center).sqrMagnitude <= radiusSq)
                {
                    result.Add(vehicle);
                }
            }

            return result;
        }

        public TrafficVehicle GetNearestVehicle(Vector3 position)
        {
            TrafficVehicle nearest = null;
            float nearestDistSq = float.MaxValue;

            foreach (var vehicle in _activeVehicles.Values)
            {
                if (vehicle == null) continue;
                float distSq = (vehicle.transform.position - position).sqrMagnitude;
                if (distSq < nearestDistSq)
                {
                    nearestDistSq = distSq;
                    nearest = vehicle;
                }
            }

            return nearest;
        }
    }
}
