using UnityEngine;

namespace RideVerse.Mission.Core
{
    [CreateAssetMenu(fileName = "MissionConfig", menuName = "RideVerse/Mission Config")]
    public class MissionConfig : ScriptableObject
    {
        [Header("General")]
        public int maxActiveMissions = 10;
        public int maxCompletedMissions = 100;
        public float missionPickupRange = 5f;
        public float objectiveUpdateInterval = 0.5f;

        [Header("Difficulty Multipliers")]
        public float easyRewardMultiplier = 1f;
        public float normalRewardMultiplier = 1.5f;
        public float hardRewardMultiplier = 2.5f;
        public float expertRewardMultiplier = 4f;
        public float legendaryRewardMultiplier = 7f;

        [Header("Difficulty Time Limits")]
        public float easyTimeMultiplier = 1.5f;
        public float normalTimeMultiplier = 1f;
        public float hardTimeMultiplier = 0.75f;
        public float expertTimeMultiplier = 0.5f;
        public float legendaryTimeMultiplier = 0.35f;

        [Header("Experience")]
        public int baseExpEasy = 50;
        public int baseExpNormal = 100;
        public int baseExpHard = 250;
        public int baseExpExpert = 500;
        public int baseExpLegendary = 1000;

        [Header("Timer")]
        public float defaultTimeLimit = 300f;
        public float warningTimeThreshold = 30f;
        public float timerTickInterval = 1f;

        [Header("Checkpoints")]
        public float checkpointRadius = 10f;
        public float checkpointReachDistance = 5f;
        public int maxCheckpoints = 20;
        public bool showCheckpointOnMinimap = true;

        [Header("Objectives")]
        public int maxObjectivesPerMission = 10;
        public float objectiveProgressSaveInterval = 5f;

        [Header("Dialogue")]
        public float dialogueTextSpeed = 0.03f;
        public float dialogueAutoAdvanceDelay = 3f;
        public int maxDialogueOptions = 4;

        [Header("Cutscene")]
        public float defaultFadeDuration = 1f;
        public float defaultCameraMoveDuration = 2f;
        public float defaultCutsceneWaitDuration = 1f;

        [Header("Markers")]
        public float markerUpdateInterval = 0.5f;
        public float markerPulseSpeed = 2f;
        public float markerMinimapScale = 1f;
        public Color missionStartColor = Color.yellow;
        public Color missionCheckpointColor = Color.cyan;
        public Color missionObjectiveColor = Color.red;
        public Color missionDestinationColor = Color.green;
        public Color missionWaypointColor = Color.white;

        [Header("Trigger Zones")]
        public float defaultTriggerRadius = 10f;
        public float triggerCheckInterval = 0.25f;
        public bool requireVehicleForVehicleZone = false;

        [Header("Tutorial")]
        public float tutorialHighlightDuration = 3f;
        public float tutorialStepDelay = 2f;
        public int maxTutorialHints = 5;

        [Header("Side Missions")]
        public int maxSideMissionsPerDay = 10;
        public float sideMissionCooldown = 60f;
        public float sideMissionCooldownReductionPerLevel = 2f;

        [Header("Daily Missions")]
        public int dailyMissionCount = 3;
        public int dailyStreakBonusMultiplier = 50;
        public int maxDailyStreak = 30;
        public float dailyResetHour = 0f;

        [Header("Random Events")]
        public float randomEventBaseChance = 0.1f;
        public float randomEventCooldown = 300f;
        public float randomEventRadius = 200f;
        public int maxConcurrentRandomEvents = 2;

        [Header("Save/Load")]
        public float autoSaveInterval = 30f;
        public int maxSaveSlots = 3;
        public bool saveOnMissionComplete = true;
        public bool saveOnMissionFail = true;

        [Header("Performance")]
        public int maxMarkerPoolSize = 50;
        public int maxTriggerZonePoolSize = 30;
        public float lodDistanceClose = 50f;
        public float lodDistanceMedium = 150f;
        public float lodDistanceFar = 300f;
        public int maxObjectsPerFrame = 5;

        [Header("Retry")]
        public int maxRetries = 3;
        public float retryCooldown = 5f;
        public bool retryRespawnAtCheckpoint = true;
        public bool retryRestoreHealth = true;
        public bool retryResetTimer = true;
    }
}
