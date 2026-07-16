using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.World.Core
{
    [Serializable]
    public class WorldSaveData
    {
        public string WorldId;
        public long SaveTimestamp;
        public PlayerSpawnData PlayerData;
        public List<PlacedBuildingData> PlacedBuildings;
        public List<PlacedEnvironmentData> PlacedEnvironment;
        public WorldSettingsData Settings;

        public WorldSaveData()
        {
            PlacedBuildings = new List<PlacedBuildingData>();
            PlacedEnvironment = new List<PlacedEnvironmentData>();
            Settings = new WorldSettingsData();
        }
    }

    [Serializable]
    public class PlayerSpawnData
    {
        public float PositionX;
        public float PositionY;
        public float PositionZ;
        public float RotationY;

        public Vector3 GetPosition() => new Vector3(PositionX, PositionY, PositionZ);

        public void SetPosition(Vector3 pos)
        {
            PositionX = pos.x;
            PositionY = pos.y;
            PositionZ = pos.z;
        }
    }

    [Serializable]
    public class PlacedBuildingData
    {
        public string Id;
        public int BuildingTypeIndex;
        public float PositionX;
        public float PositionY;
        public float PositionZ;
        public float RotationY;
        public float ScaleX;
        public float ScaleY;
        public float ScaleZ;
        public int ChunkX;
        public int ChunkZ;

        public Vector3 GetPosition() => new Vector3(PositionX, PositionY, PositionZ);
        public Vector3 GetScale() => new Vector3(ScaleX, ScaleY, ScaleZ);

        public void SetPosition(Vector3 pos)
        {
            PositionX = pos.x;
            PositionY = pos.y;
            PositionZ = pos.z;
        }

        public void SetScale(Vector3 scale)
        {
            ScaleX = scale.x;
            ScaleY = scale.y;
            ScaleZ = scale.z;
        }
    }

    [Serializable]
    public class PlacedEnvironmentData
    {
        public string Id;
        public int EnvironmentTypeIndex;
        public float PositionX;
        public float PositionY;
        public float PositionZ;
        public float RotationY;
        public int ChunkX;
        public int ChunkZ;

        public Vector3 GetPosition() => new Vector3(PositionX, PositionY, PositionZ);

        public void SetPosition(Vector3 pos)
        {
            PositionX = pos.x;
            PositionY = pos.y;
            PositionZ = pos.z;
        }
    }

    [Serializable]
    public class WorldSettingsData
    {
        public float Gravity = -9.81f;
        public float FogDensity = 0.01f;
        public float FogStartDistance = 50f;
        public float FogEndDistance = 500f;
        public float AmbientIntensity = 1f;
        public float SunIntensity = 1.2f;
        public float SunAngle = 50f;
        public int SkyboxIndex = 0;
    }
}
