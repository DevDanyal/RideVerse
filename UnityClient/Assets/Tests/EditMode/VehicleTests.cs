using NUnit.Framework;
using RideVerse.Vehicles;
using RideVerse.Core;
using UnityEngine;

[TestFixture]
public class VehicleConstantsTests
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
    public void HondaCG125_MaxSpeed_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.MaxSpeed, 0f);
    }

    [Test]
    public void HondaCG125_Acceleration_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.Acceleration, 0f);
    }

    [Test]
    public void HondaCG125_BrakingForce_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.BrakingForce, 0f);
    }

    [Test]
    public void HondaCG125_SteeringSpeed_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.SteeringSpeed, 0f);
    }

    [Test]
    public void HondaCG125_MaxLeanAngle_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.MaxLeanAngle, 0f);
    }

    [Test]
    public void HondaCG125_Mass_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.Mass, 0f);
    }

    [Test]
    public void HondaCG125_MaxFuel_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.MaxFuel, 0f);
    }

    [Test]
    public void HondaCG125_FuelConsumptionRate_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.FuelConsumptionRate, 0f);
    }

    [Test]
    public void HondaCG125_MaxHealth_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.MaxHealth, 0f);
    }

    [Test]
    public void HondaCG125_MaxGear_IsPositive()
    {
        Assert.Greater(Constants.Vehicle.HondaCG125.MaxGear, 0);
    }

    [Test]
    public void HondaCG125_GearRatios_HasCorrectLength()
    {
        float[] ratios = Constants.Vehicle.HondaCG125.GearRatios;
        Assert.AreEqual(Constants.Vehicle.HondaCG125.MaxGear + 1, ratios.Length);
    }

    [Test]
    public void HondaCG125_GearRatios_FirstIsZero()
    {
        float[] ratios = Constants.Vehicle.HondaCG125.GearRatios;
        Assert.AreEqual(0f, ratios[0]);
    }

    [Test]
    public void HondaCG125_GearRatios_LastIsOne()
    {
        float[] ratios = Constants.Vehicle.HondaCG125.GearRatios;
        Assert.AreEqual(1f, ratios[ratios.Length - 1]);
    }

    [Test]
    public void HondaCG125_GearRatios_AreInIncreasingOrder()
    {
        float[] ratios = Constants.Vehicle.HondaCG125.GearRatios;
        for (int i = 1; i < ratios.Length; i++)
        {
            Assert.GreaterOrEqual(ratios[i], ratios[i - 1]);
        }
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
public class VehicleControllerModelTests
{
    [Test]
    public void VehicleController_DefaultValues_AreCorrect()
    {
        var controller = new VehicleControllerModel();

        Assert.AreEqual("honda_cg125", controller.VehicleId);
        Assert.AreEqual("Honda CG125", controller.DisplayName);
        Assert.AreEqual(12f, controller.MaxSpeed);
        Assert.AreEqual(8f, controller.Acceleration);
        Assert.AreEqual(16f, controller.BrakingForce);
        Assert.AreEqual(120f, controller.SteeringSpeed);
        Assert.AreEqual(35f, controller.MaxLeanAngle);
        Assert.AreEqual(130f, controller.Mass);
        Assert.AreEqual(100f, controller.MaxFuel);
        Assert.AreEqual(100f, controller.MaxHealth);
    }

    [Test]
    public void VehicleControllerModel_FuelPercent_CalculatesCorrectly()
    {
        var model = new VehicleControllerModel
        {
            CurrentFuel = 50f,
            MaxFuel = 100f
        };

        Assert.AreEqual(0.5f, model.FuelPercent, 0.001f);
    }

    [Test]
    public void VehicleControllerModel_SpeedPercent_CalculatesCorrectly()
    {
        var model = new VehicleControllerModel
        {
            CurrentSpeed = 6f,
            MaxSpeed = 12f
        };

        Assert.AreEqual(0.5f, model.SpeedPercent, 0.001f);
    }

    [Test]
    public void VehicleControllerModel_Refuel_DoesNotExceedMax()
    {
        var model = new VehicleControllerModel { CurrentFuel = 80f, MaxFuel = 100f };
        model.Refuel(50f);
        Assert.AreEqual(100f, model.CurrentFuel);
    }

    [Test]
    public void VehicleControllerModel_Refuel_AddsCorrectAmount()
    {
        var model = new VehicleControllerModel { CurrentFuel = 30f, MaxFuel = 100f };
        model.Refuel(20f);
        Assert.AreEqual(50f, model.CurrentFuel);
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
    public float MaxSpeed = Constants.Vehicle.HondaCG125.MaxSpeed;
    public float Acceleration = Constants.Vehicle.HondaCG125.Acceleration;
    public float BrakingForce = Constants.Vehicle.HondaCG125.BrakingForce;
    public float SteeringSpeed = Constants.Vehicle.HondaCG125.SteeringSpeed;
    public float MaxLeanAngle = Constants.Vehicle.HondaCG125.MaxLeanAngle;
    public float Mass = Constants.Vehicle.HondaCG125.Mass;
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
