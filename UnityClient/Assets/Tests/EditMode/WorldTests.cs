using NUnit.Framework;
using UnityEngine;
using RideVerse.World.Core;
using RideVerse.World.Chunks;
using RideVerse.World.Districts;
using RideVerse.World.Layout;
using RideVerse.World.Buildings;
using RideVerse.World.Environment;
using RideVerse.World.Spawn;
using RideVerse.World.Minimap;
using RideVerse.World.Performance;
using RideVerse.World.Settings;
using RideVerse.World.Streaming;

[TestFixture]
public class ChunkCoordTests
{
    [Test]
    public void ChunkCoord_DefaultValues_AreZero()
    {
        var coord = new ChunkCoord();
        Assert.AreEqual(0, coord.X);
        Assert.AreEqual(0, coord.Z);
    }

    [Test]
    public void ChunkCoord_Constructor_SetsValues()
    {
        var coord = new ChunkCoord(5, 10);
        Assert.AreEqual(5, coord.X);
        Assert.AreEqual(10, coord.Z);
    }

    [Test]
    public void ChunkCoord_FromWorldPosition_CalculatesCorrectly()
    {
        var coord = ChunkCoord.FromWorldPosition(new Vector3(150f, 0f, 250f), 100);
        Assert.AreEqual(1, coord.X);
        Assert.AreEqual(2, coord.Z);
    }

    [Test]
    public void ChunkCoord_FromWorldPosition_NegativeValues()
    {
        var coord = ChunkCoord.FromWorldPosition(new Vector3(-50f, 0f, -150f), 100);
        Assert.AreEqual(-1, coord.X);
        Assert.AreEqual(-2, coord.Z);
    }

    [Test]
    public void ChunkCoord_ToWorldPosition_ReturnsCorrectPosition()
    {
        var coord = new ChunkCoord(3, 7);
        Vector3 pos = coord.ToWorldPosition(100);
        Assert.AreEqual(300f, pos.x);
        Assert.AreEqual(700f, pos.z);
    }

    [Test]
    public void ChunkCoord_GetWorldCenter_ReturnsCenter()
    {
        var coord = new ChunkCoord(2, 4);
        Vector3 center = coord.GetWorldCenter(100);
        Assert.AreEqual(250f, center.x);
        Assert.AreEqual(450f, center.z);
    }

    [Test]
    public void ChunkCoord_DistanceTo_CalculatesCorrectly()
    {
        var a = new ChunkCoord(0, 0);
        var b = new ChunkCoord(3, 4);
        Assert.AreEqual(5f, a.DistanceTo(b), 0.01f);
    }

    [Test]
    public void ChunkCoord_ManhattanDistanceTo_CalculatesCorrectly()
    {
        var a = new ChunkCoord(0, 0);
        var b = new ChunkCoord(3, 4);
        Assert.AreEqual(7, a.ManhattanDistanceTo(b));
    }

    [Test]
    public void ChunkCoord_Equality_Works()
    {
        var a = new ChunkCoord(5, 10);
        var b = new ChunkCoord(5, 10);
        var c = new ChunkCoord(5, 11);

        Assert.IsTrue(a == b);
        Assert.IsFalse(a == c);
        Assert.IsTrue(a != c);
        Assert.IsTrue(a.Equals(b));
    }

    [Test]
    public void ChunkCoord_GetHashCode_IsConsistent()
    {
        var a = new ChunkCoord(5, 10);
        var b = new ChunkCoord(5, 10);
        Assert.AreEqual(a.GetHashCode(), b.GetHashCode());
    }

    [Test]
    public void ChunkCoord_ToString_FormatsCorrectly()
    {
        var coord = new ChunkCoord(3, 7);
        Assert.AreEqual("(3, 7)", coord.ToString());
    }
}

