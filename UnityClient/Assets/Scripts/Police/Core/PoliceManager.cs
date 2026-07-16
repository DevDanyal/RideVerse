using System;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.Core;

namespace RideVerse.Police.Core
{
    public class PoliceManager : Singleton<PoliceManager>
    {
        [Header("Configuration")]
        [SerializeField] private PoliceConfig _config;

        [Header("References")]
        [SerializeField] private Transform _playerTransform;

        private WantedLevelSystem _wantedLevelSystem;
        private CrimeDetectionSystem _crimeDetectionSystem;
        private DispatchSystem _dispatchSystem;
        private EvidenceLogger _evidenceLogger;
        private RadioCommunicationSystem _radioSystem;
        private RoadblockSystem _roadblockSystem;
        private ArrestSystem _arrestSystem;
        private JailSystem _jailSystem;
        private FinePaymentSystem _finePaymentSystem;
        private VehiclePursuitSystem _vehiclePursuitSystem;
        private FootPursuitSystem _footPursuitSystem;
        private SWATSupportSystem _swatSupportSystem;
        private HelicopterSupportSystem _helicopterSupportSystem;

        private readonly Dictionary<string, PoliceUnit> _activeUnits;
        private readonly List<PoliceUnitData> _unitDataList;
        private readonly List<string> _cleanupBuffer = new List<string>();
        private bool _isInitialized;
        private float _updateTimer;
        private float _cleanupTimer;
        private int _nextUnitIndex;

        public PoliceConfig Config => _config;
        public WantedLevelSystem WantedLevel => _wantedLevelSystem;
        public CrimeDetectionSystem CrimeDetection => _crimeDetectionSystem;
        public DispatchSystem Dispatch => _dispatchSystem;
        public EvidenceLogger Evidence => _evidenceLogger;
        public RadioCommunicationSystem Radio => _radioSystem;
        public RoadblockSystem Roadblocks => _roadblockSystem;
        public ArrestSystem Arrest => _arrestSystem;
        public JailSystem Jail => _jailSystem;
        public FinePaymentSystem Fines => _finePaymentSystem;
        public VehiclePursuitSystem VehiclePursuit => _vehiclePursuitSystem;
        public FootPursuitSystem FootPursuit => _footPursuitSystem;
        public SWATSupportSystem SWAT => _swatSupportSystem;
        public HelicopterSupportSystem Helicopter => _helicopterSupportSystem;
        public bool IsInitialized => _isInitialized;
        public int ActiveUnitCount => _activeUnits.Count;

        public event Action<PoliceUnit> OnUnitSpawned;
        public event Action<PoliceUnit> OnUnitDespawned;
        public event Action<string, CrimeRecord> OnCrimeReported;
        public event Action<int> OnWantedLevelChanged;

        protected override void Awake()
        {
            base.Awake();
        }

        public void Initialize(PoliceConfig config)
        {
            _config = config;

            _wantedLevelSystem = new WantedLevelSystem(config);
            _crimeDetectionSystem = new CrimeDetectionSystem(config);
            _dispatchSystem = new DispatchSystem(config);
            _evidenceLogger = new EvidenceLogger(config);
            _radioSystem = new RadioCommunicationSystem(config);
            _roadblockSystem = new RoadblockSystem(config);
            _arrestSystem = new ArrestSystem(config);
            _jailSystem = new JailSystem(config);
            _finePaymentSystem = new FinePaymentSystem(config);
            _vehiclePursuitSystem = new VehiclePursuitSystem(config);
            _footPursuitSystem = new FootPursuitSystem(config);
            _swatSupportSystem = new SWATSupportSystem(config);
            _helicopterSupportSystem = new HelicopterSupportSystem(config);

            _activeUnits = new Dictionary<string, PoliceUnit>();
            _unitDataList = new List<PoliceUnitData>();
            _nextUnitIndex = 0;

            SubscribeToEvents();
            _isInitialized = true;

            Debug.Log("[PoliceManager] Police system initialized");
        }

        public void SetPlayerTransform(Transform player)
        {
            _playerTransform = player;
        }

