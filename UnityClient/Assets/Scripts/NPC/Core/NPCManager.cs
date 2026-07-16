using System;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.Core;
using RideVerse.NPC.Brain;
using RideVerse.NPC.Profession;
using RideVerse.NPC.Crowd;
using RideVerse.NPC.Performance;
using RideVerse.NPC.Vehicle;
using RideVerse.NPC.Diagnostics;
using RideVerse.World.Spawn;

namespace RideVerse.NPC.Core
{
    public class NPCManager : Singleton<NPCManager>
    {
        [Header("Configuration")]
        [SerializeField] private NPCConfig _config;

        [Header("References")]
        [SerializeField] private SpawnManager _spawnManager;
        [SerializeField] private CrowdManager _crowdManager;
        [SerializeField] private NPCLODManager _lodManager;
        [SerializeField] private NPCVehicleSpawner _vehicleSpawner;
        [SerializeField] private NPCDebugTools _debugTools;

        private List<NPCBrain> _activeNPCs = new List<NPCBrain>();
        private List<NPCData> _npcDataList = new List<NPCData>();
        private readonly List<NPCBrain> _despawnBuffer = new List<NPCBrain>();
        private Transform _playerTransform;
        private float _spawnTimer;
        private float _spawnInterval = 2f;
        private bool _isInitialized;

        public int ActiveNPCCount => _activeNPCs.Count;
        public int TotalNPCCount => _npcDataList.Count;
        public NPCConfig Config => _config;

        public event Action<NPCBrain> OnNPCSpawned;
        public event Action<NPCBrain> OnNPCDespawned;

        protected override void Awake()
        {
            base.Awake();
        }

        public void Initialize(NPCConfig config, SpawnManager spawnManager)
        {
            _config = config;
            _spawnManager = spawnManager;
            _isInitialized = true;

            if (_crowdManager == null)
                _crowdManager = GetComponentInChildren<CrowdManager>();
            if (_lodManager == null)
                _lodManager = GetComponentInChildren<NPCLODManager>();
            if (_vehicleSpawner == null)
                _vehicleSpawner = GetComponentInChildren<NPCVehicleSpawner>();
            if (_debugTools == null)
                _debugTools = GetComponentInChildren<NPCDebugTools>();

            _lodManager?.Initialize(_config);
            _vehicleSpawner?.Initialize(_config);
            _debugTools?.Initialize(this);

            GenerateNPCData();
            Debug.Log($"[NPCManager] Initialized with {_npcDataList.Count} NPCs");
        }

        public void SetPlayerTransform(Transform player)
        {
            _playerTransform = player;
            _lodManager?.SetPlayerTransform(player);
        }

        private void GenerateNPCData()
        {
            _npcDataList.Clear();

            if (_spawnManager == null || _config == null) return;

            var npcSpawns = _spawnManager.GetSpawnPointsByType(SpawnType.NPC);

            int npcsPerSpawn = Mathf.CeilToInt((float)_config.maxActiveNPCs / Mathf.Max(1, npcSpawns.Count));

            foreach (var spawn in npcSpawns)
            {
                for (int i = 0; i < npcsPerSpawn && _npcDataList.Count < _config.maxActiveNPCs; i++)
                {
                    var data = CreateRandomNPCData(spawn.Position);
                    _npcDataList.Add(data);
                }
            }

            while (_npcDataList.Count < _config.maxActiveNPCs)
            {
                Vector3 randomPos = new Vector3(
                    UnityEngine.Random.Range(-100f, 100f),
                    0f,
                    UnityEngine.Random.Range(-100f, 100f));
                _npcDataList.Add(CreateRandomNPCData(randomPos));
            }
        }

        private NPCData CreateRandomNPCData(Vector3 basePosition)
        {
            string[] maleNames = { "Ahmed", "Ali", "Hassan", "Hussein", "Omar", "Yusuf", "Ibrahim", "Khalid", "Tariq", "Majid" };
            string[] femaleNames = { "Fatima", "Aisha", "Zainab", "Maryam", "Khadija", "Safiya", "Halima", "Nora", "Layla", "Yasmin" };

            bool isMale = UnityEngine.Random.value > 0.5f;
            string name = isMale
                ? maleNames[UnityEngine.Random.Range(0, maleNames.Length)]
                : femaleNames[UnityEngine.Random.Range(0, femaleNames.Length)];

            ProfessionType profession = (ProfessionType)UnityEngine.Random.Range(0, Enum.GetValues(typeof(ProfessionType)).Length);

            Vector3 offset = new Vector3(
                UnityEngine.Random.Range(-20f, 20f),
                0f,
                UnityEngine.Random.Range(-20f, 20f));

            return new NPCData(
                Guid.NewGuid().ToString("N").Substring(0, 8),
                name,
                (int)profession,
                basePosition + offset,
                UnityEngine.Random.Range(0f, 360f),
                UnityEngine.Random.Range(0, 5));
        }

