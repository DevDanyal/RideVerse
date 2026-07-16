using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionDialogueSystem
    {
        private readonly MissionConfig _config;
        private List<MissionDialogueLine> _currentDialogue;
        private int _currentLineIndex;
        private bool _isDialogueActive;
        private float _lineTimer;
        private float _charRevealTimer;
        private int _revealedChars;
        private bool _isRevealing;

        public bool IsDialogueActive => _isDialogueActive;
        public int CurrentLineIndex => _currentLineIndex;
        public int TotalLines => _currentDialogue?.Count ?? 0;
        public bool HasMoreLines => _currentDialogue != null && _currentLineIndex < _currentDialogue.Count;
        public MissionDialogueLine CurrentLine => _currentDialogue != null && _currentLineIndex < _currentDialogue.Count
            ? _currentDialogue[_currentLineIndex] : null;

        public event Action<string, MissionDialogueLine> OnDialogueLineStarted;
        public event Action<string, MissionDialogueLine> OnDialogueLineCompleted;
        public event Action<string> OnDialogueCompleted;
        public event Action<string, string> OnDialogueTextUpdated;

        public MissionDialogueSystem(MissionConfig config)
        {
            _config = config;
            _currentDialogue = new List<MissionDialogueLine>();
        }

        public void StartDialogue(string missionId, List<MissionDialogueLine> dialogue)
        {
            if (dialogue == null || dialogue.Count == 0) return;

            _currentDialogue = dialogue;
            _currentDialogue.Sort((a, b) => a.Order.CompareTo(b.Order));
            _currentLineIndex = 0;
            _isDialogueActive = true;
            _lineTimer = 0f;
            _charRevealTimer = 0f;
            _revealedChars = 0;
            _isRevealing = true;

            OnDialogueLineStarted?.Invoke(missionId, _currentDialogue[0]);
            Debug.Log($"[MissionDialogue] Dialogue started with {dialogue.Count} lines");
        }

        public void Update(float deltaTime)
        {
            if (!_isDialogueActive || _currentDialogue == null || _currentLineIndex >= _currentDialogue.Count) return;

            var currentLine = _currentDialogue[_currentLineIndex];

            if (_isRevealing)
            {
                _charRevealTimer += deltaTime;
                float charsPerSecond = 1f / (_config != null ? _config.dialogueTextSpeed : 0.03f);

                int targetChars = Mathf.FloorToInt(_charRevealTimer * charsPerSecond);

                if (targetChars > _revealedChars)
                {
                    _revealedChars = Mathf.Min(targetChars, currentLine.Text.Length);
                    string displayedText = currentLine.Text.Substring(0, _revealedChars);
                    OnDialogueTextUpdated?.Invoke(currentLine.LineId, displayedText);
                }

                if (_revealedChars >= currentLine.Text.Length)
                {
                    _isRevealing = false;
                    _charRevealTimer = 0f;

                    if (currentLine.DisplayDuration > 0 && !currentLine.Skippable)
                    {
                        _lineTimer = 0f;
                    }
                }
            }
            else
            {
                if (currentLine.DisplayDuration > 0)
                {
                    _lineTimer += deltaTime;
                    if (_lineTimer >= currentLine.DisplayDuration)
                    {
                        AdvanceLine();
                    }
                }
            }
        }

        public void SkipOrAdvance()
        {
            if (!_isDialogueActive) return;

            var currentLine = _currentDialogue[_currentLineIndex];

            if (_isRevealing)
            {
                _revealedChars = currentLine.Text.Length;
                _isRevealing = false;
                OnDialogueTextUpdated?.Invoke(currentLine.LineId, currentLine.Text);
            }
            else
            {
                AdvanceLine();
            }
        }

        private void AdvanceLine()
        {
            var completedLine = _currentDialogue[_currentLineIndex];

            OnDialogueLineCompleted?.Invoke(completedLine.LineId, completedLine);

            _currentLineIndex++;
            _lineTimer = 0f;
            _charRevealTimer = 0f;
            _revealedChars = 0;
            _isRevealing = true;

            if (_currentLineIndex >= _currentDialogue.Count)
            {
                _isDialogueActive = false;
                OnDialogueCompleted?.Invoke(completedLine.LineId);
                Debug.Log("[MissionDialogue] Dialogue completed");
            }
            else
            {
                OnDialogueLineStarted?.Invoke(completedLine.LineId, _currentDialogue[_currentLineIndex]);
            }
        }

        public void EndDialogue()
        {
            if (!_isDialogueActive) return;

            var lastLine = _currentLineIndex < _currentDialogue.Count ? _currentDialogue[_currentLineIndex] : null;
            _isDialogueActive = false;

            if (lastLine != null)
            {
                OnDialogueCompleted?.Invoke(lastLine.LineId);
            }

            Debug.Log("[MissionDialogue] Dialogue ended");
        }

        public void SetCurrentDialogue(string missionId, List<MissionDialogueLine> dialogue)
        {
            _currentDialogue = dialogue ?? new List<MissionDialogueLine>();
            _currentLineIndex = 0;
        }

        public void ClearDialogue()
        {
            _currentDialogue = new List<MissionDialogueLine>();
            _currentLineIndex = 0;
            _isDialogueActive = false;
        }

        public MissionDialogueLine GetLine(int index)
        {
            if (_currentDialogue == null || index < 0 || index >= _currentDialogue.Count)
                return null;
            return _currentDialogue[index];
        }

        public float GetDialogueProgress()
        {
            if (_currentDialogue == null || _currentDialogue.Count == 0) return 0f;
            return (float)_currentLineIndex / _currentDialogue.Count;
        }

        public void Reset()
        {
            ClearDialogue();
            _lineTimer = 0f;
            _charRevealTimer = 0f;
            _revealedChars = 0;
        }
    }
}
