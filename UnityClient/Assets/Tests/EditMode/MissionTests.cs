using NUnit.Framework;
using UnityEngine;
using System.Collections.Generic;
using RideVerse.Mission.Core;

// ===== ENUM TESTS =====

[TestFixture]
public class MissionEnumTests
{
    [Test]
    public void MissionType_HasAllValues()
    {
        Assert.AreEqual(13, System.Enum.GetValues(typeof(MissionType)).Length);
    }

    [Test]
    public void MissionState_HasAllValues()
    {
        Assert.AreEqual(8, System.Enum.GetValues(typeof(MissionState)).Length);
    }

    [Test]
    public void MissionDifficulty_HasAllValues()
    {
        Assert.AreEqual(5, System.Enum.GetValues(typeof(MissionDifficulty)).Length);
    }

    [Test]
    public void ObjectiveType_HasAllValues()
    {
        Assert.AreEqual(10, System.Enum.GetValues(typeof(ObjectiveType)).Length);
    }

    [Test]
    public void ObjectiveState_HasAllValues()
    {
        Assert.AreEqual(4, System.Enum.GetValues(typeof(ObjectiveState)).Length);
    }

    [Test]
    public void CheckpointType_HasAllValues()
    {
        Assert.AreEqual(6, System.Enum.GetValues(typeof(CheckpointType)).Length);
    }

    [Test]
    public void RewardType_HasAllValues()
    {
        Assert.AreEqual(10, System.Enum.GetValues(typeof(RewardType)).Length);
    }

    [Test]
    public void FailureReason_HasAllValues()
    {
        Assert.AreEqual(8, System.Enum.GetValues(typeof(FailureReason)).Length);
    }

    [Test]
    public void DialogueSpeakerType_HasAllValues()
    {
        Assert.AreEqual(4, System.Enum.GetValues(typeof(DialogueSpeakerType)).Length);
    }

    [Test]
    public void CutsceneActionType_HasAllValues()
    {
        Assert.AreEqual(8, System.Enum.GetValues(typeof(CutsceneActionType)).Length);
    }

    [Test]
    public void TriggerZoneShape_HasAllValues()
    {
        Assert.AreEqual(3, System.Enum.GetValues(typeof(TriggerZoneShape)).Length);
    }

    [Test]
    public void MissionMarkerType_HasAllValues()
    {
        Assert.AreEqual(6, System.Enum.GetValues(typeof(MissionMarkerType)).Length);
    }

    [Test]
    public void DailyMissionReset_HasAllValues()
    {
        Assert.AreEqual(4, System.Enum.GetValues(typeof(DailyMissionReset)).Length);
    }

    [Test]
    public void AchievementTriggerType_HasAllValues()
    {
        Assert.AreEqual(9, System.Enum.GetValues(typeof(AchievementTriggerType)).Length);
    }
}

// ===== CONFIG TESTS =====

[TestFixture]
public class MissionConfigTests
{
    [Test]
    public void MissionConfig_DefaultValues_AreValid()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();

        Assert.Greater(config.maxActiveMissions, 0);
        Assert.Greater(config.missionPickupRange, 0f);
        Assert.Greater(config.objectiveUpdateInterval, 0f);
        Assert.Greater(config.easyRewardMultiplier, 0f);
        Assert.Greater(config.normalRewardMultiplier, config.easyRewardMultiplier);
        Assert.Greater(config.hardRewardMultiplier, config.normalRewardMultiplier);
        Assert.Greater(config.defaultTimeLimit, 0f);
        Assert.Greater(config.warningTimeThreshold, 0f);
        Assert.Greater(config.checkpointRadius, 0f);
        Assert.Greater(config.maxObjectivesPerMission, 0);
        Assert.Greater(config.dialogueTextSpeed, 0f);
        Assert.Greater(config.defaultFadeDuration, 0f);
        Assert.Greater(config.markerUpdateInterval, 0f);
        Assert.Greater(config.defaultTriggerRadius, 0f);
        Assert.Greater(config.triggerCheckInterval, 0f);
        Assert.Greater(config.tutorialHighlightDuration, 0f);
        Assert.Greater(config.maxSideMissionsPerDay, 0);
        Assert.Greater(config.dailyMissionCount, 0);
        Assert.Greater(config.randomEventBaseChance, 0f);
        Assert.Greater(config.autoSaveInterval, 0f);
        Assert.Greater(config.maxRetries, 0);
    }
}

// ===== DATA MODEL TESTS =====

[TestFixture]
public class MissionDataTests
{
    [Test]
    public void MissionData_DefaultConstructor_SetsDefaults()
    {
        var data = new MissionData();

        Assert.IsNotNull(data.MissionId);
        Assert.AreEqual(8, data.MissionId.Length);
        Assert.AreEqual(MissionState.Locked, data.State);
        Assert.IsNotNull(data.BonusRewards);
        Assert.IsNotNull(data.Checkpoints);
        Assert.IsNotNull(data.Objectives);
        Assert.IsNotNull(data.DialogueLines);
        Assert.IsNotNull(data.CutsceneEvents);
        Assert.IsNotNull(data.UnlockedMissionIds);
        Assert.AreEqual(3, data.MaxRetries);
    }

    [Test]
    public void MissionData_ParameterizedConstructor_SetsValues()
    {
        var data = new MissionData("test_001", "Test Mission", MissionType.Delivery, MissionDifficulty.Normal);

        Assert.AreEqual("test_001", data.MissionId);
        Assert.AreEqual("Test Mission", data.MissionName);
        Assert.AreEqual(MissionType.Delivery, data.Type);
        Assert.AreEqual(MissionDifficulty.Normal, data.Difficulty);
        Assert.AreEqual(MissionState.Locked, data.State);
    }

    [Test]
    public void MissionData_GetTimeRemaining_ReturnsCorrect()
    {
        var data = new MissionData { TimeLimit = 100f, ElapsedTime = 30f };
        Assert.AreEqual(70f, data.GetTimeRemaining(), 0.01f);
    }

    [Test]
    public void MissionData_GetTimeRemaining_NeverNegative()
    {
        var data = new MissionData { TimeLimit = 50f, ElapsedTime = 100f };
        Assert.AreEqual(0f, data.GetTimeRemaining(), 0.01f);
    }

    [Test]
    public void MissionData_IsTimed_TrueWhenTimeLimitPositive()
    {
        var data = new MissionData { TimeLimit = 100f };
        Assert.IsTrue(data.IsTimed);
    }

    [Test]
    public void MissionData_IsTimed_FalseWhenZero()
    {
        var data = new MissionData { TimeLimit = 0f };
        Assert.IsFalse(data.IsTimed);
    }

    [Test]
    public void MissionData_AreAllObjectivesComplete_TrueWhenAllDone()
    {
        var data = new MissionData();
        data.Objectives.Add(new MissionObjectiveData { State = ObjectiveState.Completed });
        data.Objectives.Add(new MissionObjectiveData { State = ObjectiveState.Completed });
        Assert.IsTrue(data.AreAllObjectivesComplete());
    }

    [Test]
    public void MissionData_AreAllObjectivesComplete_FalseWhenIncomplete()
    {
        var data = new MissionData();
        data.Objectives.Add(new MissionObjectiveData { State = ObjectiveState.Completed });
        data.Objectives.Add(new MissionObjectiveData { State = ObjectiveState.Active });
        Assert.IsFalse(data.AreAllObjectivesComplete());
    }

    [Test]
    public void MissionData_AreAllObjectivesComplete_FalseWhenEmpty()
    {
        var data = new MissionData();
        Assert.IsFalse(data.AreAllObjectivesComplete());
    }

    [Test]
    public void MissionData_ObjectiveProgress_ReturnsCorrect()
    {
        var data = new MissionData();
        data.Objectives.Add(new MissionObjectiveData { State = ObjectiveState.Completed });
        data.Objectives.Add(new MissionObjectiveData { State = ObjectiveState.Active });
        Assert.AreEqual(0.5f, data.ObjectiveProgress(), 0.01f);
    }

