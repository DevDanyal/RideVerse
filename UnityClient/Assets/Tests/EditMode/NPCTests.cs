using NUnit.Framework;
using UnityEngine;
using RideVerse.NPC.Core;
using RideVerse.NPC.Brain;
using RideVerse.NPC.States;
using RideVerse.NPC.Profession;
using RideVerse.NPC.Reputation;
using RideVerse.NPC.Schedule;
using RideVerse.NPC.Crowd;
using RideVerse.NPC.Performance;
using RideVerse.NPC.Vehicle;
using RideVerse.NPC.Interaction;
using RideVerse.NPC.Movement;

[TestFixture]
public class NPCDataTests
{
    [Test]
    public void NPCData_DefaultConstructor_GeneratesId()
    {
        var data = new NPCData();
        Assert.IsFalse(string.IsNullOrEmpty(data.Id));
        Assert.AreEqual(8, data.Id.Length);
    }

    [Test]
    public void NPCData_ParameterizedConstructor_SetsProperties()
    {
        var data = new NPCData("test001", "Ahmed", 2, new Vector3(10f, 0f, 20f), 90f, 1);
        Assert.AreEqual("test001", data.Id);
        Assert.AreEqual("Ahmed", data.DisplayName);
        Assert.AreEqual(2, data.ProfessionTypeIndex);
        Assert.AreEqual(90f, data.SpawnRotationY);
        Assert.AreEqual(1, data.DistrictIndex);
    }

    [Test]
    public void NPCData_GetSpawnPosition_ReturnsCorrectVector()
    {
        var data = new NPCData();
        data.SpawnPositionX = 10f;
        data.SpawnPositionY = 5f;
        data.SpawnPositionZ = 20f;
        Vector3 pos = data.GetSpawnPosition();
        Assert.AreEqual(10f, pos.x);
        Assert.AreEqual(5f, pos.y);
        Assert.AreEqual(20f, pos.z);
    }

    [Test]
    public void NPCData_Serialization_Works()
    {
        var data = new NPCData("id1", "Ali", 0, new Vector3(1f, 2f, 3f), 45f, 2);
        string json = JsonUtility.ToJson(data);
        var deserialized = JsonUtility.FromJson<NPCData>(json);
        Assert.AreEqual("id1", deserialized.Id);
        Assert.AreEqual("Ali", deserialized.DisplayName);
        Assert.AreEqual(0, deserialized.ProfessionTypeIndex);
    }
}

[TestFixture]
public class NPCConfigTests
{
    [Test]
    public void NPCConfig_DefaultValues_AreValid()
    {
        var config = ScriptableObject.CreateInstance<NPCConfig>();

        Assert.Greater(config.maxActiveNPCs, 0);
        Assert.Greater(config.walkSpeed, 0f);
        Assert.Greater(config.runSpeed, config.walkSpeed);
        Assert.Greater(config.vehicleSpeed, config.runSpeed);
        Assert.Greater(config.interactionRange, 0f);
        Assert.Greater(config.spawnRadius, 0f);
        Assert.Greater(config.despawnRadius, config.spawnRadius);
        Assert.Greater(config.lodDistanceFull, 0f);
        Assert.Greater(config.lodDistanceMedium, config.lodDistanceFull);
        Assert.Greater(config.lodDistanceLow, config.lodDistanceMedium);
        Assert.IsNotNull(config.maleNames);
        Assert.IsNotNull(config.femaleNames);
        Assert.Greater(config.maleNames.Length, 0);
        Assert.Greater(config.femaleNames.Length, 0);

        Object.DestroyImmediate(config);
    }

    [Test]
    public void NPCConfig_ScheduleHours_AreOrdered()
    {
        var config = ScriptableObject.CreateInstance<NPCConfig>();
        Assert.Less(config.wakeUpHour, config.workStartHour);
        Assert.Less(config.workStartHour, config.lunchHour);
        Assert.Less(config.lunchHour, config.workEndHour);
        Assert.Less(config.workEndHour, config.dinnerHour);
        Assert.Less(config.dinnerHour, config.sleepHour);
        Object.DestroyImmediate(config);
    }
}

[TestFixture]
public class BTNodeTests
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
            new BTCondition(() => true),
            new BTCondition(() => false));
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
    public void BTSelector_Reset_ResetsIndex()
    {
        var sel = new BTSelector(
            new BTCondition(() => true),
            new BTCondition(() => false));
        sel.Evaluate();
        sel.Reset();
        Assert.AreEqual(BTNodeStatus.Success, sel.Evaluate());
    }
}

[TestFixture]
public class StateMachineTests
{
    private class TestState : INPCState
    {
        public int EnterCount;
        public int ExitCount;
        public int TickCount;

