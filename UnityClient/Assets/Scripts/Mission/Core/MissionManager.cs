using System;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.Core;

namespace RideVerse.Mission.Core
{
    public class MissionManager : Singleton<MissionManager>
    {
        [Header("Configuration")]
        [SerializeField] private MissionConfig _config;

        [Header("References")]
        [SerializeField] private Transform _playerTransform;

        private MissionStateMachine _stateMachine;
        private MissionSaveLoadSystem _saveLoad;
        private MissionCheckpointSystem _checkpoints;
        private MissionObjectiveSystem _objectives;
        private MissionRewardSystem _rewards;
        private MissionFailureSystem _failure;
        private MissionTimerSystem _timer;
        private MissionDialogueSystem _dialogue;
        private MissionCutsceneSystem _cutscene;
        private MissionMarkerSystem _markers;
        private MissionTriggerZoneSystem _triggerZones;
        private MissionProgressSystem _progress;
        private MissionTutorialSystem _tutorial;
        private MissionSideSystem _side;
        private MissionDailySystem _daily;
        private MissionRandomEventSystem _randomEvents;
        private MissionAchievementSystem _achievements;
        private MissionEconomySystem _economy;

        private readonly List<MissionData> _registeredMissions;
        private string _activeMissionId;
        private bool _isInitialized;
        private float _objectiveUpdateTimer;
        private float _markerUpdateTimer;
        private float _triggerUpdateTimer;
        private float _playerDistanceTraveled;
        private Vector3 _lastPlayerPosition;

        public MissionConfig Config => _config;
        public bool IsInitialized => _isInitialized;
        public string ActiveMissionId => _activeMissionId;
        public MissionData ActiveMission => GetActiveMission();
        public int RegisteredMissionCount => _registeredMissions.Count;

        public MissionStateMachine StateMachine => _stateMachine;
        public MissionTimerSystem Timer => _timer;
        public MissionDialogueSystem Dialogue => _dialogue;
        public MissionCutsceneSystem Cutscene => _cutscene;
        public MissionMarkerSystem Markers => _markers;
        public MissionProgressSystem Progress => _progress;
        public MissionTutorialSystem Tutorial => _tutorial;
        public MissionSideSystem Side => _side;
        public MissionDailySystem Daily => _daily;
        public MissionRandomEventSystem RandomEvents => _randomEvents;
        public MissionAchievementSystem Achievements => _achievements;
        public MissionEconomySystem Economy => _economy;
        public MissionSaveLoadSystem SaveLoad => _saveLoad;

        public event Action<MissionData> OnMissionRegistered;
        public event Action<string> OnMissionActivated;
        public event Action<MissionData> OnMissionCompleted;
        public event Action<MissionData, FailureReason> OnMissionFailed;
        public event Action OnActiveMissionCleared;

        protected override void Awake()
        {
            base.Awake();
        }

        public void Initialize(MissionConfig config)
        {
            _config = config;

            _stateMachine = new MissionStateMachine();
            _saveLoad = new MissionSaveLoadSystem(config);
            _checkpoints = new MissionCheckpointSystem(config);
            _objectives = new MissionObjectiveSystem(config);
            _rewards = new MissionRewardSystem(config);
            _failure = new MissionFailureSystem(config);
            _timer = new MissionTimerSystem(config);
            _dialogue = new MissionDialogueSystem(config);
            _cutscene = new MissionCutsceneSystem(config);
            _markers = new MissionMarkerSystem(config);
            _triggerZones = new MissionTriggerZoneSystem(config);
            _progress = new MissionProgressSystem(config);
            _tutorial = new MissionTutorialSystem(config);
            _side = new MissionSideSystem(config);
            _daily = new MissionDailySystem(config);
            _randomEvents = new MissionRandomEventSystem(config);
            _achievements = new MissionAchievementSystem(config);
            _economy = new MissionEconomySystem(config);

            _registeredMissions = new List<MissionData>();

            SubscribeToEvents();
            _progress.Initialize();
            _isInitialized = true;

            Debug.Log("[MissionManager] Mission system initialized");
        }

        public void SetPlayerTransform(Transform player)
        {
            _playerTransform = player;
            if (_playerTransform != null)
            {
                _lastPlayerPosition = _playerTransform.position;
            }
        }