    [Test]
    public void MissionData_ObjectiveProgress_ZeroWhenEmpty()
    {
        var data = new MissionData();
        Assert.AreEqual(0f, data.ObjectiveProgress(), 0.01f);
    }
}

// ===== CHECKPOINT DATA TESTS =====

[TestFixture]
public class MissionCheckpointDataTests
{
    [Test]
    public void CheckpointData_DefaultConstructor()
    {
        var cp = new MissionCheckpointData();
        Assert.IsNotNull(cp.CheckpointId);
        Assert.AreEqual(8, cp.CheckpointId.Length);
        Assert.AreEqual(10f, cp.Radius);
        Assert.IsFalse(cp.IsReached);
    }

    [Test]
    public void CheckpointData_ParameterizedConstructor()
    {
        var cp = new MissionCheckpointData(CheckpointType.Start, new Vector3(10, 0, 5), 1);
        Assert.AreEqual(CheckpointType.Start, cp.Type);
        Assert.AreEqual(new Vector3(10, 0, 5), cp.Position);
        Assert.AreEqual(1, cp.Order);
    }
}

// ===== OBJECTIVE DATA TESTS =====

[TestFixture]
public class MissionObjectiveDataTests
{
    [Test]
    public void ObjectiveData_DefaultConstructor()
    {
        var obj = new MissionObjectiveData();
        Assert.IsNotNull(obj.ObjectiveId);
        Assert.AreEqual(ObjectiveState.Inactive, obj.State);
        Assert.AreEqual(10f, obj.TargetRadius);
        Assert.IsFalse(obj.IsOptional);
    }

    [Test]
    public void ObjectiveData_Progress_ReturnsCorrect()
    {
        var obj = new MissionObjectiveData { RequiredCount = 5, CurrentCount = 3 };
        Assert.AreEqual(0.6f, obj.Progress, 0.01f);
    }

    [Test]
    public void ObjectiveData_IsComplete_TrueWhenDone()
    {
        var obj = new MissionObjectiveData { RequiredCount = 3, CurrentCount = 3 };
        Assert.IsTrue(obj.IsComplete);
    }

    [Test]
    public void ObjectiveData_IsComplete_FalseWhenIncomplete()
    {
        var obj = new MissionObjectiveData { RequiredCount = 5, CurrentCount = 2 };
        Assert.IsFalse(obj.IsComplete);
    }
}

// ===== MISSION SAVE DATA TESTS =====

[TestFixture]
public class MissionSaveDataTests
{
    [Test]
    public void SaveData_DefaultConstructor()
    {
        var save = new MissionSaveData();
        Assert.IsNotNull(save.ActiveMissions);
        Assert.IsNotNull(save.CompletedMissions);
        Assert.IsNotNull(save.FailedMissions);
        Assert.AreEqual(0, save.TotalMissionsCompleted);
    }
}

// ===== MISSION PROGRESS SNAPSHOT TESTS =====

[TestFixture]
public class MissionProgressSnapshotTests
{
    [Test]
    public void Snapshot_CompletionPercentage_ReturnsCorrect()
    {
        var snap = new MissionProgressSnapshot { CompletedObjectives = 3, TotalObjectives = 10 };
        Assert.AreEqual(30f, snap.CompletionPercentage, 0.01f);
    }

    [Test]
    public void Snapshot_CompletionPercentage_ZeroWhenNoObjectives()
    {
        var snap = new MissionProgressSnapshot { CompletedObjectives = 0, TotalObjectives = 0 };
        Assert.AreEqual(0f, snap.CompletionPercentage, 0.01f);
    }
}

// ===== MISSION STATS TESTS =====

[TestFixture]
public class MissionStatsTests
{
    [Test]
    public void Stats_CompletionRate_ReturnsCorrect()
    {
        var stats = new MissionStats { TotalMissionsStarted = 10, TotalMissionsCompleted = 7 };
        Assert.AreEqual(70f, stats.CompletionRate, 0.01f);
    }

    [Test]
    public void Stats_FailureRate_ReturnsCorrect()
    {
        var stats = new MissionStats { TotalMissionsStarted = 10, TotalMissionsFailed = 3 };
        Assert.AreEqual(30f, stats.FailureRate, 0.01f);
    }

    [Test]
    public void Stats_CompletionRate_ZeroWhenNoMissions()
    {
        var stats = new MissionStats();
        Assert.AreEqual(0f, stats.CompletionRate, 0.01f);
    }
}

// ===== STATE MACHINE TESTS =====

[TestFixture]
public class MissionStateMachineTests
{
    [Test]
    public void StateMachine_InitialState_IsLocked()
    {
        var sm = new MissionStateMachine();
        Assert.AreEqual(MissionState.Locked, sm.CurrentState);
        Assert.IsFalse(sm.HasMission);
    }

    [Test]
    public void StateMachine_SetMission_SetsMission()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Available };
        sm.SetMission(mission);
        Assert.IsTrue(sm.HasMission);
        Assert.AreEqual(MissionState.Available, sm.CurrentState);
    }

    [Test]
    public void StateMachine_AcceptTransition_Valid()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Available };
        sm.SetMission(mission);
        Assert.IsTrue(sm.TransitionTo(MissionState.Accepted));
        Assert.AreEqual(MissionState.Accepted, sm.CurrentState);
    }

    [Test]
    public void StateMachine_AcceptTransition_InvalidFromLocked()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Locked };
        sm.SetMission(mission);
        Assert.IsFalse(sm.TransitionTo(MissionState.Accepted));
    }

    [Test]
    public void StateMachine_StartTransition_FromAccepted()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Accepted };
        sm.SetMission(mission);
        Assert.IsTrue(sm.TransitionTo(MissionState.InProgress));
        Assert.AreEqual(MissionState.InProgress, sm.CurrentState);
    }

    [Test]
    public void StateMachine_CompleteTransition_FromInProgress()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.InProgress };
        sm.SetMission(mission);
        Assert.IsTrue(sm.TransitionTo(MissionState.Completed));
        Assert.AreEqual(MissionState.Completed, sm.CurrentState);
    }

    [Test]
    public void StateMachine_FailTransition_FromInProgress()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.InProgress };
        sm.SetMission(mission);
        Assert.IsTrue(sm.TransitionTo(MissionState.Failed));
        Assert.AreEqual(MissionState.Failed, sm.CurrentState);
    }

    [Test]
    public void StateMachine_PauseTransition_FromInProgress()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.InProgress };
        sm.SetMission(mission);
        Assert.IsTrue(sm.TransitionTo(MissionState.Paused));
        Assert.AreEqual(MissionState.Paused, sm.CurrentState);
    }

    [Test]
    public void StateMachine_ResumeTransition_FromPaused()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Paused };
        sm.SetMission(mission);
        Assert.IsTrue(sm.TransitionTo(MissionState.InProgress));
        Assert.AreEqual(MissionState.InProgress, sm.CurrentState);
    }

    [Test]
    public void StateMachine_CancelTransition_FromAccepted()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Accepted };
        sm.SetMission(mission);
        Assert.IsTrue(sm.TransitionTo(MissionState.Cancelled));
        Assert.AreEqual(MissionState.Cancelled, sm.CurrentState);
    }

    [Test]
    public void StateMachine_CompleteTransition_InvalidFromAvailable()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Available };
        sm.SetMission(mission);
        Assert.IsFalse(sm.TransitionTo(MissionState.Completed));
    }

    [Test]
    public void StateMachine_Retry_FromFailed()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Failed };
        sm.SetMission(mission);
        Assert.IsTrue(sm.TransitionTo(MissionState.InProgress));
        Assert.AreEqual(MissionState.InProgress, sm.CurrentState);
    }

    [Test]
    public void StateMachine_CanAccept_FromAvailable()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Available };
        sm.SetMission(mission);
        Assert.IsTrue(sm.CanAccept());
    }

    [Test]
    public void StateMachine_CanStart_FromAccepted()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Accepted };
        sm.SetMission(mission);
        Assert.IsTrue(sm.CanStart());
    }

    [Test]
    public void StateMachine_CanPause_FromInProgress()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.InProgress };
        sm.SetMission(mission);
        Assert.IsTrue(sm.CanPause());
    }

    [Test]
    public void StateMachine_CanRetry_FromFailed()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Failed, RetryCount = 0, MaxRetries = 3 };
        sm.SetMission(mission);
        Assert.IsTrue(sm.CanRetry());
    }

    [Test]
    public void StateMachine_CanRetry_FalseWhenMaxRetries()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Failed, RetryCount = 3, MaxRetries = 3 };
        sm.SetMission(mission);
        Assert.IsFalse(sm.CanRetry());
    }

    [Test]
    public void StateMachine_GetValidTransitions_ReturnsCorrect()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.InProgress };
        sm.SetMission(mission);
        var transitions = sm.GetValidTransitions();
        Assert.IsTrue(transitions.Length > 0);
    }

    [Test]
    public void StateMachine_Reset_ClearsMission()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Available };
        sm.SetMission(mission);
        sm.Reset();
        Assert.IsFalse(sm.HasMission);
    }

    [Test]
    public void StateMachine_EventFired_OnStateChanged()
    {
        var sm = new MissionStateMachine();
        var mission = new MissionData { State = MissionState.Available };
        sm.SetMission(mission);

        bool eventFired = false;
        sm.OnStateChanged += (m, oldState, newState) => eventFired = true;

        sm.TransitionTo(MissionState.Accepted);
        Assert.IsTrue(eventFired);
    }
}

