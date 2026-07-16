using System;

namespace RideVerse.NPC.Core
{
    [Serializable]
    public class NPCData
    {
        public string Id;
        public string DisplayName;
        public int ProfessionTypeIndex;
        public float SpawnPositionX;
        public float SpawnPositionY;
        public float SpawnPositionZ;
        public float SpawnRotationY;
        public int DistrictIndex;

        public NPCData()
        {
            Id = Guid.NewGuid().ToString("N").Substring(0, 8);
            DisplayName = "Citizen";
        }

        public NPCData(string id, string name, int profession, UnityEngine.Vector3 position, float rotation, int district) : this()
        {
            Id = id;
            DisplayName = name;
            ProfessionTypeIndex = profession;
            SpawnPositionX = position.x;
            SpawnPositionY = position.y;
            SpawnPositionZ = position.z;
            SpawnRotationY = rotation;
            DistrictIndex = district;
        }

        public UnityEngine.Vector3 GetSpawnPosition() => new UnityEngine.Vector3(SpawnPositionX, SpawnPositionY, SpawnPositionZ);
    }
}
