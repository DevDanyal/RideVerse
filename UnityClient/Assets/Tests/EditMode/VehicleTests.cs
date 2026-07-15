using NUnit.Framework;
using RideVerse.Vehicles;
using RideVerse.Core;
using UnityEngine;

[TestFixture]
public class HondaCG125ConstantsTests
{
    [Test]
    public void HondaCG125_VehicleId_IsNotEmpty()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Vehicle.HondaCG125.VehicleId));
    }

    [Test]
    public void HondaCG125_DisplayName_IsNotEmpty()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Vehicle.HondaCG125.DisplayName));
    }

    [Test]
    public void HondaCG125_MaxSpeedKmh_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.MaxSpeedKmh, 80f);
        Assert.Less(Constants.Vehicle.HondaCG125.MaxSpeedKmh, 150f);
    }

    [Test]
    public void HondaCG125_MaxRPM_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.MaxRPM, 7000f);
        Assert.Less(Constants.Vehicle.HondaCG125.MaxRPM, 12000f);
    }

    [Test]
    public void HondaCG125_IdleRPM_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.IdleRPM, 0f);
        Assert.Less(Constants.Vehicle.HondaCG125.IdleRPM, 2000f);
    }

    [Test]
    public void HondaCG125_RedlineRPM_IsLessThanMaxRPM()
    {
        Assert.Less(Constants.Vehicle.HondaCG125.RedlineRPM, Constants.Vehicle.HondaCG125.MaxRPM);
    }

    [Test]
    public void HondaCG125_MaxPower_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.MaxPower, 5f);
        Assert.Less(Constants.Vehicle.HondaCG125.MaxPower, 20f);
    }

    [Test]
    public void HondaCG125_MaxTorque_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.MaxTorque, 5f);
        Assert.Less(Constants.Vehicle.HondaCG125.MaxTorque, 20f);
    }

    [Test]
    public void HondaCG125_TotalGears_IsFive()
    {
        Assert.AreEqual(5, Constants.Vehicle.HondaCG125.TotalGears);
    }

    [Test]
    public void HondaCG125_FinalDriveRatio_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.FinalDriveRatio, 2f);
        Assert.Less(Constants.Vehicle.HondaCG125.FinalDriveRatio, 4f);
    }

    [Test]
    public void HondaCG125_GearRatios_HasCorrectLength()
    {
        float[] ratios = Constants.Vehicle.HondaCG125.GearRatios;
        Assert.AreEqual(Constants.Vehicle.HondaCG125.TotalGears + 1, ratios.Length);
    }

    [Test]
    public void HondaCG125_GearRatios_NeutralIsZero()
    {
        float[] ratios = Constants.Vehicle.HondaCG125.GearRatios;
        Assert.AreEqual(0f, ratios[0]);
    }

    [Test]
    public void HondaCG125_GearRatios_AreInDecreasingOrder()
    {
        float[] ratios = Constants.Vehicle.HondaCG125.GearRatios;
        for (int i = 2; i < ratios.Length; i++)
        {
            Assert.Less(ratios[i], ratios[i - 1],
                $"Gear {i} ratio ({ratios[i]}) should be less than gear {i - 1} ({ratios[i - 1]})");
        }
    }

    [Test]
    public void HondaCG125_Mass_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.Mass, 100f);
        Assert.Less(Constants.Vehicle.HondaCG125.Mass, 160f);
    }

    [Test]
    public void HondaCG125_MaxFuel_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.MaxFuel, 10f);
        Assert.Less(Constants.Vehicle.HondaCG125.MaxFuel, 25f);
    }

    [Test]
    public void HondaCG125_MaxHealth_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.MaxHealth, 0f);
    }

    [Test]
    public void HondaCG125_SteeringAngle_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.SteeringAngle, 30f);
        Assert.Less(Constants.Vehicle.HondaCG125.SteeringAngle, 60f);
    }

    [Test]
    public void HondaCG125_MaxLeanAngle_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.MaxLeanAngle, 30f);
        Assert.Less(Constants.Vehicle.HondaCG125.MaxLeanAngle, 50f);
    }

    [Test]
    public void HondaCG125_FrontBrakeForce_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.FrontBrakeForce, 0f);
    }

    [Test]
    public void HondaCG125_RearBrakeForce_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.RearBrakeForce, 0f);
    }

    [Test]
    public void HondaCG125_ClutchEngageRPM_IsBetweenIdleAndRedline()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.ClutchEngageRPM, Constants.Vehicle.HondaCG125.IdleRPM);
        Assert.Less(Constants.Vehicle.HondaCG125.ClutchEngageRPM, Constants.Vehicle.HondaCG125.RedlineRPM);
    }

    [Test]
    public void HondaCG125_SuspensionSpringForces_ArePositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.FrontSpringForce, 0f);
        Assert.Greater(Constants.Vehicle.HondaCG125.RearSpringForce, 0f);
    }

    [Test]
    public void HondaCG125_SuspensionDamperForces_ArePositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.FrontDamperForce, 0f);
        Assert.Greater(Constants.Vehicle.HondaCG125.RearDamperForce, 0f);
    }

    [Test]
    public void Vehicle_InteractionRange_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.InteractionRange, 0f);
    }

    [Test]
    public void Vehicle_InteractionPrompt_IsNotEmpty()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Vehicle.InteractionPrompt));
    }

    [Test]
    public void Vehicle_ExitPrompt_IsNotEmpty()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Vehicle.ExitPrompt));
    }

    [Test]
    public void Vehicle_PositionSaveInterval_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.PositionSaveInterval, 0f);
    }
}