[TestFixture]
public class WorldConfigTests
{
    [Test]
    public void WorldConfig_DefaultValues_AreValid()
    {
        var config = ScriptableObject.CreateInstance<WorldConfig>();

        Assert.IsFalse(string.IsNullOrEmpty(config.worldId));
        Assert.IsFalse(string.IsNullOrEmpty(config.worldName));
        Assert.Greater(config.worldSizeX, 0);
        Assert.Greater(config.worldSizeZ, 0);
        Assert.Greater(config.chunkSize, 0);
        Assert.Greater(config.loadRadius, 0);
        Assert.Greater(config.unloadRadius, config.loadRadius);
        Assert.Greater(config.mainRoadWidth, 0f);
        Assert.Greater(config.smallRoadWidth, 0f);
        Assert.Greater(config.highwayWidth, 0f);

        Object.DestroyImmediate(config);
    }

    [Test]
    public void WorldConfig_ChunkCountX_CalculatesCorrectly()
    {
        var config = ScriptableObject.CreateInstance<WorldConfig>();
        config.worldSizeX = 1000;
        config.chunkSize = 100;
        Assert.AreEqual(10, config.ChunkCountX);
        Object.DestroyImmediate(config);
    }

    [Test]
    public void WorldConfig_TotalChunks_CalculatesCorrectly()
    {
        var config = ScriptableObject.CreateInstance<WorldConfig>();
        config.worldSizeX = 1000;
        config.worldSizeZ = 2000;
        config.chunkSize = 100;
        Assert.AreEqual(200, config.TotalChunks);
        Object.DestroyImmediate(config);
    }

    [Test]
    public void WorldConfig_WorldCenter_ReturnsCenter()
    {
        var config = ScriptableObject.CreateInstance<WorldConfig>();
        config.worldSizeX = 2000;
        config.worldSizeZ = 2000;
        Vector3 center = config.WorldCenter;
        Assert.AreEqual(1000f, center.x);
        Assert.AreEqual(1000f, center.z);
        Object.DestroyImmediate(config);
    }

    [Test]
    public void WorldConfig_LODDistances_AreOrdered()
    {
        var config = ScriptableObject.CreateInstance<WorldConfig>();
        Assert.Less(config.lodDistanceLow, config.lodDistanceMedium);
        Assert.Less(config.lodDistanceMedium, config.lodDistanceHigh);
        Object.DestroyImmediate(config);
    }
}

[TestFixture]
public class DistrictTests
{
    [Test]
    public void District_Constructor_SetsProperties()
    {
        var district = new District(DistrictType.Downtown, new Vector3(100f, 0f, 200f), 400f, 400f);

        Assert.AreEqual(DistrictType.Downtown, district.Type);
        Assert.AreEqual(400f, district.Width);
        Assert.AreEqual(400f, district.Depth);
        Assert.AreEqual("Downtown", district.Name);
        Assert.IsFalse(string.IsNullOrEmpty(district.Id));
    }

    [Test]
    public void District_ContainsPosition_InsideDistrict()
    {
        var district = new District(DistrictType.Residential, new Vector3(100f, 0f, 100f), 200f, 200f);

        Assert.IsTrue(district.ContainsPosition(new Vector3(100f, 5f, 100f)));
        Assert.IsTrue(district.ContainsPosition(new Vector3(50f, 0f, 50f)));
    }

    [Test]
    public void District_ContainsPosition_OutsideDistrict()
    {
        var district = new District(DistrictType.Residential, new Vector3(100f, 0f, 100f), 200f, 200f);

        Assert.IsFalse(district.ContainsPosition(new Vector3(300f, 0f, 300f)));
        Assert.IsFalse(district.ContainsPosition(new Vector3(-100f, 0f, -100f)));
    }

    [Test]
    public void District_GetBounds_ReturnsCorrectBounds()
    {
        var district = new District(DistrictType.Commercial, new Vector3(50f, 0f, 50f), 100f, 100f);
        Bounds bounds = district.GetBounds();

        Assert.AreEqual(50f, bounds.center.x);
        Assert.AreEqual(5f, bounds.center.y);
        Assert.AreEqual(100f, bounds.size.x);
        Assert.AreEqual(100f, bounds.size.z);
    }