        public void Enter() { EnterCount++; }
        public void Tick() { TickCount++; }
        public void Exit() { ExitCount++; }
    }

    [Test]
    public void StateMachine_SetInitialState_CallsEnter()
    {
        var sm = new NPCStateMachine();
        var state = new TestState();
        sm.RegisterState(NPCStateType.Idle, state);
        sm.SetInitialState(NPCStateType.Idle);

        Assert.AreEqual(1, state.EnterCount);
        Assert.AreEqual(NPCStateType.Idle, sm.CurrentStateType);
    }

    [Test]
    public void StateMachine_ChangeState_CallsExitAndEnter()
    {
        var sm = new NPCStateMachine();
        var idleState = new TestState();
        var walkState = new TestState();
        sm.RegisterState(NPCStateType.Idle, idleState);
        sm.RegisterState(NPCStateType.Walking, walkState);
        sm.SetInitialState(NPCStateType.Idle);

        sm.ChangeState(NPCStateType.Walking);

        Assert.AreEqual(1, idleState.ExitCount);
        Assert.AreEqual(1, walkState.EnterCount);
        Assert.AreEqual(NPCStateType.Walking, sm.CurrentStateType);
    }

    [Test]
    public void StateMachine_SameState_DoesNotTransition()
    {
        var sm = new NPCStateMachine();
        var state = new TestState();
        sm.RegisterState(NPCStateType.Idle, state);
        sm.SetInitialState(NPCStateType.Idle);

        sm.ChangeState(NPCStateType.Idle);
        Assert.AreEqual(1, state.EnterCount);
    }

    [Test]
    public void StateMachine_Update_CallsTick()
    {
        var sm = new NPCStateMachine();
        var state = new TestState();
        sm.RegisterState(NPCStateType.Idle, state);
        sm.SetInitialState(NPCStateType.Idle);

        sm.Update();
        sm.Update();
        Assert.AreEqual(2, state.TickCount);
    }

    [Test]
    public void StateMachine_OnStateChanged_Fires()
    {
        var sm = new NPCStateMachine();
        NPCStateType? from = null;
        NPCStateType? to = null;
        sm.OnStateChanged += (f, t) => { from = f; to = t; };

        sm.RegisterState(NPCStateType.Idle, new TestState());
        sm.RegisterState(NPCStateType.Walking, new TestState());
        sm.SetInitialState(NPCStateType.Idle);
        sm.ChangeState(NPCStateType.Walking);

        Assert.AreEqual(NPCStateType.Idle, from);
        Assert.AreEqual(NPCStateType.Walking, to);
    }
}

[TestFixture]
public class ProfessionTests
{
    [Test]
    public void ProfessionType_HasAllValues()
    {
        Assert.AreEqual(7, System.Enum.GetValues(typeof(ProfessionType)).Length);
    }

    [Test]
    public void ProfessionType_AllValuesAreDefined()
    {
        Assert.IsTrue(System.Enum.IsDefined(typeof(ProfessionType), ProfessionType.Citizen));
        Assert.IsTrue(System.Enum.IsDefined(typeof(ProfessionType), ProfessionType.Police));
        Assert.IsTrue(System.Enum.IsDefined(typeof(ProfessionType), ProfessionType.Mechanic));
        Assert.IsTrue(System.Enum.IsDefined(typeof(ProfessionType), ProfessionType.Shopkeeper));
        Assert.IsTrue(System.Enum.IsDefined(typeof(ProfessionType), ProfessionType.TaxiDriver));
        Assert.IsTrue(System.Enum.IsDefined(typeof(ProfessionType), ProfessionType.Doctor));
        Assert.IsTrue(System.Enum.IsDefined(typeof(ProfessionType), ProfessionType.BusinessOwner));
    }
}

[TestFixture]
public class ReputationTests
{
    private GameObject _testObj;
    private NPCReputation _reputation;

