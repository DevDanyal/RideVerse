using NUnit.Framework;
using UnityEngine;
using RideVerse.Police.Core;

[TestFixture]
public class PoliceEnumTests
{
    [Test]
    public void PoliceState_HasAllValues()
    {
        Assert.AreEqual(13, System.Enum.GetValues(typeof(PoliceState)).Length);
    }

    [Test]
    public void WantedLevel_HasAllValues()
    {
        Assert.AreEqual(7, System.Enum.GetValues(typeof(WantedLevel)).Length);
    }

    [Test]
    public void CrimeType_HasAllValues()
    {
        Assert.AreEqual(12, System.Enum.GetValues(typeof(CrimeType)).Length);
    }

    [Test]
    public void PoliceUnitType_HasAllValues()
    {
        Assert.AreEqual(8, System.Enum.GetValues(typeof(PoliceUnitType)).Length);
    }

    [Test]
    public void PursuitState_HasAllValues()
    {
        Assert.AreEqual(10, System.Enum.GetValues(typeof(PursuitState)).Length);
    }

    [Test]
    public void DispatchPriority_HasAllValues()
    {
        Assert.AreEqual(4, System.Enum.GetValues(typeof(DispatchPriority)).Length);
    }

    [Test]
    public void RoadblockType_HasAllValues()
    {
        Assert.AreEqual(4, System.Enum.GetValues(typeof(RoadblockType)).Length);
    }

    [Test]
    public void EvidenceType_HasAllValues()
    {
        Assert.AreEqual(8, System.Enum.GetValues(typeof(EvidenceType)).Length);
    }

    [Test]
    public void RadioMessageType_HasAllValues()
    {
        Assert.AreEqual(13, System.Enum.GetValues(typeof(RadioMessageType)).Length);
    }

    [Test]
    public void FineCategory_HasAllValues()
    {
        Assert.AreEqual(11, System.Enum.GetValues(typeof(FineCategory)).Length);
    }
}

[TestFixture]
public class PoliceConfigTests
{
    [Test]
    public void PoliceConfig_DefaultValues_AreValid()
    {
        var config = ScriptableObject.CreateInstance<PoliceConfig>();

        Assert.Greater(config.maxPoliceUnits, 0);
        Assert.Greater(config.spawnRadius, 0f);
        Assert.Greater(config.despawnRadius, config.spawnRadius);
        Assert.Greater(config.patrolSpeed, 0f);
        Assert.Greater(config.patrolWaypointReachDistance, 0f);
        Assert.Greater(config.patrolWaypointsPerRoute, 0);
        Assert.Greater(config.crimeDetectionRange, 0f);
        Assert.Greater(config.speedingToleranceKmh, 0f);
        Assert.Greater(config.wantedLevelDecayTime, 0f);
        Assert.Greater(config.maxWantedLevel, 0);
        Assert.Greater(config.dispatchResponseTime, 0f);
        Assert.Greater(config.maxActiveDispatchCalls, 0);
        Assert.Greater(config.pursuitMaxSpeed, 0f);
        Assert.Greater(config.pursuitCatchUpSpeed, config.pursuitMaxSpeed);
        Assert.Greater(config.pursuitLostSightTime, 0f);
        Assert.Greater(config.pursuitMaxDuration, 0f);
        Assert.Greater(config.footPursuitSpeed, 0f);
        Assert.Greater(config.footPursuitSprintSpeed, config.footPursuitSpeed);
        Assert.Greater(config.footPursuitCatchDistance, 0f);
        Assert.Greater(config.maxActiveRoadblocks, 0);
        Assert.Greater(config.roadblockSetupTime, 0f);
        Assert.Greater(config.arrestRange, 0f);
        Assert.Greater(config.arrestHandcuffTime, 0f);
        Assert.Greater(config.fineSpeeding, 0f);
        Assert.Greater(config.fineMurder, config.fineSpeeding);
        Assert.Greater(config.fineMultiplierPerStar, 1f);
        Assert.Greater(config.maxEvidencePerCrime, 0);
        Assert.Greater(config.evidenceExpiryTime, 0f);
        Assert.Greater(config.maxRadioMessages, 0);
        Assert.Greater(config.maxBackupUnits, 0);
        Assert.Greater(config.backupArrivalTime, 0f);
        Assert.Greater(config.swatMinWantedLevel, 0);
        Assert.Greater(config.swatMaxUnits, 0);
        Assert.Greater(config.helicopterAltitude, 0f);
        Assert.Greater(config.helicopterSpeed, 0f);
        Assert.Greater(config.helicopterSpotlightRange, 0f);

        Object.DestroyImmediate(config);
    }

    [Test]
    public void PoliceConfig_Fines_IncreaseWithSeverity()
    {
        var config = ScriptableObject.CreateInstance<PoliceConfig>();

        Assert.Less(config.fineSpeeding, config.fineDangerousDriving);
        Assert.Less(config.fineDangerousDriving, config.fineHitAndRun);
        Assert.Less(config.fineHitAndRun, config.fineVehicleTheft);
        Assert.Less(config.fineAssault, config.fineRobbery);
        Assert.Less(config.fineRobbery, config.finePoliceAssault);
        Assert.Less(config.finePoliceAssault, config.fineMurder);

        Object.DestroyImmediate(config);
    }

    [Test]
    public void PoliceConfig_JailSentences_IncreaseWithSeverity()
    {
        var config = ScriptableObject.CreateInstance<PoliceConfig>();

        Assert.Less(config.jailSentenceShort, config.jailSentenceMedium);
        Assert.Less(config.jailSentenceMedium, config.jailSentenceLong);
        Assert.Less(config.jailSentenceLong, config.jailSentenceExtended);

        Object.DestroyImmediate(config);
    }
}

[TestFixture]
public class CrimeRecordTests
{
    [Test]
    public void CrimeRecord_DefaultConstructor_SetsDefaults()
    {
        var crime = new CrimeRecord();

        Assert.IsNotNull(crime.CrimeId);
        Assert.AreEqual(8, crime.CrimeId.Length);
        Assert.AreEqual(CrimeType.Speeding, crime.CrimeType);
        Assert.IsFalse(crime.IsVerified);
        Assert.IsFalse(crime.IsResolved);
        Assert.IsNotNull(crime.EvidenceIds);
        Assert.IsNotNull(crime.WitnessIds);
    }

    [Test]
    public void CrimeRecord_ParameterConstructor_SetsProperties()
    {
        var crime = new CrimeRecord("player1", CrimeType.Assault, new Vector3(10, 0, 20), 2.5f);

        Assert.AreEqual("player1", crime.PlayerId);
        Assert.AreEqual(CrimeType.Assault, crime.CrimeType);
        Assert.AreEqual(new Vector3(10, 0, 20), crime.Position);
        Assert.AreEqual(2.5f, crime.Severity);
    }