    [Test]
    public void District_GetColorForType_ReturnsUniqueColors()
    {
        Color downtown = District.GetColorForType(DistrictType.Downtown);
        Color residential = District.GetColorForType(DistrictType.Residential);
        Color industrial = District.GetColorForType(DistrictType.Industrial);
        Color commercial = District.GetColorForType(DistrictType.Commercial);
        Color countryside = District.GetColorForType(DistrictType.Countryside);

        Assert.AreNotEqual(downtown, residential);
        Assert.AreNotEqual(residential, industrial);
        Assert.AreNotEqual(industrial, commercial);
        Assert.AreNotEqual(commercial, countryside);
    }
}

[TestFixture]
public class RoadDataTests
{
    [Test]
    public void RoadSegment_Constructor_SetsProperties()
    {
        var road = new RoadSegment(RoadType.MainRoad,
            new Vector3(0f, 0f, 0f),
            new Vector3(100f, 0f, 0f),
            16f, 4);

        Assert.AreEqual(RoadType.MainRoad, road.Type);
        Assert.AreEqual(16f, road.Width);
        Assert.AreEqual(4, road.Lanes);
        Assert.AreEqual(100f, road.Length, 0.1f);
        Assert.IsFalse(string.IsNullOrEmpty(road.Id));
    }

    [Test]
    public void RoadSegment_Direction_CalculatesCorrectly()
    {
        var road = new RoadSegment(RoadType.SmallRoad,
            Vector3.zero,
            new Vector3(0f, 0f, 100f),
            8f);

        Vector3 dir = road.Direction;
        Assert.AreEqual(0f, dir.x, 0.01f);
        Assert.AreEqual(1f, dir.z, 0.01f);
    }

    [Test]
    public void RoadSegment_Center_CalculatesCorrectly()
    {
        var road = new RoadSegment(RoadType.Highway,
            new Vector3(0f, 0f, 0f),
            new Vector3(100f, 0f, 100f),
            24f);

        Vector3 center = road.Center;
        Assert.AreEqual(50f, center.x);
        Assert.AreEqual(50f, center.z);
    }

    [Test]
    public void Intersection_Constructor_SetsProperties()
    {
        var intersection = new Intersection(new Vector3(50f, 0f, 50f), 16f, 4, true);

        Assert.AreEqual(16f, intersection.Size);
        Assert.AreEqual(4, intersection.ConnectedRoadCount);
        Assert.IsTrue(intersection.HasTrafficLight);
    }

    [Test]
    public void Bridge_Constructor_SetsProperties()
    {
        var bridge = new Bridge(
            new Vector3(0f, 2f, 0f),
            new Vector3(60f, 2f, 0f),
            24f, 4f, 3f);

        Assert.AreEqual(60f, bridge.Length, 0.1f);
        Assert.AreEqual(24f, bridge.Width);
        Assert.AreEqual(4f, bridge.Height);
        Assert.AreEqual(3f, bridge.DeckHeight);
    }
}

[TestFixture]
public class BuildingDataTests
{
    [Test]
    public void BuildingData_DefaultConstructor_GeneratesId()
    {
        var building = new BuildingData();
        Assert.IsFalse(string.IsNullOrEmpty(building.Id));
        Assert.AreEqual(8, building.Id.Length);
    }

    [Test]
    public void BuildingData_ParameterizedConstructor_SetsProperties()
    {
        var building = new BuildingData(
            BuildingType.Hospital,
            new Vector3(100f, 0f, 200f),
            90f,
            new Vector3(25f, 10f, 25f),
            DistrictType.Downtown);

        Assert.AreEqual(BuildingType.Hospital, building.Type);
        Assert.AreEqual(100f, building.Position.x);
        Assert.AreEqual(200f, building.Position.z);
        Assert.AreEqual(90f, building.RotationY);
        Assert.AreEqual(25f, building.Scale.x);
        Assert.AreEqual(DistrictType.Downtown, building.District);
    }

    [Test]
    public void BuildingData_Position_StoresCorrectly()
    {
        var building = new BuildingData();
        building.Position = new Vector3(10f, 20f, 30f);
        Assert.AreEqual(10f, building.Position.x);
        Assert.AreEqual(20f, building.Position.y);
        Assert.AreEqual(30f, building.Position.z);
    }

