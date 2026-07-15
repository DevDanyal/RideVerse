using NUnit.Framework;
using RideVerse.Vehicles;
using RideVerse.Core;
using UnityEngine;

[TestFixture]
public class SportsCarConstantsTests
{
    [Test]
    public void SportsCar_VehicleId_IsNotEmpty()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Vehicle.SportsCar.VehicleId));
    }

    [Test]
    public void SportsCar_DisplayName_IsNotEmpty()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Vehicle.SportsCar.DisplayName));
    }

    [Test]
    public void SportsCar_MaxSpeedKmh_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.MaxSpeedKmh, 200f);
        Assert.Less(Constants.Vehicle.SportsCar.MaxSpeedKmh, 350f);
    }

    [Test]
    public void SportsCar_MaxRPM_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.MaxRPM, 6000f);
        Assert.Less(Constants.Vehicle.SportsCar.MaxRPM, 10000f);
    }

    [Test]
    public void SportsCar_IdleRPM_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.IdleRPM, 0f);
        Assert.Less(Constants.Vehicle.SportsCar.IdleRPM, 1500f);
    }

    [Test]
    public void SportsCar_RedlineRPM_IsLessThanMaxRPM()
    {
        Assert.Less(Constants.Vehicle.SportsCar.RedlineRPM, Constants.Vehicle.SportsCar.MaxRPM);
    }

    [Test]
    public void SportsCar_MaxPower_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.MaxPower, 200f);
        Assert.Less(Constants.Vehicle.SportsCar.MaxPower, 500f);
    }

    [Test]
    public void SportsCar_MaxTorque_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.MaxTorque, 300f);
        Assert.Less(Constants.Vehicle.SportsCar.MaxTorque, 600f);
    }

    [Test]
    public void SportsCar_TotalGears_IsSix()
    {
        Assert.AreEqual(6, Constants.Vehicle.SportsCar.TotalGears);
    }

    [Test]
    public void SportsCar_GearRatios_HasCorrectLength()
    {
        float[] ratios = Constants.Vehicle.SportsCar.GearRatios;
        Assert.AreEqual(Constants.Vehicle.SportsCar.TotalGears + 1, ratios.Length);
    }

    [Test]
    public void SportsCar_GearRatios_NeutralIsZero()
    {
        float[] ratios = Constants.Vehicle.SportsCar.GearRatios;
        Assert.AreEqual(0f, ratios[0]);
    }

    [Test]
    public void SportsCar_GearRatios_AreInDecreasingOrder()
    {
        float[] ratios = Constants.Vehicle.SportsCar.GearRatios;
        for (int i = 2; i < ratios.Length - 1; i++)
        {
            Assert.Less(ratios[i], ratios[i - 1],
                $"Gear {i} ratio ({ratios[i]}) should be less than gear {i - 1} ({ratios[i - 1]})");
        }
    }

    [Test]
    public void SportsCar_Mass_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.Mass, 1200f);
        Assert.Less(Constants.Vehicle.SportsCar.Mass, 2000f);
    }

    [Test]
    public void SportsCar_MaxFuel_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.MaxFuel, 40f);
        Assert.Less(Constants.Vehicle.SportsCar.MaxFuel, 80f);
    }

    [Test]
    public void SportsCar_MaxHealth_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.MaxHealth, 0f);
    }

    [Test]
    public void SportsCar_MaxSteerAngle_IsRealistic()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.MaxSteerAngle, 25f);
        Assert.Less(Constants.Vehicle.SportsCar.MaxSteerAngle, 50f);
    }

    [Test]
    public void SportsCar_FrontBrakeForce_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.FrontBrakeForce, 0f);
    }

    [Test]
    public void SportsCar_RearBrakeForce_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.RearBrakeForce, 0f);
    }

    [Test]
    public void SportsCar_HandbrakeForce_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.HandbrakeForce, 0f);
    }

    [Test]
    public void SportsCar_DownforceCoefficient_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.DownforceCoefficient, 0f);
    }

    [Test]
    public void SportsCar_DragCoefficient_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.DragCoefficient, 0f);
    }

    [Test]
    public void SportsCar_DriftAngleThreshold_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.SportsCar.DriftAngleThreshold, 0f);
    }
}

[TestFixture]
public class CarConfigTests
{
    private CarConfig _config;

