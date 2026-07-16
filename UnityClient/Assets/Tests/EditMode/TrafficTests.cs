using NUnit.Framework;
using UnityEngine;
using RideVerse.Traffic.Core;
using RideVerse.Traffic.AI;
using RideVerse.Traffic.Navigation;
using RideVerse.Traffic.Behaviors;
using RideVerse.Traffic.Rules;
using RideVerse.Traffic.Parking;
using RideVerse.Traffic.Emergency;
using RideVerse.Traffic.Conditions;
using RideVerse.Traffic.PublicTransport;
using RideVerse.Traffic.Incidents;
using RideVerse.Traffic.Performance;

[TestFixture]
public class TrafficEnumTests
{
    [Test]
    public void TrafficVehicleType_HasAllValues()
    {
        Assert.AreEqual(14, System.Enum.GetValues(typeof(TrafficVehicleType)).Length);
    }

    [Test]
    public void TrafficAIBehaviorState_HasAllValues()
    {
        Assert.AreEqual(18, System.Enum.GetValues(typeof(TrafficAIBehaviorState)).Length);
    }

    [Test]
    public void LanePosition_HasAllValues()
    {
        Assert.AreEqual(3, System.Enum.GetValues(typeof(LanePosition)).Length);
    }

    [Test]
    public void ParkingState_HasAllValues()
    {
        Assert.AreEqual(6, System.Enum.GetValues(typeof(ParkingState)).Length);
    }

    [Test]
    public void EmergencyType_HasAllValues()
    {
        Assert.AreEqual(4, System.Enum.GetValues(typeof(EmergencyType)).Length);
    }

    [Test]
    public void TrafficDensityLevel_HasAllValues()
    {
        Assert.AreEqual(6, System.Enum.GetValues(typeof(TrafficDensityLevel)).Length);
    }

    [Test]
    public void WeatherCondition_HasAllValues()
    {
        Assert.AreEqual(6, System.Enum.GetValues(typeof(WeatherCondition)).Length);
    }

    [Test]
    public void TimeOfDay_HasAllValues()
    {
        Assert.AreEqual(6, System.Enum.GetValues(typeof(TimeOfDay)).Length);
    }

    [Test]
    public void IncidentType_HasAllValues()
    {
        Assert.AreEqual(6, System.Enum.GetValues(typeof(IncidentType)).Length);
    }

    [Test]
    public void TrafficVehicleLOD_HasAllValues()
    {
        Assert.AreEqual(3, System.Enum.GetValues(typeof(TrafficVehicleLOD)).Length);
    }
}

[TestFixture]
public class TrafficConfigTests
{
    [Test]
    public void TrafficConfig_DefaultValues_AreValid()
    {
        var config = ScriptableObject.CreateInstance<TrafficConfig>();

        Assert.Greater(config.maxTrafficVehicles, 0);
        Assert.Greater(config.spawnRadius, 0f);
        Assert.Greater(config.despawnRadius, config.spawnRadius);
        Assert.Greater(config.defaultMaxSpeed, 0f);
        Assert.Greater(config.laneWidth, 0f);
        Assert.Greater(config.normalDeceleration, 0f);
        Assert.Greater(config.emergencyBrakeDeceleration, config.normalDeceleration);
        Assert.Greater(config.smoothAcceleration, 0f);
        Assert.Greater(config.frontDetectionRange, 0f);
        Assert.Greater(config.minFollowDistance, 0f);
        Assert.Greater(config.emergencyStopDistance, 0f);
        Assert.Greater(config.trafficLightDetectRange, 0f);
        Assert.Greater(config.stopSignDetectRange, 0f);
        Assert.Greater(config.stopDuration, 0f);
        Assert.Greater(config.roundaboutEntrySpeed, 0f);
        Assert.Greater(config.parkingDetectRange, 0f);
        Assert.Greater(config.maxBuses, 0);
        Assert.Greater(config.maxTaxis, 0);
        Assert.Greater(config.emergencyVehicleSpeed, 0f);
        Assert.Greater(config.emergencyYieldDistance, 0f);
        Assert.Greater(config.maxUpdatesPerFrame, 0);

        Object.DestroyImmediate(config);
    }

    [Test]
    public void TrafficConfig_WeatherMultipliers_AreLessThanOne()
    {
        var config = ScriptableObject.CreateInstance<TrafficConfig>();

        Assert.Less(config.rainSpeedMultiplier, 1f);
        Assert.Less(config.heavyRainSpeedMultiplier, config.rainSpeedMultiplier);
        Assert.Less(config.fogSpeedMultiplier, 1f);
        Assert.Less(config.stormSpeedMultiplier, config.fogSpeedMultiplier);
        Assert.Less(config.snowSpeedMultiplier, 1f);
        Assert.Greater(config.rainBrakeMultiplier, 1f);

        Object.DestroyImmediate(config);
    }

    [Test]
    public void TrafficConfig_RushHourTimes_AreValid()
    {
        var config = ScriptableObject.CreateInstance<TrafficConfig>();

        Assert.Greater(config.rushHourMorningEnd, config.rushHourMorningStart);
        Assert.Greater(config.rushHourEveningEnd, config.rushHourEveningStart);
        Assert.Greater(config.rushHourMultiplier, 1);
        Assert.Less(config.nightReductionFactor, 1f);

        Object.DestroyImmediate(config);
    }
}

