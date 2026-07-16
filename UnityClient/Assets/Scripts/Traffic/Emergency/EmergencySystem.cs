using System.Collections.Generic;
using UnityEngine;
using RideVerse.Traffic.Core;

namespace RideVerse.Traffic.Emergency
{
    public class EmergencySystem : MonoBehaviour
    {
        private TrafficConfig _config;
        private List<TrafficVehicle> _emergencyVehicles = new List<TrafficVehicle>();

        public IReadOnlyList<TrafficVehicle> EmergencyVehicles => _emergencyVehicles;

        public void Initialize(TrafficConfig config)
        {
            _config = config;
        }

        public void RegisterEmergencyVehicle(TrafficVehicle vehicle)
        {
            if (!_emergencyVehicles.Contains(vehicle))
            {
                _emergencyVehicles.Add(vehicle);
                vehicle.SetEmergency(true, GetEmergencyType(vehicle.VehicleType));
            }
        }

        public void UnregisterEmergencyVehicle(TrafficVehicle vehicle)
        {
            _emergencyVehicles.Remove(vehicle);
            vehicle.SetEmergency(false, EmergencyType.None);
        }

        public bool ShouldYield(TrafficVehicle vehicle)
        {
            if (vehicle.IsEmergency) return false;

            foreach (var emergency in _emergencyVehicles)
            {
                if (emergency == null) continue;

                float dist = Vector3.Distance(vehicle.Position, emergency.Position);
                if (dist < _config.emergencyYieldDistance)
                {
                    float dot = Vector3.Dot(vehicle.Forward, (emergency.Position - vehicle.Position).normalized);
                    if (dot > 0f || dist < _config.emergencyYieldDistance * 0.5f)
                        return true;
                }
            }

            return false;
        }

        public bool IsEmergencyNearby(TrafficVehicle vehicle)
        {
            foreach (var emergency in _emergencyVehicles)
            {
                if (emergency == null) continue;

                float dist = Vector3.Distance(vehicle.Position, emergency.Position);
                if (dist < _config.emergencyYieldDistance)
                    return true;
            }

            return false;
        }

        public TrafficVehicle GetNearestEmergencyVehicle(Vector3 position)
        {
            TrafficVehicle nearest = null;
            float nearestDist = float.MaxValue;

            foreach (var emergency in _emergencyVehicles)
            {
                if (emergency == null) continue;

                float dist = Vector3.Distance(position, emergency.Position);
                if (dist < nearestDist)
                {
                    nearestDist = dist;
                    nearest = emergency;
                }
            }

            return nearest;
        }

        public Vector3 GetYieldDirection(TrafficVehicle yieldingVehicle, TrafficVehicle emergencyVehicle)
        {
            Vector3 awayFromEmergency = (yieldingVehicle.Position - emergencyVehicle.Position).normalized;
            awayFromEmergency.y = 0f;

            Vector3 right = Vector3.Cross(Vector3.up, awayFromEmergency);

            float lateralDist = Vector3.Dot(right, yieldingVehicle.Position - emergencyVehicle.Position);
            if (lateralDist > 0)
                return right;
            else
                return -right;
        }

        private EmergencyType GetEmergencyType(TrafficVehicleType vehicleType)
        {
            switch (vehicleType)
            {
                case TrafficVehicleType.Police:
                    return EmergencyType.Police;
                case TrafficVehicleType.Bus:
                    return EmergencyType.Ambulance;
                case TrafficVehicleType.CargoTruck:
                    return EmergencyType.FireTruck;
                default:
                    return EmergencyType.None;
            }
        }

        public void Cleanup()
        {
            _emergencyVehicles.RemoveAll(v => v == null);
        }
    }
}
