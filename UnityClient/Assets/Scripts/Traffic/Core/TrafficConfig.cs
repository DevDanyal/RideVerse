using UnityEngine;

namespace RideVerse.Traffic.Core
{
    [CreateAssetMenu(fileName = "TrafficConfig", menuName = "RideVerse/Traffic/TrafficConfig")]
    public class TrafficConfig : ScriptableObject
    {
        [Header("Spawn Limits")]
        public int maxTrafficVehicles = 50;
        public int maxTrafficPerDistrict = 15;
        public float spawnRadius = 200f;
        public float despawnRadius = 300f;
        public float playerSpawnBuffer = 30f;

        [Header("Speed")]
        public float defaultMaxSpeed = 50f;
        public float highwayMaxSpeed = 90f;
        public float residentialMaxSpeed = 30f;
        public float urbanMaxSpeed = 50f;
        public float parkingSpeed = 10f;
        public float emergencyBrakeDeceleration = 15f;
        public float normalDeceleration = 6f;
        public float smoothAcceleration = 4f;

        [Header("Lane")]
        public float laneWidth = 3.5f;
        public float laneChangeDuration = 3f;
        public float laneChangeMinGap = 20f;
        public float laneOffsetTolerance = 0.5f;

        [Header("Overtake")]
        public float overtakeDetectionRange = 40f;
        public float overtakeSpeedBoost = 15f;
        public float overtakeMinGap = 15f;
        public float overtakeReturnDistance = 30f;
        public float overtakeMaxDuration = 10f;

        [Header("Traffic Lights")]
        public float trafficLightDetectRange = 50f;
        public float yellowLightDecisionSpeed = 30f;
        public float stopAtLightBuffer = 2f;

        [Header("Stop Signs")]
        public float stopSignDetectRange = 30f;
        public float stopDuration = 2f;
        public float stopSignApproachSpeed = 15f;

        [Header("Roundabouts")]
        public float roundaboutEntrySpeed = 20f;
        public float roundaboutCirculatingSpeed = 15f;
        public float roundaboutYieldRange = 10f;

        [Header("Parking")]
        public float parkingDetectRange = 40f;
        public float parkingSpotWidth = 3f;
        public float parkingSpotDepth = 5f;
        public float parkingApproachSpeed = 8f;
        public float parkingManeuverSpeed = 3f;

        [Header("Collision Avoidance")]
        public float frontDetectionRange = 30f;
        public float sideDetectionRange = 8f;
        public float rearDetectionRange = 15f;
        public float minFollowDistance = 5f;
        public float emergencyStopDistance = 3f;
        public float pedestrianDetectionRange = 20f;

        [Header("Speed Limits")]
        public float schoolZoneSpeed = 20f;
        public float constructionZoneSpeed = 15f;

        [Header("Density")]
        public float densityUpdateInterval = 5f;
        public float rushHourMorningStart = 7f;
        public float rushHourMorningEnd = 9.5f;
        public float rushHourEveningStart = 16.5f;
        public float rushHourEveningEnd = 19f;
        public int rushHourMultiplier = 2;
        public float nightReductionFactor = 0.4f;

        [Header("Weather Effects")]
        public float rainSpeedMultiplier = 0.75f;
        public float heavyRainSpeedMultiplier = 0.55f;
        public float fogSpeedMultiplier = 0.6f;
        public float stormSpeedMultiplier = 0.4f;
        public float snowSpeedMultiplier = 0.45f;
        public float rainBrakeMultiplier = 1.3f;
        public float fogVisibilityRange = 50f;

        [Header("Public Transport")]
        public int maxBuses = 8;
        public float busStopDuration = 8f;
        public int maxTaxis = 12;
        public float taxiCruiseSpeed = 40f;
        public float taxiSearchRadius = 100f;

        [Header("Emergency")]
        public float emergencyVehicleSpeed = 70f;
        public float emergencyYieldDistance = 50f;
        public float emergencyPriorityDuration = 8f;

        [Header("Incidents")]
        public float incidentCheckInterval = 10f;
        public float minorCrashDuration = 15f;
        public float majorCrashDuration = 30f;
        public float breakdownDuration = 25f;
        public float incidentSpawnChance = 0.02f;

        [Header("Performance")]
        public float lodDistanceFull = 60f;
        public float lodDistanceSimplified = 150f;
        public float lodDistanceCulled = 250f;
        public float aiUpdateIntervalFull = 0.1f;
        public float aiUpdateIntervalSimplified = 0.5f;
        public float aiUpdateIntervalCulled = 2f;
        public int maxUpdatesPerFrame = 10;
    }
}
