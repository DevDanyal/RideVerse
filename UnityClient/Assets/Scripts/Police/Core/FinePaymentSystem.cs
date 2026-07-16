using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class FinePaymentSystem
    {
        private readonly PoliceConfig _config;
        private readonly Dictionary<string, List<FineRecord>> _playerFines;

        public event Action<FineRecord> OnFineIssued;
        public event Action<FineRecord> OnFinePaid;
        public event Action<FineRecord> OnFineFailed;

        public FinePaymentSystem(PoliceConfig config)
        {
            _config = config;
            _playerFines = new Dictionary<string, List<FineRecord>>();
        }

        public FineRecord IssueFine(string playerId, CrimeType crimeType, float wantedLevelStars, string crimeId)
        {
            var arrestSystem = new ArrestSystem(_config);
            float baseFine = arrestSystem.GetBaseFine(crimeType);
            float multiplier = Mathf.Pow(_config.fineMultiplierPerStar, wantedLevelStars);
            FineCategory category = GetFineCategory(crimeType);

            var record = new FineRecord(playerId, category, baseFine, crimeId, multiplier);
            AddFine(record);
            OnFineIssued?.Invoke(record);
            return record;
        }

        public bool PayFine(string playerId, string fineId, double playerCash)
        {
            var fines = GetUnpaidFines(playerId);
            FineRecord fine = null;

            for (int i = 0; i < fines.Count; i++)
            {
                if (fines[i].FineId == fineId)
                {
                    fine = fines[i];
                    break;
                }
            }

            if (fine == null) return false;

            float totalAmount = fine.GetTotalAmount();
            if (playerCash < totalAmount)
            {
                OnFineFailed?.Invoke(fine);
                return false;
            }

            fine.MarkPaid();
            OnFinePaid?.Invoke(fine);
            return true;
        }

        public bool PayAllFines(string playerId, double playerCash)
        {
            var fines = GetUnpaidFines(playerId);
            float totalOwed = CalculateTotalOwed(playerId);

            if (playerCash < totalOwed)
            {
                return false;
            }

            for (int i = 0; i < fines.Count; i++)
            {
                fines[i].MarkPaid();
                OnFinePaid?.Invoke(fines[i]);
            }

            return true;
        }

        public float CalculateTotalOwed(string playerId)
        {
            var fines = GetUnpaidFines(playerId);
            float total = 0f;

            for (int i = 0; i < fines.Count; i++)
            {
                total += fines[i].GetTotalAmount();
            }

            return total;
        }

        public List<FineRecord> GetUnpaidFines(string playerId)
        {
            var result = new List<FineRecord>();
            if (_playerFines.TryGetValue(playerId, out var fines))
            {
                for (int i = 0; i < fines.Count; i++)
                {
                    if (!fines[i].IsPaid)
                    {
                        result.Add(fines[i]);
                    }
                }
            }
            return result;
        }

        public List<FineRecord> GetAllFines(string playerId)
        {
            if (_playerFines.TryGetValue(playerId, out var fines))
            {
                return new List<FineRecord>(fines);
            }
            return new List<FineRecord>();
        }

        public bool HasOutstandingFines(string playerId)
        {
            return GetUnpaidFines(playerId).Count > 0;
        }

        public int GetOutstandingFineCount(string playerId)
        {
            return GetUnpaidFines(playerId).Count;
        }

        private void AddFine(FineRecord fine)
        {
            if (!_playerFines.ContainsKey(fine.PlayerId))
            {
                _playerFines[fine.PlayerId] = new List<FineRecord>();
            }
            _playerFines[fine.PlayerId].Add(fine);
        }

        private FineCategory GetFineCategory(CrimeType crimeType)
        {
            return crimeType switch
            {
                CrimeType.Speeding => FineCategory.Speeding,
                CrimeType.DangerousDriving => FineCategory.DangerousDriving,
                CrimeType.HitAndRun => FineCategory.HitAndRun,
                CrimeType.VehicleTheft => FineCategory.VehicleTheft,
                CrimeType.PropertyDamage => FineCategory.PropertyDamage,
                CrimeType.WeaponPossession => FineCategory.WeaponViolation,
                CrimeType.Assault => FineCategory.Assault,
                CrimeType.Robbery => FineCategory.Robbery,
                CrimeType.BusinessTheft => FineCategory.Robbery,
                CrimeType.IllegalRacing => FineCategory.Racing,
                CrimeType.PoliceAssault => FineCategory.PoliceAssault,
                CrimeType.Murder => FineCategory.Murder,
                _ => FineCategory.Speeding
            };
        }

        public void ClearAll()
        {
            _playerFines.Clear();
        }
    }
}
