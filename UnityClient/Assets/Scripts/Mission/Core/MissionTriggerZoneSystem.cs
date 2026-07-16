using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionTriggerZoneSystem
    {
        private readonly MissionConfig _config;
        private readonly List<TriggerZoneData> _zones;
        private readonly Dictionary<string, TriggerZoneData> _zoneLookup;
        private float _checkTimer;

        public int ActiveZoneCount
        {
            get
            {
                int count = 0;
                foreach (var zone in _zones) if (zone.IsActive) count++;
                return count;
            }
        }

        public event Action<string, TriggerZoneData> OnPlayerEnteredZone;
        public event Action<string, TriggerZoneData> OnPlayerExitedZone;
        public event Action<string, TriggerZoneData> OnZoneActivated;
        public event Action<string, TriggerZoneData> OnZoneDeactivated;

        public MissionTriggerZoneSystem(MissionConfig config)
        {
            _config = config;
            _zones = new List<TriggerZoneData>();
            _zoneLookup = new Dictionary<string, TriggerZoneData>();
        }

        public void Update(float deltaTime, Vector3 playerPosition, bool playerInVehicle)
        {
            _checkTimer += deltaTime;
            if (_checkTimer < (_config != null ? _config.triggerCheckInterval : 0.25f)) return;
            _checkTimer = 0f;

            foreach (var zone in _zones)
            {
                if (!zone.IsActive) continue;

                if (_config != null && zone.RequireVehicle && _config.requireVehicleForVehicleZone && !playerInVehicle) continue;

                bool isInside = IsPointInsideZone(playerPosition, zone);

                if (isInside)
                {
                    OnPlayerEnteredZone?.Invoke(zone.ZoneId, zone);
                }
            }
        }

        public TriggerZoneData CreateZone(string missionId, TriggerZoneShape shape, Vector3 center, Vector3 size, float radius = 10f)
        {
            var zone = new TriggerZoneData
            {
                AssociatedMissionId = missionId,
                Shape = shape,
                Center = center,
                Size = size,
                Radius = radius,
                IsActive = true
            };

            _zones.Add(zone);
            _zoneLookup[zone.ZoneId] = zone;
            OnZoneActivated?.Invoke(zone.ZoneId, zone);
            return zone;
        }

        public TriggerZoneData CreateCheckpointZone(string missionId, Vector3 position, float radius)
        {
            return CreateZone(missionId, TriggerZoneShape.Sphere, position, Vector3.zero, radius);
        }

        public TriggerZoneData CreateObjectiveZone(string missionId, string objectiveId, Vector3 position, float radius)
        {
            var zone = CreateZone(missionId, TriggerZoneShape.Sphere, position, Vector3.zero, radius);
            zone.AssociatedObjectiveId = objectiveId;
            return zone;
        }

        public void RemoveZone(string zoneId)
        {
            for (int i = _zones.Count - 1; i >= 0; i--)
            {
                if (_zones[i].ZoneId == zoneId)
                {
                    _zones.RemoveAt(i);
                    _zoneLookup.Remove(zoneId);
                    break;
                }
            }
        }

        public void RemoveZonesByMission(string missionId)
        {
            for (int i = _zones.Count - 1; i >= 0; i--)
            {
                if (_zones[i].AssociatedMissionId == missionId)
                {
                    string id = _zones[i].ZoneId;
                    _zones.RemoveAt(i);
                    _zoneLookup.Remove(id);
                }
            }
        }

        public void ActivateZone(string zoneId)
        {
            if (_zoneLookup.TryGetValue(zoneId, out var zone))
            {
                zone.IsActive = true;
                OnZoneActivated?.Invoke(zoneId, zone);
            }
        }

        public void DeactivateZone(string zoneId)
        {
            if (_zoneLookup.TryGetValue(zoneId, out var zone))
            {
                zone.IsActive = false;
                OnZoneDeactivated?.Invoke(zoneId, zone);
            }
        }

        public TriggerZoneData GetZone(string zoneId)
        {
            _zoneLookup.TryGetValue(zoneId, out var zone);
            return zone;
        }

        public List<TriggerZoneData> GetZonesByMission(string missionId)
        {
            var result = new List<TriggerZoneData>();
            foreach (var zone in _zones)
            {
                if (zone.AssociatedMissionId == missionId) result.Add(zone);
            }
            return result;
        }

        public TriggerZoneData GetNearestActiveZone(Vector3 position)
        {
            TriggerZoneData nearest = null;
            float nearestDist = float.MaxValue;

            foreach (var zone in _zones)
            {
                if (!zone.IsActive) continue;

                float dist = Vector3.Distance(position, zone.Center);
                if (dist < nearestDist)
                {
                    nearestDist = dist;
                    nearest = zone;
                }
            }

            return nearest;
        }

        public bool IsPointInsideZone(Vector3 point, TriggerZoneData zone)
        {
            switch (zone.Shape)
            {
                case TriggerZoneShape.Sphere:
                    return Vector3.Distance(point, zone.Center) <= zone.Radius;

                case TriggerZoneShape.Box:
                    Vector3 halfSize = zone.Size * 0.5f;
                    Vector3 local = point - zone.Center;
                    return Mathf.Abs(local.x) <= halfSize.x
                        && Mathf.Abs(local.y) <= halfSize.y
                        && Mathf.Abs(local.z) <= halfSize.z;

                case TriggerZoneShape.Capsule:
                    Vector3 capsuleUp = Vector3.up;
                    Vector3 capsuleCenter = zone.Center;
                    float capsuleHeight = zone.Height > 0 ? zone.Height : 2f;
                    Vector3 dir = point - capsuleCenter;
                    float projection = Vector3.Dot(dir, capsuleUp);
                    projection = Mathf.Clamp(projection, -capsuleHeight * 0.5f, capsuleHeight * 0.5f);
                    Vector3 closestPoint = capsuleCenter + capsuleUp * projection;
                    return Vector3.Distance(point, closestPoint) <= zone.Radius;

                default:
                    return false;
            }
        }

        public void ClearAll()
        {
            _zones.Clear();
            _zoneLookup.Clear();
        }
    }
}
