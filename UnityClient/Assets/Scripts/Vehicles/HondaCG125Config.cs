using UnityEngine;

namespace RideVerse.Vehicles
{
    [CreateAssetMenu(fileName = "HondaCG125Config", menuName = "RideVerse/Vehicles/HondaCG125Config")]
    public class HondaCG125Config : ScriptableObject
    {
        [Header("Engine")]
        public float engineDisplacement = 125f;
        public float maxRPM = 9500f;
        public float idleRPM = 1300f;
        public float redlineRPM = 8500f;
        public float maxPower = 11.5f;
        public float maxTorque = 10.5f;
        public float maxSpeedKmh = 110f;
        public AnimationCurve torqueCurve = AnimationCurve.EaseInOut(0f, 0f, 0.5f, 1f);
        public AnimationCurve powerCurve = AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);

        [Header("Transmission")]
        public int totalGears = 5;
        public int neutralGear = 0;
        public float finalDriveRatio = 2.533f;
        public float[] gearRatios = new float[]
        {
            0f,
            2.846f,
            1.875f,
            1.400f,
            1.115f,
            0.963f
        };

        [Header("Clutch")]
        public float clutchEngageRPM = 1500f;
        public float clutchSlipRange = 500f;
        public float clutchEngageSpeed = 5f;

        [Header("Physical Dimensions")]
        public float mass = 128f;
        public float wheelBase = 1.24f;
        public float frontWheelRadius = 0.28f;
        public float rearWheelRadius = 0.28f;
        public float handlebarWidth = 0.68f;

        [Header("Steering")]
        public float steeringAngle = 45f;
        public float steeringSpeed = 120f;
        public float speedDependentSteerFactor = 0.4f;

        [Header("Lean")]
        public float maxLeanAngle = 40f;
        public float leanSpeed = 80f;
        public float leanRecoverySpeed = 120f;
        public float lowSpeedLeanLimit = 25f;
        public float leanToSteerRatio = 0.7f;

        [Header("Suspension")]
        public float frontSuspensionTravel = 0.13f;
        public float rearSuspensionTravel = 0.09f;
        public float frontSpringForce = 35000f;
        public float rearSpringForce = 42000f;
        public float frontDamperForce = 4500f;
        public float rearDamperForce = 5000f;
        public float suspensionRestLength = 0.3f;

        [Header("Braking")]
        public float frontBrakeForce = 4500f;
        public float rearBrakeForce = 3500f;
        public float engineBrakeForce = 800f;
        public float absActivationThreshold = 0.3f;

        [Header("Fuel")]
        public float maxFuel = 17f;
        public float fuelConsumptionRate = 0.04f;
        public float fuelWarningThreshold = 3f;

        [Header("Health / Damage")]
        public float maxHealth = 100f;
        public float fallDamageThreshold = 3f;
        public float fallDamageMultiplier = 15f;

        [Header("Effects")]
        public float exhaustSmokeRate = 0.1f;
        public float dustParticleSpeed = 2f;

        [Header("Center of Mass")]
        public Vector3 centerOfMassOffset = new Vector3(0f, -0.3f, 0.1f);
    }
}
