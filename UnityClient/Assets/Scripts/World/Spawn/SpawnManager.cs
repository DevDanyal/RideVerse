using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.World.Spawn
{
    [Serializable]
    public class SpawnPoint
    {
        public string Id;
        public SpawnType Type;
        public Vector3 Position;
        public float RotationY;
        public bool IsActive;

        public SpawnPoint()
        {
            Id = Guid.NewGuid().ToString("N").Substring(0, 8);
            IsActive = true;
        }

        public SpawnPoint(SpawnType type, Vector3 position, float rotationY = 0f) : this()
        {
            Type = type;
            Position = position;
            RotationY = rotationY;
        }

        public Quaternion GetRotation() => Quaternion.Euler(0f, RotationY, 0f);
    }

    public class SpawnManager : MonoBehaviour
    {
        [SerializeField] private Transform _playerSpawnRoot;
        [SerializeField] private Transform _vehicleSpawnRoot;
        [SerializeField] private Transform _npcSpawnRoot;

        private List<SpawnPoint> _spawnPoints = new List<SpawnPoint>();
        private Dictionary<SpawnType, List<SpawnPoint>> _spawnByType = new Dictionary<SpawnType, List<SpawnPoint>>();

        public int TotalSpawnPoints => _spawnPoints.Count;

        public event Action<SpawnPoint> OnSpawnPointRegistered;
        public event Action<SpawnPoint> OnSpawnPointRemoved;

        public void Initialize()
        {
            _spawnByType.Clear();
            foreach (SpawnType type in Enum.GetValues(typeof(SpawnType)))
            {
                _spawnByType[type] = new List<SpawnPoint>();
            }
            Debug.Log("[SpawnManager] Initialized");
        }

        public SpawnPoint RegisterSpawnPoint(SpawnType type, Vector3 position, float rotationY = 0f)
        {
            var spawnPoint = new SpawnPoint(type, position, rotationY);
            _spawnPoints.Add(spawnPoint);
            _spawnByType[type].Add(spawnPoint);
            OnSpawnPointRegistered?.Invoke(spawnPoint);
            return spawnPoint;
        }

        public void RemoveSpawnPoint(string id)
        {
            for (int i = _spawnPoints.Count - 1; i >= 0; i--)
            {
                if (_spawnPoints[i].Id == id)
                {
                    var removed = _spawnPoints[i];
                    _spawnPoints.RemoveAt(i);

                    if (_spawnByType.TryGetValue(removed.Type, out var list))
                    {
                        list.Remove(removed);
                    }

                    OnSpawnPointRemoved?.Invoke(removed);
                    break;
                }
            }
        }

        public SpawnPoint GetRandomSpawnPoint(SpawnType type)
        {
            if (!_spawnByType.TryGetValue(type, out var list) || list.Count == 0)
            {
                Debug.LogWarning($"[SpawnManager] No spawn points for type {type}");
                return null;
            }

            var activePoints = list.FindAll(sp => sp.IsActive);
            if (activePoints.Count == 0) return null;

            return activePoints[UnityEngine.Random.Range(0, activePoints.Count)];
        }

        public SpawnPoint GetNearestSpawnPoint(SpawnType type, Vector3 position)
        {
            if (!_spawnByType.TryGetValue(type, out var list) || list.Count == 0)
                return null;

            SpawnPoint nearest = null;
            float nearestDistSq = float.MaxValue;

            foreach (var sp in list)
            {
                if (!sp.IsActive) continue;
                float distSq = (sp.Position - position).sqrMagnitude;
                if (distSq < nearestDistSq)
                {
                    nearestDistSq = distSq;
                    nearest = sp;
                }
            }

            return nearest;
        }

        public List<SpawnPoint> GetSpawnPointsInRadius(Vector3 center, float radius, SpawnType type)
        {
            var result = new List<SpawnPoint>();
            float radiusSq = radius * radius;

            if (!_spawnByType.TryGetValue(type, out var list)) return result;

            foreach (var sp in list)
            {
                if (!sp.IsActive) continue;
                if ((sp.Position - center).sqrMagnitude <= radiusSq)
                {
                    result.Add(sp);
                }
            }

            return result;
        }

        public List<SpawnPoint> GetAllSpawnPoints() => new List<SpawnPoint>(_spawnPoints);
        public List<SpawnPoint> GetSpawnPointsByType(SpawnType type) =>
            _spawnByType.TryGetValue(type, out var list) ? new List<SpawnPoint>(list) : new List<SpawnPoint>();
    }
}
