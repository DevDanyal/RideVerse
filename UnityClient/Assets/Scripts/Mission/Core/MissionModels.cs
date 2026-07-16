using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    [Serializable]
    public class MissionData
    {
        public string MissionId;
        public string MissionName;
        public string MissionDescription;
        public MissionType Type;
        public MissionDifficulty Difficulty;
        public MissionState State;
        public int RequiredLevel;
        public string RequiredVehicleId;
        public float TimeLimit;
        public float ElapsedTime;
        public int RetryCount;
        public int MaxRetries;
        public int RewardCash;
        public int RewardExperience;
        public List<MissionRewardEntry> BonusRewards;
        public List<MissionCheckpointData> Checkpoints;
        public List<MissionObjectiveData> Objectives;
        public List<MissionDialogueLine> DialogueLines;
        public List<MissionCutsceneEvent> CutsceneEvents;
        public List<string> UnlockedMissionIds;
        public string ParentMissionId;
        public bool IsRequiredForStory;
        public DateTime AcceptedTime;
        public DateTime CompletedTime;
        public DateTime LastSaveTime;

        public MissionData()
        {
            MissionId = Guid.NewGuid().ToString("N").Substring(0, 8);
            State = MissionState.Locked;
            BonusRewards = new List<MissionRewardEntry>();
            Checkpoints = new List<MissionCheckpointData>();
            Objectives = new List<MissionObjectiveData>();
            DialogueLines = new List<MissionDialogueLine>();
            CutsceneEvents = new List<MissionCutsceneEvent>();
            UnlockedMissionIds = new List<string>();
            MaxRetries = 3;
        }

        public MissionData(string missionId, string name, MissionType type, MissionDifficulty difficulty)
            : this()
        {
            MissionId = missionId;
            MissionName = name;
            Type = type;
            Difficulty = difficulty;
        }

        public float GetTimeRemaining() => Mathf.Max(0f, TimeLimit - ElapsedTime);
        public bool IsTimed => TimeLimit > 0f;
        public bool AreAllObjectivesComplete()
        {
            foreach (var obj in Objectives)
            {
                if (obj.State != ObjectiveState.Completed) return false;
            }
            return Objectives.Count > 0;
        }
        public bool HasFailedObjectives()
        {
            foreach (var obj in Objectives)
            {
                if (obj.State == ObjectiveState.Failed) return true;
            }
            return false;
        }
        public int CompletedObjectiveCount()
        {
            int count = 0;
            foreach (var obj in Objectives)
            {
                if (obj.State == ObjectiveState.Completed) count++;
            }
            return count;
        }
        public float ObjectiveProgress()
        {
            if (Objectives.Count == 0) return 0f;
            return (float)CompletedObjectiveCount() / Objectives.Count;
        }
    }

    [Serializable]
    public class MissionCheckpointData
    {
        public string CheckpointId;
        public CheckpointType Type;
        public Vector3 Position;
        public float Radius;
        public int Order;
        public bool IsReached;
        public string DialogueId;
        public string CutsceneId;

        public MissionCheckpointData()
        {
            CheckpointId = Guid.NewGuid().ToString("N").Substring(0, 8);
            Radius = 10f;
        }

        public MissionCheckpointData(CheckpointType type, Vector3 position, int order) : this()
        {
            Type = type;
            Position = position;
            Order = order;
        }
    }

    [Serializable]
    public class MissionObjectiveData
    {
        public string ObjectiveId;
        public string Description;
        public ObjectiveType Type;
        public ObjectiveState State;
        public Vector3 TargetPosition;
        public float TargetRadius;
        public int RequiredCount;
        public int CurrentCount;
        public bool IsOptional;
        public string TargetEntityId;
        public Dictionary<string, string> CustomData;

        public MissionObjectiveData()
        {
            ObjectiveId = Guid.NewGuid().ToString("N").Substring(0, 8);
            State = ObjectiveState.Inactive;
            TargetRadius = 10f;
            CustomData = new Dictionary<string, string>();
        }

        public MissionObjectiveData(string description, ObjectiveType type, Vector3 target, int requiredCount = 1)
            : this()
        {
            Description = description;
            Type = type;
            TargetPosition = target;
            RequiredCount = requiredCount;
        }

        public float Progress => RequiredCount > 0 ? (float)CurrentCount / RequiredCount : 0f;
        public bool IsComplete => CurrentCount >= RequiredCount;
    }

    [Serializable]
    public class MissionRewardEntry
    {
        public RewardType Type;
        public int Amount;
        public string ItemId;
        public string ItemName;
    }

    [Serializable]
    public class MissionDialogueLine
    {
        public string LineId;
        public string SpeakerName;
        public DialogueSpeakerType SpeakerType;
        public string Text;
        public float DisplayDuration;
        public int Order;
        public bool Skippable;

        public MissionDialogueLine()
        {
            LineId = Guid.NewGuid().ToString("N").Substring(0, 8);
            DisplayDuration = 3f;
            Skippable = true;
        }

        public MissionDialogueLine(string speaker, DialogueSpeakerType type, string text, int order) : this()
        {
            SpeakerName = speaker;
            SpeakerType = type;
            Text = text;
            Order = order;
        }
    }

    [Serializable]
    public class MissionCutsceneEvent
    {
        public string EventId;
        public CutsceneActionType ActionType;
        public float Duration;
        public int Order;
        public string TargetId;
        public Vector3 TargetPosition;
        public string DialogueText;

        public MissionCutsceneEvent()
        {
            EventId = Guid.NewGuid().ToString("N").Substring(0, 8);
        }
    }

    [Serializable]
    public class MissionSaveData
    {
        public string PlayerId;
        public List<MissionData> ActiveMissions;
        public List<MissionData> CompletedMissions;
        public List<MissionData> FailedMissions;
        public int TotalMissionsCompleted;
        public int TotalMissionsFailed;
        public int TotalCashEarned;
        public int TotalExperienceEarned;
        public int DailyStreak;
        public string LastDailyResetDate;
        public DateTime LastSaveTime;

        public MissionSaveData()
        {
            ActiveMissions = new List<MissionData>();
            CompletedMissions = new List<MissionData>();
            FailedMissions = new List<MissionData>();
            LastSaveTime = DateTime.UtcNow;
        }
    }

    [Serializable]
    public class DailyMissionTemplate
    {
        public string TemplateId;
        public string MissionName;
        public string MissionDescription;
        public MissionType Type;
        public MissionDifficulty Difficulty;
        public int RewardCash;
        public int RewardExperience;
        public float TimeLimit;
        public List<MissionObjectiveData> Objectives;

        public DailyMissionTemplate()
        {
            TemplateId = Guid.NewGuid().ToString("N").Substring(0, 8);
            Objectives = new List<MissionObjectiveData>();
        }
    }

    [Serializable]
    public class RandomEventTemplate
    {
        public string EventId;
        public string EventName;
        public string Description;
        public MissionType Type;
        public MissionDifficulty Difficulty;
        public float SpawnChance;
        public float Cooldown;
        public Vector3 SpawnCenter;
        public float SpawnRadius;
        public List<MissionObjectiveData> Objectives;
        public List<MissionRewardEntry> Rewards;

        public RandomEventTemplate()
        {
            EventId = Guid.NewGuid().ToString("N").Substring(0, 8);
            SpawnChance = 0.1f;
            Cooldown = 300f;
            SpawnRadius = 100f;
            Objectives = new List<MissionObjectiveData>();
            Rewards = new List<MissionRewardEntry>();
        }
    }

    [Serializable]
    public class AchievementDefinition
    {
        public string AchievementId;
        public string Name;
        public string Description;
        public AchievementTriggerType TriggerType;
        public int RequiredValue;
        public int RewardCash;
        public int RewardExperience;
        public bool IsUnlocked;

        public AchievementDefinition()
        {
            AchievementId = Guid.NewGuid().ToString("N").Substring(0, 8);
        }
    }

    [Serializable]
    public class MissionProgressSnapshot
    {
        public string MissionId;
        public MissionState State;
        public float ElapsedTime;
        public int CompletedObjectives;
        public int TotalObjectives;
        public int CurrentCheckpoint;
        public int TotalCheckpoints;
        public int RetryCount;
        public DateTime Timestamp;

        public float CompletionPercentage => TotalObjectives > 0 ? (float)CompletedObjectives / TotalObjectives * 100f : 0f;
    }

    [Serializable]
    public class TriggerZoneData
    {
        public string ZoneId;
        public TriggerZoneShape Shape;
        public Vector3 Center;
        public Vector3 Size;
        public float Radius;
        public float Height;
        public string AssociatedMissionId;
        public string AssociatedObjectiveId;
        public bool IsActive;
        public bool RequireVehicle;

        public TriggerZoneData()
        {
            ZoneId = Guid.NewGuid().ToString("N").Substring(0, 8);
            IsActive = true;
            Shape = TriggerZoneShape.Sphere;
            Radius = 10f;
        }
    }

    [Serializable]
    public class MissionMarkerData
    {
        public string MarkerId;
        public MissionMarkerType Type;
        public Vector3 WorldPosition;
        public string Label;
        public Color MarkerColor;
        public float PulseSpeed;
        public bool IsVisible;
        public string AssociatedMissionId;

        public MissionMarkerData()
        {
            MarkerId = Guid.NewGuid().ToString("N").Substring(0, 8);
            IsVisible = true;
            PulseSpeed = 2f;
        }
    }

    [Serializable]
    public class MissionStats
    {
        public int TotalMissionsStarted;
        public int TotalMissionsCompleted;
        public int TotalMissionsFailed;
        public int TotalMissionsCancelled;
        public float TotalTimeSpent;
        public int TotalRetriesUsed;
        public int LongestMissionStreak;
        public int CurrentStreak;
        public int TotalCheckpointsReached;
        public int TotalObjectivesCompleted;

        public float CompletionRate => TotalMissionsStarted > 0 ? (float)TotalMissionsCompleted / TotalMissionsStarted * 100f : 0f;
        public float FailureRate => TotalMissionsStarted > 0 ? (float)TotalMissionsFailed / TotalMissionsStarted * 100f : 0f;
    }
}
