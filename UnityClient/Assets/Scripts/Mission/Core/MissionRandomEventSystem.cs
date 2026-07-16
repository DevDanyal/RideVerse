using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionRandomEventSystem
    {
        private readonly MissionConfig _config;
        private readonly List<RandomEventTemplate> _eventTemplates;
        private readonly List<MissionData> _activeRandomEvents;
        private readonly Dictionary<string, float> _lastTriggeredTimes;
        private float _spawnTimer;
        private int _activeEventCount;

        public int ActiveEventCount => _activeEventCount;
        public bool CanSpawnNewEvent => _config == null || _activeEventCount < _config.maxConcurrentRandomEvents;

        public event Action<MissionData> OnRandomEventSpawned;
        public event Action<MissionData> OnRandomEventCompleted;
        public event Action<MissionData> OnRandomEventExpired;
        public event Action<string> OnRandomEventTriggered;

        public MissionRandomEventSystem(MissionConfig config)
        {
            _config = config;
            _eventTemplates = new List<RandomEventTemplate>();
            _activeRandomEvents = new List<MissionData>();
            _lastTriggeredTimes = new Dictionary<string, float>();
        }

        public void RegisterEventTemplate(RandomEventTemplate template)
        {
            if (template == null) return;
            _eventTemplates.Add(template);
        }

        public void Update(float deltaTime, Vector3 playerPosition, float gameTime)
        {
            _spawnTimer += deltaTime;

            if (_spawnTimer >= (_config != null ? _config.randomEventCooldown : 300f))
            {
                _spawnTimer = 0f;
                TrySpawnRandomEvent(playerPosition, gameTime);
            }

            for (int i = _activeRandomEvents.Count - 1; i >= 0; i--)
            {
                var evt = _activeRandomEvents[i];
                if (evt.IsTimed && evt.ElapsedTime >= evt.TimeLimit)
                {
                    evt.State = MissionState.Failed;
                    _activeRandomEvents.RemoveAt(i);
                    _activeEventCount--;
                    OnRandomEventExpired?.Invoke(evt);
                }
            }
        }

        public MissionData TrySpawnRandomEvent(Vector3 playerPosition, float gameTime)
        {
            if (!CanSpawnNewEvent) return null;
            if (_eventTemplates.Count == 0) return null;

            float spawnChance = _config != null ? _config.randomEventBaseChance : 0.1f;
            if (UnityEngine.Random.value > spawnChance) return null;

            var eligibleTemplates = new List<RandomEventTemplate>();
            float cooldown = _config != null ? _config.randomEventCooldown : 300f;

            foreach (var template in _eventTemplates)
            {
                if (_lastTriggeredTimes.TryGetValue(template.EventId, out float lastTime))
                {
                    if (gameTime - lastTime < template.Cooldown) continue;
                }

                float distToPlayer = Vector3.Distance(playerPosition, template.SpawnCenter);
                if (_config != null && distToPlayer > _config.randomEventRadius) continue;

                eligibleTemplates.Add(template);
            }

            if (eligibleTemplates.Count == 0) return null;

            var selectedTemplate = eligibleTemplates[UnityEngine.Random.Range(0, eligibleTemplates.Count)];
            return SpawnEvent(selectedTemplate, playerPosition, gameTime);
        }

        private MissionData SpawnEvent(RandomEventTemplate template, Vector3 playerPosition, float gameTime)
        {
            Vector3 spawnPosition = template.SpawnCenter + UnityEngine.Random.insideUnitSphere * template.SpawnRadius;
            spawnPosition.y = 0f;

            var mission = new MissionData(
                template.EventId,
                template.EventName,
                template.Type,
                template.Difficulty);

            mission.MissionDescription = template.Description;
            mission.State = MissionState.InProgress;
            mission.TimeLimit = template.Objectives.Count > 0 ? 300f : 0f;
            mission.Objectives = new List<MissionObjectiveData>(template.Objectives);
            mission.BonusRewards = new List<MissionRewardEntry>(template.Rewards);

            foreach (var obj in mission.Objectives)
            {
                obj.TargetPosition = spawnPosition + UnityEngine.Random.insideUnitSphere * 20f;
                obj.TargetPosition.y = 0f;
                obj.State = ObjectiveState.Active;
            }

            _activeRandomEvents.Add(mission);
            _activeEventCount++;
            _lastTriggeredTimes[template.EventId] = gameTime;

            OnRandomEventSpawned?.Invoke(mission);
            Debug.Log($"[MissionRandomEvent] Spawned: {template.EventName}");
            return mission;
        }

        public void CompleteRandomEvent(string eventId)
        {
            for (int i = _activeRandomEvents.Count - 1; i >= 0; i--)
            {
                if (_activeRandomEvents[i].MissionId == eventId)
                {
                    var evt = _activeRandomEvents[i];
                    evt.State = MissionState.Completed;
                    _activeRandomEvents.RemoveAt(i);
                    _activeEventCount--;
                    OnRandomEventCompleted?.Invoke(evt);
                    break;
                }
            }
        }

        public void FailRandomEvent(string eventId)
        {
            for (int i = _activeRandomEvents.Count - 1; i >= 0; i--)
            {
                if (_activeRandomEvents[i].MissionId == eventId)
                {
                    var evt = _activeRandomEvents[i];
                    evt.State = MissionState.Failed;
                    _activeRandomEvents.RemoveAt(i);
                    _activeEventCount--;
                    OnRandomEventExpired?.Invoke(evt);
                    break;
                }
            }
        }

        public List<MissionData> GetActiveRandomEvents()
        {
            return new List<MissionData>(_activeRandomEvents);
        }

        public bool HasActiveEvent(string eventId)
        {
            return _activeRandomEvents.Exists(e => e.MissionId == eventId);
        }

        public void ClearAll()
        {
            _activeRandomEvents.Clear();
            _lastTriggeredTimes.Clear();
            _activeEventCount = 0;
            _spawnTimer = 0f;
        }
    }
}