[TestFixture]
public class HondaCG125ConfigTests
{
    private HondaCG125Config _config;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<HondaCG125Config>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void DefaultValues_MatchConstants()
    {
        Assert.AreEqual(128f, _config.mass);
        Assert.AreEqual(5, _config.totalGears);
        Assert.AreEqual(110f, _config.maxSpeedKmh);
        Assert.AreEqual(9500f, _config.maxRPM);
    }

    [Test]
    public void GearRatios_HasCorrectLength()
    {
        Assert.AreEqual(6, _config.gearRatios.Length);
    }

    [Test]
    public void GearRatios_NeutralIsZero()
    {
        Assert.AreEqual(0f, _config.gearRatios[0]);
    }

    [Test]
    public void CenterOfMassOffset_IsReasonable()
    {
        Assert.Less(Mathf.Abs(_config.centerOfMassOffset.y), 1f);
    }

    [Test]
    public void SuspensionValues_ArePositive()
    {
        Assert.Greater(_config.frontSpringForce, 0f);
        Assert.Greater(_config.rearSpringForce, 0f);
        Assert.Greater(_config.frontDamperForce, 0f);
        Assert.Greater(_config.rearDamperForce, 0f);
    }
}

[TestFixture]
public class MotorcyclePhysicsTests
{
    private GameObject _go;
    private MotorcyclePhysics _physics;
    private Rigidbody _rb;
    private HondaCG125Config _config;

    [SetUp]
    public void SetUp()
    {
        _go = new GameObject("TestMotorcycle");
        _rb = _go.AddComponent<Rigidbody>();
        _physics = _go.AddComponent<MotorcyclePhysics>();
        _config = ScriptableObject.CreateInstance<HondaCG125Config>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_go);
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void CalculateSpeedKmh_ReturnsZero_WhenStationary()
    {
        float speed = _physics.CalculateSpeedKmh();
        Assert.AreEqual(0f, speed, 0.1f);
    }

    [Test]
    public void CurrentLeanAngle_StartsAtZero()
    {
        Assert.AreEqual(0f, _physics.CurrentLeanAngle, 0.01f);
    }

    [Test]
    public void IsGrounded_DefaultsFalse()
    {
        Assert.IsFalse(_physics.IsGrounded);
    }
}

[TestFixture]
public class VehicleDamageTests
{
    private GameObject _go;
    private VehicleDamage _damage;
    private HondaCG125Config _config;