    [SetUp]
    public void SetUp()
    {
        _testObj = new GameObject("TestNPC");
        _reputation = _testObj.AddComponent<NPCReputation>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_testObj);
    }

    [Test]
    public void ReputationLevel_HasAllValues()
    {
        Assert.AreEqual(4, System.Enum.GetValues(typeof(ReputationLevel)).Length);
    }

    [Test]
    public void Reputation_Initialize_SetsNeutral()
    {
        _reputation.Initialize();
        Assert.AreEqual(ReputationLevel.Neutral, _reputation.Level);
        Assert.AreEqual(50f, _reputation.Trust, 0.01f);
        Assert.AreEqual(50f, _reputation.Friendliness, 0.01f);
        Assert.AreEqual(0f, _reputation.Fear, 0.01f);
    }

    [Test]
    public void Reputation_InitializeWithLevel_SetsCorrectValues()
    {
        _reputation.Initialize(ReputationLevel.Friendly);
        Assert.AreEqual(ReputationLevel.Friendly, _reputation.Level);
        Assert.Greater(_reputation.Friendliness, 60f);

        _reputation.Initialize(ReputationLevel.Fear);
        Assert.AreEqual(ReputationLevel.Fear, _reputation.Level);
        Assert.Greater(_reputation.Fear, 60f);
    }

    [Test]
    public void Reputation_ModifyTrust_ClampsAndUpdatesLevel()
    {
        _reputation.Initialize();
        _reputation.ModifyTrust(50f);
        Assert.AreEqual(100f, _reputation.Trust);

        _reputation.ModifyTrust(-80f);
        Assert.AreEqual(0f, _reputation.Trust);
    }

    [Test]
    public void Reputation_ModifyFear_ChangesLevelToFear()
    {
        _reputation.Initialize();
        _reputation.ModifyFear(70f);
        Assert.AreEqual(ReputationLevel.Fear, _reputation.Level);
    }

    [Test]
    public void Reputation_ModifyFriendliness_ChangesLevelToFriendly()
    {
        _reputation.Initialize();
        _reputation.ModifyFriendliness(30f);
        Assert.AreEqual(ReputationLevel.Friendly, _reputation.Level);
    }

    [Test]
    public void Reputation_GetLevelEmoji_ReturnsString()
    {
        _reputation.Initialize();
        Assert.IsFalse(string.IsNullOrEmpty(_reputation.GetLevelEmoji()));
    }
}

[TestFixture]
public class NPCStateTypeTests
{
    [Test]
    public void NPCStateType_HasAllValues()
    {
        Assert.AreEqual(14, System.Enum.GetValues(typeof(NPCStateType)).Length);
    }
}

[TestFixture]
public class NPCGroupTests
{
    [Test]
    public void NPCGroup_DefaultConstructor()
    {
        var group = new NPCGroup();
        Assert.IsFalse(string.IsNullOrEmpty(group.Id));
        Assert.AreEqual(6, group.Id.Length);
        Assert.AreEqual(0, group.MemberCount);
        Assert.IsFalse(group.IsActive);
    }

    [Test]
    public void NPCGroup_AddMember_IncreasesCount()
    {
        var group = new NPCGroup();
        var go1 = new GameObject("NPC1");
        var brain1 = go1.AddComponent<NPCBrain>();

        group.AddMember(brain1);
        Assert.AreEqual(1, group.MemberCount);

        Object.DestroyImmediate(go1);
    }

    [Test]
    public void NPCGroup_RemoveMember_DecreasesCount()
    {
        var group = new NPCGroup();
        var go1 = new GameObject("NPC1");
        var brain1 = go1.AddComponent<NPCBrain>();

        group.AddMember(brain1);
        group.RemoveMember(brain1);
        Assert.AreEqual(0, group.MemberCount);

        Object.DestroyImmediate(go1);
    }

    [Test]
    public void NPCGroup_AddDuplicate_DoesNotIncrease()
    {
        var group = new NPCGroup();
        var go1 = new GameObject("NPC1");
        var brain1 = go1.AddComponent<NPCBrain>();

        group.AddMember(brain1);
        group.AddMember(brain1);
        Assert.AreEqual(1, group.MemberCount);

        Object.DestroyImmediate(go1);
    }
}

[TestFixture]
public class NPCScheduleTests
{
    [Test]
    public void Schedule_ActivityNames_AreDefined()
    {
        string[] activities = { "Sleep", "WakeUp", "GoToWork", "Lunch", "Work", "Shop", "GoHome", "Rest" };
        Assert.AreEqual(8, activities.Length);
        foreach (var activity in activities)
        {
            Assert.IsFalse(string.IsNullOrEmpty(activity));
        }
    }

    [Test]
    public void Schedule_HourRange_Is24Hours()
    {
        var config = ScriptableObject.CreateInstance<NPCConfig>();
        Assert.GreaterOrEqual(config.wakeUpHour, 0f);
        Assert.LessOrEqual(config.sleepHour, 24f);
        Object.DestroyImmediate(config);
    }
}

[TestFixture]
public class NPCVehicleTests
{
    [Test]
    public void NPCVehicleSpawner_MaxVehicles_IsPositive()
    {
        var go = new GameObject("VehicleSpawner");
        var spawner = go.AddComponent<NPCVehicleSpawner>();
        Assert.Greater(10, 0);
        Object.DestroyImmediate(go);
    }
}

[TestFixture]
public class NPCLODTests
{
    [Test]
    public void NPCLODLevel_HasAllValues()
    {
        Assert.AreEqual(4, System.Enum.GetValues(typeof(NPCLODLevel)).Length);
    }