        private void Update()
        {
            if (!_isInitialized) return;

            float deltaTime = Time.deltaTime;

            _saveLoad.Update(deltaTime);
            _daily.Update(deltaTime);
            _side.Update(deltaTime);

            if (!string.IsNullOrEmpty(_activeMissionId))
            {
                _timer.Update(deltaTime);
                _dialogue.Update(deltaTime);
                _cutscene.Update(deltaTime);

                _objectiveUpdateTimer += deltaTime;
                if (_objectiveUpdateTimer >= (_config != null ? _config.objectiveUpdateInterval : 0.5f))
                {
                    _objectiveUpdateTimer = 0f;
                    UpdateMissionObjectives(deltaTime);
                }

                if (_playerTransform != null)
                {
                    _checkpoints.Update(deltaTime, _playerTransform.position, _activeMissionId);
                    TrackPlayerDistance();
                }

                CheckMissionFailureConditions();
            }

            _markerUpdateTimer += deltaTime;
            if (_markerUpdateTimer >= (_config != null ? _config.markerUpdateInterval : 0.5f))
            {
                _markerUpdateTimer = 0f;
                _markers.Update(deltaTime, _playerTransform?.position ?? Vector3.zero);
            }

            _triggerUpdateTimer += deltaTime;
            if (_triggerUpdateTimer >= (_config != null ? _config.triggerCheckInterval : 0.25f))
            {
                _triggerUpdateTimer = 0f;
                _triggerZones.Update(deltaTime, _playerTransform?.position ?? Vector3.zero, false);
            }

            _randomEvents.Update(deltaTime, _playerTransform?.position ?? Vector3.zero, Time.time);
        }

        public void RegisterMission(MissionData mission)
        {
            if (mission == null) return;

            _registeredMissions.Add(mission);
            OnMissionRegistered?.Invoke(mission);
            Debug.Log($"[MissionManager] Mission registered: {mission.MissionName} ({mission.MissionId})");
        }

        public void RegisterMissions(List<MissionData> missions)
        {
            foreach (var mission in missions)
            {
                RegisterMission(mission);
            }
        }

        public MissionData AcceptMission(string missionId)
        {
            var mission = GetRegisteredMission(missionId);
            if (mission == null)
            {
                Debug.LogWarning($"[MissionManager] Mission {missionId} not found");
                return null;
            }

            if (!_stateMachine.SetMission(mission) || !_stateMachine.CanAccept())
            {
                Debug.LogWarning($"[MissionManager] Cannot accept mission {missionId}");
                return null;
            }

            _stateMachine.TransitionTo(MissionState.Accepted);
            _saveLoad.AddActiveMission(mission);
            OnMissionActivated?.Invoke(missionId);
            return mission;
        }

        public void StartMission(string missionId)
        {
            var mission = GetActiveMissionData(missionId);
            if (mission == null)
            {
                mission = AcceptMission(missionId);
                if (mission == null) return;
            }

            if (!_stateMachine.SetMission(mission) || !_stateMachine.CanStart())
            {
                if (mission.State != MissionState.Accepted)
                {
                    Debug.LogWarning($"[MissionManager] Cannot start mission {missionId}");
                    return;
                }
            }

            _stateMachine.TransitionTo(MissionState.InProgress);
            _activeMissionId = missionId;

            _checkpoints.InitializeMissionCheckpoints(mission);
            _objectives.InitializeMissionObjectives(mission);

            if (mission.IsTimed)
            {
                _timer.StartTimer(missionId, mission.TimeLimit);
            }

            if (mission.DialogueLines != null && mission.DialogueLines.Count > 0)
            {
                _dialogue.StartDialogue(missionId, mission.DialogueLines);
            }

            if (mission.CutsceneEvents != null && mission.CutsceneEvents.Count > 0)
            {
                _cutscene.PlayCutscene(missionId, mission.CutsceneEvents);
            }

            CreateMissionMarkers(mission);
            _progress.TrackMissionStart(mission);

            Debug.Log($"[MissionManager] Mission started: {mission.MissionName}");
        }

        public void CompleteMission(string missionId)
        {
            var mission = GetActiveMissionData(missionId);
            if (mission == null) return;

            if (!_stateMachine.SetMission(mission))
            {
                Debug.LogWarning($"[MissionManager] Cannot complete mission {missionId}");
                return;
            }

            _timer.StopTimer();

            var rewards = _rewards.CalculateRewards(mission);
            var timeBonus = _rewards.CalculateTimeBonus(mission);
            rewards.AddRange(timeBonus);

            _rewards.GrantRewards(missionId, rewards);
            _economy.GrantMissionRewards(missionId, rewards);

            _stateMachine.TransitionTo(MissionState.Completed);

            _saveLoad.RemoveActiveMission(missionId);
            _saveLoad.AddCompletedMission(mission);

            _progress.RecordMissionCompletion(mission);
            _achievements.OnMissionCompleted(mission);
            _checkpoints.RemoveMission(missionId);
            _objectives.RemoveMission(missionId);
            _markers.RemoveMarkersByMission(missionId);
            _triggerZones.RemoveZonesByMission(missionId);

            _activeMissionId = null;
            _timer.ClearActiveMission();
            _dialogue.EndDialogue();
            _cutscene.SkipCutscene();

            OnMissionCompleted?.Invoke(mission);
            Debug.Log($"[MissionManager] Mission completed: {mission.MissionName}");
        }