// ===== TIMER TESTS =====

[TestFixture]
public class MissionTimerSystemTests
{
    [Test]
    public void Timer_StartTimer_SetsValues()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var timer = new MissionTimerSystem(config);
        timer.StartTimer("mission_1", 60f);

        Assert.AreEqual(60f, timer.TimeRemaining, 0.01f);
        Assert.AreEqual("mission_1", timer.ActiveMissionId);
        Assert.IsTrue(timer.IsRunning);
    }

    [Test]
    public void Timer_Update_DecreasesTime()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var timer = new MissionTimerSystem(config);
        timer.StartTimer("mission_1", 60f);

        timer.Update(10f);
        Assert.AreEqual(50f, timer.TimeRemaining, 0.01f);
    }

    [Test]
    public void Timer_StopTimer_Stops()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var timer = new MissionTimerSystem(config);
        timer.StartTimer("mission_1", 60f);
        timer.StopTimer();

        Assert.IsFalse(timer.IsRunning);
    }

    [Test]
    public void Timer_PauseResume()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var timer = new MissionTimerSystem(config);
        timer.StartTimer("mission_1", 60f);

        timer.PauseTimer();
        Assert.IsFalse(timer.IsRunning);

        timer.ResumeTimer();
        Assert.IsTrue(timer.IsRunning);
    }

    [Test]
    public void Timer_FormattedTime_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var timer = new MissionTimerSystem(config);
        timer.StartTimer("mission_1", 125f);

        Assert.AreEqual("02:05", timer.GetFormattedTimeRemaining());
    }

    [Test]
    public void Timer_GetProgress_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var timer = new MissionTimerSystem(config);
        timer.StartTimer("mission_1", 100f);
        timer.Update(25f);

        float progress = timer.GetProgress();
        Assert.GreaterOrEqual(progress, 0f);
        Assert.LessOrEqual(progress, 1f);
    }

    [Test]
    public void Timer_AddTime_IncreasesTime()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var timer = new MissionTimerSystem(config);
        timer.StartTimer("mission_1", 60f);
        timer.AddTime(30f);

        Assert.AreEqual(90f, timer.TimeRemaining, 0.01f);
    }

    [Test]
    public void Timer_SubtractTime_DecreasesTime()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var timer = new MissionTimerSystem(config);
        timer.StartTimer("mission_1", 60f);
        timer.SubtractTime(20f);

        Assert.AreEqual(40f, timer.TimeRemaining, 0.01f);
    }

    [Test]
    public void Timer_TimeExpired_FiresEvent()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var timer = new MissionTimerSystem(config);
        timer.StartTimer("mission_1", 10f);

        bool expired = false;
        timer.OnTimerExpired += id => expired = true;

        timer.Update(15f);
        Assert.IsTrue(expired);
        Assert.IsFalse(timer.IsRunning);
    }

    [Test]
    public void Timer_Reset_ClearsValues()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var timer = new MissionTimerSystem(config);
        timer.StartTimer("mission_1", 60f);
        timer.Reset();

        Assert.IsFalse(timer.IsRunning);
        Assert.AreEqual(0f, timer.TimeRemaining, 0.01f);
    }
}

// ===== CHECKPOINT SYSTEM TESTS =====

[TestFixture]
public class MissionCheckpointSystemTests
{
    [Test]
    public void CheckpointSystem_InitializeMission_SetsCheckpoints()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionCheckpointSystem(config);

        var mission = new MissionData();
        mission.Checkpoints.Add(new MissionCheckpointData(CheckpointType.Start, Vector3.zero, 0));
        mission.Checkpoints.Add(new MissionCheckpointData(CheckpointType.Final, new Vector3(50, 0, 50), 1));

        system.InitializeMissionCheckpoints(mission);
        Assert.AreEqual(2, system.GetTotalCheckpoints(mission.MissionId));
    }

    [Test]
    public void CheckpointSystem_CheckpointReached_OnProximity()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionCheckpointSystem(config);

        var mission = new MissionData();
        mission.Checkpoints.Add(new MissionCheckpointData(CheckpointType.Start, Vector3.zero, 0) { Radius = 10f });

        system.InitializeMissionCheckpoints(mission);

        bool reached = false;
        system.OnCheckpointReached += (id, cp) => reached = true;

        system.Update(0.1f, new Vector3(2, 0, 2), mission.MissionId);
        Assert.IsTrue(reached);
    }

    [Test]
    public void CheckpointSystem_Progress_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionCheckpointSystem(config);

        var mission = new MissionData();
        mission.Checkpoints.Add(new MissionCheckpointData(CheckpointType.Start, Vector3.zero, 0) { Radius = 10f });
        mission.Checkpoints.Add(new MissionCheckpointData(CheckpointType.Final, new Vector3(100, 0, 100), 1) { Radius = 10f });

        system.InitializeMissionCheckpoints(mission);
        system.Update(0.1f, Vector3.zero, mission.MissionId);

        Assert.AreEqual(0.5f, system.GetProgress(mission.MissionId), 0.01f);
    }

    [Test]
    public void CheckpointSystem_GetCurrentCheckpoint_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionCheckpointSystem(config);

        var mission = new MissionData();
        mission.Checkpoints.Add(new MissionCheckpointData(CheckpointType.Start, Vector3.zero, 0) { Radius = 10f });
        mission.Checkpoints.Add(new MissionCheckpointData(CheckpointType.Final, new Vector3(100, 0, 100), 1) { Radius = 10f });

        system.InitializeMissionCheckpoints(mission);
        system.Update(0.1f, Vector3.zero, mission.MissionId);

        var current = system.GetCurrentCheckpoint(mission.MissionId);
        Assert.IsNotNull(current);
        Assert.AreEqual(new Vector3(100, 0, 100), current.Position);
    }

    [Test]
    public void CheckpointSystem_AllCheckpointsReached_Event()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionCheckpointSystem(config);

        var mission = new MissionData();
        mission.Checkpoints.Add(new MissionCheckpointData(CheckpointType.Start, Vector3.zero, 0) { Radius = 10f });

        system.InitializeMissionCheckpoints(mission);

        bool allReached = false;
        system.OnAllCheckpointsCompleted += id => allReached = true;

        system.Update(0.1f, Vector3.zero, mission.MissionId);
        Assert.IsTrue(allReached);
    }

    [Test]
    public void CheckpointSystem_ResetMissionCheckpoints_Resets()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionCheckpointSystem(config);

        var mission = new MissionData();
        mission.Checkpoints.Add(new MissionCheckpointData(CheckpointType.Start, Vector3.zero, 0) { Radius = 10f });

        system.InitializeMissionCheckpoints(mission);
        system.Update(0.1f, Vector3.zero, mission.MissionId);

        system.ResetMissionCheckpoints(mission.MissionId);
        Assert.AreEqual(0, system.GetReachedCount(mission.MissionId));
    }
}