        private void Update()
        {
            if (!_isInitialized) return;

            _updateTimer += Time.deltaTime;
            _cleanupTimer += Time.deltaTime;

            float deltaTime = Time.deltaTime;

            _wantedLevelSystem.Update(deltaTime);
            _crimeDetectionSystem.Update(deltaTime, _playerTransform?.position ?? Vector3.zero, 0f);
            _dispatchSystem.Update(deltaTime);
            _radioSystem.Update(deltaTime);
            _roadblockSystem.Update(deltaTime);
            _arrestSystem.Update(deltaTime);
            _jailSystem.Update(deltaTime);
            _vehiclePursuitSystem.Update(deltaTime, "local_player", Vector3.zero, Vector3.zero, 0f);
            _footPursuitSystem.Update(deltaTime, "local_player", Vector3.zero, Vector3.zero, false);
            _swatSupportSystem.Update(deltaTime, _wantedLevelSystem.CurrentStars);

            if (_playerTransform != null)
            {
                _helicopterSupportSystem.Update(deltaTime, _wantedLevelSystem.CurrentStars, _playerTransform.position);
            }

            if (_cleanupTimer >= _config.cleanupInterval)
            {
                _cleanupTimer = 0f;
                CleanupDistantUnits();
                _evidenceLogger.CleanupExpired();
            }

            UpdateUnitSpawning();
        }

        public void ReportCrime(string playerId, CrimeType type, Vector3 position, float severity = 1f)
        {
            var crime = _crimeDetectionSystem.ReportCrime(playerId, type, position, severity);
            if (crime == null) return;

            _wantedLevelSystem.AddCrime(playerId, crime);

            var evidence = _evidenceLogger.LogEvidence(
                crime.CrimeId, EvidenceType.WitnessSighting,
                $"Crime detected: {type}", position, "system");

            DispatchPriority priority = CalculateDispatchPriority(type, _wantedLevelSystem.CurrentStars);
            int requiredUnits = CalculateRequiredUnits(type, _wantedLevelSystem.CurrentStars);
            var call = _dispatchSystem.CreateDispatchCall(
                crime.CrimeId, type, position, priority, requiredUnits);

            if (call != null)
            {
                _radioSystem.SendAllUnitsAlert("dispatch",
                    $"All units: {type} reported at {position}", position);
            }

            OnCrimeReported?.Invoke(playerId, crime);
        }

        public void ReportSpeeding(string playerId, Vector3 position, float speedKmh, float speedLimit)
        {
            var crime = _crimeDetectionSystem.DetectSpeeding(playerId, position, speedKmh, speedLimit);
            if (crime != null)
            {
                ReportCrime(playerId, CrimeType.Speeding, position, 0.3f);
            }
        }

        public void ReportDangerousDriving(string playerId, Vector3 position, float angle, float speed)
        {
            var crime = _crimeDetectionSystem.DetectDangerousDriving(playerId, position, angle, speed);
            if (crime != null)
            {
                ReportCrime(playerId, CrimeType.DangerousDriving, position, 0.5f);
            }
        }

        public void ReportHitAndRun(string playerId, Vector3 position, float impactSpeed)
        {
            var crime = _crimeDetectionSystem.DetectHitAndRun(playerId, position, impactSpeed);
            if (crime != null)
            {
                ReportCrime(playerId, CrimeType.HitAndRun, position, 1.0f);
            }
        }

        public void ReportAssault(string playerId, Vector3 position)
        {
            ReportCrime(playerId, CrimeType.Assault, position, 2.0f);
        }

        public void ReportPoliceAssault(string playerId, Vector3 position)
        {
            ReportCrime(playerId, CrimeType.PoliceAssault, position, 3.0f);
        }

        public void ReportVehicleTheft(string playerId, Vector3 position)
        {
            ReportCrime(playerId, CrimeType.VehicleTheft, position, 1.5f);
        }

        public void ReportIllegalRacing(string playerId, Vector3 position)
        {
            ReportCrime(playerId, CrimeType.IllegalRacing, position, 1.5f);
        }

        public void ReportMurder(string playerId, Vector3 position)
        {
            ReportCrime(playerId, CrimeType.Murder, position, 4.0f);
        }

        public PoliceUnit SpawnPoliceUnit(PoliceUnitType type, Vector3 position, float rotation)
        {
            if (_activeUnits.Count >= _config.maxPoliceUnits)
            {
                return null;
            }

            string officerName = GetRandomOfficerName();
            var data = new PoliceUnitData(officerName, type, position, rotation, 0);

            var unitObj = new GameObject($"PoliceUnit_{type}_{_nextUnitIndex++}");
            unitObj.transform.position = position;
            unitObj.transform.rotation = Quaternion.Euler(0f, rotation, 0f);

            var unit = unitObj.AddComponent<PoliceUnit>();
            unit.Initialize(_config, data, position);

            _activeUnits[data.UnitId] = unit;
            _unitDataList.Add(data);
            _dispatchSystem.RegisterUnit(data.UnitId);

            OnUnitSpawned?.Invoke(unit);
            return unit;
        }

