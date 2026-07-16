using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class PatrolRoute
    {
        public string RouteId;
        public List<Vector3> Waypoints;
        public int CurrentWaypointIndex;
        public bool IsActive;
        public float TotalLength;

        public PatrolRoute()
        {
            RouteId = Guid.NewGuid().ToString("N").Substring(0, 8);
            Waypoints = new List<Vector3>();
            CurrentWaypointIndex = 0;
            IsActive = false;
        }

        public PatrolRoute(List<Vector3> waypoints) : this()
        {
            Waypoints = new List<Vector3>(waypoints);
            CalculateTotalLength();
            IsActive = true;
        }

        public Vector3 GetCurrentWaypoint()
        {
            if (Waypoints.Count == 0) return Vector3.zero;
            return Waypoints[CurrentWaypointIndex % Waypoints.Count];
        }

        public Vector3 GetNextWaypoint()
        {
            if (Waypoints.Count == 0) return Vector3.zero;
            return Waypoints[(CurrentWaypointIndex + 1) % Waypoints.Count];
        }

        public bool HasReachedWaypoint(Vector3 position, float threshold)
        {
            if (Waypoints.Count == 0) return true;
            return Vector3.Distance(position, GetCurrentWaypoint()) <= threshold;
        }

        public void AdvanceToNextWaypoint()
        {
            if (Waypoints.Count > 0)
            {
                CurrentWaypointIndex = (CurrentWaypointIndex + 1) % Waypoints.Count;
            }
        }

        public float GetDistanceToCurrentWaypoint(Vector3 position)
        {
            if (Waypoints.Count == 0) return 0f;
            return Vector3.Distance(position, GetCurrentWaypoint());
        }

        public float GetProgress()
        {
            if (Waypoints.Count <= 1) return 1f;
            return (float)CurrentWaypointIndex / Waypoints.Count;
        }

        public void Reset()
        {
            CurrentWaypointIndex = 0;
        }

        private void CalculateTotalLength()
        {
            TotalLength = 0f;
            for (int i = 0; i < Waypoints.Count - 1; i++)
            {
                TotalLength += Vector3.Distance(Waypoints[i], Waypoints[i + 1]);
            }
            if (Waypoints.Count > 1)
            {
                TotalLength += Vector3.Distance(Waypoints[Waypoints.Count - 1], Waypoints[0]);
            }
        }
    }

    public class RoadblockData
    {
        public string RoadblockId;
        public RoadblockType Type;
        public Vector3 Position;
        public float Rotation;
        public List<string> AssignedUnitIds;
        public float SetupProgress;
        public bool IsReady;
        public bool IsActive;
        public float Lifetime;
        public float MaxLifetime;

        public RoadblockData()
        {
            RoadblockId = Guid.NewGuid().ToString("N").Substring(0, 8);
            AssignedUnitIds = new List<string>();
            SetupProgress = 0f;
            IsReady = false;
            IsActive = false;
            MaxLifetime = 60f;
        }

        public RoadblockData(RoadblockType type, Vector3 position, float rotation) : this()
        {
            Type = type;
            Position = position;
            Rotation = rotation;
        }

        public bool IsExpired()
        {
            return Time.time - Lifetime > MaxLifetime;
        }

        public void Activate()
        {
            IsActive = true;
            Lifetime = Time.time;
        }

        public float GetEffectiveWidth()
        {
            return Type switch
            {
                RoadblockType.PoliceCars => 10f,
                RoadblockType.SpikeStrip => 8f,
                RoadblockType.Barricade => 12f,
                RoadblockType.TrafficDiversion => 15f,
                _ => 10f
            };
        }

        public float GetEffectiveHeight()
        {
            return Type switch
            {
                RoadblockType.PoliceCars => 2f,
                RoadblockType.SpikeStrip => 0.3f,
                RoadblockType.Barricade => 1.5f,
                RoadblockType.TrafficDiversion => 2f,
                _ => 1.5f
            };
        }
    }

    public class RadioMessage
    {
        public string MessageId;
        public RadioMessageType Type;
        public string SenderUnitId;
        public string TargetUnitId;
        public string Content;
        public Vector3 Position;
        public float Timestamp;
        public bool IsDelivered;

        public RadioMessage()
        {
            MessageId = Guid.NewGuid().ToString("N").Substring(0, 8);
            Timestamp = Time.time;
        }

        public RadioMessage(RadioMessageType type, string senderId, string content, Vector3 position) : this()
        {
            Type = type;
            SenderUnitId = senderId;
            Content = content;
            Position = position;
        }

        public bool IsExpired(float lifetime)
        {
            return Time.time - Timestamp > lifetime;
        }
    }
}
