using System;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.World.Core;
using RideVerse.World.Layout;

namespace RideVerse.World.Buildings
{
    public class BuildingPool : MonoBehaviour
    {
        [SerializeField] private int _initialPoolSize = 20;

        private Dictionary<BuildingType, Queue<GameObject>> _pool = new Dictionary<BuildingType, Queue<GameObject>>();
        private Dictionary<BuildingType, GameObject> _prefabs = new Dictionary<BuildingType, GameObject>();
        private Transform _poolRoot;
        private Material _defaultMaterial;

        public int TotalPooled { get; private set; }
        public int TotalActive { get; private set; }

        public void Initialize(Transform poolRoot)
        {
            _poolRoot = poolRoot;
            _defaultMaterial = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            _defaultMaterial.color = new Color(0.7f, 0.68f, 0.65f);

            foreach (BuildingType type in Enum.GetValues(typeof(BuildingType)))
            {
                _pool[type] = new Queue<GameObject>();
            }

            Debug.Log("[BuildingPool] Initialized");
        }

        public void RegisterPrefab(BuildingType type, GameObject prefab)
        {
            if (prefab == null) return;
            _prefabs[type] = prefab;
        }

        public GameObject Get(BuildingType type, Vector3 position, Quaternion rotation, Transform parent)
        {
            GameObject obj = null;

            if (_pool.TryGetValue(type, out var queue) && queue.Count > 0)
            {
                obj = queue.Dequeue();
            }

            if (obj == null)
            {
                obj = CreateDefaultBuilding(type);
            }

            obj.transform.SetParent(parent);
            obj.transform.position = position;
            obj.transform.rotation = rotation;
            obj.SetActive(true);
            TotalActive++;
            return obj;
        }

        public void Return(BuildingType type, GameObject obj)
        {
            if (obj == null) return;
            obj.SetActive(false);
            obj.transform.SetParent(_poolRoot);

            if (_pool.TryGetValue(type, out var queue))
            {
                queue.Enqueue(obj);
            }

            TotalActive--;
            TotalPooled++;
        }

        public void PreWarm(BuildingType type, int count)
        {
            if (!_pool.TryGetValue(type, out var queue)) return;

            for (int i = 0; i < count; i++)
            {
                var obj = CreateDefaultBuilding(type);
                obj.SetActive(false);
                obj.transform.SetParent(_poolRoot);
                queue.Enqueue(obj);
                TotalPooled++;
            }
        }

        public void Clear()
        {
            foreach (var kvp in _pool)
            {
                while (kvp.Value.Count > 0)
                {
                    var obj = kvp.Value.Dequeue();
                    if (obj != null) Destroy(obj);
                }
            }
            TotalPooled = 0;
            TotalActive = 0;
        }

        private GameObject CreateDefaultBuilding(BuildingType type)
        {
            var obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obj.name = $"Pooled_{type}";

            Vector3 scale = GetDefaultScale(type);
            obj.transform.localScale = scale;

            var renderer = obj.GetComponent<Renderer>();
            renderer.material = new Material(_defaultMaterial);
            renderer.material.color = GetColorForType(type);

            return obj;
        }

        private Vector3 GetDefaultScale(BuildingType type)
        {
            switch (type)
            {
                case BuildingType.House: return new Vector3(8f, 5f, 8f);
                case BuildingType.Apartment: return new Vector3(15f, 20f, 15f);
                case BuildingType.Shop: return new Vector3(10f, 5f, 10f);
                case BuildingType.PoliceStation: return new Vector3(15f, 6f, 15f);
                case BuildingType.Hospital: return new Vector3(25f, 10f, 25f);
                case BuildingType.GasStation: return new Vector3(12f, 4f, 12f);
                case BuildingType.Garage: return new Vector3(14f, 5f, 14f);
                case BuildingType.Bank: return new Vector3(15f, 8f, 12f);
                case BuildingType.ParkingArea: return new Vector3(30f, 1f, 30f);
                default: return new Vector3(8f, 5f, 8f);
            }
        }

        private Color GetColorForType(BuildingType type)
        {
            switch (type)
            {
                case BuildingType.PoliceStation: return new Color(0.2f, 0.3f, 0.6f);
                case BuildingType.Hospital: return new Color(0.9f, 0.9f, 0.95f);
                case BuildingType.GasStation: return new Color(0.9f, 0.3f, 0.2f);
                case BuildingType.Bank: return new Color(0.6f, 0.55f, 0.4f);
                default: return new Color(0.7f, 0.68f, 0.65f);
            }
        }
    }
}