    [Test]
    public void CrimeRecord_GetWantedLevelContribution_ReturnsCorrectValues()
    {
        var speeding = new CrimeRecord();
        speeding.CrimeType = CrimeType.Speeding;
        Assert.Less(speeding.GetWantedLevelContribution(), 0.5f);

        var murder = new CrimeRecord();
        murder.CrimeType = CrimeType.Murder;
        Assert.AreEqual(4f, murder.GetWantedLevelContribution());

        var assault = new CrimeRecord();
        assault.CrimeType = CrimeType.PoliceAssault;
        Assert.AreEqual(3f, assault.GetWantedLevelContribution());
    }
}

[TestFixture]
public class WantedLevelSystemTests
{
    private PoliceConfig _config;
    private WantedLevelSystem _system;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _system = new WantedLevelSystem(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void WantedLevelSystem_InitializesAtZero()
    {
        Assert.AreEqual(0, _system.CurrentStars);
        Assert.IsFalse(_system.IsWanted);
    }

    [Test]
    public void WantedLevelSystem_AddCrime_IncreasesLevel()
    {
        var crime = new CrimeRecord("local_player", CrimeType.Assault, Vector3.zero, 2f);
        _system.AddCrime("local_player", crime);
        Assert.IsTrue(_system.IsWanted);
    }

    [Test]
    public void WantedLevelSystem_ClearWantedLevel_ResetsToZero()
    {
        var crime = new CrimeRecord("local_player", CrimeType.Murder, Vector3.zero, 4f);
        _system.AddCrime("local_player", crime);
        _system.ClearWantedLevel("local_player");
        Assert.AreEqual(0, _system.CurrentStars);
        Assert.IsFalse(_system.IsWanted);
    }

    [Test]
    public void WantedLevelSystem_SetWantedLevel_SetsCorrectStars()
    {
        _system.SetWantedLevel("local_player", 3);
        Assert.AreEqual(3, _system.CurrentStars);
    }

    [Test]
    public void WantedLevelSystem_GetDispatchPriority_ReturnsCorrectPriority()
    {
        Assert.AreEqual(DispatchPriority.Low, _system.GetDispatchPriority());

        _system.SetWantedLevel("local_player", 3);
        Assert.AreEqual(DispatchPriority.High, _system.GetDispatchPriority());

        _system.SetWantedLevel("local_player", 5);
        Assert.AreEqual(DispatchPriority.Critical, _system.GetDispatchPriority());
    }

    [Test]
    public void WantedLevelSystem_ShouldDeploySWAT_AtHighLevels()
    {
        _system.SetWantedLevel("local_player", 4);
        Assert.IsFalse(_system.ShouldDeploySWAT());

        _system.SetWantedLevel("local_player", 5);
        Assert.IsTrue(_system.ShouldDeploySWAT());
    }

    [Test]
    public void WantedLevelSystem_ShouldDeployHelicopter_AtHighLevels()
    {
        _system.SetWantedLevel("local_player", 3);
        Assert.IsFalse(_system.ShouldDeployHelicopter());

        _system.SetWantedLevel("local_player", 4);
        Assert.IsTrue(_system.ShouldDeployHelicopter());
    }

    [Test]
    public void WantedLevelSystem_GetRequiredPursuitUnits_IncreasesWithStars()
    {
        _system.SetWantedLevel("local_player", 1);
        int units1 = _system.GetRequiredPursuitUnits();

        _system.SetWantedLevel("local_player", 5);
        int units5 = _system.GetRequiredPursuitUnits();

        Assert.Greater(units5, units1);
    }

    [Test]
    public void WantedLevelSystem_GetJailSentence_ReturnsCorrectSentence()
    {
        _system.SetWantedLevel("local_player", 1);
        var sentence1 = _system.GetJailSentence();

        _system.SetWantedLevel("local_player", 5);
        var sentence5 = _system.GetJailSentence();

        Assert.Greater((int)sentence5, (int)sentence1);
    }

    [Test]
    public void WantedLevelSystem_Reset_ClearsEverything()
    {
        var crime = new CrimeRecord("local_player", CrimeType.Murder, Vector3.zero, 4f);
        _system.AddCrime("local_player", crime);
        _system.Reset();
        Assert.AreEqual(0, _system.CurrentStars);
    }
}

[TestFixture]
public class CrimeDetectionSystemTests
{
    private PoliceConfig _config;
    private CrimeDetectionSystem _system;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _system = new CrimeDetectionSystem(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void CrimeDetectionSystem_InitializesEmpty()
    {
        Assert.AreEqual(0, _system.ActiveCrimeCount);
    }

    [Test]
    public void CrimeDetectionSystem_ReportCrime_AddsCrime()
    {
        var crime = _system.ReportCrime("player1", CrimeType.Assault, Vector3.zero, 2f);
        Assert.IsNotNull(crime);
        Assert.AreEqual(1, _system.ActiveCrimeCount);
        Assert.AreEqual("player1", crime.PlayerId);
    }

    [Test]
    public void CrimeDetectionSystem_DetectSpeeding_AboveLimit_ReturnsCrime()
    {
        var crime = _system.DetectSpeeding("player1", Vector3.zero, 80f, 50f);
        Assert.IsNotNull(crime);
        Assert.AreEqual(CrimeType.Speeding, crime.CrimeType);
    }

    [Test]
    public void CrimeDetectionSystem_DetectSpeeding_BelowLimit_ReturnsNull()
    {
        var crime = _system.DetectSpeeding("player1", Vector3.zero, 45f, 50f);
        Assert.IsNull(crime);
    }

    [Test]
    public void CrimeDetectionSystem_DetectDangerousDriving_AboveThreshold_ReturnsCrime()
    {
        var crime = _system.DetectDangerousDriving("player1", Vector3.zero, 90f, 30f);
        Assert.IsNotNull(crime);
        Assert.AreEqual(CrimeType.DangerousDriving, crime.CrimeType);
    }

    [Test]
    public void CrimeDetectionSystem_DetectHitAndRun_AlwaysReturns()
    {
        var crime = _system.DetectHitAndRun("player1", Vector3.zero, 20f);
        Assert.IsNotNull(crime);
        Assert.AreEqual(CrimeType.HitAndRun, crime.CrimeType);
    }

    [Test]
    public void CrimeDetectionSystem_VerifyCrime_SetsVerified()
    {
        var crime = _system.ReportCrime("player1", CrimeType.Assault, Vector3.zero, 2f);
        _system.VerifyCrime(crime.CrimeId);
        Assert.IsTrue(crime.IsVerified);
    }

    [Test]
    public void CrimeDetectionSystem_ResolveCrime_SetsResolved()
    {
        var crime = _system.ReportCrime("player1", CrimeType.Assault, Vector3.zero, 2f);
        _system.ResolveCrime(crime.CrimeId);
        Assert.IsTrue(crime.IsResolved);
    }

    [Test]
    public void CrimeDetectionSystem_GetCrimesNearPosition_ReturnsCorrect()
    {
        _system.ReportCrime("player1", CrimeType.Assault, new Vector3(5, 0, 0), 2f);
        _system.ReportCrime("player1", CrimeType.Robbery, new Vector3(100, 0, 100), 2.5f);

        var nearby = _system.GetCrimesNearPosition(Vector3.zero, 20f);
        Assert.AreEqual(1, nearby.Count);
    }

    [Test]
    public void CrimeDetectionSystem_AddWitness_CreatesWitnessReport()
    {
        var crime = _system.ReportCrime("player1", CrimeType.Assault, Vector3.zero, 2f);
        var witness = _system.AddWitness(crime.CrimeId, "witness1", new Vector3(10, 0, 0), Vector3.zero, "I saw it");
        Assert.IsNotNull(witness);
        Assert.AreEqual("witness1", witness.WitnessId);
    }

    [Test]
    public void CrimeDetectionSystem_ReportCrime_Duplicate_DoesNotCreateNew()
    {
        _system.ReportCrime("player1", CrimeType.Speeding, Vector3.zero, 0.3f);
        _system.ReportCrime("player1", CrimeType.Speeding, Vector3.zero, 0.5f);
        Assert.AreEqual(1, _system.ActiveCrimeCount);
    }

    [Test]
    public void CrimeDetectionSystem_DetectWeaponPossession_ReturnsCrime()
    {
        var crime = _system.DetectWeaponPossession("player1", Vector3.zero);
        Assert.IsNotNull(crime);
        Assert.AreEqual(CrimeType.WeaponPossession, crime.CrimeType);
    }

    [Test]
    public void CrimeDetectionSystem_DetectAssault_ReturnsCrime()
    {
        var crime = _system.DetectAssault("player1", Vector3.zero);
        Assert.IsNotNull(crime);
        Assert.AreEqual(CrimeType.Assault, crime.CrimeType);
    }

    [Test]
    public void CrimeDetectionSystem_DetectRobbery_ReturnsCrime()
    {
        var crime = _system.DetectRobbery("player1", Vector3.zero);
        Assert.IsNotNull(crime);
        Assert.AreEqual(CrimeType.Robbery, crime.CrimeType);
    }

    [Test]
    public void CrimeDetectionSystem_DetectIllegalRacing_ReturnsCrime()
    {
        var crime = _system.DetectIllegalRacing("player1", Vector3.zero);
        Assert.IsNotNull(crime);
        Assert.AreEqual(CrimeType.IllegalRacing, crime.CrimeType);
    }

    [Test]
    public void CrimeDetectionSystem_DetectPoliceAssault_ReturnsCrime()
    {
        var crime = _system.DetectPoliceAssault("player1", Vector3.zero);
        Assert.IsNotNull(crime);
        Assert.AreEqual(CrimeType.PoliceAssault, crime.CrimeType);
    }

    [Test]
    public void CrimeDetectionSystem_DetectMurder_ReturnsCrime()
    {
        var crime = _system.DetectMurder("player1", Vector3.zero);
        Assert.IsNotNull(crime);
        Assert.AreEqual(CrimeType.Murder, crime.CrimeType);
    }

    [Test]
    public void CrimeDetectionSystem_GetNearestCrime_ReturnsClosest()
    {
        _system.ReportCrime("player1", CrimeType.Assault, new Vector3(50, 0, 0), 2f);
        _system.ReportCrime("player1", CrimeType.Robbery, new Vector3(5, 0, 0), 2.5f);

        var nearest = _system.GetNearestCrime(Vector3.zero);
        Assert.IsNotNull(nearest);
        Assert.AreEqual(CrimeType.Robbery, nearest.CrimeType);
    }

    [Test]
    public void CrimeDetectionSystem_GetCrimesForPlayer_ReturnsCorrect()
    {
        _system.ReportCrime("player1", CrimeType.Assault, Vector3.zero, 2f);
        _system.ReportCrime("player2", CrimeType.Robbery, Vector3.zero, 2.5f);

        var crimes = _system.GetCrimesForPlayer("player1");
        Assert.AreEqual(1, crimes.Count);
    }
}

[TestFixture]
public class DispatchSystemTests
{
    private PoliceConfig _config;
    private DispatchSystem _system;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _system = new DispatchSystem(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void DispatchSystem_InitializesEmpty()
    {
        Assert.AreEqual(0, _system.ActiveCallCount);
    }

    [Test]
    public void DispatchSystem_CreateDispatchCall_AddsCall()
    {
        var call = _system.CreateDispatchCall("crime1", CrimeType.Assault, Vector3.zero, DispatchPriority.High);
        Assert.IsNotNull(call);
        Assert.AreEqual(1, _system.ActiveCallCount);
        Assert.AreEqual(DispatchPriority.High, call.Priority);
    }

    [Test]
    public void DispatchSystem_AssignUnit_Succeeds()
    {
        _system.RegisterUnit("unit1");
        var call = _system.CreateDispatchCall("crime1", CrimeType.Assault, Vector3.zero, DispatchPriority.High);

        bool result = _system.AssignUnit(call.CallId, "unit1");
        Assert.IsTrue(result);
        Assert.IsTrue(call.IsAssigned);
        Assert.AreEqual("unit1", call.AssignedUnitId);
    }

    [Test]
    public void DispatchSystem_AssignUnit_UnavailableUnit_Fails()
    {
        _system.RegisterUnit("unit1");
        _system.AssignUnit("fake_call", "unit1");

        var call = _system.CreateDispatchCall("crime1", CrimeType.Assault, Vector3.zero, DispatchPriority.High);
        bool result = _system.AssignUnit(call.CallId, "unit1");
        Assert.IsFalse(result);
    }

    [Test]
    public void DispatchSystem_CompleteDispatch_FreesUnit()
    {
        _system.RegisterUnit("unit1");
        var call = _system.CreateDispatchCall("crime1", CrimeType.Assault, Vector3.zero, DispatchPriority.High);
        _system.AssignUnit(call.CallId, "unit1");

        _system.CompleteDispatch(call.CallId);
        Assert.IsTrue(_system.IsUnitAvailable("unit1"));
    }

    [Test]
    public void DispatchSystem_GetBestCallForUnit_ReturnsHighestPriority()
    {
        _system.CreateDispatchCall("crime1", CrimeType.Speeding, new Vector3(50, 0, 0), DispatchPriority.Low);
        _system.CreateDispatchCall("crime2", CrimeType.Assault, new Vector3(10, 0, 0), DispatchPriority.High);

        var best = _system.GetBestCallForUnit("unit1", Vector3.zero);
        Assert.IsNotNull(best);
        Assert.AreEqual("crime2", best.CrimeId);
    }

    [Test]
    public void DispatchSystem_IsUnitAvailable_ReturnsCorrectly()
    {
        _system.RegisterUnit("unit1");
        Assert.IsTrue(_system.IsUnitAvailable("unit1"));
    }

    [Test]
    public void DispatchSystem_GetUnitState_ReturnsState()
    {
        _system.RegisterUnit("unit1");
        var state = _system.GetUnitState("unit1");
        Assert.IsNotNull(state);
        Assert.IsTrue(state.IsAvailable);
    }

    [Test]
    public void DispatchSystem_SetUnitState_UpdatesState()
    {
        _system.RegisterUnit("unit1");
        _system.SetUnitState("unit1", PoliceState.Patrolling);
        var state = _system.GetUnitState("unit1");
        Assert.AreEqual(PoliceState.Patrolling, state.CurrentState);
    }
}

[TestFixture]
public class PatrolRouteTests
{
    [Test]
    public void PatrolRoute_CreateWithWaypoints_SetsProperties()
    {
        var waypoints = new System.Collections.Generic.List<Vector3>
        {
            new Vector3(0, 0, 0),
            new Vector3(10, 0, 0),
            new Vector3(10, 0, 10),
            new Vector3(0, 0, 10)
        };

        var route = new PatrolRoute(waypoints);
        Assert.AreEqual(4, route.Waypoints.Count);
        Assert.IsTrue(route.IsActive);
        Assert.Greater(route.TotalLength, 0f);
    }