    [SetUp]
    public void SetUp()
    {
        _go = new GameObject("TestVehicle");
        _go.AddComponent<Rigidbody>();
        _damage = _go.AddComponent<VehicleDamage>();
        _config = ScriptableObject.CreateInstance<HondaCG125Config>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_go);
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void InitialHealth_IsMax()
    {
        Assert.AreEqual(100f, _damage.CurrentHealth, 0.01f);
    }

    [Test]
    public void HealthPercentage_IsOneInitially()
    {
        Assert.AreEqual(1f, _damage.HealthPercentage, 0.01f);
    }

    [Test]
    public void TakeDamage_ReducesHealth()
    {
        _damage.TakeDamage(30f);
        Assert.AreEqual(70f, _damage.CurrentHealth, 0.01f);
    }

    [Test]
    public void TakeDamage_DoesNotGoBelowZero()
    {
        _damage.TakeDamage(200f);
        Assert.AreEqual(0f, _damage.CurrentHealth);
    }

    [Test]
    public void IsDestroyed_TrueWhenHealthZero()
    {
        _damage.TakeDamage(100f);
        Assert.IsTrue(_damage.IsDestroyed);
    }

    [Test]
    public void Repair_RestoresHealth()
    {
        _damage.TakeDamage(50f);
        _damage.Repair(30f);
        Assert.AreEqual(80f, _damage.CurrentHealth, 0.01f);
    }

    [Test]
    public void Repair_DoesNotExceedMax()
    {
        _damage.Repair(50f);
        Assert.AreEqual(100f, _damage.CurrentHealth);
    }

    [Test]
    public void ResetDamage_FullRestore()
    {
        _damage.TakeDamage(80f);
        _damage.ResetDamage();
        Assert.AreEqual(100f, _damage.CurrentHealth);
        Assert.IsFalse(_damage.IsDestroyed);
    }
}

[TestFixture]
public class VehicleLightsTests
{
    private GameObject _go;
    private VehicleLights _lights;

    [SetUp]
    public void SetUp()
    {
        _go = new GameObject("TestLights");
        _lights = _go.AddComponent<VehicleLights>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_go);
    }

    [Test]
    public void HeadlightOn_DefaultsFalse()
    {
        Assert.IsFalse(_lights.HeadlightOn);
    }

    [Test]
    public void BrakeActive_DefaultsFalse()
    {
        Assert.IsFalse(_lights.BrakeActive);
    }

    [Test]
    public void LeftIndicatorOn_DefaultsFalse()
    {
        Assert.IsFalse(_lights.LeftIndicatorOn);
    }

    [Test]
    public void RightIndicatorOn_DefaultsFalse()
    {
        Assert.IsFalse(_lights.RightIndicatorOn);
    }

    [Test]
    public void ToggleHeadlight_TogglesState()
    {
        _lights.ToggleHeadlight();
        Assert.IsTrue(_lights.HeadlightOn);
        _lights.ToggleHeadlight();
        Assert.IsFalse(_lights.HeadlightOn);
    }

    [Test]
    public void SetBrake_SetsState()
    {
        _lights.SetBrake(true);
        Assert.IsTrue(_lights.BrakeActive);
        _lights.SetBrake(false);
        Assert.IsFalse(_lights.BrakeActive);
    }

    [Test]
    public void ToggleLeftIndicator_SetsLeftAndClearsRight()
    {
        _lights.ToggleLeftIndicator();
        Assert.IsTrue(_lights.LeftIndicatorOn);
        Assert.IsFalse(_lights.RightIndicatorOn);
    }

    [Test]
    public void ToggleRightIndicator_SetsRightAndClearsLeft()
    {
        _lights.ToggleRightIndicator();
        Assert.IsTrue(_lights.RightIndicatorOn);
        Assert.IsFalse(_lights.LeftIndicatorOn);
    }

    [Test]
    public void CancelIndicators_ClearsAll()
    {
        _lights.ToggleLeftIndicator();
        _lights.ToggleRightIndicator();
        _lights.CancelIndicators();
        Assert.IsFalse(_lights.LeftIndicatorOn);
        Assert.IsFalse(_lights.RightIndicatorOn);
    }
}

