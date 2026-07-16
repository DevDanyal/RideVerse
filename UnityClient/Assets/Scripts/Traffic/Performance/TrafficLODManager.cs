using System.Collections.Generic;
using UnityEngine;
using RideVerse.Traffic.Core;
using RideVerse.Traffic.AI;

namespace RideVerse.Traffic.Performance
{
    public class TrafficLODManager : MonoBehaviour
    {
        private TrafficConfig _config;
        private Transform _playerTransform;
        private Dictionary<TrafficVehicle, TrafficVehicleLOD> _vehicleLODs = new Dictionary<TrafficVehicle, TrafficVehicleLOD>();
        private Dictionary<TrafficVehicle, float> _updateTimers = new Dictionary<TrafficVehicle, float>();
        private int _updateQueueIndex;

        public int ManagedVehicleCount => _vehicleLODs.Count;

        public void Initialize(TrafficConfig config)
        {
            _config = config;
        }

        public void SetPlayerTransform(Transform player)
        {
            _playerTransform = player;
        }

        public void RegisterVehicle(TrafficVehicle vehicle)
        {
            if (!_vehicleLODs.ContainsKey(vehicle))
            {
                _vehicleLODs[vehicle] = TrafficVehicleLOD.Full;
                _updateTimers[vehicle] = 0f;
            }
        }

        public void UnregisterVehicle(TrafficVehicle vehicle)
        {
            _vehicleLODs.Remove(vehicle);
            _updateTimers.Remove(vehicle);
        }

        public TrafficVehicleLOD GetLODLevel(TrafficVehicle vehicle)
        {
            if (_playerTransform == null || vehicle == null)
                return TrafficVehicleLOD.Culled;

            if (!_vehicleLODs.ContainsKey(vehicle))
                return TrafficVehicleLOD.Culled;

            float distance = Vector3.Distance(_playerTransform.position, vehicle.transform.position);

            if (distance <= _config.lodDistanceFull)
                return TrafficVehicleLOD.Full;
            if (distance <= _config.lodDistanceSimplified)
                return TrafficVehicleLOD.Simplified;
            return TrafficVehicleLOD.Culled;
        }

        public bool ShouldUpdate(TrafficVehicle vehicle)
        {
            if (!_vehicleLODs.ContainsKey(vehicle)) return false;

            var lod = GetLODLevel(vehicle);
            _vehicleLODs[vehicle] = lod;
            vehicle.SetLODLevel(lod);

            float interval = GetUpdateInterval(lod);
            if (!_updateTimers.ContainsKey(vehicle))
                _updateTimers[vehicle] = 0f;

            _updateTimers[vehicle] += Time.deltaTime;
            if (_updateTimers[vehicle] >= interval)
            {
                _updateTimers[vehicle] = 0f;
                return true;
            }

            return false;
        }

        public void UpdateAllLODs(List<TrafficVehicle> vehicles)
        {
            foreach (var vehicle in vehicles)
            {
                if (vehicle == null) continue;

                var lod = GetLODLevel(vehicle);
                _vehicleLODs[vehicle] = lod;
                vehicle.SetLODLevel(lod);

                bool shouldEnable = lod != TrafficVehicleLOD.Culled;
                if (vehicle.gameObject.activeSelf != shouldEnable)
                {
                    vehicle.gameObject.SetActive(shouldEnable);
                }
            }
        }

        public int GetUpdatesPerFrame(List<TrafficVehicle> vehicles, int maxUpdates)
        {
            int updated = 0;
            int startIdx = _updateQueueIndex;

            while (updated < maxUpdates && vehicles.Count > 0)
            {
                int idx = (_updateQueueIndex + updated) % vehicles.Count;
                var vehicle = vehicles[idx];

                if (vehicle != null && ShouldUpdate(vehicle))
                {
                    updated++;
                }

                _updateQueueIndex = (idx + 1) % vehicles.Count;

                if (_updateQueueIndex == startIdx && updated == 0)
                    break;
            }

            return updated;
        }

        private float GetUpdateInterval(TrafficVehicleLOD lod)
        {
            switch (lod)
            {
                case TrafficVehicleLOD.Full: return _config.aiUpdateIntervalFull;
                case TrafficVehicleLOD.Simplified: return _config.aiUpdateIntervalSimplified;
                case TrafficVehicleLOD.Culled: return _config.aiUpdateIntervalCulled;
                default: return _config.aiUpdateIntervalSimplified;
            }
        }

        public void SetEnabled(TrafficVehicle vehicle, bool enabled)
        {
            if (vehicle != null)
                vehicle.gameObject.SetActive(enabled);
        }

        public void Cleanup()
        {
            var toRemove = new List<TrafficVehicle>();

            foreach (var kvp in _vehicleLODs)
            {
                if (kvp.Key == null)
                    toRemove.Add(kvp.Key);
            }

            foreach (var vehicle in toRemove)
            {
                UnregisterVehicle(vehicle);
            }
        }
    }
}