    [Test]
    public void NPCLODLevel_ValuesAreDefined()
    {
        Assert.IsTrue(System.Enum.IsDefined(typeof(NPCLODLevel), NPCLODLevel.Full));
        Assert.IsTrue(System.Enum.IsDefined(typeof(NPCLODLevel), NPCLODLevel.Medium));
        Assert.IsTrue(System.Enum.IsDefined(typeof(NPCLODLevel), NPCLODLevel.Low));
        Assert.IsTrue(System.Enum.IsDefined(typeof(NPCLODLevel), NPCLODLevel.Culled));
    }
}

[TestFixture]
public class NPCInteractionTests
{
    [Test]
    public void Greeting_IsNotEmpty()
    {
        var go = new GameObject("TestNPC");
        var brain = go.AddComponent<NPCBrain>();
        var interaction = go.AddComponent<NPCInteraction>();
        interaction.Initialize(brain);

        string greeting = interaction.GetGreeting();
        Assert.IsFalse(string.IsNullOrEmpty(greeting));

        Object.DestroyImmediate(go);
    }

    [Test]
    public void Farewell_IsNotEmpty()
    {
        var go = new GameObject("TestNPC");
        var brain = go.AddComponent<NPCBrain>();
        var interaction = go.AddComponent<NPCInteraction>();
        interaction.Initialize(brain);

        string farewell = interaction.GetFarewell();
        Assert.IsFalse(string.IsNullOrEmpty(farewell));

        Object.DestroyImmediate(go);
    }
}

[TestFixture]
public class NPCMovementTests
{
    [Test]
    public void NPCMovement_HasReachedDestination_Close_ReturnsTrue()
    {
        var go = new GameObject("TestNPC");
        var cc = go.AddComponent<CharacterController>();
        var movement = go.AddComponent<NPCMovement>();
        movement.Initialize(cc, 2f, 5f);
        go.transform.position = new Vector3(10f, 0f, 10f);

        Assert.IsTrue(movement.HasReachedDestination(new Vector3(10.5f, 0f, 10f)));

        Object.DestroyImmediate(go);
    }

    [Test]
    public void NPCMovement_HasReachedDestination_Far_ReturnsFalse()
    {
        var go = new GameObject("TestNPC");
        var cc = go.AddComponent<CharacterController>();
        var movement = go.AddComponent<NPCMovement>();
        movement.Initialize(cc, 2f, 5f);
        go.transform.position = Vector3.zero;

        Assert.IsFalse(movement.HasReachedDestination(new Vector3(10f, 0f, 10f)));

        Object.DestroyImmediate(go);
    }

    [Test]
    public void NPCMovement_Stop_StopsMoving()
    {
        var go = new GameObject("TestNPC");
        var cc = go.AddComponent<CharacterController>();
        var movement = go.AddComponent<NPCMovement>();
        movement.Initialize(cc, 2f, 5f);
        movement.Stop();
        Assert.IsFalse(movement.IsMoving);

        Object.DestroyImmediate(go);
    }

    [Test]
    public void NPCMovement_SetSpeed_UpdatesSpeed()
    {
        var go = new GameObject("TestNPC");
        var cc = go.AddComponent<CharacterController>();
        var movement = go.AddComponent<NPCMovement>();
        movement.Initialize(cc, 2f, 5f);
        movement.SetSpeed(5f);
        Assert.AreEqual(5f, movement.Speed);

        Object.DestroyImmediate(go);
    }
}

[TestFixture]
public class NPCDataSerializationTests
{
    [Test]
    public void NPCData_MultipleInstances_HaveUniqueIds()
    {
        var data1 = new NPCData();
        var data2 = new NPCData();
        Assert.AreNotEqual(data1.Id, data2.Id);
    }

    [Test]
    public void NPCData_AllFieldsSurviveSerialization()
    {
        var data = new NPCData("abc12345", "TestNPC", 3, new Vector3(100f, 50f, 200f), 180f, 4);
        string json = JsonUtility.ToJson(data);
        var result = JsonUtility.FromJson<NPCData>(json);

        Assert.AreEqual("abc12345", result.Id);
        Assert.AreEqual("TestNPC", result.DisplayName);
        Assert.AreEqual(3, result.ProfessionTypeIndex);
        Assert.AreEqual(100f, result.SpawnPositionX);
        Assert.AreEqual(50f, result.SpawnPositionY);
        Assert.AreEqual(200f, result.SpawnPositionZ);
        Assert.AreEqual(180f, result.SpawnRotationY);
        Assert.AreEqual(4, result.DistrictIndex);
    }
}