    [Test]
    public void PatrolRoute_GetCurrentWaypoint_ReturnsFirst()
    {
        var waypoints = new System.Collections.Generic.List<Vector3>
        {
            new Vector3(5, 0, 5),
            new Vector3(10, 0, 10)
        };

        var route = new PatrolRoute(waypoints);
        Assert.AreEqual(new Vector3(5, 0, 5), route.GetCurrentWaypoint());
    }

    [Test]
    public void PatrolRoute_HasReachedWaypoint_Close_ReturnsTrue()
    {
        var waypoints = new System.Collections.Generic.List<Vector3>
        {
            new Vector3(0, 0, 0),
            new Vector3(10, 0, 10)
        };

        var route = new PatrolRoute(waypoints);
        Assert.IsTrue(route.HasReachedWaypoint(new Vector3(1, 0, 1), 5f));
    }

    [Test]
    public void PatrolRoute_HasReachedWaypoint_Far_ReturnsFalse()
    {
        var waypoints = new System.Collections.Generic.List<Vector3>
        {
            new Vector3(0, 0, 0),
            new Vector3(100, 0, 100)
        };

        var route = new PatrolRoute(waypoints);
        Assert.IsFalse(route.HasReachedWaypoint(new Vector3(50, 0, 50), 5f));
    }

