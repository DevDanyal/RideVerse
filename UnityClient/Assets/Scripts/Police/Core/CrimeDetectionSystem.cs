using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class CrimeDetectionSystem
    {
        private readonly PoliceConfig _config;
        private readonly List<CrimeRecord> _activeCrimes;
        private readonly List<WitnessReport> _witnessReports;
        private float _detectionTimer;
        private int _nextCrimeIndex;

        public int ActiveCrimeCount => _activeCrimes.Count;
        public IReadOnlyList<CrimeRecord> ActiveCrimes => _activeCrimes;

        public event Action<CrimeRecord> OnCrimeDetected;
        public event Action<CrimeRecord> OnCrimeVerified;

        public CrimeDetectionSystem(PoliceConfig config)
        {
            _config = config;
            _activeCrimes = new List<CrimeRecord>();
            _witnessReports = new List<WitnessReport>();
            _nextCrimeIndex = 0;
        }

        public void Update(float deltaTime, Vector3 playerPosition, float playerSpeedKmh)
        {
            _detectionTimer += deltaTime;
            if (_detectionTimer < _config.crimeVerificationDelay) return;
            _detectionTimer = 0f;

            CleanupExpiredCrimes();
            CleanupExpiredWitnesses();
        }

        public CrimeRecord ReportCrime(string playerId, CrimeType type, Vector3 position, float severity = 1f)
        {
            var existing = FindActiveCrime(playerId, type);
            if (existing != null)
            {
                existing.Severity = Mathf.Max(existing.Severity, severity);
                existing.Timestamp = Time.time;
                return existing;
            }

            var crime = new CrimeRecord(playerId, type, position, severity);
            _activeCrimes.Add(crime);
            OnCrimeDetected?.Invoke(crime);
            return crime;
        }

        public CrimeRecord DetectSpeeding(string playerId, Vector3 position, float speedKmh, float speedLimitKmh)
        {
            if (speedKmh <= speedLimitKmh + _config.speedingToleranceKmh)
                return null;

            float severity = Mathf.InverseLerp(speedLimitKmh, speedLimitKmh * 2f, speedKmh);
            return ReportCrime(playerId, CrimeType.Speeding, position, severity);
        }

        public CrimeRecord DetectDangerousDriving(string playerId, Vector3 position, float angle, float speed)
        {
            if (angle < _config.dangerousDrivingAngleThreshold || speed < 20f)
                return null;

            float severity = Mathf.InverseLerp(_config.dangerousDrivingAngleThreshold, 180f, angle);
            return ReportCrime(playerId, CrimeType.DangerousDriving, position, severity);
        }

        public CrimeRecord DetectHitAndRun(string playerId, Vector3 position, float impactSpeed)
        {
            float severity = Mathf.InverseLerp(5f, 50f, impactSpeed);
            return ReportCrime(playerId, CrimeType.HitAndRun, position, severity);
        }

        public CrimeRecord DetectVehicleTheft(string playerId, Vector3 position)
        {
            return ReportCrime(playerId, CrimeType.VehicleTheft, position, 1.5f);
        }

        public CrimeRecord DetectPropertyDamage(string playerId, Vector3 position, float damageAmount)
        {
            float severity = Mathf.InverseLerp(0f, 1000f, damageAmount);
            return ReportCrime(playerId, CrimeType.PropertyDamage, position, severity);
        }

        public CrimeRecord DetectWeaponPossession(string playerId, Vector3 position)
        {
            return ReportCrime(playerId, CrimeType.WeaponPossession, position, 1.5f);
        }

        public CrimeRecord DetectAssault(string playerId, Vector3 position)
        {
            return ReportCrime(playerId, CrimeType.Assault, position, 2f);
        }

        public CrimeRecord DetectRobbery(string playerId, Vector3 position)
        {
            return ReportCrime(playerId, CrimeType.Robbery, position, 2.5f);
        }

        public CrimeRecord DetectIllegalRacing(string playerId, Vector3 position)
        {
            return ReportCrime(playerId, CrimeType.IllegalRacing, position, 1.5f);
        }

        public CrimeRecord DetectPoliceAssault(string playerId, Vector3 position)
        {
            return ReportCrime(playerId, CrimeType.PoliceAssault, position, 3f);
        }

        public CrimeRecord DetectMurder(string playerId, Vector3 position)
        {
            return ReportCrime(playerId, CrimeType.Murder, position, 4f);
        }

        public void VerifyCrime(string crimeId)
        {
            var crime = FindCrimeById(crimeId);
            if (crime != null && !crime.IsVerified)
            {
                crime.IsVerified = true;
                OnCrimeVerified?.Invoke(crime);
            }
        }

        public void ResolveCrime(string crimeId)
        {
            var crime = FindCrimeById(crimeId);
            if (crime != null)
            {
                crime.IsResolved = true;
            }
        }

        public WitnessReport AddWitness(string crimeId, string witnessId, Vector3 witnessPosition, Vector3 crimePosition, string description)
        {
            var crime = FindCrimeById(crimeId);
            if (crime == null) return null;

            if (crime.WitnessIds.Count >= _config.maxCrimeWitnesses)
                return null;

            var report = new WitnessReport(crimeId, witnessId, witnessPosition, crimePosition, description);
            _witnessReports.Add(report);
            crime.WitnessIds.Add(report.ReportId);

            return report;
        }

        public void AddEvidence(string crimeId, EvidenceEntry evidence)
        {
            var crime = FindCrimeById(crimeId);
            if (crime == null) return;

            if (crime.EvidenceIds.Count >= _config.maxEvidencePerCrime)
                return;

            crime.EvidenceIds.Add(evidence.EvidenceId);
        }

        public CrimeRecord FindCrimeById(string crimeId)
        {
            for (int i = 0; i < _activeCrimes.Count; i++)
            {
                if (_activeCrimes[i].CrimeId == crimeId)
                    return _activeCrimes[i];
            }
            return null;
        }

        private CrimeRecord FindActiveCrime(string playerId, CrimeType type)
        {
            for (int i = _activeCrimes.Count - 1; i >= 0; i--)
            {
                if (_activeCrimes[i].PlayerId == playerId &&
                    _activeCrimes[i].CrimeType == type &&
                    !_activeCrimes[i].IsResolved)
                {
                    return _activeCrimes[i];
                }
            }
            return null;
        }

        public List<CrimeRecord> GetCrimesNearPosition(Vector3 position, float radius)
        {
            float radiusSq = radius * radius;
            var result = new List<CrimeRecord>();

            for (int i = 0; i < _activeCrimes.Count; i++)
            {
                if (_activeCrimes[i].IsResolved) continue;
                if ((_activeCrimes[i].Position - position).sqrMagnitude <= radiusSq)
                {
                    result.Add(_activeCrimes[i]);
                }
            }

            return result;
        }

        public List<CrimeRecord> GetCrimesForPlayer(string playerId)
        {
            var result = new List<CrimeRecord>();
            for (int i = 0; i < _activeCrimes.Count; i++)
            {
                if (_activeCrimes[i].PlayerId == playerId && !_activeCrimes[i].IsResolved)
                {
                    result.Add(_activeCrimes[i]);
                }
            }
            return result;
        }

        public CrimeRecord GetNearestCrime(Vector3 position)
        {
            CrimeRecord nearest = null;
            float nearestDistSq = float.MaxValue;

            for (int i = 0; i < _activeCrimes.Count; i++)
            {
                if (_activeCrimes[i].IsResolved) continue;
                float distSq = (_activeCrimes[i].Position - position).sqrMagnitude;
                if (distSq < nearestDistSq)
                {
                    nearestDistSq = distSq;
                    nearest = _activeCrimes[i];
                }
            }

            return nearest;
        }

        private void CleanupExpiredCrimes()
        {
            _activeCrimes.RemoveAll(c => c.IsResolved || Time.time - c.Timestamp > _config.evidenceExpiryTime);
        }

        private void CleanupExpiredWitnesses()
        {
            _witnessReports.RemoveAll(w => Time.time - w.Timestamp > _config.evidenceExpiryTime);
        }

        public List<WitnessReport> GetWitnessesForCrime(string crimeId)
        {
            var result = new List<WitnessReport>();
            for (int i = 0; i < _witnessReports.Count; i++)
            {
                if (_witnessReports[i].CrimeId == crimeId)
                {
                    result.Add(_witnessReports[i]);
                }
            }
            return result;
        }

        public void ClearAll()
        {
            _activeCrimes.Clear();
            _witnessReports.Clear();
        }
    }
}
