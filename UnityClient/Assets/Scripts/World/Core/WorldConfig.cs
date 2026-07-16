using UnityEngine;

namespace RideVerse.World.Core
{
    [CreateAssetMenu(fileName = "WorldConfig", menuName = "RideVerse/World/WorldConfig")]
    public class WorldConfig : ScriptableObject
    {
        [Header("World Identity")]
        public string worldId = "rideverse_city";
        public string worldName = "RideVerse City";

        [Header("World Size")]
        public int worldSizeX = 2000;
        public int worldSizeZ = 2000;

        [Header("Chunks")]
        public int chunkSize = 100;
        public int loadRadius = 3;
        public int unloadRadius = 5;

        [Header("Spawn")]
        public Vector3 defaultSpawnPoint = new Vector3(0f, 1f, 0f);
        public float defaultSpawnRotationY = 0f;

        [Header("Roads")]
        public float mainRoadWidth = 16f;
        public float smallRoadWidth = 8f;
        public float highwayWidth = 24f;
        public float sidewalkWidth = 2.5f;
        public float sidewalkHeight = 0.15f;

        [Header("Buildings")]
        public float minBuildingSpacing = 2f;
        public float buildingSetbackFromRoad = 3f;

        [Header("Streaming")]
        public float streamingUpdateInterval = 0.5f;
        public int maxChunksPerFrame = 2;

        [Header("Performance")]
        public int maxActiveObjects = 500;
        public float lodDistanceLow = 100f;
        public float lodDistanceMedium = 200f;
        public float lodDistanceHigh = 400f;

        public int ChunkCountX => Mathf.CeilToInt((float)worldSizeX / chunkSize);
        public int ChunkCountZ => Mathf.CeilToInt((float)worldSizeZ / chunkSize);
        public int TotalChunks => ChunkCountX * ChunkCountZ;
        public Vector3 WorldCenter => new Vector3(worldSizeX * 0.5f, 0f, worldSizeZ * 0.5f);
    }
}