        public void DespawnUnit(string unitId)
        {
            if (_activeUnits.TryGetValue(unitId, out var unit))
            {
                _dispatchSystem.UnregisterUnit(unitId);
                _activeUnits.Remove(unitId);
                _unitDataList.Remove(unit.Data);
                OnUnitDespawned?.Invoke(unit);
                Destroy(unit.gameObject);
            }
        }

        public PoliceUnit GetUnit(string unitId)
        {
            _activeUnits.TryGetValue(unitId, out var unit);
            return unit;
        }

        public List<PoliceUnit> GetAllUnits()
        {
            return new List<PoliceUnit>(_activeUnits.Values);
        }

        public List<PoliceUnit> GetUnitsInRadius(Vector3 center, float radius)
        {
            float radiusSq = radius * radius;
            var result = new List<PoliceUnit>();

            foreach (var kvp in _activeUnits)
            {
                if (kvp.Value == null) continue;
                if ((kvp.Value.transform.position - center).sqrMagnitude <= radiusSq)
                {
                    result.Add(kvp.Value);
                }
            }

            return result;
        }

        public PoliceUnit GetNearestUnit(Vector3 position, bool availableOnly = false)
        {
            PoliceUnit nearest = null;
            float nearestDistSq = float.MaxValue;

            foreach (var kvp in _activeUnits)
            {
                if (kvp.Value == null) continue;
                if (availableOnly && !_dispatchSystem.IsUnitAvailable(kvp.Key)) continue;

                float distSq = (kvp.Value.transform.position - position).sqrMagnitude;
                if (distSq < nearestDistSq)
                {
                    nearestDistSq = distSq;
                    nearest = kvp.Value;
                }
            }

            return nearest;
        }

        public void RequestBackup(string unitId, Vector3 position, DispatchPriority priority, string reason)
        {
            _radioSystem.SendBackupRequest(unitId, position, priority, reason);

            var unit = GetUnit(unitId);
            if (unit == null) return;

            float searchRadius = _config.backupSearchRadius;
            var nearbyUnits = GetUnitsInRadius(position, searchRadius);

            int dispatched = 0;
            for (int i = 0; i < nearbyUnits.Count && dispatched < _config.maxBackupUnits; i++)
            {
                if (nearbyUnits[i].UnitId == unitId) continue;
                if (!_dispatchSystem.IsUnitAvailable(nearbyUnits[i].UnitId)) continue;

                _radioSystem.SendBackupResponse(nearbyUnits[i].UnitId, unitId, nearbyUnits[i].transform.position, true);
                dispatched++;
            }
        }

        public RoadblockData DeployRoadblock(RoadblockType type, Vector3 position, float rotation)
        {
            var roadblock = _roadblockSystem.CreateRoadblock(type, position, rotation);
            if (roadblock != null)
            {
                _radioSystem.SendAllUnitsAlert("dispatch",
                    $"Roadblock deployed at {position}", position);
            }
            return roadblock;
        }

        public RoadblockData DeploySpikeStrip(Vector3 position, float rotation)
        {
            return _roadblockSystem.CreateSpikeStrip(position, rotation);
        }

        public void ClearWantedLevel(string playerId)
        {
            _wantedLevelSystem.ClearWantedLevel(playerId);
        }

        public void SetWantedLevel(string playerId, int stars)
        {
            _wantedLevelSystem.SetWantedLevel(playerId, stars);
        }

        private void SubscribeToEvents()
        {
            _wantedLevelSystem.OnStarsChanged += HandleStarsChanged;
            _wantedLevelSystem.OnWantedLevelChanged += HandleWantedLevelChanged;
        }

        private void HandleStarsChanged(int oldStars, int newStars)
        {
            if (newStars > oldStars)
            {
                _radioSystem.SendAllUnitsAlert("dispatch",
                    $"Wanted level increased to {newStars} stars", _playerTransform?.position ?? Vector3.zero);
            }
        }

        private void HandleWantedLevelChanged(int stars)
        {
            OnWantedLevelChanged?.Invoke(stars);

            if (stars == 0)
            {
                _radioSystem.SendStandDown("dispatch");
                _roadblockSystem.ClearAll();
                _vehiclePursuitSystem.ClearAll();
                _footPursuitSystem.ClearAll();
            }
        }