    [Test]
    public void PatrolRoute_AdvanceToNextWaypoint_IncrementsIndex()
    {
        var waypoints = new System.Collections.Generic.List<Vector3>
        {
            new Vector3(0, 0, 0),
            new Vector3(10, 0, 0),
            new Vector3(20, 0, 0)
        };

        var route = new PatrolRoute(waypoints);
        Assert.AreEqual(new Vector3(0, 0, 0), route.GetCurrentWaypoint());
        route.AdvanceToNextWaypoint();
        Assert.AreEqual(new Vector3(10, 0, 0), route.GetCurrentWaypoint());
    }

    [Test]
    public void PatrolRoute_AdanceWrapsAround()
    {
        var waypoints = new System.Collections.Generic.List<Vector3>
        {
            new Vector3(0, 0, 0),
            new Vector3(10, 0, 0)
        };

        var route = new PatrolRoute(waypoints);
        route.AdvanceToNextWaypoint();
        route.AdvanceToNextWaypoint();
        Assert.AreEqual(new Vector3(0, 0, 0), route.GetCurrentWaypoint());
    }

    [Test]
    public void PatrolRoute_Reset_ResetsIndex()
    {
        var waypoints = new System.Collections.Generic.List<Vector3>
        {
            new Vector3(0, 0, 0),
            new Vector3(10, 0, 0)
        };

        var route = new PatrolRoute(waypoints);
        route.AdvanceToNextWaypoint();
        route.Reset();
        Assert.AreEqual(0, route.CurrentWaypointIndex);
    }
}

[TestFixture]
public class EvidenceLoggerTests
{
    private PoliceConfig _config;
    private EvidenceLogger _logger;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _logger = new EvidenceLogger(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void EvidenceLogger_InitializesEmpty()
    {
        Assert.AreEqual(0, _logger.TotalEvidenceCount);
    }

    [Test]
    public void EvidenceLogger_LogEvidence_AddsEvidence()
    {
        var entry = _logger.LogEvidence("crime1", EvidenceType.WitnessSighting, "I saw it", Vector3.zero, "witness1");
        Assert.IsNotNull(entry);
        Assert.AreEqual(1, _logger.TotalEvidenceCount);
    }

    [Test]
    public void EvidenceLogger_LogSpeedReading_AddsSpeedEvidence()
    {
        var entry = _logger.LogSpeedReading("crime1", "camera1", Vector3.zero, 120f);
        Assert.IsNotNull(entry);
        Assert.AreEqual(EvidenceType.SpeedReading, entry.Type);
    }

    [Test]
    public void EvidenceLogger_GetEvidenceForCrime_ReturnsCorrect()
    {
        _logger.LogEvidence("crime1", EvidenceType.WitnessSighting, "saw it", Vector3.zero, "w1");
        _logger.LogEvidence("crime2", EvidenceType.SpeedReading, "fast", Vector3.zero, "cam1");

        var evidence = _logger.GetEvidenceForCrime("crime1");
        Assert.AreEqual(1, evidence.Count);
    }

    [Test]
    public void EvidenceLogger_GetTotalReliability_CalculatesAverage()
    {
        _logger.LogEvidence("crime1", EvidenceType.WitnessSighting, "saw it", Vector3.zero, "w1", 0.8f);
        _logger.LogEvidence("crime1", EvidenceType.SpeedReading, "fast", Vector3.zero, "cam1", 1.0f);

        float reliability = _logger.GetTotalReliability("crime1");
        Assert.AreEqual(0.9f, reliability, 0.01f);
    }

    [Test]
    public void EvidenceLogger_HasStrongEvidence_ReturnsCorrect()
    {
        _logger.LogEvidence("crime1", EvidenceType.SpeedReading, "fast", Vector3.zero, "cam1", 0.9f);
        Assert.IsTrue(_logger.HasStrongEvidence("crime1", 0.7f));
        Assert.IsFalse(_logger.HasStrongEvidence("crime1", 0.95f));
    }

    [Test]
    public void EvidenceLogger_ClearAll_EmptiesEverything()
    {
        _logger.LogEvidence("crime1", EvidenceType.WitnessSighting, "saw it", Vector3.zero, "w1");
        _logger.ClearAll();
        Assert.AreEqual(0, _logger.TotalEvidenceCount);
    }
}

[TestFixture]
public class RadioCommunicationSystemTests
{
    private PoliceConfig _config;
    private RadioCommunicationSystem _radio;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _radio = new RadioCommunicationSystem(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void RadioSystem_InitializesEmpty()
    {
        Assert.AreEqual(0, _radio.ActiveMessageCount);
    }

    [Test]
    public void RadioSystem_SendMessage_AddsMessage()
    {
        var msg = _radio.SendMessage(RadioMessageType.StatusUpdate, "unit1", "All clear", Vector3.zero);
        Assert.IsNotNull(msg);
        Assert.AreEqual(1, _radio.ActiveMessageCount);
    }

    [Test]
    public void RadioSystem_SendBackupRequest_CreatesRequest()
    {
        var msg = _radio.SendBackupRequest("unit1", Vector3.zero, DispatchPriority.High, "Need backup");
        Assert.IsNotNull(msg);
        Assert.AreEqual(RadioMessageType.BackupRequest, msg.Type);
    }

    [Test]
    public void RadioSystem_SendAllUnitsAlert_CreatesBroadcast()
    {
        var msg = _radio.SendAllUnitsAlert("dispatch", "Alert!", Vector3.zero);
        Assert.IsNotNull(msg);
        Assert.AreEqual(RadioMessageType.AllUnitsAlert, msg.Type);
    }

    [Test]
    public void RadioSystem_GetMessagesByType_ReturnsCorrect()
    {
        _radio.SendMessage(RadioMessageType.StatusUpdate, "unit1", "Status", Vector3.zero);
        _radio.SendMessage(RadioMessageType.BackupRequest, "unit2", "Backup", Vector3.zero);

        var statusMessages = _radio.GetMessagesByType(RadioMessageType.StatusUpdate);
        Assert.AreEqual(1, statusMessages.Count);
    }

    [Test]
    public void RadioSystem_GetLatestMessageByType_ReturnsMostRecent()
    {
        _radio.SendMessage(RadioMessageType.StatusUpdate, "unit1", "First", Vector3.zero);
        _radio.SendMessage(RadioMessageType.StatusUpdate, "unit1", "Second", Vector3.zero);

        var latest = _radio.GetLatestMessageByType(RadioMessageType.StatusUpdate);
        Assert.AreEqual("Second", latest.Content);
    }

    [Test]
    public void RadioSystem_CanUnitSendChatter_FirstTime_ReturnsTrue()
    {
        Assert.IsTrue(_radio.CanUnitSendChatter("unit1"));
    }

    [Test]
    public void RadioSystem_ClearAll_EmptiesEverything()
    {
        _radio.SendMessage(RadioMessageType.StatusUpdate, "unit1", "Status", Vector3.zero);
        _radio.ClearAll();
        Assert.AreEqual(0, _radio.ActiveMessageCount);
    }
}

[TestFixture]
public class RoadblockSystemTests
{
    private PoliceConfig _config;
    private RoadblockSystem _system;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _system = new RoadblockSystem(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void RoadblockSystem_InitializesEmpty()
    {
        Assert.AreEqual(0, _system.ActiveRoadblockCount);
        Assert.IsFalse(_system.HasActiveRoadblocks());
    }

    [Test]
    public void RoadblockSystem_CreateRoadblock_AddsRoadblock()
    {
        var rb = _system.CreateRoadblock(RoadblockType.PoliceCars, Vector3.zero, 0f);
        Assert.IsNotNull(rb);
        Assert.AreEqual(1, _system.ActiveRoadblockCount);
        Assert.IsTrue(_system.HasActiveRoadblocks());
    }

    [Test]
    public void RoadblockSystem_CreateSpikeStrip_CreatesCorrectType()
    {
        var rb = _system.CreateSpikeStrip(new Vector3(10, 0, 0), 0f);
        Assert.IsNotNull(rb);
        Assert.AreEqual(RoadblockType.SpikeStrip, rb.Type);
    }

    [Test]
    public void RoadblockSystem_RemoveRoadblock_DecrementsCount()
    {
        var rb = _system.CreateRoadblock(RoadblockType.PoliceCars, Vector3.zero, 0f);
        _system.RemoveRoadblock(rb.RoadblockId);
        Assert.AreEqual(0, _system.ActiveRoadblockCount);
    }

    [Test]
    public void RoadblockSystem_IsPositionInRoadblock_Near_ReturnsTrue()
    {
        var rb = _system.CreateRoadblock(RoadblockType.PoliceCars, Vector3.zero, 0f);
        rb.SetupProgress = 1f;
        rb.IsReady = true;
        rb.Activate();
        Assert.IsTrue(_system.IsPositionInRoadblock(new Vector3(1, 0, 0)));
    }

    [Test]
    public void RoadblockSystem_IsPositionInRoadblock_Far_ReturnsFalse()
    {
        var rb = _system.CreateRoadblock(RoadblockType.PoliceCars, Vector3.zero, 0f);
        rb.SetupProgress = 1f;
        rb.IsReady = true;
        rb.Activate();
        Assert.IsFalse(_system.IsPositionInRoadblock(new Vector3(100, 0, 100)));
    }

    [Test]
    public void RoadblockSystem_GetSpikeStripDamage_Near_ReturnsDamage()
    {
        var rb = _system.CreateSpikeStrip(Vector3.zero, 0f);
        rb.SetupProgress = 1f;
        rb.IsReady = true;
        rb.Activate();

        float damage = _system.GetSpikeStripDamage(Vector3.zero);
        Assert.Greater(damage, 0f);
    }

    [Test]
    public void RoadblockSystem_GetRequiredUnits_ReturnsCorrectCount()
    {
        Assert.Greater(_system.GetRequiredUnitsForRoadblock(RoadblockType.PoliceCars), 0);
        Assert.AreEqual(1, _system.GetRequiredUnitsForRoadblock(RoadblockType.SpikeStrip));
    }

    [Test]
    public void RoadblockSystem_ClearAll_EmptiesEverything()
    {
        _system.CreateRoadblock(RoadblockType.PoliceCars, Vector3.zero, 0f);
        _system.ClearAll();
        Assert.AreEqual(0, _system.ActiveRoadblockCount);
    }
}

[TestFixture]
public class ArrestSystemTests
{
    private PoliceConfig _config;
    private ArrestSystem _system;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _system = new ArrestSystem(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void ArrestSystem_CanAttemptArrest_InRange_ReturnsTrue()
    {
        Assert.IsTrue(_system.CanAttemptArrest("officer1", Vector3.zero, new Vector3(2, 0, 0), 1f));
    }

    [Test]
    public void ArrestSystem_CanAttemptArrest_OutOfRange_ReturnsFalse()
    {
        Assert.IsFalse(_system.CanAttemptArrest("officer1", Vector3.zero, new Vector3(100, 0, 0), 1f));
    }

    [Test]
    public void ArrestSystem_CanAttemptArrest_ZeroWanted_ReturnsFalse()
    {
        Assert.IsFalse(_system.CanAttemptArrest("officer1", Vector3.zero, new Vector3(1, 0, 0), 0f));
    }

    [Test]
    public void ArrestSystem_CalculateSurrenderChance_ReturnsPositive()
    {
        float chance = _system.CalculateSurrenderChance(1f);
        Assert.Greater(chance, 0f);
        Assert.LessOrEqual(chance, 1f);
    }

    [Test]
    public void ArrestSystem_CalculateSurrenderChance_HigherWanted_LowersChance()
    {
        float lowChance = _system.CalculateSurrenderChance(1f);
        float highChance = _system.CalculateSurrenderChance(5f);
        Assert.Greater(lowChance, highChance);
    }

    [Test]
    public void ArrestSystem_IsWithinArrestRange_InRange_ReturnsTrue()
    {
        Assert.IsTrue(_system.IsWithinArrestRange(Vector3.zero, new Vector3(2, 0, 0)));
    }

    [Test]
    public void ArrestSystem_IsWithinArrestRange_OutOfRange_ReturnsFalse()
    {
        Assert.IsFalse(_system.IsWithinArrestRange(Vector3.zero, new Vector3(100, 0, 0)));
    }

    [Test]
    public void ArrestSystem_CalculateFine_ReturnsPositive()
    {
        float fine = _system.CalculateFine(CrimeType.Speeding, 1f);
        Assert.Greater(fine, 0f);
    }

    [Test]
    public void ArrestSystem_CalculateFine_HigherWanted_IncreasesFine()
    {
        float fine1 = _system.CalculateFine(CrimeType.Assault, 1f);
        float fine5 = _system.CalculateFine(CrimeType.Assault, 5f);
        Assert.Greater(fine5, fine1);
    }

    [Test]
    public void ArrestSystem_GetJailSentence_ReturnsCorrectSentence()
    {
        var sentence = _system.GetJailSentence(CrimeType.Murder, 5f);
        Assert.AreEqual(JailSentence.ExtendedDetention, sentence);
    }

    [Test]
    public void ArrestSystem_GetJailDuration_ReturnsPositive()
    {
        float duration = _system.GetJailDuration(JailSentence.MediumDetention);
        Assert.Greater(duration, 0f);
    }

    [Test]
    public void ArrestSystem_IsSuspectEscaping_Far_ReturnsTrue()
    {
        Assert.IsTrue(_system.IsSuspectEscaping(new Vector3(50, 0, 0), Vector3.zero, 10f));
    }

    [Test]
    public void ArrestSystem_IsSuspectEscaping_Close_ReturnsFalse()
    {
        Assert.IsFalse(_system.IsSuspectEscaping(new Vector3(5, 0, 0), Vector3.zero, 10f));
    }
}

[TestFixture]
public class JailSystemTests
{
    private PoliceConfig _config;
    private JailSystem _system;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _system = new JailSystem(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void JailSystem_InitializesEmpty()
    {
        Assert.AreEqual(0, _system.ActiveSentenceCount);
        Assert.IsFalse(_system.HasActiveSentences());
    }

    [Test]
    public void JailSystem_SendToJail_CreatesSentence()
    {
        var record = _system.SendToJail("player1", JailSentence.ShortDetention);
        Assert.IsNotNull(record);
        Assert.AreEqual(1, _system.ActiveSentenceCount);
        Assert.IsTrue(_system.IsInJail("player1"));
    }

    [Test]
    public void JailSystem_GetRemainingTime_ReturnsPositive()
    {
        _system.SendToJail("player1", JailSentence.MediumDetention);
        float remaining = _system.GetRemainingTime("player1");
        Assert.Greater(remaining, 0f);
    }

    [Test]
    public void JailSystem_ReleaseFromJail_RemovesSentence()
    {
        _system.SendToJail("player1", JailSentence.ShortDetention);
        _system.ReleaseFromJail("player1");
        Assert.IsFalse(_system.IsInJail("player1"));
    }

    [Test]
    public void JailSystem_EscapeJail_RemovesSentence()
    {
        _system.SendToJail("player1", JailSentence.ShortDetention);
        _system.EscapeJail("player1");
        Assert.IsFalse(_system.IsInJail("player1"));
    }

    [Test]
    public void JailSystem_GetSentenceProgress_ReturnsZeroAtStart()
    {
        _system.SendToJail("player1", JailSentence.MediumDetention);
        float progress = _system.GetSentenceProgress("player1");
        Assert.AreEqual(0f, progress, 0.01f);
    }

    [Test]
    public void JailSystem_GetSentenceDuration_ReturnsCorrect()
    {
        float shortDuration = _system.GetSentenceDuration(JailSentence.ShortDetention);
        float longDuration = _system.GetSentenceDuration(JailSentence.LongDetention);
        Assert.Greater(longDuration, shortDuration);
    }

    [Test]
    public void JailSystem_ClearAll_EmptiesEverything()
    {
        _system.SendToJail("player1", JailSentence.ShortDetention);
        _system.SendToJail("player2", JailSentence.MediumDetention);
        _system.ClearAll();
        Assert.AreEqual(0, _system.ActiveSentenceCount);
    }
}

[TestFixture]
public class FinePaymentSystemTests
{
    private PoliceConfig _config;
    private FinePaymentSystem _system;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _system = new FinePaymentSystem(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void FineSystem_IssueFine_CreatesRecord()
    {
        var fine = _system.IssueFine("player1", CrimeType.Speeding, 1f, "crime1");
        Assert.IsNotNull(fine);
        Assert.Greater(fine.GetTotalAmount(), 0f);
    }

    [Test]
    public void FineSystem_PayFine_WithEnoughMoney_Succeeds()
    {
        var fine = _system.IssueFine("player1", CrimeType.Speeding, 1f, "crime1");
        bool paid = _system.PayFine("player1", fine.FineId, 10000f);
        Assert.IsTrue(paid);
        Assert.IsTrue(fine.IsPaid);
    }

    [Test]
    public void FineSystem_PayFine_WithNotEnoughMoney_Fails()
    {
        var fine = _system.IssueFine("player1", CrimeType.Murder, 5f, "crime1");
        bool paid = _system.PayFine("player1", fine.FineId, 1f);
        Assert.IsFalse(paid);
    }

    [Test]
    public void FineSystem_CalculateTotalOwed_SumsUnpaidFines()
    {
        _system.IssueFine("player1", CrimeType.Speeding, 1f, "crime1");
        _system.IssueFine("player1", CrimeType.Assault, 2f, "crime2");

        float total = _system.CalculateTotalOwed("player1");
        Assert.Greater(total, 0f);
    }

    [Test]
    public void FineSystem_HasOutstandingFines_ReturnsCorrect()
    {
        Assert.IsFalse(_system.HasOutstandingFines("player1"));
        _system.IssueFine("player1", CrimeType.Speeding, 1f, "crime1");
        Assert.IsTrue(_system.HasOutstandingFines("player1"));
    }

    [Test]
    public void FineSystem_PayAllFines_WithEnoughMoney_PaysAll()
    {
        _system.IssueFine("player1", CrimeType.Speeding, 1f, "crime1");
        _system.IssueFine("player1", CrimeType.Assault, 1f, "crime2");

        bool paid = _system.PayAllFines("player1", 100000f);
        Assert.IsTrue(paid);
        Assert.IsFalse(_system.HasOutstandingFines("player1"));
    }

    [Test]
    public void FineSystem_ClearAll_EmptiesEverything()
    {
        _system.IssueFine("player1", CrimeType.Speeding, 1f, "crime1");
        _system.ClearAll();
        Assert.AreEqual(0, _system.GetOutstandingFineCount("player1"));
    }
}

[TestFixture]
public class VehiclePursuitSystemTests
{
    private PoliceConfig _config;
    private VehiclePursuitSystem _system;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _system = new VehiclePursuitSystem(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void VehiclePursuit_InitializesEmpty()
    {
        Assert.AreEqual(0, _system.ActivePursuitCount);
    }

    [Test]
    public void VehiclePursuit_StartPursuit_SetsState()
    {
        _system.StartPursuit("unit1", "target1");
        Assert.IsTrue(_system.IsInPursuit("unit1"));
    }

    [Test]
    public void VehiclePursuit_TerminatePursuit_Removes()
    {
        _system.StartPursuit("unit1", "target1");
        _system.TerminatePursuit("unit1");
        Assert.IsFalse(_system.IsInPursuit("unit1"));
    }

    [Test]
    public void VehiclePursuit_TargetArrested_Removes()
    {
        _system.StartPursuit("unit1", "target1");
        _system.TargetArrested("unit1");
        Assert.IsFalse(_system.IsInPursuit("unit1"));
    }

    [Test]
    public void VehiclePursuit_CalculateInterceptPosition_ReturnsPosition()
    {
        Vector3 intercept = _system.CalculateInterceptPosition(
            Vector3.zero, new Vector3(50, 0, 0), new Vector3(10, 0, 0), 30f);
        Assert.AreNotEqual(Vector3.zero, intercept);
    }

    [Test]
    public void VehiclePursuit_GetPursuitSpeedMultiplier_ReturnsPositive()
    {
        _system.StartPursuit("unit1", "target1");
        float mult = _system.GetPursuitSpeedMultiplier("unit1", 3f);
        Assert.Greater(mult, 0f);
    }
}

[TestFixture]
public class FootPursuitSystemTests
{
    private PoliceConfig _config;
    private FootPursuitSystem _system;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _system = new FootPursuitSystem(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void FootPursuit_InitializesEmpty()
    {
        Assert.AreEqual(0, _system.ActivePursuitCount);
    }

    [Test]
    public void FootPursuit_StartPursuit_SetsActive()
    {
        _system.StartPursuit("unit1", "target1", Vector3.zero);
        Assert.IsTrue(_system.IsInPursuit("unit1"));
    }

    [Test]
    public void FootPursuit_TerminatePursuit_Removes()
    {
        _system.StartPursuit("unit1", "target1", Vector3.zero);
        _system.TerminatePursuit("unit1");
        Assert.IsFalse(_system.IsInPursuit("unit1"));
    }

    [Test]
    public void FootPursuit_CanTase_InitiallyTrue()
    {
        _system.StartPursuit("unit1", "target1", Vector3.zero);
        Assert.IsTrue(_system.CanTase("unit1"));
    }

    [Test]
    public void FootPursuit_Tase_InRange_Succeeds()
    {
        _system.StartPursuit("unit1", "target1", Vector3.zero);
        bool tased = _system.Tase("unit1", Vector3.zero, new Vector3(5, 0, 0));
        Assert.IsTrue(tased);
    }

    [Test]
    public void FootPursuit_Tase_OutOfRange_Fails()
    {
        _system.StartPursuit("unit1", "target1", Vector3.zero);
        bool tased = _system.Tase("unit1", Vector3.zero, new Vector3(50, 0, 0));
        Assert.IsFalse(tased);
    }

    [Test]
    public void FootPursuit_IsWithinCatchDistance_Close_ReturnsTrue()
    {
        Assert.IsTrue(_system.IsWithinCatchDistance(Vector3.zero, new Vector3(1, 0, 0)));
    }

    [Test]
    public void FootPursuit_IsWithinCatchDistance_Far_ReturnsFalse()
    {
        Assert.IsFalse(_system.IsWithinCatchDistance(Vector3.zero, new Vector3(10, 0, 0)));
    }

    [Test]
    public void FootPursuit_CalculateChaseDirection_ReturnsNormalized()
    {
        Vector3 dir = _system.CalculateChaseDirection(Vector3.zero, new Vector3(10, 0, 0));
        Assert.AreEqual(1f, dir.magnitude, 0.01f);
    }
}

[TestFixture]
public class SWATSupportSystemTests
{
    private PoliceConfig _config;
    private SWATSupportSystem _system;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _system = new SWATSupportSystem(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void SWAT_InitializesNotDeployed()
    {
        Assert.IsFalse(_system.IsDeployed);
        Assert.AreEqual(0, _system.SWATAvailable);
    }

    [Test]
    public void SWAT_DeploySWAT_CreatesUnits()
    {
        _system.DeploySWAT();
        Assert.IsTrue(_system.IsDeployed);
        Assert.Greater(_system.SWATAvailable, 0);
    }

    [Test]
    public void SWAT_StandDown_RemovesUnits()
    {
        _system.DeploySWAT();
        _system.StandDown();
        Assert.IsFalse(_system.IsDeployed);
    }

    [Test]
    public void SWAT_GetAvailableSWATUnit_ReturnsUnit()
    {
        _system.DeploySWAT();
        var unit = _system.GetAvailableSWATUnit();
        Assert.IsNotNull(unit);
    }

    [Test]
    public void SWAT_ShouldDeployForLevel_ReturnsCorrect()
    {
        Assert.IsFalse(_system.ShouldDeployForLevel(4));
        Assert.IsTrue(_system.ShouldDeployForLevel(5));
    }
}

[TestFixture]
public class HelicopterSupportSystemTests
{
    private PoliceConfig _config;
    private HelicopterSupportSystem _system;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<PoliceConfig>();
        _system = new HelicopterSupportSystem(_config);
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void Helicopter_InitializesEmpty()
    {
        Assert.IsFalse(_system.IsDeployed);
        Assert.AreEqual(0, _system.HelicopterCount);
    }