    [Test]
    public void BuildingData_Scale_StoresCorrectly()
    {
        var building = new BuildingData();
        building.Scale = new Vector3(5f, 10f, 15f);
        Assert.AreEqual(5f, building.Scale.x);
        Assert.AreEqual(10f, building.Scale.y);
        Assert.AreEqual(15f, building.Scale.z);
    }
}

[TestFixture]
public class SpawnPointTests
{
    [Test]
    public void SpawnPoint_DefaultConstructor_SetsDefaults()
    {
        var spawn = new SpawnPoint();
        Assert.IsTrue(spawn.IsActive);
        Assert.IsFalse(string.IsNullOrEmpty(spawn.Id));
    }

    [Test]
    public void SpawnPoint_ParameterizedConstructor_SetsProperties()
    {
        var spawn = new SpawnPoint(SpawnType.Vehicle, new Vector3(10f, 0f, 20f), 90f);

        Assert.AreEqual(SpawnType.Vehicle, spawn.Type);
        Assert.AreEqual(10f, spawn.Position.x);
        Assert.AreEqual(20f, spawn.Position.z);
        Assert.AreEqual(90f, spawn.RotationY);
        Assert.IsTrue(spawn.IsActive);
    }

    [Test]
    public void SpawnPoint_GetRotation_ReturnsCorrectQuaternion()
    {
        var spawn = new SpawnPoint(SpawnType.Player, Vector3.zero, 180f);
        Quaternion rot = spawn.GetRotation();
        Assert.AreEqual(180f, rot.eulerAngles.y, 0.1f);
    }

    [Test]
    public void SpawnPoint_SetPosition_UpdatesValues()
    {
        var spawn = new SpawnPoint();
        spawn.Position = new Vector3(5f, 10f, 15f);
        Assert.AreEqual(5f, spawn.Position.x);
        Assert.AreEqual(10f, spawn.Position.y);
        Assert.AreEqual(15f, spawn.Position.z);
    }
}

[TestFixture]
public class WorldSaveDataTests
{
    [Test]
    public void WorldSaveData_DefaultConstructor_InitializesLists()
    {
        var data = new WorldSaveData();
        Assert.IsNotNull(data.PlacedBuildings);
        Assert.IsNotNull(data.PlacedEnvironment);
        Assert.IsNotNull(data.Settings);
        Assert.AreEqual(0, data.PlacedBuildings.Count);
        Assert.AreEqual(0, data.PlacedEnvironment.Count);
    }

    [Test]
    public void PlayerSpawnData_GetSetPosition_Works()
    {
        var data = new PlayerSpawnData();
        data.SetPosition(new Vector3(10f, 20f, 30f));

        Vector3 pos = data.GetPosition();
        Assert.AreEqual(10f, pos.x);
        Assert.AreEqual(20f, pos.y);
        Assert.AreEqual(30f, pos.z);
    }

    [Test]
    public void PlacedBuildingData_GetSetPosition_Works()
    {
        var data = new PlacedBuildingData();
        data.SetPosition(new Vector3(100f, 50f, 200f));

        Vector3 pos = data.GetPosition();
        Assert.AreEqual(100f, pos.x);
        Assert.AreEqual(50f, pos.y);
        Assert.AreEqual(200f, pos.z);
    }

    [Test]
    public void PlacedBuildingData_GetSetScale_Works()
    {
        var data = new PlacedBuildingData();
        data.SetScale(new Vector3(10f, 20f, 30f));

        Vector3 scale = data.GetScale();
        Assert.AreEqual(10f, scale.x);
        Assert.AreEqual(20f, scale.y);
        Assert.AreEqual(30f, scale.z);
    }

    [Test]
    public void WorldSettingsData_DefaultValues_AreValid()
    {
        var settings = new WorldSettingsData();
        Assert.AreEqual(-9.81f, settings.Gravity, 0.01f);
        Assert.Greater(settings.FogDensity, 0f);
        Assert.Greater(settings.FogEndDistance, settings.FogStartDistance);
        Assert.Greater(settings.SunIntensity, 0f);
    }

