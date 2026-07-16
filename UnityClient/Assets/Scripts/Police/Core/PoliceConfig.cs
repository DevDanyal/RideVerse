using UnityEngine;

namespace RideVerse.Police.Core
{
    [CreateAssetMenu(fileName = "PoliceConfig", menuName = "RideVerse/Police/PoliceConfig")]
    public class PoliceConfig : ScriptableObject
    {
        [Header("Spawn Limits")]
        public int maxPoliceUnits = 20;
        public int maxPolicePerDistrict = 6;
        public float spawnRadius = 250f;
        public float despawnRadius = 350f;
        public float playerSpawnBuffer = 40f;

        [Header("Patrol")]
        public float patrolSpeed = 35f;
        public float patrolWaypointReachDistance = 8f;
        public float patrolRouteLength = 200f;
        public int patrolWaypointsPerRoute = 6;
        public float patrolIdleTimeAtWaypoint = 3f;
        public float patrolLookAroundRange = 30f;
        public float patrolRouteRegenerateInterval = 120f;

        [Header("Crime Detection")]
        public float crimeDetectionRange = 50f;
        public float speedingToleranceKmh = 10f;
        public float dangerousDrivingAngleThreshold = 60f;
        public float hitAndRunDetectionRange = 30f;
        public float weaponDetectionRange = 25f;
        public float assaultDetectionRange = 40f;
        public float crimeVerificationDelay = 0.5f;
        public int maxCrimeWitnesses = 5;

        [Header("Wanted Level")]
        public float wantedLevelDecayTime = 30f;
        public float wantedLevelDecayMultiplier = 0.5f;
        public float wantedLevelIncreaseCooldown = 2f;
        public int[] wantedLevelCrimeThresholds = { 0, 1, 3, 6, 10, 15, 20 };
        public int maxWantedLevel = 6;
        public float wantedLevel5RequiredCrimes = 15f;

        [Header("Dispatch")]
        public float dispatchResponseTime = 2f;
        public int maxActiveDispatchCalls = 10;
        public float dispatchCallExpiryTime = 60f;
        public float dispatchRadiusLowPriority = 200f;
        public float dispatchRadiusHighPriority = 100f;
        public float dispatchRadiusCritical = 50f;

        [Header("Vehicle Pursuit")]
        public float pursuitMaxSpeed = 70f;
        public float pursuitCatchUpSpeed = 80f;
        public float pursuitRamDamage = 20f;
        public float pursuitSpikeStripSlowdown = 0.3f;
        public float pursuitLostSightTime = 8f;
        public float pursuitMaxDuration = 120f;
        public float pursuitBackupCallInterval = 15f;
        public float pursuitPITManeuverAngle = 30f;
        public float pursuitPITManeuverMinSpeed = 20f;
        public float pursuitPITManeuverMaxSpeed = 60f;
        public float pursuitMinDistanceToCallPIT = 5f;

        [Header("Foot Pursuit")]
        public float footPursuitSpeed = 8f;
        public float footPursuitSprintSpeed = 12f;
        public float footPursuitCatchDistance = 2f;
        public float footPursuitMaxDuration = 60f;
        public float footPursuitTaserRange = 15f;
        public float footPursuitTaserCooldown = 5f;
        public float footPursuitLostSightTime = 6f;

        [Header("Roadblocks")]
        public int maxActiveRoadblocks = 3;
        public float roadblockSetupTime = 3f;
        public float roadblockEffectivenessRadius = 20f;
        public int roadblockMinUnitsRequired = 2;
        public float roadblockDeployDistanceAhead = 100f;
        public float roadblockDeployMinDistance = 50f;
        public float spikeStripLength = 8f;
        public float spikeStripSlowdownDuration = 5f;
        public float spikeStripDamageAmount = 30f;

        [Header("Arrest")]
        public float arrestRange = 3f;
        public float arrestHandcuffTime = 2f;
        public float arrestResistanceTimer = 5f;
        public float arrestSurrenderChance = 0.3f;
        public float arrestEscapeDistance = 10f;
        public float arrestCooldown = 10f;

        [Header("Jail")]
        public float jailSentenceShort = 30f;
        public float jailSentenceMedium = 60f;
        public float jailSentenceLong = 120f;
        public float jailSentenceExtended = 300f;
        public float jailRespawnDelay = 3f;
        public bool jailInventoryConfiscate = false;

        [Header("Fine")]
        public float fineSpeeding = 100f;
        public float fineDangerousDriving = 250f;
        public float fineHitAndRun = 500f;
        public float fineVehicleTheft = 1000f;
        public float finePropertyDamage = 750f;
        public float fineWeaponViolation = 800f;
        public float fineAssault = 1500f;
        public float fineRobbery = 2000f;
        public float fineRacing = 1200f;
        public float finePoliceAssault = 3000f;
        public float fineMurder = 5000f;
        public float fineMultiplierPerStar = 1.5f;

        [Header("Evidence")]
        public int maxEvidencePerCrime = 10;
        public float evidenceExpiryTime = 300f;
        public float witnessReportDelay = 2f;
        public int maxActiveEvidenceEntries = 50;

        [Header("Radio")]
        public float radioMessageLifetime = 15f;
        public float radioBackupResponseTime = 3f;
        public int maxRadioMessages = 20;
        public float radioChatterMinInterval = 5f;
        public float radioChatterMaxInterval = 15f;

        [Header("Backup")]
        public int maxBackupUnits = 4;
        public float backupArrivalTime = 5f;
        public float backupSearchRadius = 100f;
        public int swatMinWantedLevel = 5;
        public int swatMaxUnits = 6;

        [Header("SWAT")]
        public float swatResponseTime = 10f;
        public float swatHelicopterArrivalTime = 15f;
        public float swatArrestRange = 4f;
        public float swatHealthMultiplier = 2f;
        public float swatDamageMultiplier = 1.5f;

        [Header("Helicopter")]
        public float helicopterAltitude = 50f;
        public float helicopterSpeed = 40f;
        public float helicopterSearchRadius = 100f;
        public float helicopterSpotlightRange = 60f;
        public float helicopterMinWantedLevel = 4;

        [Header("AI Behavior")]
        public float aiUpdateInterval = 0.3f;
        public float aiFullUpdateInterval = 0.1f;
        public float aiSimplifiedUpdateInterval = 0.5f;
        public float aiCulledUpdateInterval = 2f;
        public float aiDecisionCooldown = 1f;
        public float aiInvestigationDuration = 10f;
        public float aiSearchDuration = 15f;
        public float aiSearchRadius = 50f;

        [Header("Performance")]
        public float lodDistanceFull = 60f;
        public float lodDistanceSimplified = 150f;
        public float lodDistanceCulled = 250f;
        public int maxUpdatesPerFrame = 5;
        public float cleanupInterval = 10f;

        [Header("Unit Types")]
        public float patrolCarMaxSpeed = 65f;
        public float patrolBikeMaxSpeed = 55f;
        public float suvMaxSpeed = 60f;
        public float unmarkedCarMaxSpeed = 70f;
        public float swatVanMaxSpeed = 50f;
        public float helicopterMaxSpeed = 45f;
        public float k9UnitFootSpeed = 10f;
    }
}
