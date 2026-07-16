using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    [Serializable]
    public class CrimeRecord
    {
        public string CrimeId;
        public string PlayerId;
        public CrimeType CrimeType;
        public Vector3 Position;
        public float Severity;
        public float Timestamp;
        public bool IsVerified;
        public bool IsResolved;
        public List<string> EvidenceIds;
        public List<string> WitnessIds;

        public CrimeRecord()
        {
            CrimeId = Guid.NewGuid().ToString("N").Substring(0, 8);
            EvidenceIds = new List<string>();
            WitnessIds = new List<string>();
            Timestamp = Time.time;
        }

        public CrimeRecord(string playerId, CrimeType type, Vector3 position, float severity) : this()
        {
            PlayerId = playerId;
            CrimeType = type;
            Position = position;
            Severity = severity;
        }

        public float GetWantedLevelContribution()
        {
            return CrimeType switch
            {
                CrimeType.Speeding => 0.3f,
                CrimeType.DangerousDriving => 0.5f,
                CrimeType.HitAndRun => 1.0f,
                CrimeType.VehicleTheft => 1.5f,
                CrimeType.PropertyDamage => 1.0f,
                CrimeType.WeaponPossession => 1.5f,
                CrimeType.Assault => 2.0f,
                CrimeType.Robbery => 2.5f,
                CrimeType.BusinessTheft => 2.0f,
                CrimeType.IllegalRacing => 1.5f,
                CrimeType.PoliceAssault => 3.0f,
                CrimeType.Murder => 4.0f,
                _ => 0.5f
            };
        }
    }

    [Serializable]
    public class EvidenceEntry
    {
        public string EvidenceId;
        public string CrimeId;
        public EvidenceType Type;
        public string Description;
        public Vector3 Position;
        public float Timestamp;
        public float Reliability;
        public string SourceId;

        public EvidenceEntry()
        {
            EvidenceId = Guid.NewGuid().ToString("N").Substring(0, 8);
            Timestamp = Time.time;
            Reliability = 1f;
        }

        public EvidenceEntry(string crimeId, EvidenceType type, string description, Vector3 position, string sourceId) : this()
        {
            CrimeId = crimeId;
            Type = type;
            Description = description;
            Position = position;
            SourceId = sourceId;
        }

        public bool IsExpired(float expiryTime)
        {
            return Time.time - Timestamp > expiryTime;
        }
    }

    [Serializable]
    public class WitnessReport
    {
        public string ReportId;
        public string CrimeId;
        public string WitnessId;
        public Vector3 WitnessPosition;
        public Vector3 CrimePosition;
        public float Timestamp;
        public float Credibility;
        public string Description;

        public WitnessReport()
        {
            ReportId = Guid.NewGuid().ToString("N").Substring(0, 8);
            Timestamp = Time.time;
            Credibility = 1f;
        }

        public WitnessReport(string crimeId, string witnessId, Vector3 witnessPos, Vector3 crimePos, string description) : this()
        {
            CrimeId = crimeId;
            WitnessId = witnessId;
            WitnessPosition = witnessPos;
            CrimePosition = crimePos;
            Description = description;
        }
    }

    [Serializable]
    public class DispatchCall
    {
        public string CallId;
        public string CrimeId;
        public CrimeType CrimeType;
        public Vector3 Position;
        public DispatchPriority Priority;
        public float Timestamp;
        public bool IsActive;
        public bool IsAssigned;
        public string AssignedUnitId;
        public float ExpiryTime;
        public int RequiredUnits;

        public DispatchCall()
        {
            CallId = Guid.NewGuid().ToString("N").Substring(0, 8);
            Timestamp = Time.time;
            IsActive = true;
            IsAssigned = false;
            RequiredUnits = 1;
        }

        public DispatchCall(string crimeId, CrimeType type, Vector3 position, DispatchPriority priority) : this()
        {
            CrimeId = crimeId;
            CrimeType = type;
            Position = position;
            Priority = priority;
        }

        public bool IsExpired(float currentTime)
        {
            return currentTime - Timestamp > ExpiryTime;
        }

        public float GetPriorityScore()
        {
            return Priority switch
            {
                DispatchPriority.Low => 1f,
                DispatchPriority.Medium => 2f,
                DispatchPriority.High => 4f,
                DispatchPriority.Critical => 8f,
                _ => 1f
            };
        }
    }

    [Serializable]
    public class PoliceUnitData
    {
        public string UnitId;
        public string OfficerName;
        public PoliceUnitType UnitType;
        public Vector3 SpawnPosition;
        public float SpawnRotation;
        public int DistrictIndex;
        public float Health;
        public float MaxHealth;
        public bool IsInVehicle;
        public bool IsAvailable;

        public PoliceUnitData()
        {
            UnitId = Guid.NewGuid().ToString("N").Substring(0, 8);
            OfficerName = "Officer";
            Health = 100f;
            MaxHealth = 100f;
            IsAvailable = true;
            IsInVehicle = true;
        }

        public PoliceUnitData(string name, PoliceUnitType type, Vector3 position, float rotation, int district) : this()
        {
            OfficerName = name;
            UnitType = type;
            SpawnPosition = position;
            SpawnRotation = rotation;
            DistrictIndex = district;
        }

        public float GetMaxSpeed(float configSpeed)
        {
            return UnitType switch
            {
                PoliceUnitType.PatrolCar => configSpeed,
                PoliceUnitType.PatrolBike => configSpeed * 0.85f,
                PoliceUnitType.SUV => configSpeed * 0.9f,
                PoliceUnitType.UnmarkedCar => configSpeed * 1.1f,
                PoliceUnitType.SWATVan => configSpeed * 0.75f,
                PoliceUnitType.SWATTeam => configSpeed * 0.4f,
                PoliceUnitType.Helicopter => configSpeed * 0.7f,
                PoliceUnitType.K9Unit => configSpeed * 0.3f,
                _ => configSpeed
            };
        }

        public bool CanPursue()
        {
            return UnitType == PoliceUnitType.PatrolCar ||
                   UnitType == PoliceUnitType.PatrolBike ||
                   UnitType == PoliceUnitType.SUV ||
                   UnitType == PoliceUnitType.UnmarkedCar;
        }

        public bool CanSetRoadblock()
        {
            return UnitType == PoliceUnitType.PatrolCar ||
                   UnitType == PoliceUnitType.SUV ||
                   UnitType == PoliceUnitType.SWATVan;
        }

        public bool IsSWAT()
        {
            return UnitType == PoliceUnitType.SWATVan ||
                   UnitType == PoliceUnitType.SWATTeam;
        }
    }

    [Serializable]
    public class JailRecord
    {
        public string RecordId;
        public string PlayerId;
        public JailSentence Sentence;
        public float SentenceDuration;
        public float TimeServed;
        public float Timestamp;
        public bool IsCompleted;

        public JailRecord()
        {
            RecordId = Guid.NewGuid().ToString("N").Substring(0, 8);
            Timestamp = Time.time;
        }

        public JailRecord(string playerId, JailSentence sentence, float duration) : this()
        {
            PlayerId = playerId;
            Sentence = sentence;
            SentenceDuration = duration;
        }

        public bool IsFinished()
        {
            return TimeServed >= SentenceDuration;
        }

        public float GetRemainingTime()
        {
            return Mathf.Max(0f, SentenceDuration - TimeServed);
        }

        public void TickServing(float deltaTime)
        {
            TimeServed += deltaTime;
        }
    }

    [Serializable]
    public class FineRecord
    {
        public string FineId;
        public string PlayerId;
        public FineCategory Category;
        public float Amount;
        public float WantedLevelMultiplier;
        public bool IsPaid;
        public float Timestamp;
        public string CrimeId;

        public FineRecord()
        {
            FineId = Guid.NewGuid().ToString("N").Substring(0, 8);
            Timestamp = Time.time;
            WantedLevelMultiplier = 1f;
        }

        public FineRecord(string playerId, FineCategory category, float amount, string crimeId, float starMultiplier) : this()
        {
            PlayerId = playerId;
            Category = category;
            Amount = amount;
            CrimeId = crimeId;
            WantedLevelMultiplier = starMultiplier;
        }

        public float GetTotalAmount()
        {
            return Amount * WantedLevelMultiplier;
        }

        public void MarkPaid()
        {
            IsPaid = true;
        }
    }

    [Serializable]
    public class PoliceUnitState
    {
        public string UnitId;
        public PoliceState CurrentState;
        public string CurrentDispatchCallId;
        public string PursuitTargetId;
        public Vector3 LastKnownTargetPosition;
        public float StateTimer;
        public float DecisionTimer;
        public bool IsAvailable;

        public PoliceUnitState()
        {
            CurrentState = PoliceState.Idle;
            IsAvailable = true;
        }

        public PoliceUnitState(string unitId) : this()
        {
            UnitId = unitId;
        }
    }
}