// ===== OBJECTIVE SYSTEM TESTS =====

[TestFixture]
public class MissionObjectiveSystemTests
{
    [Test]
    public void ObjectiveSystem_Initialize_ActivatesRequired()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionObjectiveSystem(config);

        var mission = new MissionData();
        mission.Objectives.Add(new MissionObjectiveData("Reach A", ObjectiveType.ReachCheckpoint, Vector3.zero));

        system.InitializeMissionObjectives(mission);
        var objs = system.GetObjectives(mission.MissionId);
        Assert.AreEqual(ObjectiveState.Active, objs[0].State);
    }

    [Test]
    public void ObjectiveSystem_IncrementObjective_UpdatesCount()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionObjectiveSystem(config);

        var mission = new MissionData();
        var obj = new MissionObjectiveData("Collect 5", ObjectiveType.CollectItem, Vector3.zero, 5);
        mission.Objectives.Add(obj);

        system.InitializeMissionObjectives(mission);
        system.IncrementObjective(mission.MissionId, obj.ObjectiveId, 3);

        var updatedObjs = system.GetObjectives(mission.MissionId);
        Assert.AreEqual(3, updatedObjs[0].CurrentCount);
    }

    [Test]
    public void ObjectiveSystem_CompleteObjective_SetsCompleted()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionObjectiveSystem(config);

        var mission = new MissionData();
        var obj = new MissionObjectiveData("Collect 3", ObjectiveType.CollectItem, Vector3.zero, 3);
        mission.Objectives.Add(obj);

        system.InitializeMissionObjectives(mission);
        system.IncrementObjective(mission.MissionId, obj.ObjectiveId, 3);

        var updatedObjs = system.GetObjectives(mission.MissionId);
        Assert.AreEqual(ObjectiveState.Completed, updatedObjs[0].State);
    }

    [Test]
    public void ObjectiveSystem_AllRequiredComplete_ReturnsTrue()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionObjectiveSystem(config);

        var mission = new MissionData();
        var obj = new MissionObjectiveData("Reach", ObjectiveType.ReachCheckpoint, Vector3.zero, 1);
        mission.Objectives.Add(obj);

        system.InitializeMissionObjectives(mission);
        system.IncrementObjective(mission.MissionId, obj.ObjectiveId, 1);

        Assert.IsTrue(system.AreAllRequiredComplete(mission.MissionId));
    }

    [Test]
    public void ObjectiveSystem_FailObjective_SetsFailed()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionObjectiveSystem(config);

        var mission = new MissionData();
        var obj = new MissionObjectiveData("Reach", ObjectiveType.ReachCheckpoint, Vector3.zero);
        mission.Objectives.Add(obj);

        system.InitializeMissionObjectives(mission);
        system.FailObjective(mission.MissionId, obj.ObjectiveId);

        var updatedObjs = system.GetObjectives(mission.MissionId);
        Assert.AreEqual(ObjectiveState.Failed, updatedObjs[0].State);
    }

    [Test]
    public void ObjectiveSystem_Progress_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionObjectiveSystem(config);

        var mission = new MissionData();
        mission.Objectives.Add(new MissionObjectiveData("A", ObjectiveType.CollectItem, Vector3.zero, 1));
        mission.Objectives.Add(new MissionObjectiveData("B", ObjectiveType.CollectItem, Vector3.zero, 1));

        system.InitializeMissionObjectives(mission);
        var objs = system.GetObjectives(mission.MissionId);
        system.CompleteObjective(objs[0]);

        Assert.AreEqual(0.5f, system.GetProgress(mission.MissionId), 0.01f);
    }

    [Test]
    public void ObjectiveSystem_OptionalObjective_NotRequired()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionObjectiveSystem(config);

        var mission = new MissionData();
        var required = new MissionObjectiveData("Required", ObjectiveType.CollectItem, Vector3.zero, 1);
        required.IsOptional = false;
        var optional = new MissionObjectiveData("Optional", ObjectiveType.CollectItem, Vector3.zero, 1);
        optional.IsOptional = true;
        mission.Objectives.Add(required);
        mission.Objectives.Add(optional);

        system.InitializeMissionObjectives(mission);
        system.IncrementObjective(mission.MissionId, required.ObjectiveId, 1);

        Assert.IsTrue(system.AreAllRequiredComplete(mission.MissionId));
    }
}

// ===== REWARD SYSTEM TESTS =====

[TestFixture]
public class MissionRewardSystemTests
{
    [Test]
    public void RewardSystem_CalculateRewards_ReturnsCashAndExp()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionRewardSystem(config);

        var mission = new MissionData { RewardCash = 500, RewardExperience = 100, Difficulty = MissionDifficulty.Normal };

        var rewards = system.CalculateRewards(mission);
        Assert.IsTrue(rewards.Count >= 2);

        var cashReward = rewards.Find(r => r.Type == RewardType.Cash);
        Assert.IsNotNull(cashReward);
        Assert.Greater(cashReward.Amount, 0);

        var expReward = rewards.Find(r => r.Type == RewardType.Experience);
        Assert.IsNotNull(expReward);
        Assert.Greater(expReward.Amount, 0);
    }

    [Test]
    public void RewardSystem_DifficultyMultiplier_AffectsReward()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionRewardSystem(config);

        var easyMission = new MissionData { RewardCash = 100, Difficulty = MissionDifficulty.Easy };
        var hardMission = new MissionData { RewardCash = 100, Difficulty = MissionDifficulty.Hard };

        var easyRewards = system.CalculateRewards(easyMission);
        var hardRewards = system.CalculateRewards(hardMission);

        var easyCash = easyRewards.Find(r => r.Type == RewardType.Cash);
        var hardCash = hardRewards.Find(r => r.Type == RewardType.Cash);

        Assert.Greater(hardCash.Amount, easyCash.Amount);
    }

    [Test]
    public void RewardSystem_TimeBonus_GivenWhenFast()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionRewardSystem(config);

        var mission = new MissionData { TimeLimit = 100f, ElapsedTime = 20f };
        var bonus = system.CalculateTimeBonus(mission);
        Assert.IsTrue(bonus.Count > 0);
    }

    [Test]
    public void RewardSystem_TimeBonus_NoneWhenSlow()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionRewardSystem(config);

        var mission = new MissionData { TimeLimit = 100f, ElapsedTime = 80f };
        var bonus = system.CalculateTimeBonus(mission);
        Assert.AreEqual(0, bonus.Count);
    }

    [Test]
    public void RewardSystem_BaseExperience_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionRewardSystem(config);

        Assert.AreEqual(config.baseExpEasy, system.GetBaseExperience(MissionDifficulty.Easy));
        Assert.AreEqual(config.baseExpNormal, system.GetBaseExperience(MissionDifficulty.Normal));
        Assert.AreEqual(config.baseExpHard, system.GetBaseExperience(MissionDifficulty.Hard));
    }

    [Test]
    public void RewardSystem_GrantRewards_FiresEvent()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionRewardSystem(config);

        bool granted = false;
        system.OnRewardsGranted += (id, rewards) => granted = true;

        var rewards = new List<MissionRewardEntry>
        {
            new MissionRewardEntry { Type = RewardType.Cash, Amount = 100 }
        };

        system.GrantRewards("mission_1", rewards);
        Assert.IsTrue(granted);
    }
}

// ===== FAILURE SYSTEM TESTS =====

[TestFixture]
public class MissionFailureSystemTests
{
    [Test]
    public void FailureSystem_CheckTimeExpired_ReturnsTrue()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionFailureSystem(config);

