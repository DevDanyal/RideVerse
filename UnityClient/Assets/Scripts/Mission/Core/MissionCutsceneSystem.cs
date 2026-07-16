using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionCutsceneSystem
    {
        private readonly MissionConfig _config;
        private List<MissionCutsceneEvent> _currentCutscene;
        private int _currentEventIndex;
        private bool _isPlaying;
        private float _eventTimer;
        private bool _isFading;
        private float _fadeTimer;
        private float _fadeDuration;
        private Color _fadeTargetColor;

        public bool IsCutscenePlaying => _isPlaying;
        public int CurrentEventIndex => _currentEventIndex;
        public int TotalEvents => _currentCutscene?.Count ?? 0;
        public bool IsFading => _isFading;
        public float FadeAlpha => _isFading ? _fadeTimer / _fadeDuration : (_fadeTargetColor == Color.black ? 1f : 0f);

        public event Action<string, MissionCutsceneEvent> OnCutsceneEventStarted;
        public event Action<string, MissionCutsceneEvent> OnCutsceneEventCompleted;
        public event Action<string> OnCutsceneStarted;
        public event Action<string> OnCutsceneCompleted;
        public event Action<float> OnFadeUpdated;
        public event Action<string, string> OnCutsceneDialogueShown;

        public MissionCutsceneSystem(MissionConfig config)
        {
            _config = config;
            _currentCutscene = new List<MissionCutsceneEvent>();
        }

        public void PlayCutscene(string missionId, List<MissionCutsceneEvent> events)
        {
            if (events == null || events.Count == 0) return;

            _currentCutscene = events;
            _currentCutscene.Sort((a, b) => a.Order.CompareTo(b.Order));
            _currentEventIndex = 0;
            _isPlaying = true;
            _eventTimer = 0f;

            OnCutsceneStarted?.Invoke(missionId);
            ExecuteEvent(missionId, _currentCutscene[0]);
            Debug.Log($"[MissionCutscene] Playing cutscene with {events.Count} events");
        }

        public void Update(float deltaTime)
        {
            if (!_isPlaying || _currentCutscene == null || _currentEventIndex >= _currentCutscene.Count) return;

            var currentEvent = _currentCutscene[_currentEventIndex];

            if (_isFading)
            {
                _fadeTimer += deltaTime;
                float alpha = Mathf.Clamp01(_fadeTimer / _fadeDuration);
                OnFadeUpdated?.Invoke(_fadeTargetColor == Color.black ? alpha : 1f - alpha);

                if (_fadeTimer >= _fadeDuration)
                {
                    _isFading = false;
                }
                return;
            }

            _eventTimer += deltaTime;

            if (currentEvent.Duration > 0 && _eventTimer >= currentEvent.Duration)
            {
                CompleteCurrentEvent();
            }
        }

        private void ExecuteEvent(string missionId, MissionCutsceneEvent cutsceneEvent)
        {
            switch (cutsceneEvent.ActionType)
            {
                case CutsceneActionType.FadeIn:
                    _isFading = true;
                    _fadeTimer = 0f;
                    _fadeDuration = cutsceneEvent.Duration > 0 ? cutsceneEvent.Duration : (_config != null ? _config.defaultFadeDuration : 1f);
                    _fadeTargetColor = Color.clear;
                    break;

                case CutsceneActionType.FadeOut:
                    _isFading = true;
                    _fadeTimer = 0f;
                    _fadeDuration = cutsceneEvent.Duration > 0 ? cutsceneEvent.Duration : (_config != null ? _config.defaultFadeDuration : 1f);
                    _fadeTargetColor = Color.black;
                    break;

                case CutsceneActionType.CameraMove:
                    break;

                case CutsceneActionType.Wait:
                    break;

                case CutsceneActionType.Dialogue:
                    OnCutsceneDialogueShown?.Invoke(cutsceneEvent.EventId, cutsceneEvent.DialogueText);
                    break;

                case CutsceneActionType.SpawnEntity:
                case CutsceneActionType.Teleport:
                case CutsceneActionType.TriggerEvent:
                    break;
            }

            OnCutsceneEventStarted?.Invoke(missionId, cutsceneEvent);
        }

        private void CompleteCurrentEvent()
        {
            var completedEvent = _currentCutscene[_currentEventIndex];
            OnCutsceneEventCompleted?.Invoke(completedEvent.EventId, completedEvent);

            _currentEventIndex++;
            _eventTimer = 0f;

            if (_currentEventIndex >= _currentCutscene.Count)
            {
                _isPlaying = false;
                OnCutsceneCompleted?.Invoke(completedEvent.EventId);
                Debug.Log("[MissionCutscene] Cutscene completed");
            }
            else
            {
                OnCutsceneEventStarted?.Invoke(null, _currentCutscene[_currentEventIndex]);
            }
        }

        public void SkipCutscene()
        {
            if (!_isPlaying) return;

            _isPlaying = false;
            _isFading = false;

            string cutsceneId = _currentCutscene.Count > 0 ? _currentCutscene[_currentCutscene.Count - 1].EventId : null;
            OnCutsceneCompleted?.Invoke(cutsceneId);
            Debug.Log("[MissionCutscene] Cutscene skipped");
        }

        public void PauseCutscene()
        {
            _isPlaying = false;
        }

        public void ResumeCutscene()
        {
            _isPlaying = true;
        }

        public void SetCutscene(string missionId, List<MissionCutsceneEvent> events)
        {
            _currentCutscene = events ?? new List<MissionCutsceneEvent>();
            _currentEventIndex = 0;
        }

        public void ClearCutscene()
        {
            _currentCutscene = new List<MissionCutsceneEvent>();
            _currentEventIndex = 0;
            _isPlaying = false;
            _isFading = false;
        }

        public float GetCutsceneProgress()
        {
            if (_currentCutscene == null || _currentCutscene.Count == 0) return 0f;
            return (float)_currentEventIndex / _currentCutscene.Count;
        }

        public MissionCutsceneEvent GetCurrentEvent()
        {
            if (_currentCutscene == null || _currentEventIndex >= _currentCutscene.Count)
                return null;
            return _currentCutscene[_currentEventIndex];
        }

        public void Reset()
        {
            ClearCutscene();
            _eventTimer = 0f;
            _fadeTimer = 0f;
        }
    }
}
