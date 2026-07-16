using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionTutorialSystem
    {
        private readonly MissionConfig _config;
        private readonly Dictionary<string, MissionData> _tutorialMissions;
        private readonly List<string> _completedTutorials;
        private readonly List<string> _shownHints;
        private string _currentTutorialId;
        private bool _isActive;

        public bool IsActive => _isActive;
        public string CurrentTutorialId => _currentTutorialId;
        public int CompletedCount => _completedTutorials.Count;

        public event Action<string, MissionData> OnTutorialStarted;
        public event Action<string> OnTutorialCompleted;
        public event Action<string, string> OnHintShown;
        public event Action<string> OnHintDismissed;
        public event Action<string, int> OnTutorialStepCompleted;

        public MissionTutorialSystem(MissionConfig config)
        {
            _config = config;
            _tutorialMissions = new Dictionary<string, MissionData>();
            _completedTutorials = new List<string>();
            _shownHints = new List<string>();
        }

        public void RegisterTutorial(MissionData tutorial)
        {
            if (tutorial == null) return;
            tutorial.Type = MissionType.Tutorial;
            _tutorialMissions[tutorial.MissionId] = tutorial;
        }

        public void StartTutorial(string tutorialId)
        {
            if (!_tutorialMissions.ContainsKey(tutorialId))
            {
                Debug.LogWarning($"[MissionTutorial] Tutorial {tutorialId} not found");
                return;
            }

            if (_completedTutorials.Contains(tutorialId))
            {
                Debug.LogWarning($"[MissionTutorial] Tutorial {tutorialId} already completed");
                return;
            }

            _currentTutorialId = tutorialId;
            _isActive = true;

            var tutorial = _tutorialMissions[tutorialId];
            tutorial.State = MissionState.InProgress;

            OnTutorialStarted?.Invoke(tutorialId, tutorial);
            Debug.Log($"[MissionTutorial] Tutorial started: {tutorial.MissionName}");
        }

        public void CompleteTutorialStep(string tutorialId, int stepIndex)
        {
            if (!_isActive || _currentTutorialId != tutorialId) return;

            OnTutorialStepCompleted?.Invoke(tutorialId, stepIndex);
        }

        public void CompleteTutorial(string tutorialId)
        {
            if (_currentTutorialId != tutorialId) return;

            _completedTutorials.Add(tutorialId);
            _isActive = false;

            if (_tutorialMissions.TryGetValue(tutorialId, out var tutorial))
            {
                tutorial.State = MissionState.Completed;
            }

            OnTutorialCompleted?.Invoke(tutorialId);
            _currentTutorialId = null;

            Debug.Log($"[MissionTutorial] Tutorial completed: {tutorialId}");
        }

        public void ShowHint(string hintId, string hintText)
        {
            if (_shownHints.Contains(hintId)) return;
            if (_config != null && _shownHints.Count >= _config.maxTutorialHints) return;

            _shownHints.Add(hintId);
            OnHintShown?.Invoke(hintId, hintText);
        }

        public void DismissHint(string hintId)
        {
            OnHintDismissed?.Invoke(hintId);
        }

        public bool IsTutorialCompleted(string tutorialId)
        {
            return _completedTutorials.Contains(tutorialId);
        }

        public List<MissionData> GetAvailableTutorials()
        {
            var available = new List<MissionData>();
            foreach (var kvp in _tutorialMissions)
            {
                if (!_completedTutorials.Contains(kvp.Key))
                {
                    available.Add(kvp.Value);
                }
            }
            return available;
        }

        public int GetTotalTutorialCount()
        {
            return _tutorialMissions.Count;
        }

        public float GetCompletionRate()
        {
            if (_tutorialMissions.Count == 0) return 0f;
            return (float)_completedTutorials.Count / _tutorialMissions.Count;
        }

        public void Reset()
        {
            _isActive = false;
            _currentTutorialId = null;
        }

        public void ClearAll()
        {
            _tutorialMissions.Clear();
            _completedTutorials.Clear();
            _shownHints.Clear();
            _isActive = false;
            _currentTutorialId = null;
        }
    }
}