        public void FailMission(string missionId, FailureReason reason)
        {
            var mission = GetActiveMissionData(missionId);
            if (mission == null) return;

            if (!_stateMachine.SetMission(mission))
            {
                return;
            }

            _timer.StopTimer();
            _failure.FailMission(mission, reason);

            _stateMachine.TransitionTo(MissionState.Failed, reason);

            _saveLoad.RemoveActiveMission(missionId);
            _saveLoad.AddFailedMission(mission);

            _progress.RecordMissionFailure(mission);
            _checkpoints.RemoveMission(missionId);
            _objectives.RemoveMission(missionId);
            _markers.RemoveMarkersByMission(missionId);
            _triggerZones.RemoveZonesByMission(missionId);

            _activeMissionId = null;
            _timer.ClearActiveMission();

            OnMissionFailed?.Invoke(mission, reason);
            Debug.Log($"[MissionManager] Mission failed: {mission.MissionName} ({reason})");
        }

        public void CancelMission(string missionId)
        {
            var mission = GetActiveMissionData(missionId);
            if (mission == null) return;

            if (!_stateMachine.SetMission(mission))
            {
                return;
            }

            _timer.StopTimer();
            _failure.CancelMission(mission);

            _stateMachine.TransitionTo(MissionState.Cancelled);

            _saveLoad.RemoveActiveMission(missionId);
            _progress.RecordMissionCancellation(mission);
            _checkpoints.RemoveMission(missionId);
            _objectives.RemoveMission(missionId);
            _markers.RemoveMarkersByMission(missionId);
            _triggerZones.RemoveZonesByMission(missionId);

            _activeMissionId = null;
            _timer.ClearActiveMission();
            OnActiveMissionCleared?.Invoke();

            Debug.Log($"[MissionManager] Mission cancelled: {missionId}");
        }

        public bool RetryMission(string missionId)
        {
            var mission = GetActiveMissionData(missionId);
            if (mission == null) return false;

            if (!_failure.CanRetry(mission)) return false;

            _failure.ResetFailureState(mission);
            _failure.AttemptRetry(mission);
            _checkpoints.ResetMissionCheckpoints(missionId);
            _objectives.ResetMissionObjectives(missionId);

            _stateMachine.SetMission(mission);
            _saveLoad.UpdateMissionProgress(mission);

            StartMission(missionId);
            return true;
        }

        public void PauseMission()
        {
            if (string.IsNullOrEmpty(_activeMissionId)) return;

            var mission = GetActiveMissionData(_activeMissionId);
            if (mission == null) return;

            if (_stateMachine.SetMission(mission) && _stateMachine.CanPause())
            {
                _timer.PauseTimer();
                _stateMachine.TransitionTo(MissionState.Paused);
            }
        }

        public void ResumeMission()
        {
            if (string.IsNullOrEmpty(_activeMissionId)) return;

            var mission = GetActiveMissionData(_activeMissionId);
            if (mission == null) return;

            if (_stateMachine.SetMission(mission) && _stateMachine.CanResume())
            {
                _timer.ResumeTimer();
                _stateMachine.TransitionTo(MissionState.InProgress);
            }
        }

        public void IncrementObjective(string objectiveId, int amount = 1)
        {
            if (string.IsNullOrEmpty(_activeMissionId)) return;
            _objectives.IncrementObjective(_activeMissionId, objectiveId, amount);

            if (_objectives.AreAllRequiredComplete(_activeMissionId))
            {
                CompleteMission(_activeMissionId);
            }
        }

        public void IncrementObjectiveByType(ObjectiveType type, int amount = 1)
        {
            if (string.IsNullOrEmpty(_activeMissionId)) return;
            _objectives.IncrementObjectiveByType(_activeMissionId, type, amount);

            if (_objectives.AreAllRequiredComplete(_activeMissionId))
            {
                CompleteMission(_activeMissionId);
            }
        }

        private void UpdateMissionObjectives(float deltaTime)
        {
            if (_playerTransform == null || string.IsNullOrEmpty(_activeMissionId)) return;

            _objectives.Update(deltaTime, _activeMissionId, _playerTransform.position);
        }