    [Test]
    public void WorldSaveData_Serialization_Works()
    {
        var data = new WorldSaveData
        {
            WorldId = "test_world",
            SaveTimestamp = 1234567890
        };
        data.PlacedBuildings.Add(new PlacedBuildingData
        {
            Id = "b1",
            BuildingTypeIndex = 0,
            PositionX = 10f,
            PositionY = 0f,
            PositionZ = 20f
        });

        string json = JsonUtility.ToJson(data);
        var deserialized = JsonUtility.FromJson<WorldSaveData>(json);

        Assert.AreEqual("test_world", deserialized.WorldId);
        Assert.AreEqual(1, deserialized.PlacedBuildings.Count);
        Assert.AreEqual("b1", deserialized.PlacedBuildings[0].Id);
    }
}

[TestFixture]
public class WorldSettingsTests
{
    [Test]
    public void WorldSettings_DefaultValues_AreValid()
    {
        var settings = ScriptableObject.CreateInstance<WorldSettings>();

        Assert.AreEqual(-9.81f, settings.gravity, 0.01f);
        Assert.IsTrue(settings.fogEnabled);
        Assert.Greater(settings.fogDensity, 0f);
        Assert.Greater(settings.ambientIntensity, 0f);
        Assert.Greater(settings.sunIntensity, 0f);

        Object.DestroyImmediate(settings);
    }

    [Test]
    public void WorldSettings_ToSaveData_ConvertsCorrectly()
    {
        var settings = ScriptableObject.CreateInstance<WorldSettings>();
        settings.gravity = -10f;
        settings.fogDensity = 0.01f;
        settings.sunIntensity = 1.5f;

        var saveData = settings.ToSaveData();
        Assert.AreEqual(-10f, saveData.Gravity, 0.01f);
        Assert.AreEqual(0.01f, saveData.FogDensity, 0.001f);
        Assert.AreEqual(1.5f, saveData.SunIntensity, 0.01f);

        Object.DestroyImmediate(settings);
    }

    [Test]
    public void WorldSettings_LoadFromSaveData_UpdatesValues()
    {
        var settings = ScriptableObject.CreateInstance<WorldSettings>();
        var saveData = new WorldSettingsData
        {
            Gravity = -15f,
            FogDensity = 0.02f,
            SunIntensity = 2f,
            SunAngle = 60f
        };

        settings.LoadFromSaveData(saveData);
        Assert.AreEqual(-15f, settings.gravity, 0.01f);
        Assert.AreEqual(0.02f, settings.fogDensity, 0.001f);
        Assert.AreEqual(2f, settings.sunIntensity, 0.01f);
        Assert.AreEqual(60f, settings.sunAngle, 0.01f);

        Object.DestroyImmediate(settings);
    }

    [Test]
    public void WorldSettings_LoadFromSaveData_Null_DoesNotCrash()
    {
        var settings = ScriptableObject.CreateInstance<WorldSettings>();
        settings.LoadFromSaveData(null);
        Assert.AreEqual(-9.81f, settings.gravity, 0.01f);
        Object.DestroyImmediate(settings);
    }
}

[TestFixture]
public class ObjectPoolTests
{
    private GameObject _poolPrefab;
    private GameObject _poolRoot;

    [SetUp]
    public void PoolSetUp()
    {
        _poolPrefab = new GameObject("PoolPrefab");
        _poolRoot = new GameObject("PoolRoot");
    }

    [TearDown]
    public void PoolTearDown()
    {
        Object.DestroyImmediate(_poolPrefab);
        Object.DestroyImmediate(_poolRoot);
        _poolPrefab = null;
        _poolRoot = null;
    }

    [Test]
    public void ObjectPool_AvailableCount_ReflectsPrewarm()
    {
        var pool = new GameObjectPool(_poolPrefab, _poolRoot.transform, 5);

        Assert.AreEqual(5, pool.AvailableCount);
        Assert.AreEqual(5, pool.TotalCount);

        pool.Clear();
    }

