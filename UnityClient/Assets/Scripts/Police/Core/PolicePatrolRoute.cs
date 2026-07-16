using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class PolicePatrolRoute
    {
        private readonly PoliceConfig _config;
        private PatrolRoute _currentRoute;
        private float _waypointTimer;
        private float _routeTimer;

        public PatrolRoute CurrentRoute => _currentRoute;
        public bool HasRoute => _currentRoute != null && _currentRoute.IsActive;

        public PolicePatrolRoute(PoliceConfig config)
        {
            _config = config;
        }

        public PatrolRoute GenerateRoute(Vector3 centerPosition, float routeRadius)
        {
            int waypointCount = _config.patrolWaypointsPerRoute;
            var waypoints = new List<Vector3>();

            float angleStep = 360f / waypointCount;

            for (int i = 0; i < waypointCount; i++)
            {
                float angle = angleStep * i * Mathf.Deg2Rad;
                float radius = routeRadius * (0.5f + UnityEngine.Random.Range(0f, 0.5f));

                Vector3 waypoint = centerPosition + new Vector3(
                    Mathf.Cos(angle) * radius,
                    0f,
                    Mathf.Sin(angle) * radius
                );
                waypoint.y = 0f;
                waypoints.Add(waypoint);
            }

            _currentRoute = new PatrolRoute(waypoints);
            _routeTimer = 0f;
            return _currentRoute;
        }

        public PatrolRoute GeneratePatrolRoute(Vector3 startPosition)
        {
            return GenerateRoute(startPosition, _config.patrolRouteLength);
        }

        public Vector3 GetCurrentWaypoint()
        {
            if (_currentRoute == null || !_currentRoute.IsActive)
                return Vector3.zero;

            return _currentRoute.GetCurrentWaypoint();
        }

        public Vector3 GetNextWaypoint()
        {
            if (_currentRoute == null || !_currentRoute.IsActive)
                return Vector3.zero;

            return _currentRoute.GetNextWaypoint();
        }

        public bool HasReachedCurrentWaypoint(Vector3 position)
        {
            if (_currentRoute == null || !_currentRoute.IsActive)
                return true;

            return _currentRoute.HasReachedWaypoint(position, _config.patrolWaypointReachDistance);
        }

        public void AdvanceToNextWaypoint()
        {
            _currentRoute?.AdvanceToNextWaypoint();
            _waypointTimer = 0f;
        }

        public bool ShouldRegenerate()
        {
            if (_currentRoute == null) return true;
            _routeTimer += Time.deltaTime;
            return _routeTimer >= _config.patrolRouteRegenerateInterval;
        }

        public float GetDistanceToWaypoint(Vector3 position)
        {
            if (_currentRoute == null) return 0f;
            return _currentRoute.GetDistanceToCurrentWaypoint(position);
        }

        public float GetRouteProgress()
        {
            if (_currentRoute == null) return 0f;
            return _currentRoute.GetProgress();
        }

        public Vector3 GetPatrolDirection(Vector3 currentPosition)
        {
            Vector3 waypoint = GetCurrentWaypoint();
            Vector3 direction = (waypoint - currentPosition).normalized;
            direction.y = 0f;
            return direction;
        }

        public void Reset()
        {
            _currentRoute?.Reset();
            _waypointTimer = 0f;
            _routeTimer = 0f;
        }

        public void Invalidate()
        {
            _currentRoute = null;
            _routeTimer = 0f;
        }
    }
}
