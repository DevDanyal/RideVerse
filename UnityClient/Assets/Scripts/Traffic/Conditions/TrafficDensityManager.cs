using System;
using UnityEngine;
using RideVerse.Traffic.Core;
using RideVerse.Core;

namespace RideVerse.Traffic.Conditions
{
    public class TrafficDensityManager : MonoBehaviour
    {
        private TrafficConfig _config;
        private TrafficDensityLevel _currentDensity;
        private TimeOfDay _currentTimeOfDay;
        private float _densityMultiplier;
        private float _updateTimer;
        private float _gameHour;
        private bool _isRushHour;

        public TrafficDensityLevel CurrentDensity => _currentDensity;
        public TimeOfDay CurrentTimeOfDay => _currentTimeOfDay;
        public float DensityMultiplier => _densityMultiplier;
        public bool IsRushHour => _isRushHour;

        public event Action<TrafficDensityLevel> OnDensityChanged;
        public event Action<TimeOfDay> OnTimeOfDayChanged;

        public void Initialize(TrafficConfig config)
        {
            _config = config;
            _gameHour = 8f;
            _densityMultiplier = 1f;
            UpdateDensity();
        }

        public void SetGameHour(float hour)
        {
            _gameHour = hour % 24f;
        }

        public void AdvanceTime(float deltaHours)
        {
            _gameHour = (_gameHour + deltaHours) % 24f;
        }

        public void UpdateTime(float realDeltaTime, float timeScale)
        {
            _gameHour = (_gameHour + realDeltaTime * timeScale / 3600f) % 24f;

            _updateTimer += realDeltaTime;
            if (_updateTimer >= _config.densityUpdateInterval)
            {
                _updateTimer = 0f;
                UpdateDensity();
            }
        }

        private void UpdateDensity()
        {
            TimeOfDay newTimeOfDay = GetTimeOfDay();
            if (newTimeOfDay != _currentTimeOfDay)
            {
                _currentTimeOfDay = newTimeOfDay;
                OnTimeOfDayChanged?.Invoke(_currentTimeOfDay);
            }

            _isRushHour = IsCurrentTimeRushHour();
            _densityMultiplier = CalculateDensityMultiplier();

            TrafficDensityLevel newDensity = GetDensityLevel();
            if (newDensity != _currentDensity)
            {
                _currentDensity = newDensity;
                OnDensityChanged?.Invoke(_currentDensity);
            }
        }

        private TimeOfDay GetTimeOfDay()
        {
            if (_gameHour >= 5f && _gameHour < 7f) return TimeOfDay.Dawn;
            if (_gameHour >= 7f && _gameHour < 11f) return TimeOfDay.Morning;
            if (_gameHour >= 11f && _gameHour < 14f) return TimeOfDay.Midday;
            if (_gameHour >= 14f && _gameHour < 17f) return TimeOfDay.Afternoon;
            if (_gameHour >= 17f && _gameHour < 19f) return TimeOfDay.Dusk;
            return TimeOfDay.Night;
        }

        private bool IsCurrentTimeRushHour()
        {
            return (_gameHour >= _config.rushHourMorningStart && _gameHour <= _config.rushHourMorningEnd) ||
                   (_gameHour >= _config.rushHourEveningStart && _gameHour <= _config.rushHourEveningEnd);
        }

        private float CalculateDensityMultiplier()
        {
            float multiplier = 1f;

            if (_isRushHour)
                multiplier *= _config.rushHourMultiplier;
            else if (_currentTimeOfDay == TimeOfDay.Night)
                multiplier *= _config.nightReductionFactor;
            else if (_currentTimeOfDay == TimeOfDay.Dawn || _currentTimeOfDay == TimeOfDay.Dusk)
                multiplier *= 1.3f;

            return multiplier;
        }

        private TrafficDensityLevel GetDensityLevel()
        {
            if (_isRushHour) return TrafficDensityLevel.RushHour;

            float ratio = _densityMultiplier;
            if (ratio <= 0.3f) return TrafficDensityLevel.VeryLow;
            if (ratio <= 0.6f) return TrafficDensityLevel.Low;
            if (ratio <= 1.0f) return TrafficDensityLevel.Medium;
            if (ratio <= 1.5f) return TrafficDensityLevel.High;
            return TrafficDensityLevel.VeryHigh;
        }

        public int GetTargetVehicleCount()
        {
            return Mathf.RoundToInt(_config.maxTrafficVehicles * _densityMultiplier);
        }

        public float GetSpawnInterval()
        {
            float baseInterval = 2f;
            return baseInterval / Mathf.Max(0.1f, _densityMultiplier);
        }

        public float GetHeadlightIntensity()
        {
            if (_currentTimeOfDay == TimeOfDay.Night) return 1f;
            if (_currentTimeOfDay == TimeOfDay.Dawn || _currentTimeOfDay == TimeOfDay.Dusk) return 0.5f;
            return 0f;
        }
    }
}