    [SetUp]
    public void SetUp()
    {
        _config = ScriptableObject.CreateInstance<CarConfig>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_config);
    }

    [Test]
    public void DefaultValues_MatchConstants()
    {
        Assert.AreEqual(1500f, _config.mass);
        Assert.AreEqual(6, _config.totalGears);
        Assert.AreEqual(260f, _config.maxSpeedKmh);
        Assert.AreEqual(8000f, _config.maxRPM);
    }

    [Test]
    public void GearRatios_HasCorrectLength()
    {
        Assert.AreEqual(7, _config.gearRatios.Length);
    }

    [Test]
    public void GearRatios_NeutralIsZero()
    {
        Assert.AreEqual(0f, _config.gearRatios[0]);
    }

    [Test]
    public void CenterOfMassOffset_IsReasonable()
    {
        Assert.Less(Mathf.Abs(_config.centerOfMassOffset.y), 2f);
    }

    [Test]
    public void SuspensionValues_ArePositive()
    {
        Assert.Greater(_config.frontSpringForce, 0f);
        Assert.Greater(_config.rearSpringForce, 0f);
        Assert.Greater(_config.frontDamperForce, 0f);
        Assert.Greater(_config.rearDamperForce, 0f);
    }

    [Test]
    public void BrakeValues_ArePositive()
    {
        Assert.Greater(_config.frontBrakeForce, 0f);
        Assert.Greater(_config.rearBrakeForce, 0f);
        Assert.Greater(_config.handbrakeForce, 0f);
    }

    [Test]
    public void DriftValues_ArePositive()
    {
        Assert.Greater(_config.driftSteerAssist, 0f);
        Assert.Greater(_config.driftThrottleBoost, 0f);
        Assert.Greater(_config.driftAngleThreshold, 0f);
    }

    [Test]
    public void AerodynamicsValues_ArePositive()
    {
        Assert.Greater(_config.downforceCoefficient, 0f);
        Assert.Greater(_config.dragCoefficient, 0f);
        Assert.Greater(_config.frontalArea, 0f);
    }

    [Test]
    public void FuelValues_ArePositive()
    {
        Assert.Greater(_config.maxFuel, 0f);
        Assert.Greater(_config.fuelConsumptionRate, 0f);
    }
}

[TestFixture]
public class CarPhysicsTests
{
    private GameObject _go;
    private CarPhysics _physics;
    private Rigidbody _rb;

    [SetUp]
    public void SetUp()
    {
        _go = new GameObject("TestCarPhysics");
        _rb = _go.AddComponent<Rigidbody>();
        _physics = _go.AddComponent<CarPhysics>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_go);
    }

    [Test]
    public void IsGrounded_DefaultsFalse()
    {
        Assert.IsFalse(_physics.IsGrounded);
    }

    [Test]
    public void WeightTransferFront_DefaultsZero()
    {
        Assert.AreEqual(0f, _physics.WeightTransferFront, 0.01f);
    }

    [Test]
    public void WeightTransferRear_DefaultsZero()
    {
        Assert.AreEqual(0f, _physics.WeightTransferRear, 0.01f);
    }
}

[TestFixture]
public class CarDriftControllerTests
{
    private GameObject _go;
    private CarDriftController _driftController;
    private Rigidbody _rb;

    [SetUp]
    public void SetUp()
    {
        _go = new GameObject("TestDriftController");
        _rb = _go.AddComponent<Rigidbody>();
        _driftController = _go.AddComponent<CarDriftController>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_go);
    }

    [Test]
    public void DriftAngle_DefaultsToZero()
    {
        Assert.AreEqual(0f, _driftController.DriftAngle, 0.01f);
    }

    [Test]
    public void IsDrifting_DefaultsFalse()
    {
        Assert.IsFalse(_driftController.IsDrifting);
    }

    [Test]
    public void DriftScore_DefaultsZero()
    {
        Assert.AreEqual(0f, _driftController.DriftScore, 0.01f);
    }

    [Test]
    public void DriftTime_DefaultsZero()
    {
        Assert.AreEqual(0f, _driftController.DriftTime, 0.01f);
    }

    [Test]
    public void ResetDrift_ClearsAll()
    {
        _driftController.ResetDrift();
        Assert.IsFalse(_driftController.IsDrifting);
        Assert.AreEqual(0f, _driftController.DriftAngle, 0.01f);
        Assert.AreEqual(0f, _driftController.DriftScore, 0.01f);
    }
}

[TestFixture]
public class CarDamageTests
{
    private GameObject _go;
    private CarDamage _damage;
    private CarConfig _config;

    [SetUp]
    public void SetUp()
    {
        _go = new GameObject("TestCarDamage");
        _go.AddComponent<Rigidbody>();
        _damage = _go.AddComponent<CarDamage>();
        _config = ScriptableObject.CreateInstance<CarConfig>();
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

    [Test]
    public void TakeWheelDamage_ReducesHealth()
    {
        _damage.TakeWheelDamage(100f);
        Assert.Less(_damage.CurrentHealth, 100f);
    }

    [Test]
    public void TakeEngineDamage_ReducesHealth()
    {
        _damage.TakeEngineDamage(100f);
        Assert.Less(_damage.CurrentHealth, 100f);
    }
}

[TestFixture]
public class CarLightsTests
{
    private GameObject _go;
    private CarLights _lights;