    [Test]
    public void Helicopter_DeployHelicopter_CreatesHelicopter()
    {
        var heli = _system.DeployHelicopter(Vector3.zero);
        Assert.IsNotNull(heli);
        Assert.AreEqual(1, _system.HelicopterCount);
        Assert.IsTrue(_system.IsDeployed);
    }

    [Test]
    public void Helicopter_RecallHelicopters_RemovesAll()
    {
        _system.DeployHelicopter(Vector3.zero);
        _system.RecallHelicopters();
        Assert.IsFalse(_system.IsDeployed);
        Assert.AreEqual(0, _system.HelicopterCount);
    }

    [Test]
    public void Helicopter_CanSeeTarget_Near_ReturnsTrue()
    {
        _system.DeployHelicopter(Vector3.zero);
        Assert.IsTrue(_system.CanSeeTarget(new Vector3(10, 0, 0)));
    }

    [Test]
    public void Helicopter_IsTargetInSpotlight_InRange_ReturnsTrue()
    {
        var heli = _system.DeployHelicopter(Vector3.zero);
        Assert.IsTrue(_system.IsTargetInSpotlight(heli.HeliId, new Vector3(10, 0, 0)));
    }
}

[TestFixture]
public class PoliceDataModelTests
{
    [Test]
    public void PoliceUnitData_CanPursue_PatrolCar_ReturnsTrue()
    {
        var data = new PoliceUnitData("Officer", PoliceUnitType.PatrolCar, Vector3.zero, 0f, 0);
        Assert.IsTrue(data.CanPursue());
    }