        var mission = new MissionData { TimeLimit = 100f, ElapsedTime = 100f, State = MissionState.InProgress };
        Assert.IsTrue(system.CheckTimeExpired(mission));
        Assert.AreEqual(MissionState.Failed, mission.State);
    }

    [Test]
    public void FailureSystem_CheckTimeExpired_FalseWhenTimeRemaining()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionFailureSystem(config);

        var mission = new MissionData { TimeLimit = 100f, ElapsedTime = 50f, State = MissionState.InProgress };
        Assert.IsFalse(system.CheckTimeExpired(mission));
    }

    [Test]
    public void FailureSystem_AttemptRetry_Succeeds()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionFailureSystem(config);

        var mission = new MissionData { State = MissionState.Failed, RetryCount = 0, MaxRetries = 3 };
        Assert.IsTrue(system.AttemptRetry(mission));
        Assert.AreEqual(1, mission.RetryCount);
        Assert.AreEqual(MissionState.Available, mission.State);
    }

    [Test]
    public void FailureSystem_AttemptRetry_FailsWhenMaxRetries()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionFailureSystem(config);

        var mission = new MissionData { State = MissionState.Failed, RetryCount = 3, MaxRetries = 3 };
        Assert.IsFalse(system.AttemptRetry(mission));
    }

    [Test]
    public void FailureSystem_CanRetry_TrueWhenAvailable()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionFailureSystem(config);

        var mission = new MissionData { State = MissionState.Failed, RetryCount = 0, MaxRetries = 3 };
        Assert.IsTrue(system.CanRetry(mission));
    }

    [Test]
    public void FailureSystem_GetRemainingRetries_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionFailureSystem(config);

        var mission = new MissionData { RetryCount = 1, MaxRetries = 3 };
        Assert.AreEqual(2, system.GetRemainingRetries(mission));
    }

    [Test]
    public void FailureSystem_FailMission_FiresEvent()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionFailureSystem(config);

        var mission = new MissionData { State = MissionState.InProgress };
        bool failed = false;
        system.OnMissionFailed += (id, reason) => failed = true;

        system.FailMission(mission, FailureReason.TimeExpired);
        Assert.IsTrue(failed);
    }
}

// ===== DIALOGUE SYSTEM TESTS =====

[TestFixture]
public class MissionDialogueSystemTests
{
    [Test]
    public void DialogueSystem_StartDialogue_SetsActive()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionDialogueSystem(config);

        var lines = new List<MissionDialogueLine>
        {
            new MissionDialogueLine("NPC", DialogueSpeakerType.NPC, "Hello!", 0),
            new MissionDialogueLine("Player", DialogueSpeakerType.Player, "Hi!", 1)
        };

        system.StartDialogue("mission_1", lines);
        Assert.IsTrue(system.IsDialogueActive);
        Assert.AreEqual(2, system.TotalLines);
    }

    [Test]
    public void DialogueSystem_SkipOrAdvance_MovesToNextLine()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionDialogueSystem(config);

        var lines = new List<MissionDialogueLine>
        {
            new MissionDialogueLine("NPC", DialogueSpeakerType.NPC, "Hello!", 0),
            new MissionDialogueLine("Player", DialogueSpeakerType.Player, "Hi!", 1)
        };

        system.StartDialogue("mission_1", lines);
        system.SkipOrAdvance();

        Assert.AreEqual(1, system.CurrentLineIndex);
    }

    [Test]
    public void DialogueSystem_EndDialogue_SetsInactive()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionDialogueSystem(config);

        var lines = new List<MissionDialogueLine>
        {
            new MissionDialogueLine("NPC", DialogueSpeakerType.NPC, "Hello!", 0)
        };

        system.StartDialogue("mission_1", lines);
        system.EndDialogue();

        Assert.IsFalse(system.IsDialogueActive);
    }

    [Test]
    public void DialogueSystem_GetDialogueProgress_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionDialogueSystem(config);

        var lines = new List<MissionDialogueLine>
        {
            new MissionDialogueLine("NPC", DialogueSpeakerType.NPC, "Line 1", 0),
            new MissionDialogueLine("NPC", DialogueSpeakerType.NPC, "Line 2", 1),
            new MissionDialogueLine("NPC", DialogueSpeakerType.NPC, "Line 3", 2)
        };

        system.StartDialogue("mission_1", lines);
        Assert.AreEqual(0f, system.GetDialogueProgress(), 0.01f);
    }

    [Test]
    public void DialogueSystem_Skip_CompletesAllLines()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionDialogueSystem(config);

        var lines = new List<MissionDialogueLine>
        {
            new MissionDialogueLine("NPC", DialogueSpeakerType.NPC, "Line 1", 0),
            new MissionDialogueLine("NPC", DialogueSpeakerType.NPC, "Line 2", 1)
        };

        system.StartDialogue("mission_1", lines);
        bool completed = false;
        system.OnDialogueCompleted += id => completed = true;

        system.SkipOrAdvance();
        system.SkipOrAdvance();

        Assert.IsTrue(completed);
        Assert.IsFalse(system.IsDialogueActive);
    }
}

// ===== CUTSCENE SYSTEM TESTS =====

[TestFixture]
public class MissionCutsceneSystemTests
{
    [Test]
    public void CutsceneSystem_PlayCutscene_SetsPlaying()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionCutsceneSystem(config);

        var events = new List<MissionCutsceneEvent>
        {
            new MissionCutsceneEvent { ActionType = CutsceneActionType.FadeIn, Duration = 1f, Order = 0 }
        };

        system.PlayCutscene("mission_1", events);
        Assert.IsTrue(system.IsCutscenePlaying);
        Assert.AreEqual(1, system.TotalEvents);
    }

    [Test]
    public void CutsceneSystem_SkipCutscene_Stops()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionCutsceneSystem(config);

        var events = new List<MissionCutsceneEvent>
        {
            new MissionCutsceneEvent { ActionType = CutsceneActionType.Wait, Duration = 10f, Order = 0 }
        };

        system.PlayCutscene("mission_1", events);
        system.SkipCutscene();
        Assert.IsFalse(system.IsCutscenePlaying);
    }

    [Test]
    public void CutsceneSystem_GetProgress_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionCutsceneSystem(config);

        Assert.AreEqual(0f, system.GetCutsceneProgress(), 0.01f);
    }

    [Test]
    public void CutsceneSystem_GetCurrentEvent_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionCutsceneSystem(config);

        var events = new List<MissionCutsceneEvent>
        {
            new MissionCutsceneEvent { ActionType = CutsceneActionType.FadeIn, Duration = 0.1f, Order = 0 }
        };

        system.PlayCutscene("mission_1", events);
        var current = system.GetCurrentEvent();
        Assert.IsNotNull(current);
        Assert.AreEqual(CutsceneActionType.FadeIn, current.ActionType);
    }
}

// ===== MARKER SYSTEM TESTS =====

[TestFixture]
public class MissionMarkerSystemTests
{
    [Test]
    public void MarkerSystem_AddMarker_IncreasesCount()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionMarkerSystem(config);

