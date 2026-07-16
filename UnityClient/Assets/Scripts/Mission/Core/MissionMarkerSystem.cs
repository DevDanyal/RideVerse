using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionMarkerSystem
    {
        private readonly MissionConfig _config;
        private readonly List<MissionMarkerData> _markers;
        private readonly Dictionary<string, MissionMarkerData> _markerLookup;
        private float _updateTimer;

        public int MarkerCount => _markers.Count;
        public IReadOnlyList<MissionMarkerData> Markers => _markers;

        public event Action<MissionMarkerData> OnMarkerAdded;
        public event Action<string> OnMarkerRemoved;
        public event Action<MissionMarkerData> OnMarkerUpdated;

        public MissionMarkerSystem(MissionConfig config)
        {
            _config = config;
            _markers = new List<MissionMarkerData>();
            _markerLookup = new Dictionary<string, MissionMarkerData>();
        }

        public void Update(float deltaTime, Vector3 playerPosition)
        {
            _updateTimer += deltaTime;

            if (_updateTimer < (_config != null ? _config.markerUpdateInterval : 0.5f)) return;
            _updateTimer = 0f;

            foreach (var marker in _markers)
            {
                if (!marker.IsVisible) continue;

                float distance = Vector3.Distance(playerPosition, marker.WorldPosition);
                bool shouldShow = distance <= (_config != null ? _config.lodDistanceFar : 300f);

                if (!shouldShow && marker.IsVisible)
                {
                    marker.IsVisible = false;
                    OnMarkerUpdated?.Invoke(marker);
                }
                else if (shouldShow && !marker.IsVisible)
                {
                    marker.IsVisible = true;
                    OnMarkerUpdated?.Invoke(marker);
                }
            }
        }

        public MissionMarkerData AddMarker(string missionId, MissionMarkerType type, Vector3 position, string label, Color color)
        {
            var marker = new MissionMarkerData
            {
                MarkerId = $"{missionId}_{type}_{_markers.Count}",
                Type = type,
                WorldPosition = position,
                Label = label,
                MarkerColor = color,
                PulseSpeed = _config != null ? _config.markerPulseSpeed : 2f,
                IsVisible = true,
                AssociatedMissionId = missionId
            };

            _markers.Add(marker);
            _markerLookup[marker.MarkerId] = marker;
            OnMarkerAdded?.Invoke(marker);
            return marker;
        }

        public void RemoveMarker(string markerId)
        {
            for (int i = _markers.Count - 1; i >= 0; i--)
            {
                if (_markers[i].MarkerId == markerId)
                {
                    _markers.RemoveAt(i);
                    _markerLookup.Remove(markerId);
                    OnMarkerRemoved?.Invoke(markerId);
                    break;
                }
            }
        }

        public void RemoveMarkersByMission(string missionId)
        {
            for (int i = _markers.Count - 1; i >= 0; i--)
            {
                if (_markers[i].AssociatedMissionId == missionId)
                {
                    string id = _markers[i].MarkerId;
                    _markers.RemoveAt(i);
                    _markerLookup.Remove(id);
                    OnMarkerRemoved?.Invoke(id);
                }
            }
        }

        public void UpdateMarkerPosition(string markerId, Vector3 newPosition)
        {
            if (_markerLookup.TryGetValue(markerId, out var marker))
            {
                marker.WorldPosition = newPosition;
                OnMarkerUpdated?.Invoke(marker);
            }
        }

        public void UpdateMarkerLabel(string markerId, string newLabel)
        {
            if (_markerLookup.TryGetValue(markerId, out var marker))
            {
                marker.Label = newLabel;
                OnMarkerUpdated?.Invoke(marker);
            }
        }

        public MissionMarkerData GetMarker(string markerId)
        {
            _markerLookup.TryGetValue(markerId, out var marker);
            return marker;
        }

        public List<MissionMarkerData> GetMarkersByType(MissionMarkerType type)
        {
            var result = new List<MissionMarkerData>();
            foreach (var marker in _markers)
            {
                if (marker.Type == type) result.Add(marker);
            }
            return result;
        }

        public List<MissionMarkerData> GetMarkersByMission(string missionId)
        {
            var result = new List<MissionMarkerData>();
            foreach (var marker in _markers)
            {
                if (marker.AssociatedMissionId == missionId) result.Add(marker);
            }
            return result;
        }

        public MissionMarkerData GetNearestMarker(Vector3 position, MissionMarkerType? type = null)
        {
            MissionMarkerData nearest = null;
            float nearestDist = float.MaxValue;

            foreach (var marker in _markers)
            {
                if (!marker.IsVisible) continue;
                if (type.HasValue && marker.Type != type.Value) continue;

                float dist = Vector3.Distance(position, marker.WorldPosition);
                if (dist < nearestDist)
                {
                    nearestDist = dist;
                    nearest = marker;
                }
            }

            return nearest;
        }

        public float GetDistanceToMarker(string markerId, Vector3 playerPosition)
        {
            if (_markerLookup.TryGetValue(markerId, out var marker))
            {
                return Vector3.Distance(playerPosition, marker.WorldPosition);
            }
            return float.MaxValue;
        }

        public void SetMarkerVisible(string markerId, bool visible)
        {
            if (_markerLookup.TryGetValue(markerId, out var marker))
            {
                marker.IsVisible = visible;
                OnMarkerUpdated?.Invoke(marker);
            }
        }

        public void SetAllVisible(bool visible)
        {
            foreach (var marker in _markers)
            {
                marker.IsVisible = visible;
            }
        }

        public void ClearAll()
        {
            _markers.Clear();
            _markerLookup.Clear();
        }
    }
}