    [Test]
    public void PoliceUnitData_CanPursue_SWATTeam_ReturnsFalse()
    {
        var data = new PoliceUnitData("SWAT", PoliceUnitType.SWATTeam, Vector3.zero, 0f, 0);
        Assert.IsFalse(data.CanPursue());
    }

    [Test]
    public void PoliceUnitData_CanSetRoadblock_PatrolCar_ReturnsTrue()
    {
        var data = new PoliceUnitData("Officer", PoliceUnitType.PatrolCar, Vector3.zero, 0f, 0);
        Assert.IsTrue(data.CanSetRoadblock());
    }

    [Test]
    public void PoliceUnitData_IsSWAT_SWATTeam_ReturnsTrue()
    {
        var data = new PoliceUnitData("SWAT", PoliceUnitType.SWATTeam, Vector3.zero, 0f, 0);
        Assert.IsTrue(data.IsSWAT());
    }

    [Test]
    public void PoliceUnitData_GetMaxSpeed_ReturnsCorrect()
    {
        var patrolCar = new PoliceUnitData("Officer", PoliceUnitType.PatrolCar, Vector3.zero, 0f, 0);
        var bike = new PoliceUnitData("Officer", PoliceUnitType.PatrolBike, Vector3.zero, 0f, 0);

        float carSpeed = patrolCar.GetMaxSpeed(60f);
        float bikeSpeed = bike.GetMaxSpeed(60f);

        Assert.Greater(carSpeed, bikeSpeed);
    }