        system.AddMarker("mission_1", MissionMarkerType.Start, Vector3.zero, "Start", Color.yellow);
        Assert.AreEqual(1, system.MarkerCount);
    }

    [Test]
    public void MarkerSystem_RemoveMarker_DecreasesCount()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionMarkerSystem(config);

        var marker = system.AddMarker("mission_1", MissionMarkerType.Start, Vector3.zero, "Start", Color.yellow);
        system.RemoveMarker(marker.MarkerId);
        Assert.AreEqual(0, system.MarkerCount);
    }

    [Test]
    public void MarkerSystem_GetNearestMarker_ReturnsClosest()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionMarkerSystem(config);

        system.AddMarker("m1", MissionMarkerType.Start, new Vector3(100, 0, 100), "Far", Color.yellow);
        system.AddMarker("m2", MissionMarkerType.Checkpoint, new Vector3(5, 0, 5), "Near", Color.cyan);

        var nearest = system.GetNearestMarker(Vector3.zero);
        Assert.IsNotNull(nearest);
        Assert.AreEqual("Near", nearest.Label);
    }

    [Test]
    public void MarkerSystem_GetMarkersByType_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionMarkerSystem(config);

        system.AddMarker("m1", MissionMarkerType.Start, Vector3.zero, "Start", Color.yellow);
        system.AddMarker("m2", MissionMarkerType.Checkpoint, Vector3.zero, "CP", Color.cyan);

        var starts = system.GetMarkersByType(MissionMarkerType.Start);
        Assert.AreEqual(1, starts.Count);
    }

    [Test]
    public void MarkerSystem_RemoveMarkersByMission_RemovesAll()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionMarkerSystem(config);

        system.AddMarker("mission_1", MissionMarkerType.Start, Vector3.zero, "A", Color.yellow);
        system.AddMarker("mission_1", MissionMarkerType.Checkpoint, Vector3.zero, "B", Color.cyan);
        system.AddMarker("mission_2", MissionMarkerType.Start, Vector3.zero, "C", Color.red);

        system.RemoveMarkersByMission("mission_1");
        Assert.AreEqual(1, system.MarkerCount);
    }

    [Test]
    public void MarkerSystem_GetDistanceToMarker_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionMarkerSystem(config);

        var marker = system.AddMarker("m1", MissionMarkerType.Start, new Vector3(10, 0, 0), "Test", Color.yellow);
        float dist = system.GetDistanceToMarker(marker.MarkerId, Vector3.zero);
        Assert.AreEqual(10f, dist, 0.01f);
    }
}

// ===== TRIGGER ZONE SYSTEM TESTS =====

[TestFixture]
public class MissionTriggerZoneSystemTests
{
    [Test]
    public void TriggerZoneSystem_CreateZone_AddsZone()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionTriggerZoneSystem(config);

        var zone = system.CreateZone("mission_1", TriggerZoneShape.Sphere, Vector3.zero, Vector3.zero, 10f);
        Assert.IsNotNull(zone);
        Assert.AreEqual(1, system.ActiveZoneCount);
    }

    [Test]
    public void TriggerZoneSystem_RemoveZone_RemovesZone()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionTriggerZoneSystem(config);

        var zone = system.CreateZone("mission_1", TriggerZoneShape.Sphere, Vector3.zero, Vector3.zero, 10f);
        system.RemoveZone(zone.ZoneId);
        Assert.AreEqual(0, system.ActiveZoneCount);
    }

    [Test]
    public void TriggerZoneSystem_IsPointInsideZone_Sphere()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionTriggerZoneSystem(config);

        var zone = new TriggerZoneData { Shape = TriggerZoneShape.Sphere, Center = Vector3.zero, Radius = 10f };
        Assert.IsTrue(system.IsPointInsideZone(new Vector3(3, 0, 3), zone));
        Assert.IsFalse(system.IsPointInsideZone(new Vector3(20, 0, 20), zone));
    }

    [Test]
    public void TriggerZoneSystem_IsPointInsideZone_Box()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionTriggerZoneSystem(config);

        var zone = new TriggerZoneData { Shape = TriggerZoneShape.Box, Center = Vector3.zero, Size = new Vector3(10, 10, 10) };
        Assert.IsTrue(system.IsPointInsideZone(new Vector3(3, 3, 3), zone));
        Assert.IsFalse(system.IsPointInsideZone(new Vector3(20, 20, 20), zone));
    }

    [Test]
    public void TriggerZoneSystem_CreateCheckpointZone_CreatesSphere()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionTriggerZoneSystem(config);

        var zone = system.CreateCheckpointZone("mission_1", new Vector3(50, 0, 50), 15f);
        Assert.AreEqual(TriggerZoneShape.Sphere, zone.Shape);
        Assert.AreEqual(15f, zone.Radius);
    }

    [Test]
    public void TriggerZoneSystem_GetZonesByMission_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionTriggerZoneSystem(config);

        system.CreateZone("mission_1", TriggerZoneShape.Sphere, Vector3.zero, Vector3.zero, 10f);
        system.CreateZone("mission_2", TriggerZoneShape.Sphere, Vector3.zero, Vector3.zero, 10f);

        var zones = system.GetZonesByMission("mission_1");
        Assert.AreEqual(1, zones.Count);
    }
}

// ===== TUTORIAL SYSTEM TESTS =====

[TestFixture]
public class MissionTutorialSystemTests
{
    [Test]
    public void TutorialSystem_RegisterTutorial_AddsTutorial()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionTutorialSystem(config);

        var tutorial = new MissionData("tut_1", "Basics", MissionType.Tutorial, MissionDifficulty.Easy);
        system.RegisterTutorial(tutorial);

        Assert.AreEqual(1, system.GetTotalTutorialCount());
    }

    [Test]
    public void TutorialSystem_StartTutorial_SetsActive()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionTutorialSystem(config);

        var tutorial = new MissionData("tut_1", "Basics", MissionType.Tutorial, MissionDifficulty.Easy);
        system.RegisterTutorial(tutorial);
        system.StartTutorial("tut_1");

        Assert.IsTrue(system.IsActive);
        Assert.AreEqual("tut_1", system.CurrentTutorialId);
    }

    [Test]
    public void TutorialSystem_CompleteTutorial_SetsCompleted()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionTutorialSystem(config);

        var tutorial = new MissionData("tut_1", "Basics", MissionType.Tutorial, MissionDifficulty.Easy);
        system.RegisterTutorial(tutorial);
        system.StartTutorial("tut_1");
        system.CompleteTutorial("tut_1");

        Assert.IsFalse(system.IsActive);
        Assert.IsTrue(system.IsTutorialCompleted("tut_1"));
    }

    [Test]
    public void TutorialSystem_ShowHint_FiresEvent()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionTutorialSystem(config);

        bool hintShown = false;
        system.OnHintShown += (id, text) => hintShown = true;

        system.ShowHint("hint_1", "Press W to move");
        Assert.IsTrue(hintShown);
    }

    [Test]
    public void TutorialSystem_CompletionRate_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionTutorialSystem(config);

        system.RegisterTutorial(new MissionData("t1", "A", MissionType.Tutorial, MissionDifficulty.Easy));
        system.RegisterTutorial(new MissionData("t2", "B", MissionType.Tutorial, MissionDifficulty.Easy));

        system.StartTutorial("t1");
        system.CompleteTutorial("t1");

        Assert.AreEqual(50f, system.GetCompletionRate(), 0.01f);
    }
}

// ===== SIDE MISSION SYSTEM TESTS =====

[TestFixture]
public class MissionSideSystemTests
{
    [Test]
    public void SideSystem_CanStartSideMission_True()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionSideSystem(config);

        Assert.IsTrue(system.CanStartSideMission());
    }

    [Test]
    public void SideSystem_StartSideMission_SetsInProgress()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionSideSystem(config);

        var mission = new MissionData("side_1", "Side Quest", MissionType.Side, MissionDifficulty.Easy);
        mission.State = MissionState.Available;
        system.RegisterSideMission(mission);

        var result = system.StartSideMission("side_1");
        Assert.IsNotNull(result);
        Assert.AreEqual(MissionState.InProgress, result.State);
    }

    [Test]
    public void SideSystem_CompleteSideMission_MovesToCompleted()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionSideSystem(config);

        var mission = new MissionData("side_1", "Side Quest", MissionType.Side, MissionDifficulty.Easy);
        mission.State = MissionState.Available;
        system.RegisterSideMission(mission);

        system.StartSideMission("side_1");
        system.CompleteSideMission("side_1");

        Assert.AreEqual(1, system.CompletedCount);
        Assert.AreEqual(0, system.ActiveCount);
    }

    [Test]
    public void SideSystem_MaxSideMissions_StopsStart()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        config.maxSideMissionsPerDay = 1;
        var system = new MissionSideSystem(config);

        var mission1 = new MissionData("s1", "A", MissionType.Side, MissionDifficulty.Easy) { State = MissionState.Available };
        var mission2 = new MissionData("s2", "B", MissionType.Side, MissionDifficulty.Easy) { State = MissionState.Available };
        system.RegisterSideMission(mission1);
        system.RegisterSideMission(mission2);

        system.StartSideMission("s1");
        Assert.IsFalse(system.CanStartSideMission());
    }
}

