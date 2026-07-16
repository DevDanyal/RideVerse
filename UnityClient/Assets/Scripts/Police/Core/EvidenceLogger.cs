using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class EvidenceLogger
    {
        private readonly PoliceConfig _config;
        private readonly Dictionary<string, List<EvidenceEntry>> _evidenceByCrime;
        private readonly List<EvidenceEntry> _allEvidence;

        public int TotalEvidenceCount => _allEvidence.Count;

        public EvidenceLogger(PoliceConfig config)
        {
            _config = config;
            _evidenceByCrime = new Dictionary<string, List<EvidenceEntry>>();
            _allEvidence = new List<EvidenceEntry>();
        }

        public EvidenceEntry LogEvidence(string crimeId, EvidenceType type, string description, Vector3 position, string sourceId, float reliability = 1f)
        {
            if (_allEvidence.Count >= _config.maxActiveEvidenceEntries)
            {
                CleanupOldestEvidence();
            }

            var entry = new EvidenceEntry(crimeId, type, description, position, sourceId);
            entry.Reliability = Mathf.Clamp01(reliability);
            _allEvidence.Add(entry);

            if (!_evidenceByCrime.ContainsKey(crimeId))
            {
                _evidenceByCrime[crimeId] = new List<EvidenceEntry>();
            }
            _evidenceByCrime[crimeId].Add(entry);

            return entry;
        }

        public EvidenceEntry LogWitnessSighting(string crimeId, string witnessId, Vector3 position, string description)
        {
            return LogEvidence(crimeId, EvidenceType.WitnessSighting, description, position, witnessId, 0.8f);
        }

        public EvidenceEntry LogSpeedReading(string crimeId, string sourceId, Vector3 position, float speedKmh)
        {
            string desc = $"Speed detected: {speedKmh:F1} km/h";
            return LogEvidence(crimeId, EvidenceType.SpeedReading, desc, position, sourceId, 0.95f);
        }

        public EvidenceEntry LogVehicleDescription(string crimeId, string sourceId, Vector3 position, string vehicleDesc)
        {
            return LogEvidence(crimeId, EvidenceType.VehicleDescription, vehicleDesc, position, sourceId, 0.7f);
        }

        public EvidenceEntry LogDamageReport(string crimeId, string sourceId, Vector3 position, float damageAmount)
        {
            string desc = $"Damage reported: ${damageAmount:F0}";
            return LogEvidence(crimeId, EvidenceType.DamageReport, desc, position, sourceId, 0.85f);
        }

        public EvidenceEntry LogWeaponReport(string crimeId, string sourceId, Vector3 position, string weaponDesc)
        {
            return LogEvidence(crimeId, EvidenceType.WeaponReport, weaponDesc, position, sourceId, 0.9f);
        }

        public List<EvidenceEntry> GetEvidenceForCrime(string crimeId)
        {
            if (_evidenceByCrime.TryGetValue(crimeId, out var evidence))
            {
                return new List<EvidenceEntry>(evidence);
            }
            return new List<EvidenceEntry>();
        }

        public List<EvidenceEntry> GetEvidenceNearPosition(Vector3 position, float radius)
        {
            float radiusSq = radius * radius;
            var result = new List<EvidenceEntry>();

            for (int i = 0; i < _allEvidence.Count; i++)
            {
                if ((_allEvidence[i].Position - position).sqrMagnitude <= radiusSq)
                {
                    result.Add(_allEvidence[i]);
                }
            }

            return result;
        }

        public EvidenceEntry GetNearestEvidence(Vector3 position)
        {
            EvidenceEntry nearest = null;
            float nearestDistSq = float.MaxValue;

            for (int i = 0; i < _allEvidence.Count; i++)
            {
                float distSq = (_allEvidence[i].Position - position).sqrMagnitude;
                if (distSq < nearestDistSq)
                {
                    nearestDistSq = distSq;
                    nearest = _allEvidence[i];
                }
            }

            return nearest;
        }

        public float GetTotalReliability(string crimeId)
        {
            var evidence = GetEvidenceForCrime(crimeId);
            if (evidence.Count == 0) return 0f;

            float total = 0f;
            for (int i = 0; i < evidence.Count; i++)
            {
                total += evidence[i].Reliability;
            }
            return total / evidence.Count;
        }

        public int GetEvidenceCount(string crimeId)
        {
            if (_evidenceByCrime.TryGetValue(crimeId, out var evidence))
            {
                return evidence.Count;
            }
            return 0;
        }

        public bool HasStrongEvidence(string crimeId, float threshold = 0.7f)
        {
            return GetTotalReliability(crimeId) >= threshold;
        }

        private void CleanupOldestEvidence()
        {
            if (_allEvidence.Count == 0) return;

            int removeCount = Mathf.Max(1, _allEvidence.Count / 4);
            for (int i = 0; i < removeCount; i++)
            {
                var oldest = _allEvidence[0];
                _allEvidence.RemoveAt(0);

                if (_evidenceByCrime.TryGetValue(oldest.CrimeId, out var evidence))
                {
                    evidence.Remove(oldest);
                }
            }
        }

        public void CleanupExpired()
        {
            for (int i = _allEvidence.Count - 1; i >= 0; i--)
            {
                if (_allEvidence[i].IsExpired(_config.evidenceExpiryTime))
                {
                    var entry = _allEvidence[i];
                    _allEvidence.RemoveAt(i);

                    if (_evidenceByCrime.TryGetValue(entry.CrimeId, out var evidence))
                    {
                        evidence.Remove(entry);
                    }
                }
            }
        }

        public void ClearAll()
        {
            _allEvidence.Clear();
            _evidenceByCrime.Clear();
        }
    }
}
