using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class SWATSupportSystem
    {
        private readonly PoliceConfig _config;
        private readonly List<PoliceUnitData> _swatUnits;
        private bool _isDeployed;
        private float _deploymentTimer;
        private float _responseTimer;

        public bool IsDeployed => _isDeployed;
        public int SWATAvailable => _swatUnits.Count;
        public IReadOnlyList<PoliceUnitData> SWATUnits => _swatUnits;

        public event Action OnSWATDeployed;
        public event Action OnSWATStandDown;

        public SWATSupportSystem(PoliceConfig config)
        {
            _config = config;
            _swatUnits = new List<PoliceUnitData>();
            _isDeployed = false;
        }

        public void Update(float deltaTime, int wantedLevelStars)
        {
            if (wantedLevelStars >= _config.swatMinWantedLevel && !_isDeployed)
            {
                _responseTimer += deltaTime;
                if (_responseTimer >= _config.swatResponseTime)
                {
                    DeploySWAT();
                }
            }
            else if (wantedLevelStars < _config.swatMinWantedLevel && _isDeployed)
            {
                StandDown();
            }
        }

        public void DeploySWAT()
        {
            if (_isDeployed) return;

            _isDeployed = true;
            _swatUnits.Clear();

            for (int i = 0; i < _config.swatMaxUnits; i++)
            {
                var unit = new PoliceUnitData(
                    $"SWAT-{i + 1}",
                    PoliceUnitType.SWATTeam,
                    Vector3.zero,
                    0f,
                    0
                );
                unit.MaxHealth = 100f * _config.swatHealthMultiplier;
                unit.Health = unit.MaxHealth;
                _swatUnits.Add(unit);
            }

            OnSWATDeployed?.Invoke();
        }

        public void StandDown()
        {
            if (!_isDeployed) return;

            _isDeployed = false;
            _swatUnits.Clear();
            _responseTimer = 0f;

            OnSWATStandDown?.Invoke();
        }

        public PoliceUnitData GetAvailableSWATUnit()
        {
            for (int i = 0; i < _swatUnits.Count; i++)
            {
                if (_swatUnits[i].IsAvailable)
                {
                    return _swatUnits[i];
                }
            }
            return null;
        }

        public bool HasAvailableUnits()
        {
            for (int i = 0; i < _swatUnits.Count; i++)
            {
                if (_swatUnits[i].IsAvailable)
                    return true;
            }
            return false;
        }

        public float GetSWATDamageMultiplier()
        {
            return _config.swatDamageMultiplier;
        }

        public float GetSWATHealthMultiplier()
        {
            return _config.swatHealthMultiplier;
        }

        public bool ShouldDeployForLevel(int wantedLevelStars)
        {
            return wantedLevelStars >= _config.swatMinWantedLevel;
        }
    }
}