// ===== DAILY MISSION SYSTEM TESTS =====

[TestFixture]
public class MissionDailySystemTests
{
    [Test]
    public void DailySystem_GenerateDailyMissions_ReturnsMissions()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        config.dailyMissionCount = 3;
        var system = new MissionDailySystem(config);

        var missions = system.GenerateDailyMissions();
        Assert.AreEqual(3, missions.Count);
    }

    [Test]
    public void DailySystem_CompleteDailyMission_IncrementsStreak()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        config.dailyMissionCount = 3;
        var system = new MissionDailySystem(config);

        var missions = system.GenerateDailyMissions();
        int streakBefore = system.StreakCount;

        system.CompleteDailyMission(missions[0].MissionId);
        Assert.AreEqual(streakBefore + 1, system.StreakCount);
    }

    [Test]
    public void DailySystem_FailDailyMission_ResetsStreak()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        config.dailyMissionCount = 3;
        var system = new MissionDailySystem(config);

        system.SetStreak(5);
        var missions = system.GenerateDailyMissions();
        system.FailDailyMission(missions[0].MissionId);

        Assert.AreEqual(0, system.StreakCount);
    }

    [Test]
    public void DailySystem_GetStreakBonus_ReturnsBonus()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        config.dailyStreakBonusMultiplier = 50;
        var system = new MissionDailySystem(config);

        system.SetStreak(5);
        Assert.AreEqual(250, system.GetStreakBonus());
    }

    [Test]
    public void DailySystem_GetStreakBonus_ZeroWhenLow()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionDailySystem(config);

        system.SetStreak(2);
        Assert.AreEqual(0, system.GetStreakBonus());
    }
}

// ===== RANDOM EVENT SYSTEM TESTS =====

[TestFixture]
public class MissionRandomEventSystemTests
{
    [Test]
    public void RandomEventSystem_CanSpawn_True()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        config.maxConcurrentRandomEvents = 2;
        var system = new MissionRandomEventSystem(config);

        Assert.IsTrue(system.CanSpawnNewEvent);
    }

    [Test]
    public void RandomEventSystem_RegisterTemplate_Works()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionRandomEventSystem(config);

        var template = new RandomEventTemplate { EventName = "Test Event" };
        system.RegisterEventTemplate(template);
        Assert.AreEqual(1, system.ActiveEventCount);
    }

    [Test]
    public void RandomEventSystem_CompleteRandomEvent_DecreasesCount()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionRandomEventSystem(config);

        var template = new RandomEventTemplate
        {
            EventName = "Test",
            SpawnChance = 1f,
            SpawnCenter = Vector3.zero,
            SpawnRadius = 100f
        };
        system.RegisterEventTemplate(template);

        var evt = system.TrySpawnRandomEvent(Vector3.zero, 0f);
        if (evt != null)
        {
            system.CompleteRandomEvent(evt.MissionId);
            Assert.AreEqual(0, system.ActiveEventCount);
        }
    }
}

// ===== ACHIEVEMENT SYSTEM TESTS =====

[TestFixture]
public class MissionAchievementSystemTests
{
    [Test]
    public void AchievementSystem_RegisterAchievement_AddsToTotal()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionAchievementSystem(config);

        var achievement = new AchievementDefinition { Name = "First Mission", RequiredValue = 1 };
        system.RegisterAchievement(achievement);

        Assert.AreEqual(1, system.TotalAchievements);
    }

    [Test]
    public void AchievementSystem_OnMissionCompleted_IncrementsProgress()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionAchievementSystem(config);

        var achievement = new AchievementDefinition
        {
            Name = "Complete 1",
            TriggerType = AchievementTriggerType.MissionCompleted,
            RequiredValue = 1
        };
        system.RegisterAchievement(achievement);

        var mission = new MissionData { Type = MissionType.Side };
        system.OnMissionCompleted(mission);

        Assert.AreEqual(1, system.GetProgress(achievement.AchievementId));
    }

    [Test]
    public void AchievementSystem_UnlocksAchievement_WhenProgressMet()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionAchievementSystem(config);

        var achievement = new AchievementDefinition
        {
            Name = "First Cash",
            TriggerType = AchievementTriggerType.TotalCashEarned,
            RequiredValue = 100
        };
        system.RegisterAchievement(achievement);

        bool unlocked = false;
        system.OnAchievementUnlocked += a => unlocked = true;

        system.OnCashEarned(100);
        Assert.IsTrue(unlocked);
        Assert.IsTrue(achievement.IsUnlocked);
    }

    [Test]
    public void AchievementSystem_GetCompletionRate_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionAchievementSystem(config);

        var a1 = new AchievementDefinition { Name = "A", TriggerType = AchievementTriggerType.MissionCompleted, RequiredValue = 1 };
        var a2 = new AchievementDefinition { Name = "B", TriggerType = AchievementTriggerType.MissionCompleted, RequiredValue = 2 };
        system.RegisterAchievement(a1);
        system.RegisterAchievement(a2);

        var mission = new MissionData { Type = MissionType.Side };
        system.OnMissionCompleted(mission);

        Assert.AreEqual(50f, system.GetCompletionRate(), 0.01f);
    }

    [Test]
    public void AchievementSystem_GetUnlockedAchievements_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionAchievementSystem(config);

        var a1 = new AchievementDefinition { Name = "A", TriggerType = AchievementTriggerType.MissionCompleted, RequiredValue = 1 };
        system.RegisterAchievement(a1);

        var mission = new MissionData { Type = MissionType.Side };
        system.OnMissionCompleted(mission);

        var unlocked = system.GetUnlockedAchievements();
        Assert.AreEqual(1, unlocked.Count);
    }

    [Test]
    public void AchievementSystem_DistanceTraveled_Increments()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionAchievementSystem(config);

        var a = new AchievementDefinition
        {
            Name = "Travel 100",
            TriggerType = AchievementTriggerType.TotalDistanceTraveled,
            RequiredValue = 100
        };
        system.RegisterAchievement(a);

        system.OnDistanceTraveled(150f);
        Assert.IsTrue(a.IsUnlocked);
    }
}

// ===== ECONOMY SYSTEM TESTS =====

[TestFixture]
public class MissionEconomySystemTests
{
    [Test]
    public void EconomySystem_AddCash_IncreasesBalance()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionEconomySystem(config);
        system.Initialize(0, 0);

        system.AddCash(500);
        Assert.AreEqual(500, system.Cash, 0.01);
    }

    [Test]
    public void EconomySystem_SpendCash_DecreasesBalance()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionEconomySystem(config);
        system.Initialize(1000, 0);

        system.SpendCash(300);
        Assert.AreEqual(700, system.Cash, 0.01);
    }

    [Test]
    public void EconomySystem_SpendCash_FalseWhenInsufficient()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionEconomySystem(config);
        system.Initialize(100, 0);

        Assert.IsFalse(system.SpendCash(500));
        Assert.AreEqual(100, system.Cash, 0.01);
    }

    [Test]
    public void EconomySystem_CanAfford_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionEconomySystem(config);
        system.Initialize(500, 0);

        Assert.IsTrue(system.CanAfford(300));
        Assert.IsFalse(system.CanAfford(1000));
    }

    [Test]
    public void EconomySystem_DepositToBank_Transfers()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionEconomySystem(config);
        system.Initialize(1000, 0);

        system.DepositToBank(500);
        Assert.AreEqual(500, system.Cash, 0.01);
        Assert.AreEqual(500, system.BankBalance, 0.01);
    }

    [Test]
    public void EconomySystem_WithdrawFromBank_Transfers()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionEconomySystem(config);
        system.Initialize(0, 1000);

        system.WithdrawFromBank(400);
        Assert.AreEqual(400, system.Cash, 0.01);
        Assert.AreEqual(600, system.BankBalance, 0.01);
    }

    [Test]
    public void EconomySystem_GetNetWorth_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionEconomySystem(config);
        system.Initialize(500, 1000);

        Assert.AreEqual(1500, system.GetNetWorth(), 0.01);
    }

    [Test]
    public void EconomySystem_TotalCashEarned_TracksCorrectly()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionEconomySystem(config);
        system.Initialize(0, 0);

        system.AddCash(100);
        system.AddCash(200);

        Assert.AreEqual(300, system.TotalCashEarned);
    }
}

