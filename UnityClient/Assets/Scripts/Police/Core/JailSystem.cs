using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class JailSystem
    {
        private readonly PoliceConfig _config;
        private readonly Dictionary<string, JailRecord> _activeSentences;

        public int ActiveSentenceCount => _activeSentences.Count;

        public event Action<JailRecord> OnJailSentenceStarted;
        public event Action<string> OnJailSentenceCompleted;
        public event Action<string> OnJailEscape;

        public JailSystem(PoliceConfig config)
        {
            _config = config;
            _activeSentences = new Dictionary<string, JailRecord>();
        }

        public void Update(float deltaTime)
        {
            List<string> completedIds = new List<string>();

            foreach (var kvp in _activeSentences)
            {
                kvp.Value.TickServing(deltaTime);
                if (kvp.Value.IsFinished())
                {
                    completedIds.Add(kvp.Key);
                }
            }

            for (int i = 0; i < completedIds.Count; i++)
            {
                string playerId = completedIds[i];
                _activeSentences.Remove(playerId);
                OnJailSentenceCompleted?.Invoke(playerId);
            }
        }

        public JailRecord SendToJail(string playerId, JailSentence sentence)
        {
            if (_activeSentences.ContainsKey(playerId))
            {
                return _activeSentences[playerId];
            }

            float duration = GetSentenceDuration(sentence);
            var record = new JailRecord(playerId, sentence, duration);
            _activeSentences[playerId] = record;

            OnJailSentenceStarted?.Invoke(record);
            return record;
        }

        public JailRecord SendToJail(string playerId, CrimeType crimeType, float wantedLevelStars)
        {
            var arrestSystem = new ArrestSystem(_config);
            JailSentence sentence = arrestSystem.GetJailSentence(crimeType, wantedLevelStars);
            return SendToJail(playerId, sentence);
        }

        public bool IsInJail(string playerId)
        {
            return _activeSentences.ContainsKey(playerId);
        }

        public JailRecord GetSentence(string playerId)
        {
            _activeSentences.TryGetValue(playerId, out var record);
            return record;
        }

        public float GetRemainingTime(string playerId)
        {
            if (_activeSentences.TryGetValue(playerId, out var record))
            {
                return record.GetRemainingTime();
            }
            return 0f;
        }

        public void ReleaseFromJail(string playerId)
        {
            if (_activeSentences.ContainsKey(playerId))
            {
                _activeSentences.Remove(playerId);
                OnJailSentenceCompleted?.Invoke(playerId);
            }
        }

        public void EscapeJail(string playerId)
        {
            if (_activeSentences.ContainsKey(playerId))
            {
                _activeSentences.Remove(playerId);
                OnJailEscape?.Invoke(playerId);
            }
        }

        public Vector3 GetJailRespawnPosition(Vector3 jailPosition)
        {
            return jailPosition + new Vector3(
                UnityEngine.Random.Range(-3f, 3f),
                0f,
                UnityEngine.Random.Range(-3f, 3f));
        }

        public float GetSentenceDuration(JailSentence sentence)
        {
            return sentence switch
            {
                JailSentence.Warning => 0f,
                JailSentence.ShortDetention => _config.jailSentenceShort,
                JailSentence.MediumDetention => _config.jailSentenceMedium,
                JailSentence.LongDetention => _config.jailSentenceLong,
                JailSentence.ExtendedDetention => _config.jailSentenceExtended,
                _ => 0f
            };
        }

        public bool HasActiveSentences()
        {
            return _activeSentences.Count > 0;
        }

        public List<JailRecord> GetAllActiveSentences()
        {
            return new List<JailRecord>(_activeSentences.Values);
        }

        public float GetTotalSentenceTimeServed(string playerId)
        {
            if (_activeSentences.TryGetValue(playerId, out var record))
            {
                return record.TimeServed;
            }
            return 0f;
        }

        public float GetSentenceProgress(string playerId)
        {
            if (_activeSentences.TryGetValue(playerId, out var record))
            {
                if (record.SentenceDuration <= 0f) return 1f;
                return record.TimeServed / record.SentenceDuration;
            }
            return 0f;
        }

        public void ClearAll()
        {
            _activeSentences.Clear();
        }
    }
}
