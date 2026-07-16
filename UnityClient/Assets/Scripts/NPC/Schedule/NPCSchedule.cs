using System;
using UnityEngine;
using RideVerse.NPC.Core;

namespace RideVerse.NPC.Schedule
{
    public class NPCSchedule : MonoBehaviour
    {
        private NPCConfig _config;
        private float _currentHour;
        private string _currentActivity;
        private bool _isActive;

        public float CurrentHour => _currentHour;
        public string CurrentActivity => _currentActivity;
        public bool IsActive => _isActive;

        public event Action<string> OnActivityChanged;
        public event Action<float> OnHourChanged;

        public void Initialize(NPCConfig config)
        {
            _config = config;
            _currentHour = Random.Range(6f, 8f);
            _isActive = true;
            _currentActivity = "Idle";
        }

        public void UpdateTime(float deltaTime)
        {
            if (!_isActive || _config == null) return;

            float previousHour = _currentHour;
            _currentHour += deltaTime;
            if (_currentHour >= 24f) _currentHour -= 24f;

            if (Mathf.FloorToInt(_currentHour) != Mathf.FloorToInt(previousHour))
            {
                OnHourChanged?.Invoke(_currentHour);
            }

            UpdateActivity();
        }

        private void UpdateActivity()
        {
            string newActivity = DetermineActivity();
            if (newActivity != _currentActivity)
            {
                _currentActivity = newActivity;
                OnActivityChanged?.Invoke(_currentActivity);
            }
        }

        private string DetermineActivity()
        {
            if (_currentHour >= _config.sleepHour || _currentHour < _config.wakeUpHour)
                return "Sleep";

            if (_currentHour >= _config.wakeUpHour && _currentHour < _config.workStartHour)
                return "WakeUp";

            if (_currentHour >= _config.workStartHour && _currentHour < _config.lunchHour)
                return "GoToWork";

            if (_currentHour >= _config.lunchHour && _currentHour < _config.lunchHour + 1f)
                return "Lunch";

            if (_currentHour >= _config.lunchHour + 1f && _currentHour < _config.workEndHour)
                return "Work";

            if (_currentHour >= _config.workEndHour && _currentHour < _config.dinnerHour)
                return "Shop";

            if (_currentHour >= _config.dinnerHour && _currentHour < _config.sleepHour)
                return "GoHome";

            return "Rest";
        }

        public void ForceNextActivity()
        {
            string nextActivity = GetNextActivity();
            if (nextActivity != _currentActivity)
            {
                _currentActivity = nextActivity;
                OnActivityChanged?.Invoke(_currentActivity);
            }
        }

        private string GetNextActivity()
        {
            float nextHour = _currentHour + 1f;
            if (nextHour >= 24f) nextHour -= 24f;

            if (nextHour >= _config.sleepHour || nextHour < _config.wakeUpHour) return "Sleep";
            if (nextHour >= _config.wakeUpHour && nextHour < _config.workStartHour) return "WakeUp";
            if (nextHour >= _config.workStartHour && nextHour < _config.lunchHour) return "GoToWork";
            if (nextHour >= _config.lunchHour && nextHour < _config.lunchHour + 1f) return "Lunch";
            if (nextHour >= _config.lunchHour + 1f && nextHour < _config.workEndHour) return "Work";
            if (nextHour >= _config.workEndHour && nextHour < _config.dinnerHour) return "Shop";
            if (nextHour >= _config.dinnerHour && nextHour < _config.sleepHour) return "GoHome";
            return "Rest";
        }

        public void SetHour(float hour)
        {
            _currentHour = hour % 24f;
            UpdateActivity();
        }

        public void SetActive(bool active)
        {
            _isActive = active;
        }
    }
}
