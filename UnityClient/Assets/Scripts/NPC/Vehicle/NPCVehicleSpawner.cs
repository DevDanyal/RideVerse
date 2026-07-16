using System.Collections.Generic;
using UnityEngine;
using RideVerse.NPC.Core;
using RideVerse.NPC.Brain;
using RideVerse.NPC.Movement;

namespace RideVerse.NPC.Vehicle
{
    public class NPCVehicleSpawner : MonoBehaviour
    {
        [SerializeField] private float _spawnRadius = 100f;
        [SerializeField] private int _maxVehicles = 10;

        private List<GameObject> _spawnedVehicles = new List<GameObject>();
        private NPCConfig _config;

        public int ActiveVehicles => _spawnedVehicles.Count;

        public void Initialize(NPCConfig config)
        {
            _config = config;
        }

        public GameObject SpawnPersonalVehicle(Vector3 position, float rotation)
        {
            if (_spawnedVehicles.Count >= _maxVehicles) return null;

            var vehicle = CreateDefaultVehicle(position, rotation);
            _spawnedVehicles.Add(vehicle);
            return vehicle;
        }

        public void DespawnVehicle(GameObject vehicle)
        {
            if (vehicle == null) return;
            _spawnedVehicles.Remove(vehicle);
            Destroy(vehicle);
        }

        public void DespawnAllVehicles()
        {
            foreach (var vehicle in _spawnedVehicles)
            {
                if (vehicle != null) Destroy(vehicle);
            }
            _spawnedVehicles.Clear();
        }

        private GameObject CreateDefaultVehicle(Vector3 position, float rotation)
        {
            var vehicle = GameObject.CreatePrimitive(PrimitiveType.Cube);
            vehicle.name = "NPC_Vehicle";
            vehicle.transform.position = position;
            vehicle.transform.rotation = Quaternion.Euler(0f, rotation, 0f);
            vehicle.transform.localScale = new Vector3(2f, 1f, 4f);

            var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            mat.color = new Color(
                Random.Range(0.3f, 0.9f),
                Random.Range(0.3f, 0.9f),
                Random.Range(0.3f, 0.9f));
            vehicle.GetComponent<Renderer>().material = mat;

            return vehicle;
        }
    }
}
