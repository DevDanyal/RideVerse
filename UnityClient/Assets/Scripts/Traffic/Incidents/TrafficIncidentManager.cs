using System;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.Traffic.Core;

namespace RideVerse.Traffic.Incidents
{
    [Serializable]
    public class TrafficIncident
    {
        public string Id;
        public IncidentType Type;
        public Vector3 Position;
        public float Radius;
        public float Duration;
        public float ElapsedTime;
        public bool IsActive;
        public List<string> AffectedVehicleIds;

        public TrafficIncident(string id, IncidentType type, Vector3 position, float duration)
        {
            Id = id;
            Type = type;
            Position = position;
            Duration = duration;
            ElapsedTime = 0f;
            IsActive = true;
            AffectedVehicleIds = new List<string>();

            switch (type)
            {
                case IncidentType.MinorCrash: Radius = 5f; break;
                case IncidentType.MajorCrash: Radius = 15f; break;
                case IncidentType.VehicleBreakdown: Radius = 4f; break;
                case IncidentType.TrafficJam: Radius = 20f; break;
                case IncidentType.RoadClosure: Radius = 30f; break;
                case IncidentType.Construction: Radius = 25f; break;
            }
        }

        public bool IsExpired => ElapsedTime >= Duration;
        public float RemainingTime => Mathf.Max(0f, Duration - ElapsedTime);
    }

    public class TrafficIncidentManager : MonoBehaviour
    {
        private TrafficConfig _config;
        private List<TrafficIncident> _activeIncidents = new List<TrafficIncident>();
        private float _checkTimer;
        private int _nextIncidentId;

        public int ActiveIncidentCount => _activeIncidents.Count;
        public IReadOnlyList<TrafficIncident> ActiveIncidents => _activeIncidents;

        public event Action<TrafficIncident> OnIncidentCreated;
        public event Action<TrafficIncident> OnIncidentResolved;

        public void Initialize(TrafficConfig config)
        {
            _config = config;
            _nextIncidentId = 0;
        }

        public void UpdateIncidents(float deltaTime)
        {
            _checkTimer += deltaTime;

            if (_checkTimer >= _config.incidentCheckInterval)
            {
                _checkTimer = 0f;
                TrySpawnIncident();
            }

            for (int i = _activeIncidents.Count - 1; i >= 0; i--)
            {
                _activeIncidents[i].ElapsedTime += deltaTime;

                if (_activeIncidents[i].IsExpired)
                {
                    var incident = _activeIncidents[i];
                    _activeIncidents.RemoveAt(i);
                    OnIncidentResolved?.Invoke(incident);
                }
            }
        }

        public TrafficIncident CreateIncident(IncidentType type, Vector3 position)
        {
            string id = $"INC_{_nextIncidentId++}";
            float duration = GetDurationForType(type);

            var incident = new TrafficIncident(id, type, position, duration);
            _activeIncidents.Add(incident);
            OnIncidentCreated?.Invoke(incident);

            return incident;
        }

        public void RemoveIncident(string incidentId)
        {
            for (int i = _activeIncidents.Count - 1; i >= 0; i--)
            {
                if (_activeIncidents[i].Id == incidentId)
                {
                    var incident = _activeIncidents[i];
                    _activeIncidents.RemoveAt(i);
                    OnIncidentResolved?.Invoke(incident);
                    break;
                }
            }
        }

        public bool IsPositionBlocked(Vector3 position)
        {
            foreach (var incident in _activeIncidents)
            {
                if (!incident.IsActive) continue;

                float dist = Vector3.Distance(position, incident.Position);
                if (dist < incident.Radius)
                    return true;
            }

            return false;
        }

        public float GetSpeedReductionAtPosition(Vector3 position)
        {
            float reduction = 1f;

            foreach (var incident in _activeIncidents)
            {
                if (!incident.IsActive) continue;

                float dist = Vector3.Distance(position, incident.Position);
                if (dist < incident.Radius * 2f)
                {
                    float factor = Mathf.Clamp01(dist / (incident.Radius * 2f));
                    float incidentReduction = Mathf.Lerp(0.3f, 1f, factor);

                    switch (incident.Type)
                    {
                        case IncidentType.MajorCrash:
                            incidentReduction *= 0.5f;
                            break;
                        case IncidentType.TrafficJam:
                            incidentReduction *= 0.6f;
                            break;
                        case IncidentType.Construction:
                            incidentReduction *= 0.7f;
                            break;
                    }

                    reduction = Mathf.Min(reduction, incidentReduction);
                }
            }

            return reduction;
        }

        public TrafficIncident GetNearestIncident(Vector3 position)
        {
            TrafficIncident nearest = null;
            float nearestDist = float.MaxValue;

            foreach (var incident in _activeIncidents)
            {
                float dist = Vector3.Distance(position, incident.Position);
                if (dist < nearestDist)
                {
                    nearestDist = dist;
                    nearest = incident;
                }
            }

            return nearest;
        }

        public List<TrafficIncident> GetIncidentsInRadius(Vector3 center, float radius)
        {
            var result = new List<TrafficIncident>();
            float radiusSq = radius * radius;

            foreach (var incident in _activeIncidents)
            {
                if ((incident.Position - center).sqrMagnitude <= radiusSq)
                {
                    result.Add(incident);
                }
            }

            return result;
        }

        private void TrySpawnIncident()
        {
            if (_activeIncidents.Count >= 5) return;
            if (Random.value > _config.incidentSpawnChance) return;

            IncidentType type = GetRandomIncidentType();
            Vector3 position = new Vector3(
                Random.Range(-200f, 200f),
                0f,
                Random.Range(-200f, 200f));

            CreateIncident(type, position);
        }

        private IncidentType GetRandomIncidentType()
        {
            float roll = Random.value;
            if (roll < 0.3f) return IncidentType.MinorCrash;
            if (roll < 0.5f) return IncidentType.VehicleBreakdown;
            if (roll < 0.7f) return IncidentType.MajorCrash;
            if (roll < 0.85f) return IncidentType.TrafficJam;
            if (roll < 0.95f) return IncidentType.Construction;
            return IncidentType.RoadClosure;
        }

        private float GetDurationForType(IncidentType type)
        {
            switch (type)
            {
                case IncidentType.MinorCrash: return _config.minorCrashDuration;
                case IncidentType.MajorCrash: return _config.majorCrashDuration;
                case IncidentType.VehicleBreakdown: return _config.breakdownDuration;
                case IncidentType.TrafficJam: return _config.majorCrashDuration * 1.5f;
                case IncidentType.RoadClosure: return _config.majorCrashDuration * 2f;
                case IncidentType.Construction: return _config.majorCrashDuration * 3f;
                default: return 20f;
            }
        }
    }
}
