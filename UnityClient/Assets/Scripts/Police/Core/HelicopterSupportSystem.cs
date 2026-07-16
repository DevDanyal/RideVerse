using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class HelicopterSupportSystem
    {
        private readonly PoliceConfig _config;
        private readonly List<HelicopterData> _helicopters;
        private bool _isDeployed;

        public bool IsDeployed => _isDeployed;
        public int HelicopterCount => _helicopters.Count;
        public IReadOnlyList<HelicopterData> Helicopters => _helicopters;

        public event Action<HelicopterData> OnHelicopterDeployed;
        public event Action<HelicopterData> OnHelicopterRecalled;

        public HelicopterSupportSystem(PoliceConfig config)
        {
            _config = config;
            _helicopters = new List<HelicopterData>();
        }

        public void Update(float deltaTime, int wantedLevelStars, Vector3 targetPosition)
        {
            if (wantedLevelStars >= _config.helicopterMinWantedLevel && !_isDeployed)
            {
                DeployHelicopter(targetPosition);
            }
            else if (wantedLevelStars < _config.helicopterMinWantedLevel && _isDeployed)
            {
                RecallHelicopters();
            }

            if (_isDeployed)
            {
                UpdateHelicopters(deltaTime, targetPosition);
            }
        }

        public HelicopterData DeployHelicopter(Vector3 targetPosition)
        {
            var heli = new HelicopterData
            {
                HeliId = Guid.NewGuid().ToString("N").Substring(0, 8),
                Position = targetPosition + new Vector3(
                    UnityEngine.Random.Range(-50f, 50f),
                    _config.helicopterAltitude,
                    UnityEngine.Random.Range(-50f, 50f)),
                TargetPosition = targetPosition,
                Altitude = _config.helicopterAltitude,
                Speed = _config.helicopterSpeed,
                IsSpotlightOn = true,
                IsSearching = true
            };

            _helicopters.Add(heli);
            _isDeployed = true;
            OnHelicopterDeployed?.Invoke(heli);
            return heli;
        }

        public void RecallHelicopters()
        {
            for (int i = _helicopters.Count - 1; i >= 0; i--)
            {
                OnHelicopterRecalled?.Invoke(_helicopters[i]);
            }
            _helicopters.Clear();
            _isDeployed = false;
        }

        private void UpdateHelicopters(float deltaTime, Vector3 targetPosition)
        {
            for (int i = _helicopters.Count - 1; i >= 0; i--)
            {
                var heli = _helicopters[i];
                heli.TargetPosition = targetPosition;

                Vector3 direction = (targetPosition - heli.Position);
                direction.y = heli.Altitude - heli.Position.y;

                if (direction.magnitude > 5f)
                {
                    heli.Position += direction.normalized * heli.Speed * deltaTime;
                }

                heli.Position.y = heli.Altitude;
                heli.IsSpotlightOn = true;
                heli.IsSearching = true;
            }
        }

        public bool IsTargetInSpotlight(string heliId, Vector3 targetPosition)
        {
            for (int i = 0; i < _helicopters.Count; i++)
            {
                if (_helicopters[i].HeliId == heliId)
                {
                    Vector3 heliPos = _helicopters[i].Position;
                    float distance = Vector3.Distance(heliPos, targetPosition);
                    return distance <= _config.helicopterSpotlightRange;
                }
            }
            return false;
        }

        public bool CanSeeTarget(Vector3 targetPosition)
        {
            for (int i = 0; i < _helicopters.Count; i++)
            {
                Vector3 heliPos = _helicopters[i].Position;
                float distance = Vector3.Distance(heliPos, targetPosition);
                if (distance <= _config.helicopterSearchRadius)
                {
                    return true;
                }
            }
            return false;
        }

        public Vector3 GetNearestHelicopterPosition(Vector3 position)
        {
            Vector3 nearest = Vector3.zero;
            float nearestDist = float.MaxValue;

            for (int i = 0; i < _helicopters.Count; i++)
            {
                float dist = Vector3.Distance(_helicopters[i].Position, position);
                if (dist < nearestDist)
                {
                    nearestDist = dist;
                    nearest = _helicopters[i].Position;
                }
            }

            return nearest;
        }

        public void ClearAll()
        {
            _helicopters.Clear();
            _isDeployed = false;
        }

        public class HelicopterData
        {
            public string HeliId;
            public Vector3 Position;
            public Vector3 TargetPosition;
            public float Altitude;
            public float Speed;
            public bool IsSpotlightOn;
            public bool IsSearching;
        }
    }
}
