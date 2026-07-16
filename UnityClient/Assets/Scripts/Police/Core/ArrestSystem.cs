using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class ArrestSystem
    {
        private readonly PoliceConfig _config;
        private readonly Dictionary<string, float> _arrestCooldowns;

        public event Action<string, string> OnArrestAttempt;
        public event Action<string> OnArrestSuccess;
        public event Action<string> OnArrestFailed;
        public event Action<string, float> OnFineIssued;

        public ArrestSystem(PoliceConfig config)
        {
            _config = config;
            _arrestCooldowns = new Dictionary<string, float>();
        }

        public void Update(float deltaTime)
        {
            List<string> keys = new List<string>(_arrestCooldowns.Keys);
            for (int i = 0; i < keys.Count; i++)
            {
                _arrestCooldowns[keys[i]] -= deltaTime;
                if (_arrestCooldowns[keys[i]] <= 0f)
                {
                    _arrestCooldowns.Remove(keys[i]);
                }
            }
        }

        public bool CanAttemptArrest(string officerId, Vector3 officerPos, Vector3 suspectPos, float wantedLevel)
        {
            if (wantedLevel <= 0f) return false;
            if (IsOnCooldown(officerId)) return false;

            float distance = Vector3.Distance(officerPos, suspectPos);
            return distance <= _config.arrestRange;
        }

        public bool AttemptArrest(string officerId, string suspectId, Vector3 officerPos, Vector3 suspectPos, float wantedLevel)
        {
            if (!CanAttemptArrest(officerId, officerPos, suspectPos, wantedLevel))
                return false;

            OnArrestAttempt?.Invoke(officerId, suspectId);

            float surrenderChance = CalculateSurrenderChance(wantedLevel);
            if (UnityEngine.Random.value <= surrenderChance)
            {
                OnArrestSuccess?.Invoke(suspectId);
                _arrestCooldowns[officerId] = _config.arrestCooldown;
                return true;
            }

            float arrestChance = CalculateArrestChance(officerPos, suspectPos);
            if (UnityEngine.Random.value <= arrestChance)
            {
                OnArrestSuccess?.Invoke(suspectId);
                _arrestCooldowns[officerId] = _config.arrestCooldown;
                return true;
            }

            OnArrestFailed?.Invoke(officerId);
            _arrestCooldowns[officerId] = _config.arrestCooldown * 0.5f;
            return false;
        }

        public float CalculateSurrenderChance(float wantedLevel)
        {
            float baseChance = _config.arrestSurrenderChance;
            float wantedPenalty = wantedLevel * 0.05f;
            return Mathf.Clamp01(baseChance - wantedPenalty);
        }

        public float CalculateArrestChance(Vector3 officerPos, Vector3 suspectPos)
        {
            float distance = Vector3.Distance(officerPos, suspectPos);
            float rangeFactor = 1f - Mathf.InverseLerp(0f, _config.arrestEscapeDistance, distance);
            return Mathf.Clamp01(0.6f + rangeFactor * 0.3f);
        }

        public bool IsOnCooldown(string officerId)
        {
            return _arrestCooldowns.ContainsKey(officerId) && _arrestCooldowns[officerId] > 0f;
        }

        public float CalculateFine(CrimeType crimeType, float wantedLevelStars)
        {
            float baseFine = GetBaseFine(crimeType);
            float multiplier = Mathf.Pow(_config.fineMultiplierPerStar, wantedLevelStars);
            return baseFine * multiplier;
        }

        public float GetBaseFine(CrimeType crimeType)
        {
            return crimeType switch
            {
                CrimeType.Speeding => _config.fineSpeeding,
                CrimeType.DangerousDriving => _config.fineDangerousDriving,
                CrimeType.HitAndRun => _config.fineHitAndRun,
                CrimeType.VehicleTheft => _config.fineVehicleTheft,
                CrimeType.PropertyDamage => _config.finePropertyDamage,
                CrimeType.WeaponPossession => _config.fineWeaponViolation,
                CrimeType.Assault => _config.fineAssault,
                CrimeType.Robbery => _config.fineRobbery,
                CrimeType.IllegalRacing => _config.fineRacing,
                CrimeType.PoliceAssault => _config.finePoliceAssault,
                CrimeType.Murder => _config.fineMurder,
                CrimeType.BusinessTheft => _config.fineRobbery,
                _ => 100f
            };
        }

        public JailSentence GetJailSentence(CrimeType crimeType, float wantedLevelStars)
        {
            if (wantedLevelStars >= 5f) return JailSentence.ExtendedDetention;
            if (wantedLevelStars >= 4f) return JailSentence.LongDetention;
            if (wantedLevelStars >= 3f) return JailSentence.MediumDetention;
            if (wantedLevelStars >= 2f) return JailSentence.ShortDetention;

            return crimeType switch
            {
                CrimeType.Murder => JailSentence.ExtendedDetention,
                CrimeType.PoliceAssault => JailSentence.LongDetention,
                CrimeType.Robbery => JailSentence.LongDetention,
                CrimeType.Assault => JailSentence.MediumDetention,
                CrimeType.VehicleTheft => JailSentence.MediumDetention,
                CrimeType.WeaponPossession => JailSentence.ShortDetention,
                CrimeType.HitAndRun => JailSentence.ShortDetention,
                CrimeType.DangerousDriving => JailSentence.Warning,
                CrimeType.Speeding => JailSentence.Warning,
                _ => JailSentence.Warning
            };
        }

        public float GetJailDuration(JailSentence sentence)
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

        public bool IsWithinArrestRange(Vector3 officerPos, Vector3 suspectPos)
        {
            return Vector3.Distance(officerPos, suspectPos) <= _config.arrestRange;
        }

        public bool IsSuspectEscaping(Vector3 suspectPos, Vector3 lastKnownPos, float escapeDistance)
        {
            return Vector3.Distance(suspectPos, lastKnownPos) > escapeDistance;
        }

        public void ClearCooldowns()
        {
            _arrestCooldowns.Clear();
        }
    }
}