[TestFixture]
public class VehicleControllerModelTests
{
    [Test]
    public void VehicleControllerModel_FuelPercent_CalculatesCorrectly()
    {
        var model = new VehicleControllerModel
        {
            CurrentFuel = 8.5f,
            MaxFuel = 17f
        };

        Assert.AreEqual(0.5f, model.FuelPercent, 0.001f);
    }

    [Test]
    public void VehicleControllerModel_SpeedPercent_CalculatesCorrectly()
    {
        var model = new VehicleControllerModel
        {
            CurrentSpeed = 55f,
            MaxSpeed = 110f
        };

        Assert.AreEqual(0.5f, model.SpeedPercent, 0.001f);
    }

    [Test]
    public void VehicleControllerModel_Refuel_DoesNotExceedMax()
    {
        var model = new VehicleControllerModel { CurrentFuel = 15f, MaxFuel = 17f };
        model.Refuel(5f);
        Assert.AreEqual(17f, model.CurrentFuel);
    }

    [Test]
    public void VehicleControllerModel_Refuel_AddsCorrectAmount()
    {
        var model = new VehicleControllerModel { CurrentFuel = 5f, MaxFuel = 17f };
        model.Refuel(5f);
        Assert.AreEqual(10f, model.CurrentFuel);
    }

    [Test]
    public void VehicleControllerModel_TakeDamage_ReducesHealth()
    {
        var model = new VehicleControllerModel { CurrentHealth = 100f };
        model.TakeDamage(30f);
        Assert.AreEqual(70f, model.CurrentHealth);
    }

    [Test]
    public void VehicleControllerModel_TakeDamage_DoesNotGoBelowZero()
    {
        var model = new VehicleControllerModel { CurrentHealth = 10f };
        model.TakeDamage(50f);
        Assert.AreEqual(0f, model.CurrentHealth);
    }

    [Test]
    public void VehicleControllerModel_Repair_IncreasesHealth()
    {
        var model = new VehicleControllerModel { CurrentHealth = 50f, MaxHealth = 100f };
        model.Repair(20f);
        Assert.AreEqual(70f, model.CurrentHealth);
    }

    [Test]
    public void VehicleControllerModel_Repair_DoesNotExceedMax()
    {
        var model = new VehicleControllerModel { CurrentHealth = 90f, MaxHealth = 100f };
        model.Repair(20f);
        Assert.AreEqual(100f, model.CurrentHealth);
    }
}

public class VehicleControllerModel
{
    public string VehicleId = Constants.Vehicle.HondaCG125.VehicleId;
    public string DisplayName = Constants.Vehicle.HondaCG125.DisplayName;
    public float MaxSpeed = Constants.Vehicle.HondaCG125.MaxSpeedKmh;
    public float MaxFuel = Constants.Vehicle.HondaCG125.MaxFuel;
    public float MaxHealth = Constants.Vehicle.HondaCG125.MaxHealth;
    public float CurrentFuel;
    public float CurrentHealth;
    public float CurrentSpeed;
    public int CurrentGear;
    public bool IsEngineRunning;
    public bool HasRider;

    public float FuelPercent => MaxFuel > 0 ? CurrentFuel / MaxFuel : 0f;
    public float SpeedPercent => MaxSpeed > 0 ? Mathf.Abs(CurrentSpeed) / MaxSpeed : 0f;

    public void Refuel(float amount)
    {
        CurrentFuel = Mathf.Min(CurrentFuel + amount, MaxFuel);
    }

    public void TakeDamage(float amount)
    {
        CurrentHealth = Mathf.Max(0f, CurrentHealth - amount);
    }

    public void Repair(float amount)
    {
        CurrentHealth = Mathf.Min(CurrentHealth + amount, MaxHealth);
    }
}
