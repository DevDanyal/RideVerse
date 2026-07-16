using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class RadioCommunicationSystem
    {
        private readonly PoliceConfig _config;
        private readonly List<RadioMessage> _messages;
        private readonly Dictionary<string, float> _unitChatterTimers;

        public int ActiveMessageCount => _messages.Count;

        public event Action<RadioMessage> OnMessageSent;
        public event Action<RadioMessage> OnMessageReceived;
        public event Action<string> OnBackupRequested;

        public RadioCommunicationSystem(PoliceConfig config)
        {
            _config = config;
            _messages = new List<RadioMessage>();
            _unitChatterTimers = new Dictionary<string, float>();
        }

        public void Update(float deltaTime)
        {
            for (int i = _messages.Count - 1; i >= 0; i--)
            {
                if (_messages[i].IsExpired(_config.radioMessageLifetime))
                {
                    _messages.RemoveAt(i);
                }
            }

            List<string> keys = new List<string>(_unitChatterTimers.Keys);
            for (int i = 0; i < keys.Count; i++)
            {
                _unitChatterTimers[keys[i]] += deltaTime;
            }
        }

        public RadioMessage SendMessage(RadioMessageType type, string senderId, string content, Vector3 position)
        {
            var message = new RadioMessage(type, senderId, content, position);
            _messages.Add(message);
            OnMessageSent?.Invoke(message);
            return message;
        }

        public RadioMessage SendBackupRequest(string senderId, Vector3 position, DispatchPriority priority, string reason)
        {
            string content = $"Backup needed - Priority: {priority} - Reason: {reason}";
            var message = SendMessage(RadioMessageType.BackupRequest, senderId, content, position);
            OnBackupRequested?.Invoke(senderId);
            return message;
        }

        public RadioMessage SendBackupResponse(string senderId, string targetUnitId, Vector3 position, bool accepted)
        {
            string content = accepted ? "Backup en route" : "Backup unavailable";
            var message = SendMessage(RadioMessageType.BackupResponse, senderId, content, position);
            message.TargetUnitId = targetUnitId;
            return message;
        }

        public RadioMessage SendStatusUpdate(string senderId, PoliceState state, Vector3 position)
        {
            string content = $"Status: {state}";
            return SendMessage(RadioMessageType.StatusUpdate, senderId, content, position);
        }

        public RadioMessage SendPursuitUpdate(string senderId, PursuitState state, Vector3 position, string targetId = null)
        {
            string content = $"Pursuit: {state}";
            var message = SendMessage(RadioMessageType.PursuitUpdate, senderId, content, position);
            message.TargetUnitId = targetId;
            return message;
        }

        public RadioMessage SendRoadblockRequest(string senderId, Vector3 position, Vector3 targetPosition)
        {
            string content = $"Roadblock requested ahead";
            var message = SendMessage(RadioMessageType.RoadblockRequest, senderId, content, position);
            message.TargetUnitId = targetPosition.ToString();
            return message;
        }

        public RadioMessage SendAllUnitsAlert(string senderId, string alert, Vector3 position)
        {
            return SendMessage(RadioMessageType.AllUnitsAlert, senderId, alert, position);
        }

        public RadioMessage SendUnitDispatched(string senderId, string callId, Vector3 position)
        {
            string content = $"Unit dispatched to call {callId}";
            var message = SendMessage(RadioMessageType.UnitDispatched, senderId, content, position);
            message.TargetUnitId = callId;
            return message;
        }

        public RadioMessage SendUnitOnScene(string senderId, Vector3 position)
        {
            return SendMessage(RadioMessageType.UnitOnScene, senderId, "Unit on scene", position);
        }

        public RadioMessage SendEvidenceLogged(string senderId, string evidenceId, Vector3 position)
        {
            string content = $"Evidence logged: {evidenceId}";
            return SendMessage(RadioMessageType.EvidenceLogged, senderId, content, position);
        }

        public RadioMessage SendWantedLevelChanged(string senderId, int oldLevel, int newLevel)
        {
            string content = $"Wanted level: {oldLevel} -> {newLevel}";
            return SendMessage(RadioMessageType.WantedLevelChanged, senderId, content, Vector3.zero);
        }

        public RadioMessage SendStandDown(string senderId)
        {
            return SendMessage(RadioMessageType.StandDown, senderId, "All units stand down", Vector3.zero);
        }

        public RadioMessage SendClearScene(string senderId, Vector3 position)
        {
            return SendMessage(RadioMessageType.ClearScene, senderId, "Scene clear", position);
        }

        public bool CanUnitSendChatter(string unitId)
        {
            if (!_unitChatterTimers.ContainsKey(unitId))
            {
                _unitChatterTimers[unitId] = 0f;
                return true;
            }

            float elapsed = _unitChatterTimers[unitId];
            float cooldown = UnityEngine.Random.Range(_config.radioChatterMinInterval, _config.radioChatterMaxInterval);
            return elapsed >= cooldown;
        }

        public void ResetUnitChatter(string unitId)
        {
            _unitChatterTimers[unitId] = 0f;
        }

        public List<RadioMessage> GetMessagesByType(RadioMessageType type)
        {
            var result = new List<RadioMessage>();
            for (int i = 0; i < _messages.Count; i++)
            {
                if (_messages[i].Type == type)
                {
                    result.Add(_messages[i]);
                }
            }
            return result;
        }

        public List<RadioMessage> GetMessagesForUnit(string unitId)
        {
            var result = new List<RadioMessage>();
            for (int i = 0; i < _messages.Count; i++)
            {
                if (_messages[i].TargetUnitId == unitId ||
                    string.IsNullOrEmpty(_messages[i].TargetUnitId) ||
                    _messages[i].Type == RadioMessageType.AllUnitsAlert)
                {
                    result.Add(_messages[i]);
                }
            }
            return result;
        }

        public RadioMessage GetLatestMessageByType(RadioMessageType type)
        {
            for (int i = _messages.Count - 1; i >= 0; i--)
            {
                if (_messages[i].Type == type)
                {
                    return _messages[i];
                }
            }
            return null;
        }

        public void ClearAll()
        {
            _messages.Clear();
            _unitChatterTimers.Clear();
        }
    }
}
