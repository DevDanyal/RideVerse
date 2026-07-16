using System;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionTimerSystem
    {
        private readonly MissionConfig _config;
        private string _activeMissionId;
        private bool _isRunning;
        private float _tickTimer;

        public event Action<string, float> OnTimerUpdated;
        public event Action<string> OnTimerWarning;
        public event Action<string> OnTimerExpired;

        public float TimeRemaining { get; private set; }
        public float ElapsedTime { get; private set; }
        public bool IsRunning => _isRunning;
        public string ActiveMissionId => _activeMissionId;
        public bool IsWarning => _config != null && TimeRemaining <= _config.warningTimeThreshold && TimeRemaining > 0f;

        public MissionTimerSystem(MissionConfig config)
        {
            _config = config;
        }

        public void StartTimer(string missionId, float timeLimit)
        {
            _activeMissionId = missionId;
            _isRunning = true;
            ElapsedTime = 0f;
            TimeRemaining = timeLimit;
            _tickTimer = 0f;

            Debug.Log($"[MissionTimer] Started: {timeLimit}s for mission {missionId}");
        }

        public void StopTimer()
        {
            _isRunning = false;
            Debug.Log("[MissionTimer] Stopped");
        }

        public void PauseTimer()
        {
            _isRunning = false;
        }

        public void ResumeTimer()
        {
            _isRunning = true;
        }

        public void Update(float deltaTime)
        {
            if (!_isRunning || string.IsNullOrEmpty(_activeMissionId)) return;

            _tickTimer += deltaTime;

            if (_tickTimer >= (_config != null ? _config.timerTickInterval : 1f))
            {
                _tickTimer = 0f;
            }

            ElapsedTime += deltaTime;
            TimeRemaining = Mathf.Max(0f, TimeRemaining - deltaTime);

            OnTimerUpdated?.Invoke(_activeMissionId, TimeRemaining);

            if (_config != null && TimeRemaining <= _config.warningTimeThreshold && TimeRemaining > _config.warningTimeThreshold - _config.timerTickInterval * 2f)
            {
                OnTimerWarning?.Invoke(_activeMissionId);
            }

            if (TimeRemaining <= 0f)
            {
                _isRunning = false;
                OnTimerExpired?.Invoke(_activeMissionId);
                Debug.Log($"[MissionTimer] Expired for mission {_activeMissionId}");
            }
        }

        public void SetTime(string missionId, float timeRemaining)
        {
            _activeMissionId = missionId;
            TimeRemaining = timeRemaining;
            ElapsedTime = 0f;
        }

        public void AddTime(float additionalTime)
        {
            TimeRemaining += additionalTime;
        }

        public void SubtractTime(float timeToSubtract)
        {
            TimeRemaining = Mathf.Max(0f, TimeRemaining - timeToSubtract);
        }

        public float GetProgress()
        {
            if (string.IsNullOrEmpty(_activeMissionId)) return 0f;

            float totalTime = ElapsedTime + TimeRemaining;
            if (totalTime <= 0f) return 0f;

            return ElapsedTime / totalTime;
        }

        public string GetFormattedTimeRemaining()
        {
            int minutes = Mathf.FloorToInt(TimeRemaining / 60f);
            int seconds = Mathf.FloorToInt(TimeRemaining % 60f);
            return $"{minutes:00}:{seconds:00}";
        }

        public string GetFormattedElapsedTime()
        {
            int minutes = Mathf.FloorToInt(ElapsedTime / 60f);
            int seconds = Mathf.FloorToInt(ElapsedTime % 60f);
            return $"{minutes:00}:{seconds:00}";
        }

        public float GetTimePercentRemaining()
        {
            float totalTime = ElapsedTime + TimeRemaining;
            if (totalTime <= 0f) return 0f;
            return TimeRemaining / totalTime;
        }

        public void Reset()
        {
            _activeMissionId = null;
            _isRunning = false;
            ElapsedTime = 0f;
            TimeRemaining = 0f;
            _tickTimer = 0f;
        }

        public void ClearActiveMission()
        {
            Reset();
        }
    }
}
