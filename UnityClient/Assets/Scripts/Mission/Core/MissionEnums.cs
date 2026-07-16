namespace RideVerse.Mission.Core
{
    public enum MissionType
    {
        Story,
        Side,
        Daily,
        Weekly,
        Delivery,
        Racing,
        Police,
        Business,
        Treasure,
        Tutorial,
        RandomEvent,
        Achievement,
        Special
    }

    public enum MissionState
    {
        Locked,
        Available,
        Accepted,
        InProgress,
        Paused,
        Completed,
        Failed,
        Cancelled
    }

    public enum MissionDifficulty
    {
        Easy,
        Normal,
        Hard,
        Expert,
        Legendary
    }

    public enum ObjectiveType
    {
        ReachCheckpoint,
        CollectItem,
        EliminateTarget,
        DeliverItem,
        SurviveTime,
        RaceFinish,
        EscortNPC,
        GatherIntel,
        TriggerEvent,
        Custom
    }

    public enum ObjectiveState
    {
        Inactive,
        Active,
        Completed,
        Failed
    }

    public enum CheckpointType
    {
        Start,
        Intermediate,
        Final,
        Vehicle,
        Dialogue,
        Cutscene
    }

    public enum RewardType
    {
        Cash,
        Experience,
        VehiclePart,
        Weapon,
        Ammo,
        VehiclePaint,
        Skin,
        Property,
        Business,
        Item
    }

    public enum FailureReason
    {
        None,
        TimeExpired,
        VehicleDestroyed,
        PlayerDefeated,
        LeftMissionArea,
        ObjectiveFailed,
        PlayerCancelled,
        ScriptedFailure
    }

    public enum DialogueSpeakerType
    {
        Player,
        NPC,
        Narrator,
        System
    }

    public enum CutsceneActionType
    {
        CameraMove,
        FadeIn,
        FadeOut,
        Dialogue,
        Wait,
        SpawnEntity,
        Teleport,
        TriggerEvent
    }

    public enum TriggerZoneShape
    {
        Box,
        Sphere,
        Capsule
    }

    public enum MissionMarkerType
    {
        Start,
        Checkpoint,
        Objective,
        Destination,
        Optional,
        Waypoint
    }

    public enum DailyMissionReset
    {
        None,
        Daily,
        Weekly,
        Monthly
    }

    public enum AchievementTriggerType
    {
        MissionCompleted,
        MissionsCompletedCount,
        TotalCashEarned,
        TotalDistanceTraveled,
        TimePlayed,
        StreakDays,
        DailyMissionCompleted,
        SideMissionCompleted,
        StoryProgress
    }
}