        private void CheckMissionFailureConditions()
        {
            if (string.IsNullOrEmpty(_activeMissionId)) return;

            var mission = GetActiveMissionData(_activeMissionId);
            if (mission == null) return;

            _failure.CheckTimeExpired(mission);
            _failure.CheckObjectiveFailed(mission);
        }

        private void TrackPlayerDistance()
        {
            if (_playerTransform == null) return;

            float dist = Vector3.Distance(_lastPlayerPosition, _playerTransform.position);
            _playerDistanceTraveled += dist;
            _lastPlayerPosition = _playerTransform.position;

            _achievements.OnDistanceTraveled(dist);
        }

        private void CreateMissionMarkers(MissionData mission)
        {
            if (mission == null || _config == null) return;

            _markers.AddMarker(mission.MissionId, MissionMarkerType.Start,
                mission.Checkpoints.Count > 0 ? mission.Checkpoints[0].Position : Vector3.zero,
                mission.MissionName, _config.missionStartColor);

            foreach (var checkpoint in mission.Checkpoints)
            {
                _markers.AddMarker(mission.MissionId, MissionMarkerType.Checkpoint,
                    checkpoint.Position, $"Checkpoint {checkpoint.Order}",
                    _config.missionCheckpointColor);
            }
        }

        private void SubscribeToEvents()
        {
            _timer.OnTimerExpired += HandleTimerExpired;
            _checkpoints.OnAllCheckpointsCompleted += HandleAllCheckpointsCompleted;
            _objectives.OnAllObjectivesCompleted += HandleAllObjectivesCompleted;
        }

        private void HandleTimerExpired(string missionId)
        {
            FailMission(missionId, FailureReason.TimeExpired);
        }

        private void HandleAllCheckpointsCompleted(string missionId)
        {
            if (missionId == _activeMissionId && _objectives.AreAllRequiredComplete(missionId))
            {
                CompleteMission(missionId);
            }
        }

        private void HandleAllObjectivesCompleted(string missionId)
        {
            if (missionId == _activeMissionId)
            {
                CompleteMission(missionId);
            }
        }

        private MissionData GetActiveMission()
        {
            if (string.IsNullOrEmpty(_activeMissionId)) return null;
            return GetActiveMissionData(_activeMissionId);
        }

        private MissionData GetRegisteredMission(string missionId)
        {
            foreach (var mission in _registeredMissions)
            {
                if (mission.MissionId == missionId) return mission;
            }
            return null;
        }

        private MissionData GetActiveMissionData(string missionId)
        {
            return _saveLoad.GetActiveMission(missionId);
        }

        public MissionData GetMission(string missionId)
        {
            return GetRegisteredMission(missionId) ?? GetActiveMissionData(missionId);
        }

        public List<MissionData> GetMissionsByType(MissionType type)
        {
            var result = new List<MissionData>();
            foreach (var mission in _registeredMissions)
            {
                if (mission.Type == type) result.Add(mission);
            }
            return result;
        }

        public List<MissionData> GetAvailableMissions()
        {
            var result = new List<MissionData>();
            foreach (var mission in _registeredMissions)
            {
                if (mission.State == MissionState.Available) result.Add(mission);
            }
            return result;
        }

        public int GetCompletedCount()
        {
            return _saveLoad.GetCompletedMissionCount();
        }

        public void Save()
        {
            _saveLoad.Save(_saveLoad.SaveData?.PlayerId ?? "local");
        }

        public void Load(string playerId)
        {
            _saveLoad.Initialize(playerId);
        }

        public void ClearAll()
        {
            _timer.StopTimer();
            _dialogue.EndDialogue();
            _cutscene.SkipCutscene();

            _checkpoints.ClearAll();
            _objectives.ClearAll();
            _markers.ClearAll();
            _triggerZones.ClearAll();
            _progress.ClearAll();
            _tutorial.ClearAll();
            _side.ClearAll();
            _daily.ClearAll();
            _randomEvents.ClearAll();
            _achievements.ClearAll();
            _economy.ClearAll();
            _saveLoad.ClearAll();

            _registeredMissions.Clear();
            _activeMissionId = null;
            _stateMachine?.Reset();

            Debug.Log("[MissionManager] All cleared");
        }

        private void OnApplicationQuit()
        {
            UnsubscribeFromEvents();
            Save();
        }

        private void OnDestroy()
        {
            UnsubscribeFromEvents();
        }

        private void UnsubscribeFromEvents()
        {
            if (_timer != null) _timer.OnTimerExpired -= HandleTimerExpired;
            if (_checkpoints != null) _checkpoints.OnAllCheckpointsCompleted -= HandleAllCheckpointsCompleted;
            if (_objectives != null) _objectives.OnAllObjectivesCompleted -= HandleAllObjectivesCompleted;
        }
    }
}