// ===== PROGRESS SYSTEM TESTS =====

[TestFixture]
public class MissionProgressSystemTests
{
    [Test]
    public void ProgressSystem_TrackMissionStart_CreatesSnapshot()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionProgressSystem(config);
        system.Initialize();

        var mission = new MissionData { MissionId = "m1", MissionName = "Test" };
        mission.Objectives.Add(new MissionObjectiveData("A", ObjectiveType.CollectItem, Vector3.zero));
        mission.Checkpoints.Add(new MissionCheckpointData(CheckpointType.Start, Vector3.zero, 0));

        system.TrackMissionStart(mission);
        var snapshot = system.GetProgress("m1");

        Assert.IsNotNull(snapshot);
        Assert.AreEqual(1, snapshot.TotalObjectives);
        Assert.AreEqual(1, snapshot.TotalCheckpoints);
    }

    [Test]
    public void ProgressSystem_RecordMissionCompletion_UpdatesStats()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionProgressSystem(config);
        system.Initialize();

        var mission = new MissionData { MissionId = "m1" };
        system.TrackMissionStart(mission);
        system.RecordMissionCompletion(mission);

        Assert.AreEqual(1, system.CurrentStats.TotalMissionsCompleted);
        Assert.AreEqual(1, system.CurrentStats.CurrentStreak);
    }

    [Test]
    public void ProgressSystem_RecordMissionFailure_ResetsStreak()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionProgressSystem(config);
        system.Initialize();

        var mission = new MissionData { MissionId = "m1" };
        system.TrackMissionStart(mission);
        system.RecordMissionCompletion(mission);
        system.RecordMissionFailure(mission);

        Assert.AreEqual(0, system.CurrentStats.CurrentStreak);
    }

    [Test]
    public void ProgressSystem_GetCompletionPercentage_ReturnsCorrect()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionProgressSystem(config);
        system.Initialize();

        var mission = new MissionData { MissionId = "m1" };
        mission.Objectives.Add(new MissionObjectiveData("A", ObjectiveType.CollectItem, Vector3.zero, 1));
        mission.Objectives.Add(new MissionObjectiveData("B", ObjectiveType.CollectItem, Vector3.zero, 1));

        system.TrackMissionStart(mission);
        system.UpdateProgress(mission);

        Assert.AreEqual(0f, system.GetCompletionPercentage("m1"), 0.01f);
    }

    [Test]
    public void ProgressSystem_GetFormattedStats_ReturnsString()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var system = new MissionProgressSystem(config);
        system.Initialize();

        string stats = system.GetFormattedStats();
        Assert.IsNotNull(stats);
        Assert.IsTrue(stats.Contains("Started"));
    }
}

// ===== MISSION MANAGER TESTS =====

[TestFixture]
public class MissionManagerTests
{
    [Test]
    public void MissionManager_Initialize_SetsInitialized()
    {
        var go = new GameObject("TestMissionManager");
        var manager = go.AddComponent<MissionManager>();
        var config = ScriptableObject.CreateInstance<MissionConfig>();

        manager.Initialize(config);
        Assert.IsTrue(manager.IsInitialized);

        Object.DestroyImmediate(go);
    }

    [Test]
    public void MissionManager_RegisterMission_IncreasesCount()
    {
        var go = new GameObject("TestMissionManager");
        var manager = go.AddComponent<MissionManager>();
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        manager.Initialize(config);

        var mission = new MissionData("m1", "Test", MissionType.Side, MissionDifficulty.Easy);
        manager.RegisterMission(mission);

        Assert.AreEqual(1, manager.RegisteredMissionCount);

        Object.DestroyImmediate(go);
    }

    [Test]
    public void MissionManager_AcceptMission_ReturnsMission()
    {
        var go = new GameObject("TestMissionManager");
        var manager = go.AddComponent<MissionManager>();
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        manager.Initialize(config);

        var mission = new MissionData("m1", "Test", MissionType.Side, MissionDifficulty.Easy);
        mission.State = MissionState.Available;
        manager.RegisterMission(mission);

        var accepted = manager.AcceptMission("m1");
        Assert.IsNotNull(accepted);

        Object.DestroyImmediate(go);
    }

    [Test]
    public void MissionManager_GetMissionsByType_ReturnsCorrect()
    {
        var go = new GameObject("TestMissionManager");
        var manager = go.AddComponent<MissionManager>();
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        manager.Initialize(config);

        manager.RegisterMission(new MissionData("m1", "A", MissionType.Side, MissionDifficulty.Easy));
        manager.RegisterMission(new MissionData("m2", "B", MissionType.Delivery, MissionDifficulty.Normal));
        manager.RegisterMission(new MissionData("m3", "C", MissionType.Side, MissionDifficulty.Hard));

        var sides = manager.GetMissionsByType(MissionType.Side);
        Assert.AreEqual(2, sides.Count);

        Object.DestroyImmediate(go);
    }

    [Test]
    public void MissionManager_ClearAll_ResetsEverything()
    {
        var go = new GameObject("TestMissionManager");
        var manager = go.AddComponent<MissionManager>();
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        manager.Initialize(config);

        manager.RegisterMission(new MissionData("m1", "Test", MissionType.Side, MissionDifficulty.Easy));
        manager.ClearAll();

        Assert.AreEqual(0, manager.RegisteredMissionCount);

        Object.DestroyImmediate(go);
    }
}

// ===== INTEGRATION TESTS =====

[TestFixture]
public class MissionIntegrationTests
{
    [Test]
    public void FullMissionLifecycle_AcceptStartComplete()
    {
        var go = new GameObject("TestMissionManager");
        var manager = go.AddComponent<MissionManager>();
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        manager.Initialize(config);

        var mission = new MissionData("m1", "Test Mission", MissionType.Side, MissionDifficulty.Normal);
        mission.State = MissionState.Available;
        mission.RewardCash = 500;
        mission.RewardExperience = 100;
        mission.Objectives.Add(new MissionObjectiveData("Reach A", ObjectiveType.ReachCheckpoint, new Vector3(10, 0, 10), 1));
        manager.RegisterMission(mission);

        manager.AcceptMission("m1");
        manager.StartMission("m1");

        Assert.AreEqual(MissionState.InProgress, manager.ActiveMission.State);

        manager.IncrementObjective(mission.Objectives[0].ObjectiveId, 1);

        Assert.AreEqual(MissionState.Completed, manager.ActiveMission.State);

        Object.DestroyImmediate(go);
    }

    [Test]
    public void MissionWithTimer_FailsOnTimeout()
    {
        var go = new GameObject("TestMissionManager");
        var manager = go.AddComponent<MissionManager>();
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        manager.Initialize(config);

        var mission = new MissionData("m1", "Timed Mission", MissionType.Side, MissionDifficulty.Normal);
        mission.State = MissionState.Available;
        mission.TimeLimit = 5f;
        manager.RegisterMission(mission);

        manager.AcceptMission("m1");
        manager.StartMission("m1");

        manager.Timer.Update(6f);

        Assert.IsNull(manager.ActiveMissionId);

        Object.DestroyImmediate(go);
    }

    [Test]
    public void EconomyAndRewards_Integrated()
    {
        var config = ScriptableObject.CreateInstance<MissionConfig>();
        var economy = new MissionEconomySystem(config);
        var rewards = new MissionRewardSystem(config);

        economy.Initialize(0, 0);

        var mission = new MissionData { RewardCash = 1000, Difficulty = MissionDifficulty.Normal };
        var rewardList = rewards.CalculateRewards(mission);

        economy.GrantMissionRewards("m1", rewardList);

        Assert.Greater(economy.Cash, 0);
    }
}