    [Test]
    public void DispatchCall_GetPriorityScore_ReturnsCorrect()
    {
        var low = new DispatchCall();
        low.Priority = DispatchPriority.Low;
        var high = new DispatchCall();
        high.Priority = DispatchPriority.High;
        var critical = new DispatchCall();
        critical.Priority = DispatchPriority.Critical;

        Assert.Less(low.GetPriorityScore(), high.GetPriorityScore());
        Assert.Less(high.GetPriorityScore(), critical.GetPriorityScore());
    }

    [Test]
    public void JailRecord_GetRemainingTime_ReturnsPositive()
    {
        var record = new JailRecord("player1", JailSentence.MediumDetention, 60f);
        Assert.AreEqual(60f, record.GetRemainingTime(), 0.01f);
    }

    [Test]
    public void JailRecord_IsFinished_FalseAtStart()
    {
        var record = new JailRecord("player1", JailSentence.ShortDetention, 30f);
        Assert.IsFalse(record.IsFinished());
    }

    [Test]
    public void FineRecord_GetTotalAmount_IncludesMultiplier()
    {
        var fine = new FineRecord("player1", FineCategory.Speeding, 100f, "crime1", 2f);
        Assert.AreEqual(200f, fine.GetTotalAmount(), 0.01f);
    }