[TestFixture]
public class TrafficVehicleTests
{
    private GameObject _testObj;
    private TrafficVehicle _vehicle;

    [SetUp]
    public void SetUp()
    {
        _testObj = new GameObject("TestTrafficVehicle");
        _vehicle = _testObj.AddComponent<TrafficVehicle>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_testObj);
    }

    [Test]
    public void TrafficVehicle_Initialize_SetsProperties()
    {
        _vehicle.Initialize("TV001", TrafficVehicleType.Sedan, new Vector3(10, 0, 20), 45f, 55f);

        Assert.AreEqual("TV001", _vehicle.VehicleId);
        Assert.AreEqual(TrafficVehicleType.Sedan, _vehicle.VehicleType);
        Assert.AreEqual(55f, _vehicle.MaxSpeed);
        Assert.AreEqual(0f, _vehicle.CurrentSpeed);
        Assert.IsTrue(_vehicle.IsActive);
        Assert.IsFalse(_vehicle.IsEmergency);
    }

    [Test]
    public void TrafficVehicle_SetTargetSpeed_ClampsToMax()
    {
        _vehicle.Initialize("TV002", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        _vehicle.SetTargetSpeed(100f);
        Assert.AreEqual(50f, _vehicle.TargetSpeed);

        _vehicle.SetTargetSpeed(-10f);
        Assert.AreEqual(0f, _vehicle.TargetSpeed);
    }

    [Test]
    public void TrafficVehicle_SetCurrentSpeed_ClampsToZero()
    {
        _vehicle.Initialize("TV003", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        _vehicle.SetCurrentSpeed(-10f);
        Assert.AreEqual(0f, _vehicle.CurrentSpeed);
    }

    [Test]
    public void TrafficVehicle_Stop_SetsSpeedToZero()
    {
        _vehicle.Initialize("TV004", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        _vehicle.SetCurrentSpeed(30f);
        _vehicle.Stop();
        Assert.AreEqual(0f, _vehicle.CurrentSpeed);
        Assert.AreEqual(0f, _vehicle.TargetSpeed);
    }

    [Test]
    public void TrafficVehicle_DistanceTo_ReturnsCorrectDistance()
    {
        _vehicle.Initialize("TV005", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        float dist = _vehicle.DistanceTo(new Vector3(3, 4, 0));
        Assert.AreEqual(5f, dist, 0.01f);
    }

    [Test]
    public void TrafficVehicle_DistanceAlongForward_ReturnsPositiveAhead()
    {
        _vehicle.Initialize("TV006", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        _vehicle.transform.forward = Vector3.forward;
        float dist = _vehicle.DistanceAlongForward(new Vector3(0, 0, 10));
        Assert.Greater(dist, 0f);
        Assert.AreEqual(10f, dist, 0.01f);
    }

    [Test]
    public void TrafficVehicle_DistanceAlongForward_ReturnsNegativeBehind()
    {
        _vehicle.Initialize("TV007", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        _vehicle.transform.forward = Vector3.forward;
        float dist = _vehicle.DistanceAlongForward(new Vector3(0, 0, -10));
        Assert.Less(dist, 0f);
    }

    [Test]
    public void TrafficVehicle_SetEmergency_UpdatesProperties()
    {
        _vehicle.Initialize("TV008", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        _vehicle.SetEmergency(true, EmergencyType.Ambulance);
        Assert.IsTrue(_vehicle.IsEmergency);
        Assert.AreEqual(EmergencyType.Ambulance, _vehicle.EmergencyType);
    }

    [Test]
    public void TrafficVehicle_SetBehaviorState_UpdatesState()
    {
        _vehicle.Initialize("TV009", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        _vehicle.SetBehaviorState(TrafficAIBehaviorState.Cruising);
        Assert.AreEqual(TrafficAIBehaviorState.Cruising, _vehicle.BehaviorState);
    }

    [Test]
    public void TrafficVehicle_SetLODLevel_UpdatesLevel()
    {
        _vehicle.Initialize("TV010", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        _vehicle.SetLODLevel(TrafficVehicleLOD.Simplified);
        Assert.AreEqual(TrafficVehicleLOD.Simplified, _vehicle.LODLevel);
    }

    [Test]
    public void TrafficVehicle_Motorcycle_HasSmallDimensions()
    {
        _vehicle.Initialize("TV011", TrafficVehicleType.Motorcycle, Vector3.zero, 0f, 45f);
        Assert.Less(_vehicle.Mass, 500f);
        Assert.Less(_vehicle.Length, 3f);
        Assert.Less(_vehicle.Width, 1.5f);
    }

    [Test]
    public void TrafficVehicle_Bus_HasLargeDimensions()
    {
        _vehicle.Initialize("TV012", TrafficVehicleType.Bus, Vector3.zero, 0f, 40f);
        Assert.Greater(_vehicle.Mass, 5000f);
        Assert.Greater(_vehicle.Length, 8f);
    }
}

[TestFixture]
public class RoadNetworkTests
{
    [Test]
    public void RoadNetwork_AddNode_IncreasesCount()
    {
        var network = new RoadNetwork();
        network.AddNode(Vector3.zero);
        Assert.AreEqual(1, network.NodeCount);
    }

    [Test]
    public void RoadNetwork_AddEdge_IncreasesCount()
    {
        var network = new RoadNetwork();
        var n1 = network.AddNode(Vector3.zero);
        var n2 = network.AddNode(Vector3.forward * 10f);
        network.AddEdge(n1, n2);
        Assert.AreEqual(1, network.EdgeCount);
    }

    [Test]
    public void RoadNetwork_AddEdge_CreatesBidirectionalLinks()
    {
        var network = new RoadNetwork();
        var n1 = network.AddNode(Vector3.zero);
        var n2 = network.AddNode(Vector3.forward * 10f);
        network.AddEdge(n1, n2);
        network.AddEdge(n2, n1);

        Assert.AreEqual(1, n1.OutgoingEdges.Count);
        Assert.AreEqual(1, n1.IncomingEdges.Count);
        Assert.AreEqual(1, n2.OutgoingEdges.Count);
        Assert.AreEqual(1, n2.IncomingEdges.Count);
    }

    [Test]
    public void RoadNetwork_GetNearestNode_FindsClosest()
    {
        var network = new RoadNetwork();
        var n1 = network.AddNode(new Vector3(0, 0, 0));
        var n2 = network.AddNode(new Vector3(100, 0, 100));
        var n3 = network.AddNode(new Vector3(5, 0, 5));

        var nearest = network.GetNearestNode(new Vector3(3, 0, 3));
        Assert.AreEqual(n3.Id, nearest.Id);
    }

    [Test]
    public void RoadNetwork_GetNodesInRadius_ReturnsCorrectNodes()
    {
        var network = new RoadNetwork();
        network.AddNode(new Vector3(0, 0, 0));
        network.AddNode(new Vector3(5, 0, 0));
        network.AddNode(new Vector3(50, 0, 50));

        var inRadius = network.GetNodesInRadius(Vector3.zero, 10f);
        Assert.AreEqual(2, inRadius.Count);
    }

    [Test]
    public void RoadNetwork_GenerateGridNetwork_CreatesNodesAndEdges()
    {
        var network = new RoadNetwork();
        network.GenerateGridNetwork(Vector3.zero, 3, 3, 50f, 50f, 30f);

        Assert.Greater(network.NodeCount, 0);
        Assert.Greater(network.EdgeCount, 0);
        Assert.AreEqual(16, network.NodeCount);
    }

    [Test]
    public void RoadNetwork_Clear_ResetsEverything()
    {
        var network = new RoadNetwork();
        network.AddNode(Vector3.zero);
        network.AddNode(Vector3.forward * 10f);
        network.Clear();

        Assert.AreEqual(0, network.NodeCount);
        Assert.AreEqual(0, network.EdgeCount);
    }

    [Test]
    public void RoadNode_DistanceTo_ReturnsCorrectDistance()
    {
        var n1 = new RoadNode("1", Vector3.zero);
        var n2 = new RoadNode("2", new Vector3(3, 4, 0));
        Assert.AreEqual(5f, n1.DistanceTo(n2), 0.01f);
    }

    [Test]
    public void RoadEdge_GetDirection_ReturnsNormalized()
    {
        var n1 = new RoadNode("1", Vector3.zero);
        var n2 = new RoadNode("2", new Vector3(0, 0, 10));
        var edge = new RoadEdge(n1, n2);

        Vector3 dir = edge.GetDirection();
        Assert.AreEqual(0f, dir.x, 0.01f);
        Assert.AreEqual(0f, dir.y, 0.01f);
        Assert.AreEqual(1f, dir.z, 0.01f);
    }

    [Test]
    public void RoadEdge_GetLaneOffset_ReturnsCorrectOffset()
    {
        var n1 = new RoadNode("1", Vector3.zero);
        var n2 = new RoadNode("2", new Vector3(0, 0, 10));
        var edge = new RoadEdge(n1, n2, 3, 50f);

        Vector3 offset0 = edge.GetLaneOffset(0, 3.5f);
        Vector3 offset1 = edge.GetLaneOffset(1, 3.5f);
        Vector3 offset2 = edge.GetLaneOffset(2, 3.5f);

        Assert.AreNotEqual(offset0, offset2);
        Assert.AreEqual(Vector3.zero, offset1, "Center lane should have zero offset");
    }
}

[TestFixture]
public class TrafficPathfinderTests
{
    [Test]
    public void TrafficPathfinder_FindPath_ReturnsPath()
    {
        var network = new RoadNetwork();
        network.GenerateGridNetwork(Vector3.zero, 5, 5, 50f, 50f, 30f);

        var pathfinder = new TrafficPathfinder(network);
        var path = pathfinder.FindPath(Vector3.zero, new Vector3(200, 0, 200));

        Assert.IsNotNull(path);
        Assert.Greater(path.Count, 0);
    }

    [Test]
    public void TrafficPathfinder_FindPath_StartEqualsEnd_ReturnsShortPath()
    {
        var network = new RoadNetwork();
        network.GenerateGridNetwork(Vector3.zero, 5, 5, 50f, 50f, 30f);

        var pathfinder = new TrafficPathfinder(network);
        var path = pathfinder.FindPath(Vector3.zero, Vector3.zero);

        Assert.IsNotNull(path);
        Assert.GreaterOrEqual(path.Count, 1);
    }

    [Test]
    public void TrafficPathfinder_GetCurrentEdge_FindsNearestEdge()
    {
        var network = new RoadNetwork();
        var n1 = network.AddNode(Vector3.zero);
        var n2 = network.AddNode(new Vector3(0, 0, 100));
        network.AddEdge(n1, n2);

        var pathfinder = new TrafficPathfinder(network);
        var edge = pathfinder.GetCurrentEdge(new Vector3(0, 0, 50));

        Assert.IsNotNull(edge);
    }
}

[TestFixture]
public class BehaviorTreeTests
{
    [Test]
    public void BTCondition_ReturnsSuccess_WhenTrue()
    {
        var node = new BTCondition(() => true);
        Assert.AreEqual(BTNodeStatus.Success, node.Evaluate());
    }

    [Test]
    public void BTCondition_ReturnsFailure_WhenFalse()
    {
        var node = new BTCondition(() => false);
        Assert.AreEqual(BTNodeStatus.Failure, node.Evaluate());
    }

    [Test]
    public void BTAction_ReturnsStatus_FromDelegate()
    {
        var node = new BTAction(() => BTNodeStatus.Running);
        Assert.AreEqual(BTNodeStatus.Running, node.Evaluate());
    }

    [Test]
    public void BTSequence_ReturnsSuccess_WhenAllSucceed()
    {
        var seq = new BTSequence(
            new BTCondition(() => true),
            new BTCondition(() => true));
        Assert.AreEqual(BTNodeStatus.Success, seq.Evaluate());
    }

    [Test]
    public void BTSequence_ReturnsFailure_WhenAnyFails()
    {
        var seq = new BTSequence(
            new BTCondition(() => true),
            new BTCondition(() => false),
            new BTCondition(() => true));
        Assert.AreEqual(BTNodeStatus.Failure, seq.Evaluate());
    }

    [Test]
    public void BTSelector_ReturnsSuccess_WhenAnySucceeds()
    {
        var sel = new BTSelector(
            new BTCondition(() => false),
            new BTCondition(() => true));
        Assert.AreEqual(BTNodeStatus.Success, sel.Evaluate());
    }

    [Test]
    public void BTSelector_ReturnsFailure_WhenAllFail()
    {
        var sel = new BTSelector(
            new BTCondition(() => false),
            new BTCondition(() => false));
        Assert.AreEqual(BTNodeStatus.Failure, sel.Evaluate());
    }

    [Test]
    public void BTSequence_Reset_ResetsIndex()
    {
        var seq = new BTSequence(
            new BTCondition(() => true),
            new BTCondition(() => false));
        seq.Evaluate();
        seq.Reset();
        Assert.AreEqual(BTNodeStatus.Failure, seq.Evaluate());
    }

    [Test]
    public void BTRepeater_RepeatsUntilMax()
    {
        int count = 0;
        var repeater = new BTRepeater(new BTAction(() => { count++; return BTNodeStatus.Success; }), 3);

        repeater.Evaluate();
        repeater.Evaluate();
        repeater.Evaluate();

        Assert.AreEqual(3, count);
    }

    [Test]
    public void BTRepeater_Reset_ResetsCount()
    {
        int count = 0;
        var repeater = new BTRepeater(new BTAction(() => { count++; return BTNodeStatus.Success; }), 2);

        repeater.Evaluate();
        repeater.Evaluate();
        repeater.Reset();
        repeater.Evaluate();

        Assert.AreEqual(3, count);
    }
}

[TestFixture]
public class SpeedControllerTests
{
    private GameObject _testObj;
    private TrafficVehicle _vehicle;
    private SpeedController _speedCtrl;
    private TrafficConfig _config;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<TrafficConfig>();
        _testObj = new GameObject("TestVehicle");
        _vehicle = _testObj.AddComponent<TrafficVehicle>();
        _vehicle.Initialize("SC001", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        _speedCtrl = _testObj.AddComponent<SpeedController>();
        _speedCtrl.Initialize(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
        Object.DestroyImmediate(_testObj);
    }

    [Test]
    public void SpeedController_CalculateSafeSpeedForWeather_Clear_ReturnsFullSpeed()
    {
        float speed = _speedCtrl.CalculateSafeSpeedForWeather(_vehicle, WeatherCondition.Clear);
        Assert.AreEqual(_vehicle.MaxSpeed, speed);
    }

    [Test]
    public void SpeedController_CalculateSafeSpeedForWeather_Rain_ReducesSpeed()
    {
        float speed = _speedCtrl.CalculateSafeSpeedForWeather(_vehicle, WeatherCondition.Rain);
        Assert.Less(speed, _vehicle.MaxSpeed);
    }

    [Test]
    public void SpeedController_CalculateSafeSpeedForWeather_Storm_ReducesMoreThanRain()
    {
        float rainSpeed = _speedCtrl.CalculateSafeSpeedForWeather(_vehicle, WeatherCondition.Rain);
        float stormSpeed = _speedCtrl.CalculateSafeSpeedForWeather(_vehicle, WeatherCondition.Storm);
        Assert.Less(stormSpeed, rainSpeed);
    }

    [Test]
    public void SpeedController_IsSpeedSafe_InRange_ReturnsTrue()
    {
        _vehicle.SetCurrentSpeed(25f);
        Assert.IsTrue(_speedCtrl.IsSpeedSafe(_vehicle, 20f, 30f));
    }

    [Test]
    public void SpeedController_IsSpeedSafe_OutOfRange_ReturnsFalse()
    {
        _vehicle.SetCurrentSpeed(35f);
        Assert.IsFalse(_speedCtrl.IsSpeedSafe(_vehicle, 20f, 30f));
    }
}

[TestFixture]
public class CollisionAvoidanceTests
{
    private GameObject _testObj;
    private TrafficVehicle _vehicle;
    private CollisionAvoidance _collision;
    private TrafficConfig _config;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<TrafficConfig>();
        _testObj = new GameObject("TestVehicle");
        _vehicle = _testObj.AddComponent<TrafficVehicle>();
        _vehicle.Initialize("CA001", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        _collision = _testObj.AddComponent<CollisionAvoidance>();
        _collision.Initialize(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
        Object.DestroyImmediate(_testObj);
    }

    [Test]
    public void CollisionAvoidance_DetectVehicleAhead_NoVehicle_ReturnsNull()
    {
        var result = _collision.DetectVehicleAhead(_vehicle);
        Assert.IsNull(result);
    }

    [Test]
    public void CollisionAvoidance_IsRoadBlocked_NoObstacle_ReturnsFalse()
    {
        Assert.IsFalse(_collision.IsRoadBlocked(_vehicle));
    }

    [Test]
    public void CollisionAvoidance_IsPedestrianAhead_None_ReturnsFalse()
    {
        Assert.IsFalse(_collision.IsPedestrianAhead(_vehicle));
    }

    [Test]
    public void CollisionAvoidance_DetectVehicleBehind_NoVehicle_ReturnsNull()
    {
        var result = _collision.DetectVehicleBehind(_vehicle);
        Assert.IsNull(result);
    }

    [Test]
    public void CollisionAvoidance_IsVehicleAlongside_NoVehicles_ReturnsFalse()
    {
        Assert.IsFalse(_collision.IsVehicleAlongside(_vehicle, 10f));
    }
}

[TestFixture]
public class EmergencySystemTests
{
    private GameObject _testObj;
    private EmergencySystem _emergencySystem;
    private TrafficConfig _config;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<TrafficConfig>();
        _testObj = new GameObject("EmergencySystemObj");
        _emergencySystem = _testObj.AddComponent<EmergencySystem>();
        _emergencySystem.Initialize(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
        Object.DestroyImmediate(_testObj);
    }

    [Test]
    public void EmergencySystem_ShouldYield_NoEmergency_ReturnsFalse()
    {
        var go = new GameObject("NormalVehicle");
        var vehicle = go.AddComponent<TrafficVehicle>();
        vehicle.Initialize("E001", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);

        Assert.IsFalse(_emergencySystem.ShouldYield(vehicle));

        Object.DestroyImmediate(go);
    }

    [Test]
    public void EmergencySystem_IsEmergencyNearby_NoEmergency_ReturnsFalse()
    {
        var go = new GameObject("NormalVehicle");
        var vehicle = go.AddComponent<TrafficVehicle>();
        vehicle.Initialize("E002", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);

        Assert.IsFalse(_emergencySystem.IsEmergencyNearby(vehicle));

        Object.DestroyImmediate(go);
    }

    [Test]
    public void EmergencySystem_GetNearestEmergencyVehicle_NoEmergency_ReturnsNull()
    {
        var result = _emergencySystem.GetNearestEmergencyVehicle(Vector3.zero);
        Assert.IsNull(result);
    }

    [Test]
    public void EmergencySystem_Cleanup_RemovesNullVehicles()
    {
        _emergencySystem.Cleanup();
        Assert.AreEqual(0, _emergencySystem.EmergencyVehicles.Count);
    }
}

[TestFixture]
public class TrafficDensityManagerTests
{
    private GameObject _testObj;
    private TrafficDensityManager _densityManager;
    private TrafficConfig _config;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<TrafficConfig>();
        _testObj = new GameObject("DensityManager");
        _densityManager = _testObj.AddComponent<TrafficDensityManager>();
        _densityManager.Initialize(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
        Object.DestroyImmediate(_testObj);
    }

    [Test]
    public void TrafficDensityManager_Initialize_SetsMediumDensity()
    {
        Assert.AreEqual(TrafficDensityLevel.Medium, _densityManager.CurrentDensity);
    }

    [Test]
    public void TrafficDensityManager_SetGameHour_RushHour_SetsRushHour()
    {
        _densityManager.SetGameHour(8f);
        _densityManager.UpdateTime(1f, 1f);
        Assert.IsTrue(_densityManager.IsRushHour);
    }

    [Test]
    public void TrafficDensityManager_SetGameHour_Night_ReducesDensity()
    {
        _densityManager.SetGameHour(2f);
        _densityManager.UpdateTime(1f, 1f);
        Assert.Less(_densityManager.DensityMultiplier, 1f);
    }

    [Test]
    public void TrafficDensityManager_GetTargetVehicleCount_ReturnsPositive()
    {
        Assert.Greater(_densityManager.GetTargetVehicleCount(), 0);
    }

    [Test]
    public void TrafficDensityManager_GetSpawnInterval_ReturnsPositive()
    {
        Assert.Greater(_densityManager.GetSpawnInterval(), 0f);
    }

    [Test]
    public void TrafficDensityManager_GetHeadlightIntensity_Night_ReturnsFull()
    {
        _densityManager.SetGameHour(23f);
        _densityManager.UpdateTime(1f, 1f);
        Assert.AreEqual(1f, _densityManager.GetHeadlightIntensity());
    }
}

[TestFixture]
public class WeatherDrivingEffectsTests
{
    private GameObject _testObj;
    private WeatherDrivingEffects _weatherEffects;
    private TrafficConfig _config;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<TrafficConfig>();
        _testObj = new GameObject("WeatherEffects");
        _weatherEffects = _testObj.AddComponent<WeatherDrivingEffects>();
        _weatherEffects.Initialize(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
        Object.DestroyImmediate(_testObj);
    }

    [Test]
    public void WeatherEffects_Initialize_DefaultsToClear()
    {
        Assert.AreEqual(WeatherCondition.Clear, _weatherEffects.CurrentWeather);
    }

    [Test]
    public void WeatherEffects_GetSpeedMultiplier_Clear_Returns1()
    {
        Assert.AreEqual(1f, _weatherEffects.GetSpeedMultiplier(), 0.01f);
    }

    [Test]
    public void WeatherEffects_GetSpeedMultiplier_Rain_Reduces()
    {
        _weatherEffects.SetWeather(WeatherCondition.Rain);
        _weatherEffects.UpdateWeather(10f);
        Assert.Less(_weatherEffects.GetSpeedMultiplier(), 1f);
    }

    [Test]
    public void WeatherEffects_GetBrakeMultiplier_Clear_Returns1()
    {
        Assert.AreEqual(1f, _weatherEffects.GetBrakeMultiplier(), 0.01f);
    }

    [Test]
    public void WeatherEffects_GetBrakeMultiplier_Rain_Increases()
    {
        _weatherEffects.SetWeather(WeatherCondition.Rain);
        _weatherEffects.UpdateWeather(10f);
        Assert.Greater(_weatherEffects.GetBrakeMultiplier(), 1f);
    }

    [Test]
    public void WeatherEffects_GetVisibilityRange_Clear_ReturnsMax()
    {
        Assert.AreEqual(float.MaxValue, _weatherEffects.GetVisibilityRange());
    }

    [Test]
    public void WeatherEffects_GetVisibilityRange_Fog_Reduces()
    {
        _weatherEffects.SetWeather(WeatherCondition.Fog);
        _weatherEffects.UpdateWeather(10f);
        Assert.Less(_weatherEffects.GetVisibilityRange(), float.MaxValue);
    }

    [Test]
    public void WeatherEffects_ShouldUseWipers_Clear_ReturnsFalse()
    {
        Assert.IsFalse(_weatherEffects.ShouldUseWipers());
    }

    [Test]
    public void WeatherEffects_ShouldUseWipers_Rain_ReturnsTrue()
    {
        _weatherEffects.SetWeather(WeatherCondition.Rain);
        _weatherEffects.UpdateWeather(10f);
        Assert.IsTrue(_weatherEffects.ShouldUseWipers());
    }

    [Test]
    public void WeatherEffects_GetTractionLossChance_Clear_ReturnsZero()
    {
        Assert.AreEqual(0f, _weatherEffects.GetTractionLossChance(), 0.01f);
    }

    [Test]
    public void WeatherEffects_GetTractionLossChance_Snow_ReturnsHigh()
    {
        _weatherEffects.SetWeather(WeatherCondition.Snow);
        _weatherEffects.UpdateWeather(10f);
        Assert.Greater(_weatherEffects.GetTractionLossChance(), 0.3f);
    }
}

[TestFixture]
public class BusRouteSystemTests
{
    [Test]
    public void BusRoute_AddStop_IncreasesCount()
    {
        var route = new BusRoute("R001", "Test Route");
        route.AddStop(new BusStop("S001", Vector3.zero, "Stop 1"));
        Assert.AreEqual(1, route.Stops.Count);
    }

    [Test]
    public void BusRoute_GetNextStop_WrapsAround()
    {
        var route = new BusRoute("R001", "Test Route");
        route.AddStop(new BusStop("S001", Vector3.zero, "Stop 1"));
        route.AddStop(new BusStop("S002", Vector3.forward * 10, "Stop 2"));

        var next = route.GetNextStop(1);
        Assert.AreEqual("S001", next.Id);
    }

    [Test]
    public void BusRoute_GetTotalRouteLength_ReturnsPositive()
    {
        var route = new BusRoute("R001", "Test Route");
        route.AddStop(new BusStop("S001", Vector3.zero, "Stop 1"));
        route.AddStop(new BusStop("S002", Vector3.forward * 100, "Stop 2"));

        Assert.Greater(route.GetTotalRouteLength(), 0f);
    }

    [Test]
    public void BusRoute_EmptyRoute_GetNextStop_ReturnsNull()
    {
        var route = new BusRoute("R001", "Test Route");
        Assert.IsNull(route.GetNextStop(0));
    }
}

[TestFixture]
public class TrafficIncidentTests
{
    [Test]
    public void TrafficIncident_Creation_SetsProperties()
    {
        var incident = new TrafficIncident("INC001", IncidentType.MinorCrash, Vector3.zero, 15f);

        Assert.AreEqual("INC001", incident.Id);
        Assert.AreEqual(IncidentType.MinorCrash, incident.Type);
        Assert.AreEqual(Vector3.zero, incident.Position);
        Assert.AreEqual(15f, incident.Duration);
        Assert.IsTrue(incident.IsActive);
        Assert.IsFalse(incident.IsExpired);
    }

    [Test]
    public void TrafficIncident_RemainingTime_DecreasesWithElapsed()
    {
        var incident = new TrafficIncident("INC002", IncidentType.MinorCrash, Vector3.zero, 10f);
        incident.ElapsedTime = 3f;
        Assert.AreEqual(7f, incident.RemainingTime, 0.01f);
    }

    [Test]
    public void TrafficIncident_IsExpired_ReturnsTrueWhenElapsed()
    {
        var incident = new TrafficIncident("INC003", IncidentType.MinorCrash, Vector3.zero, 10f);
        incident.ElapsedTime = 10f;
        Assert.IsTrue(incident.IsExpired);
    }

    [Test]
    public void TrafficIncident_MajorCrash_HasLargeRadius()
    {
        var incident = new TrafficIncident("INC004", IncidentType.MajorCrash, Vector3.zero, 30f);
        Assert.Greater(incident.Radius, 10f);
    }

    [Test]
    public void TrafficIncident_RoadClosure_HasLargestRadius()
    {
        var incident = new TrafficIncident("INC005", IncidentType.RoadClosure, Vector3.zero, 60f);
        var minor = new TrafficIncident("INC006", IncidentType.MinorCrash, Vector3.zero, 15f);
        Assert.Greater(incident.Radius, minor.Radius);
    }
}

[TestFixture]
public class TrafficIncidentManagerTests
{
    private GameObject _testObj;
    private TrafficIncidentManager _incidentManager;
    private TrafficConfig _config;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<TrafficConfig>();
        _testObj = new GameObject("IncidentManager");
        _incidentManager = _testObj.AddComponent<TrafficIncidentManager>();
        _incidentManager.Initialize(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
        Object.DestroyImmediate(_testObj);
    }

    [Test]
    public void TrafficIncidentManager_CreateIncident_IncreasesCount()
    {
        _incidentManager.CreateIncident(IncidentType.MinorCrash, Vector3.zero);
        Assert.AreEqual(1, _incidentManager.ActiveIncidentCount);
    }

    [Test]
    public void TrafficIncidentManager_RemoveIncident_DecreasesCount()
    {
        var incident = _incidentManager.CreateIncident(IncidentType.MinorCrash, Vector3.zero);
        _incidentManager.RemoveIncident(incident.Id);
        Assert.AreEqual(0, _incidentManager.ActiveIncidentCount);
    }

    [Test]
    public void TrafficIncidentManager_IsPositionBlocked_NearIncident_ReturnsTrue()
    {
        _incidentManager.CreateIncident(IncidentType.MajorCrash, Vector3.zero);
        Assert.IsTrue(_incidentManager.IsPositionBlocked(Vector3.zero));
    }

    [Test]
    public void TrafficIncidentManager_IsPositionBlocked_FarFromIncident_ReturnsFalse()
    {
        _incidentManager.CreateIncident(IncidentType.MinorCrash, Vector3.zero);
        Assert.IsFalse(_incidentManager.IsPositionBlocked(new Vector3(100, 0, 100)));
    }

    [Test]
    public void TrafficIncidentManager_GetSpeedReductionAtPosition_NearIncident_Reduces()
    {
        _incidentManager.CreateIncident(IncidentType.MajorCrash, Vector3.zero);
        float reduction = _incidentManager.GetSpeedReductionAtPosition(new Vector3(5, 0, 0));
        Assert.Less(reduction, 1f);
    }

    [Test]
    public void TrafficIncidentManager_GetNearestIncident_ReturnsClosest()
    {
        _incidentManager.CreateIncident(IncidentType.MinorCrash, new Vector3(50, 0, 0));
        _incidentManager.CreateIncident(IncidentType.MajorCrash, new Vector3(10, 0, 0));

        var nearest = _incidentManager.GetNearestIncident(Vector3.zero);
        Assert.IsNotNull(nearest);
        Assert.AreEqual(10f, Vector3.Distance(nearest.Position, Vector3.zero), 0.01f);
    }

    [Test]
    public void TrafficIncidentManager_GetIncidentsInRadius_ReturnsCorrect()
    {
        _incidentManager.CreateIncident(IncidentType.MinorCrash, new Vector3(5, 0, 0));
        _incidentManager.CreateIncident(IncidentType.MajorCrash, new Vector3(100, 0, 100));

        var inRadius = _incidentManager.GetIncidentsInRadius(Vector3.zero, 20f);
        Assert.AreEqual(1, inRadius.Count);
    }
}

[TestFixture]
public class TrafficLODManagerTests
{
    private GameObject _testObj;
    private TrafficLODManager _lodManager;
    private TrafficConfig _config;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<TrafficConfig>();
        _testObj = new GameObject("LODManager");
        _lodManager = _testObj.AddComponent<TrafficLODManager>();
        _lodManager.Initialize(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
        Object.DestroyImmediate(_testObj);
    }

    [Test]
    public void TrafficLODManager_GetLODLevel_NoPlayer_ReturnsCulled()
    {
        var go = new GameObject("Vehicle");
        var vehicle = go.AddComponent<TrafficVehicle>();
        vehicle.Initialize("LOD001", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        _lodManager.RegisterVehicle(vehicle);

        Assert.AreEqual(TrafficVehicleLOD.Culled, _lodManager.GetLODLevel(vehicle));

        Object.DestroyImmediate(go);
    }

    [Test]
    public void TrafficLODManager_GetLODLevel_CloseToPlayer_ReturnsFull()
    {
        var playerObj = new GameObject("Player");
        _lodManager.SetPlayerTransform(playerObj.transform);

        var go = new GameObject("Vehicle");
        var vehicle = go.AddComponent<TrafficVehicle>();
        vehicle.Initialize("LOD002", TrafficVehicleType.Sedan, Vector3.forward * 10f, 0f, 50f);
        _lodManager.RegisterVehicle(vehicle);

        Assert.AreEqual(TrafficVehicleLOD.Full, _lodManager.GetLODLevel(vehicle));

        Object.DestroyImmediate(playerObj);
        Object.DestroyImmediate(go);
    }

    [Test]
    public void TrafficLODManager_GetLODLevel_FarFromPlayer_ReturnsCulled()
    {
        var playerObj = new GameObject("Player");
        _lodManager.SetPlayerTransform(playerObj.transform);

        var go = new GameObject("Vehicle");
        var vehicle = go.AddComponent<TrafficVehicle>();
        vehicle.Initialize("LOD003", TrafficVehicleType.Sedan, new Vector3(500, 0, 500), 0f, 50f);
        _lodManager.RegisterVehicle(vehicle);

        Assert.AreEqual(TrafficVehicleLOD.Culled, _lodManager.GetLODLevel(vehicle));

        Object.DestroyImmediate(playerObj);
        Object.DestroyImmediate(go);
    }

    [Test]
    public void TrafficLODManager_Cleanup_RemovesNullVehicles()
    {
        _lodManager.Cleanup();
        Assert.AreEqual(0, _lodManager.ManagedVehicleCount);
    }
}

[TestFixture]
public class ParkingSystemTests
{
    private GameObject _testObj;
    private ParkingSystem _parkingSystem;
    private TrafficConfig _config;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<TrafficConfig>();
        _testObj = new GameObject("ParkingSystem");
        _parkingSystem = _testObj.AddComponent<ParkingSystem>();
        _parkingSystem.Initialize(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
        Object.DestroyImmediate(_testObj);
    }

    [Test]
    public void ParkingSystem_Initialize_DefaultsToNone()
    {
        Assert.AreEqual(ParkingState.None, _parkingSystem.State);
    }

    [Test]
    public void ParkingSystem_ResetState_ResetsToNone()
    {
        _parkingSystem.ResetState();
        Assert.AreEqual(ParkingState.None, _parkingSystem.State);
    }
}

[TestFixture]
public class LaneControllerTests
{
    private GameObject _testObj;
    private LaneController _laneController;
    private TrafficConfig _config;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<TrafficConfig>();
        _testObj = new GameObject("LaneController");
        _laneController = _testObj.AddComponent<LaneController>();
        _laneController.Initialize(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
        Object.DestroyImmediate(_testObj);
    }

    [Test]
    public void LaneController_Initialize_DefaultsToLane1()
    {
        Assert.AreEqual(1, _laneController.CurrentLaneIndex);
    }

    [Test]
    public void LaneController_SetLane_UpdatesIndex()
    {
        _laneController.SetLane(0);
        Assert.AreEqual(0, _laneController.CurrentLaneIndex);
        Assert.IsFalse(_laneController.IsChangingLane);
    }

    [Test]
    public void LaneController_ShouldChangeLane_WhenNotChanging_ReturnsFalse()
    {
        var go = new GameObject("Vehicle");
        var vehicle = go.AddComponent<TrafficVehicle>();
        vehicle.Initialize("LC001", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);
        vehicle.SetCurrentSpeed(0f);

        Assert.IsFalse(_laneController.ShouldChangeLane(vehicle));

        Object.DestroyImmediate(go);
    }

    [Test]
    public void LaneController_ExecuteLaneChange_NotChanging_ReturnsTrue()
    {
        var go = new GameObject("Vehicle");
        var vehicle = go.AddComponent<TrafficVehicle>();
        vehicle.Initialize("LC002", TrafficVehicleType.Sedan, Vector3.zero, 0f, 50f);

        Assert.IsTrue(_laneController.ExecuteLaneChange(vehicle, 0.1f));

        Object.DestroyImmediate(go);
    }
}

[TestFixture]
public class TrafficAIBehaviorStateTests
{
    [Test]
    public void AllBehaviorStates_AreDefined()
    {
        Assert.AreEqual(18, System.Enum.GetValues(typeof(TrafficAIBehaviorState)).Length);
        Assert.IsTrue(System.Enum.IsDefined(typeof(TrafficAIBehaviorState), TrafficAIBehaviorState.Idle));
        Assert.IsTrue(System.Enum.IsDefined(typeof(TrafficAIBehaviorState), TrafficAIBehaviorState.FollowingLane));
        Assert.IsTrue(System.Enum.IsDefined(typeof(TrafficAIBehaviorState), TrafficAIBehaviorState.Overtaking));
        Assert.IsTrue(System.Enum.IsDefined(typeof(TrafficAIBehaviorState), TrafficAIBehaviorState.Parking));
        Assert.IsTrue(System.Enum.IsDefined(typeof(TrafficAIBehaviorState), TrafficAIBehaviorState.EmergencyBraking));
        Assert.IsTrue(System.Enum.IsDefined(typeof(TrafficAIBehaviorState), TrafficAIBehaviorState.YieldingToEmergency));
        Assert.IsTrue(System.Enum.IsDefined(typeof(TrafficAIBehaviorState), TrafficAIBehaviorState.Cruising));
    }
}
