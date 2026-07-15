using UnityEngine;

namespace RideVerse.Vehicles
{
    [CreateAssetMenu(fileName = "CarConfig", menuName = "RideVerse/Vehicles/CarConfig")]
    public class CarConfig : ScriptableObject
    {
        [Header("Identity")]
        public string vehicleId = "sports_car";
        public string displayName = "Sports Car";

        [Header("Engine")]
        public float maxRPM = 8000f;
        public float idleRPM = 800f;
        public float redlineRPM = 7500f;
        public float maxPower = 320f;
        public float maxTorque = 400f;
        public float maxSpeedKmh = 260f;
        public AnimationCurve torqueCurve = AnimationCurve.Linear(0f, 0f, 1f, 1f);

        [Header("Transmission")]
        public int totalGears = 6;
        public int neutralGear = 0;
        public int reverseGear = -1;
        public float finalDriveRatio = 3.42f;
        public float[] gearRatios = new float[]
        {
            0f, 3.636f, 2.375f, 1.761f, 1.346f, 1.062f, 0.872f
        };

        [Header("Clutch")]
        public float clutchEngageRPM = 1200f;
        public float clutchSlipRange = 400f;

        [Header("Physical")]
        public float mass = 1500f;
        public float wheelBase = 2.45f;
        public float trackWidth = 1.55f;
        public float frontWheelRadius = 0.33f;
        public float rearWheelRadius = 0.34f;

        [Header("Steering")]
        public float maxSteerAngle = 35f;
        public float steeringSpeed = 150f;
        public float speedDependentSteerFactor = 0.6f;

        [Header("Suspension")]
        public float frontSuspensionTravel = 0.08f;
        public float rearSuspensionTravel = 0.09f;
        public float frontSpringForce = 45000f;
        public float rearSpringForce = 52000f;
        public float frontDamperForce = 5500f;
        public float rearDamperForce = 6000f;
        public float antiRollBarForce = 8000f;

        [Header("Braking")]
        public float frontBrakeForce = 5500f;
        public float rearBrakeForce = 4500f;
        public float engineBrakeForce = 1200f;
        public float handbrakeForce = 3500f;
        public float absActivationThreshold = 0.2f;

        [Header("Drift")]
        public float driftSteerAssist = 0.4f;
        public float driftThrottleBoost = 1.2f;
        public float driftAngleThreshold = 10f;

        [Header("Aerodynamics")]
        public float downforceCoefficient = 0.3f;
        public float dragCoefficient = 0.35f;
        public float frontalArea = 2.2f;

        [Header("Fuel")]
        public float maxFuel = 60f;
        public float fuelConsumptionRate = 0.08f;
        public float fuelWarningThreshold = 8f;

        [Header("Health / Damage")]
        public float maxHealth = 100f;
        public float rolloverDamageThreshold = 60f;
        public float rolloverDamageAmount = 25f;

        [Header("Effects")]
        public float exhaustSmokeRate = 0.15f;
        public float dustParticleSpeed = 5f;

        [Header("Center of Mass")]
        public Vector3 centerOfMassOffset = new Vector3(0f, -0.4f, 0.2f);

        public int GetReverseGearIndex() => gearRatios.Length - 1;
    }
}