        private void Update()
        {
            if (!_isInitialized) return;

            _spawnTimer += Time.deltaTime;
            if (_spawnTimer >= _spawnInterval)
            {
                _spawnTimer = 0f;
                UpdateNPCSpawning();
                _lodManager?.UpdateAllLODs();
            }

            UpdateActiveNPCs();
        }

        private void UpdateNPCSpawning()
        {
            if (_playerTransform == null) return;

            int targetSpawnCount = Mathf.Min(_config.maxActiveNPCs, _config.maxNPCsPerDistrict * 5);

            if (_activeNPCs.Count < targetSpawnCount)
            {
                int toSpawn = Mathf.Min(3, targetSpawnCount - _activeNPCs.Count);
                for (int i = 0; i < toSpawn; i++)
                {
                    SpawnNearestNPC();
                }
            }

            _despawnBuffer.Clear();
            foreach (var npc in _activeNPCs)
            {
                if (npc == null) continue;
                float distance = Vector3.Distance(_playerTransform.position, npc.transform.position);
                if (distance > _config.despawnRadius)
                {
                    _despawnBuffer.Add(npc);
                }
            }

            foreach (var npc in _despawnBuffer)
            {
                DespawnNPC(npc);
            }
        }

        private void SpawnNearestNPC()
        {
            if (_playerTransform == null) return;

            NPCData closestData = null;
            float closestDist = float.MaxValue;

            foreach (var data in _npcDataList)
            {
                if (IsNPCActive(data.Id)) continue;

                float dist = Vector3.Distance(_playerTransform.position, data.GetSpawnPosition());
                if (dist < closestDist && dist <= _config.spawnRadius)
                {
                    closestDist = dist;
                    closestData = data;
                }
            }

            if (closestData != null)
            {
                SpawnNPC(closestData);
            }
        }

        public NPCBrain SpawnNPC(NPCData data)
        {
            var go = new GameObject($"NPC_{data.DisplayName}_{data.Id}");
            go.transform.position = data.GetSpawnPosition();

            var cc = go.AddComponent<CharacterController>();
            cc.height = 1.8f;
            cc.radius = 0.3f;
            cc.center = new Vector3(0f, 0.9f, 0f);

            var brain = go.AddComponent<NPCBrain>();
            brain.Initialize(data, _config);

            var interaction = go.AddComponent<Interaction.NPCInteraction>();
            interaction.Initialize(brain);

            var reaction = go.AddComponent<Interaction.NPCReaction>();
            reaction.Initialize(brain);

            _activeNPCs.Add(brain);
            _lodManager?.RegisterNPC(brain);
            _crowdManager?.RegisterUngrouped(brain);

            OnNPCSpawned?.Invoke(brain);
            return brain;
        }

        public void DespawnNPC(NPCBrain npc)
        {
            if (npc == null) return;

            _lodManager?.UnregisterNPC(npc);
            _crowdManager?.UnregisterUngrouped(npc);
            _activeNPCs.Remove(npc);

            OnNPCDespawned?.Invoke(npc);
            Destroy(npc.gameObject);
        }

        public void DespawnAllNPCs()
        {
            foreach (var npc in _activeNPCs)
            {
                if (npc != null)
                {
                    _lodManager?.UnregisterNPC(npc);
                    Destroy(npc.gameObject);
                }
            }
            _activeNPCs.Clear();
        }

        private void UpdateActiveNPCs()
        {
            foreach (var npc in _activeNPCs)
            {
                if (npc == null) continue;

                if (_lodManager != null && !_lodManager.ShouldUpdate(npc)) continue;
            }
        }

        private bool IsNPCActive(string id)
        {
            foreach (var npc in _activeNPCs)
            {
                if (npc != null && npc.Data.Id == id) return true;
            }
            return false;
        }

        public NPCBrain GetNearestNPC(Vector3 position)
        {
            NPCBrain nearest = null;
            float nearestDist = float.MaxValue;

            foreach (var npc in _activeNPCs)
            {
                if (npc == null) continue;
                float dist = Vector3.Distance(position, npc.transform.position);
                if (dist < nearestDist)
                {
                    nearestDist = dist;
                    nearest = npc;
                }
            }

            return nearest;
        }

        public List<NPCBrain> GetNPCsInRadius(Vector3 center, float radius)
        {
            var result = new List<NPCBrain>();
            float radiusSq = radius * radius;

            foreach (var npc in _activeNPCs)
            {
                if (npc == null) continue;
                if ((npc.transform.position - center).sqrMagnitude <= radiusSq)
                {
                    result.Add(npc);
                }
            }

            return result;
        }

        public NPCConfig GetConfig() => _config;
        public CrowdManager GetCrowdManager() => _crowdManager;
        public NPCLODManager GetLODManager() => _lodManager;
        public NPCVehicleSpawner GetVehicleSpawner() => _vehicleSpawner;
        public NPCDebugTools GetDebugTools() => _debugTools;
        public List<NPCBrain> GetAllNPCs() => new List<NPCBrain>(_activeNPCs);
    }
}