    [Test]
    public void ObjectPool_Get_ReturnsActiveObject()
    {
        var pool = new GameObjectPool(_poolPrefab, _poolRoot.transform, 3);

        var obj = pool.Get();
        Assert.IsNotNull(obj);
        Assert.IsTrue(obj.activeSelf);
        Assert.AreEqual(2, pool.AvailableCount);

        pool.Clear();
    }

    [Test]
    public void ObjectPool_Return_MakesObjectAvailable()
    {
        var pool = new GameObjectPool(_poolPrefab, _poolRoot.transform, 2);

        var obj = pool.Get();
        pool.Return(obj);
        Assert.AreEqual(2, pool.AvailableCount);

        pool.Clear();
    }

    [Test]
    public void ObjectPool_ReturnAll_ResetsAllObjects()
    {
        var pool = new GameObjectPool(_poolPrefab, _poolRoot.transform, 3);

        pool.Get();
        pool.Get();
        pool.ReturnAll();
        Assert.AreEqual(3, pool.AvailableCount);

        pool.Clear();
    }
}

[TestFixture]
public class EnumTests
{
    [Test]
    public void DistrictType_HasAllValues()
    {
        Assert.AreEqual(5, System.Enum.GetValues(typeof(DistrictType)).Length);
    }

    [Test]
    public void RoadType_HasAllValues()
    {
        Assert.AreEqual(6, System.Enum.GetValues(typeof(RoadType)).Length);
    }

    [Test]
    public void BuildingType_HasAllValues()
    {
        Assert.AreEqual(9, System.Enum.GetValues(typeof(BuildingType)).Length);
    }

    [Test]
    public void EnvironmentType_HasAllValues()
    {
        Assert.AreEqual(8, System.Enum.GetValues(typeof(EnvironmentType)).Length);
    }

    [Test]
    public void SpawnType_HasAllValues()
    {
        Assert.AreEqual(3, System.Enum.GetValues(typeof(SpawnType)).Length);
    }

    [Test]
    public void LODLevel_HasAllValues()
    {
        Assert.AreEqual(4, System.Enum.GetValues(typeof(LODLevel)).Length);
    }

    [Test]
    public void MinimapIconType_HasAllValues()
    {
        Assert.AreEqual(10, System.Enum.GetValues(typeof(MinimapIconType)).Length);
    }
}

[TestFixture]
public class MinimapIconEntryTests
{
    [Test]
    public void MinimapIconEntry_DefaultValues_AreValid()
    {
        var entry = new MinimapIconEntry();
        Assert.AreEqual(Vector3.zero, entry.WorldPosition);
    }

    [Test]
    public void MinimapIconEntry_CanSetProperties()
    {
        var entry = new MinimapIconEntry
        {
            Id = "player_1",
            Type = MinimapIconType.Player,
            WorldPosition = new Vector3(10f, 0f, 20f),
            Color = Color.red
        };

        Assert.AreEqual("player_1", entry.Id);
        Assert.AreEqual(MinimapIconType.Player, entry.Type);
        Assert.AreEqual(10f, entry.WorldPosition.x);
        Assert.AreEqual(Color.red, entry.Color);
    }
}

[TestFixture]
public class TrafficLightStateTests
{
    [Test]
    public void TrafficLightState_HasAllValues()
    {
        Assert.AreEqual(3, System.Enum.GetValues(typeof(TrafficLightState)).Length);
    }

    [Test]
    public void TrafficLightState_CanCompare()
    {
        Assert.IsTrue(TrafficLightState.Red != TrafficLightState.Green);
        Assert.IsFalse(TrafficLightState.Red == TrafficLightState.Green);
    }
}

[TestFixture]
public class PerformanceStatsTests
{
    [Test]
    public void PerformanceStats_DefaultValues_AreZero()
    {
        var stats = new PerformanceStats();
        Assert.AreEqual(0, stats.FrameRate);
        Assert.AreEqual(0, stats.MemoryUsed);
        Assert.AreEqual(0, stats.ActiveObjects);
    }
}