    [SetUp]
    public void SetUp()
    {
        _go = new GameObject("TestCarLights");
        _lights = _go.AddComponent<CarLights>();
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
    public void ReverseActive_DefaultsFalse()
    {
        Assert.IsFalse(_lights.ReverseActive);
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
    public void SetReverse_SetsState()
    {
        _lights.SetReverse(true);
        Assert.IsTrue(_lights.ReverseActive);
        _lights.SetReverse(false);
        Assert.IsFalse(_lights.ReverseActive);
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
public class GearIndicatorUITests
{
    private GameObject _go;
    private GearIndicatorUI _gearUI;

    [SetUp]
    public void SetUp()
    {
        _go = new GameObject("TestGearUI");
        _gearUI = _go.AddComponent<GearIndicatorUI>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_go);
    }

    [Test]
    public void ResetDisplay_SetsNeutral()
    {
        _gearUI.ResetDisplay();
        _gearUI.UpdateGear(0);
        _gearUI.UpdateGear(1);
    }
}

[TestFixture]
public class FuelGaugeUITests
{
    private GameObject _go;
    private FuelGaugeUI _fuelUI;

    [SetUp]
    public void SetUp()
    {
        _go = new GameObject("TestFuelUI");
        _fuelUI = _go.AddComponent<FuelGaugeUI>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_go);
    }

    [Test]
    public void ResetGauge_NoError()
    {
        _fuelUI.ResetGauge();
    }

    [Test]
    public void UpdateFuel_NoError()
    {
        _fuelUI.UpdateFuel(50f, 60f);
    }

    [Test]
    public void UpdateFuelPercent_NoError()
    {
        _fuelUI.UpdateFuelPercent(0.5f);
    }
}

[TestFixture]
public class CarControllerModelTests
{
    [Test]
    public void CarControllerModel_FuelPercent_CalculatesCorrectly()
    {
        var model = new CarControllerModel
        {
            CurrentFuel = 30f,
            MaxFuel = 60f
        };
        Assert.AreEqual(0.5f, model.FuelPercent, 0.001f);
    }

    [Test]
    public void CarControllerModel_SpeedPercent_CalculatesCorrectly()
    {
        var model = new CarControllerModel
        {
            CurrentSpeed = 130f,
            MaxSpeed = 260f
        };
        Assert.AreEqual(0.5f, model.SpeedPercent, 0.001f);
    }

    [Test]
    public void CarControllerModel_Refuel_DoesNotExceedMax()
    {
        var model = new CarControllerModel { CurrentFuel = 50f, MaxFuel = 60f };
        model.Refuel(20f);
        Assert.AreEqual(60f, model.CurrentFuel);
    }

    [Test]
    public void CarControllerModel_Refuel_AddsCorrectAmount()
    {
        var model = new CarControllerModel { CurrentFuel = 20f, MaxFuel = 60f };
        model.Refuel(20f);
        Assert.AreEqual(40f, model.CurrentFuel);
    }

    [Test]
    public void CarControllerModel_TakeDamage_ReducesHealth()
    {
        var model = new CarControllerModel { CurrentHealth = 100f };
        model.TakeDamage(30f);
        Assert.AreEqual(70f, model.CurrentHealth);
    }

    [Test]
    public void CarControllerModel_TakeDamage_DoesNotGoBelowZero()
    {
        var model = new CarControllerModel { CurrentHealth = 10f };
        model.TakeDamage(50f);
        Assert.AreEqual(0f, model.CurrentHealth);
    }

    [Test]
    public void CarControllerModel_Repair_IncreasesHealth()
    {
        var model = new CarControllerModel { CurrentHealth = 50f, MaxHealth = 100f };
        model.Repair(20f);
        Assert.AreEqual(70f, model.CurrentHealth);
    }

    [Test]
    public void CarControllerModel_Repair_DoesNotExceedMax()
    {
        var model = new CarControllerModel { CurrentHealth = 90f, MaxHealth = 100f };
        model.Repair(20f);
        Assert.AreEqual(100f, model.CurrentHealth);
    }
}

public class CarControllerModel
{
    public string VehicleId = Constants.Vehicle.SportsCar.VehicleId;
    public string DisplayName = Constants.Vehicle.SportsCar.DisplayName;
    public float MaxSpeed = Constants.Vehicle.SportsCar.MaxSpeedKmh;
    public float MaxFuel = Constants.Vehicle.SportsCar.MaxFuel;
    public float MaxHealth = Constants.Vehicle.SportsCar.MaxHealth;
    public float CurrentFuel;
    public float CurrentHealth;
    public float CurrentSpeed;
    public int CurrentGear;
    public bool IsEngineRunning;
    public bool HasDriver;

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
