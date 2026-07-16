using UnityEngine;

namespace RideVerse.NPC.Core
{
    [CreateAssetMenu(fileName = "NPCConfig", menuName = "RideVerse/NPC/NPCConfig")]
    public class NPCConfig : ScriptableObject
    {
        [Header("Spawn Limits")]
        public int maxActiveNPCs = 30;
        public int maxNPCsPerDistrict = 10;
        public float spawnRadius = 200f;
        public float despawnRadius = 300f;

        [Header("Movement")]
        public float walkSpeed = 2f;
        public float runSpeed = 5f;
        public float vehicleSpeed = 30f;
        public float stoppingDistance = 1.5f;
        public float obstacleAvoidanceRadius = 2f;
        public float roadCrossingPause = 2f;

        [Header("Interaction")]
        public float interactionRange = 3f;
        public float conversationDistance = 2f;
        public float greetingRange = 5f;
        public float playerReactionRange = 10f;

        [Header("Schedule")]
        public float wakeUpHour = 6f;
        public float workStartHour = 8f;
        public float lunchHour = 12f;
        public float workEndHour = 17f;
        public float dinnerHour = 19f;
        public float sleepHour = 22f;
        public float timeScale = 60f;

        [Header("Performance")]
        public float lodDistanceFull = 50f;
        public float lodDistanceMedium = 100f;
        public float lodDistanceLow = 200f;
        public float updateIntervalFull = 0.1f;
        public float updateIntervalMedium = 0.5f;
        public float updateIntervalLow = 2f;
        public float updateIntervalCulled = 5f;

        [Header("Crowd")]
        public int maxGroupSize = 5;
        public float groupSpacing = 1.5f;
        public float groupFollowSpeed = 1.8f;

        [Header("Names")]
        public string[] maleNames = { "Ahmed", "Ali", "Hassan", "Hussein", "Omar", "Yusuf", "Ibrahim", "Khalid", "Tariq", "Majid" };
        public string[] femaleNames = { "Fatima", "Aisha", "Zainab", "Maryam", "Khadija", "Safiya", "Halima", "Nora", "Layla", "Yasmin" };
    }
}