    [Test]
    public void FineRecord_MarkPaid_SetsPaid()
    {
        var fine = new FineRecord("player1", FineCategory.Speeding, 100f, "crime1", 1f);
        Assert.IsFalse(fine.IsPaid);
        fine.MarkPaid();
        Assert.IsTrue(fine.IsPaid);
    }
}

[TestFixture]
public class PoliceUnitStateTests
{
    [Test]
    public void PoliceUnitState_DefaultState_IsIdle()
    {
        var state = new PoliceUnitState();
        Assert.AreEqual(PoliceState.Idle, state.CurrentState);
        Assert.IsTrue(state.IsAvailable);
    }

    [Test]
    public void PoliceUnitState_SetUnitId_SetsId()
    {
        var state = new PoliceUnitState("unit1");
        Assert.AreEqual("unit1", state.UnitId);
    }
}

[TestFixture]
public class RoadblockDataTests
{
    [Test]
    public void RoadblockData_Create_SetsProperties()
    {
        var rb = new RoadblockData(RoadblockType.PoliceCars, new Vector3(10, 0, 0), 45f);
        Assert.AreEqual(RoadblockType.PoliceCars, rb.Type);
        Assert.AreEqual(new Vector3(10, 0, 0), rb.Position);
        Assert.AreEqual(45f, rb.Rotation);
        Assert.IsFalse(rb.IsReady);
    }

    [Test]
    public void RoadblockData_GetEffectiveWidth_DifferentTypes()
    {
        var cars = new RoadblockData(RoadblockType.PoliceCars, Vector3.zero, 0f);
        var spike = new RoadblockData(RoadblockType.SpikeStrip, Vector3.zero, 0f);
        var barricade = new RoadblockData(RoadblockType.Barricade, Vector3.zero, 0f);

        Assert.Greater(cars.GetEffectiveWidth(), spike.GetEffectiveWidth());
        Assert.Greater(barricade.GetEffectiveWidth(), spike.GetEffectiveWidth());
    }

    [Test]
    public void RoadblockData_Activate_SetsActive()
    {
        var rb = new RoadblockData(RoadblockType.PoliceCars, Vector3.zero, 0f);
        rb.Activate();
        Assert.IsTrue(rb.IsActive);
    }
}

[TestFixture]
public class RadioMessageTests
{
    [Test]
    public void RadioMessage_Create_SetsProperties()
    {
        var msg = new RadioMessage(RadioMessageType.BackupRequest, "unit1", "Need backup", new Vector3(10, 0, 0));
        Assert.AreEqual(RadioMessageType.BackupRequest, msg.Type);
        Assert.AreEqual("unit1", msg.SenderUnitId);
        Assert.AreEqual("Need backup", msg.Content);
        Assert.IsFalse(msg.IsDelivered);
    }

    [Test]
    public void RadioMessage_IsExpired_Fresh_ReturnsFalse()
    {
        var msg = new RadioMessage();
        Assert.IsFalse(msg.IsExpired(60f));
    }
}