        private void UpdateUnitSpawning()
        {
            if (_playerTransform == null) return;
            if (_activeUnits.Count >= _config.maxPoliceUnits) return;

            if (_wantedLevelSystem.IsWanted && _activeUnits.Count < Mathf.Min(_wantedLevelSystem.GetRequiredPursuitUnits() + 2, _config.maxPoliceUnits))
            {
                Vector3 spawnPos = GetSpawnPositionNearPlayer();
                float rotation = GetSpawnRotation(spawnPos);
                SpawnPoliceUnit(PoliceUnitType.PatrolCar, spawnPos, rotation);
            }
        }

        private void CleanupDistantUnits()
        {
            if (_playerTransform == null) return;

            _cleanupBuffer.Clear();

            foreach (var kvp in _activeUnits)
            {
                if (kvp.Value == null)
                {
                    _cleanupBuffer.Add(kvp.Key);
                    continue;
                }

                float distance = Vector3.Distance(_playerTransform.position, kvp.Value.transform.position);
                if (distance > _config.despawnRadius && !_vehiclePursuitSystem.IsInPursuit(kvp.Key))
                {
                    _cleanupBuffer.Add(kvp.Key);
                }
            }

            foreach (var id in _cleanupBuffer)
            {
                DespawnUnit(id);
            }
        }

        private Vector3 GetSpawnPositionNearPlayer()
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

        private DispatchPriority CalculateDispatchPriority(CrimeType type, int wantedStars)
        {
            if (wantedStars >= 5) return DispatchPriority.Critical;
            if (wantedStars >= 3 || type == CrimeType.PoliceAssault || type == CrimeType.Murder)
                return DispatchPriority.High;
            if (wantedStars >= 2 || type == CrimeType.Assault || type == CrimeType.Robbery)
                return DispatchPriority.Medium;
            return DispatchPriority.Low;
        }

        private int CalculateRequiredUnits(CrimeType type, int wantedStars)
        {
            if (type == CrimeType.Murder || type == CrimeType.PoliceAssault) return 3;
            if (wantedStars >= 4) return 3;
            if (wantedStars >= 3) return 2;
            return 1;
        }

        private string GetRandomOfficerName()
        {
            string[] names = { "Ahmed", "Ali", "Hassan", "Omar", "Yusuf", "Khalid", "Tariq", "Majid", "Sami", "Faris" };
            return names[UnityEngine.Random.Range(0, names.Length)];
        }

        public PoliceUnit SpawnSWATUnit(Vector3 position)
        {
            if (_swatSupportSystem.SWATAvailable <= 0) return null;

            var unit = SpawnPoliceUnit(PoliceUnitType.SWATTeam, position, 0f);
            if (unit != null)
            {
                _radioSystem.SendAllUnitsAlert("swat",
                    $"SWAT unit deployed at {position}", position);
            }
            return unit;
        }

        public void DeployHelicopter(Vector3 targetPosition)
        {
            _helicopterSupportSystem.DeployHelicopter(targetPosition);
            _radioSystem.SendAllUnitsAlert("air",
                $"Air support en route to target", targetPosition);
        }

        public void ClearAll()
        {
            foreach (var kvp in _activeUnits)
            {
                if (kvp.Value != null)
                    Destroy(kvp.Value.gameObject);
            }
            _activeUnits.Clear();
            _unitDataList.Clear();

            _wantedLevelSystem.Reset();
            _crimeDetectionSystem.ClearAll();
            _dispatchSystem.ClearAll();
            _evidenceLogger.ClearAll();
            _radioSystem.ClearAll();
            _roadblockSystem.ClearAll();
            _vehiclePursuitSystem.ClearAll();
            _footPursuitSystem.ClearAll();
            _jailSystem.ClearAll();
            _finePaymentSystem.ClearAll();
            _swatSupportSystem.StandDown();
            _helicopterSupportSystem.ClearAll();
        }

        private void OnApplicationQuit()
        {
            UnsubscribeFromEvents();
            ClearAll();
        }

        private void OnDestroy()
        {
            UnsubscribeFromEvents();
        }

        private void UnsubscribeFromEvents()
        {
            if (_wantedLevelSystem != null)
            {
                _wantedLevelSystem.OnStarsChanged -= HandleStarsChanged;
                _wantedLevelSystem.OnWantedLevelChanged -= HandleWantedLevelChanged;
            }
        }
    }
}
