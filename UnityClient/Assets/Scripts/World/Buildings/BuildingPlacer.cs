using System;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.World.Core;
using RideVerse.World.Districts;
using RideVerse.World.Layout;

namespace RideVerse.World.Buildings
{
    [Serializable]
    public class BuildingData
    {
        public string Id;
        public BuildingType Type;
        public Vector3 Position;
        public float RotationY;
        public Vector3 Scale;
        public DistrictType District;

        public BuildingData() { Id = Guid.NewGuid().ToString("N").Substring(0, 8); }

        public BuildingData(BuildingType type, Vector3 position, float rotationY, Vector3 scale, DistrictType district)
            : this()
        {
            Type = type;
            Position = position;
            RotationY = rotationY;
            Scale = scale;
            District = district;
        }
    }

    public class BuildingPlacer : MonoBehaviour
    {
        [SerializeField] private WorldConfig _config;

        private List<BuildingData> _placedBuildings = new List<BuildingData>();
        private Dictionary<BuildingType, int> _buildingCounts = new Dictionary<BuildingType, int>();
        private Material _buildingMaterial;
        private Material _windowMaterial;
        private Material _roofMaterial;
        private Material _doorMaterial;

        public IReadOnlyList<BuildingData> PlacedBuildings => _placedBuildings;
        public int TotalBuildings => _placedBuildings.Count;

        public void Initialize(WorldConfig config)
        {
            _config = config;
            CreateMaterials();
            foreach (BuildingType type in Enum.GetValues(typeof(BuildingType)))
            {
                _buildingCounts[type] = 0;
            }
            Debug.Log("[BuildingPlacer] Initialized");
        }

        private void CreateMaterials()
        {
            _buildingMaterial = CreateMaterial(new Color(0.7f, 0.68f, 0.65f), "BuildingMat");
            _windowMaterial = CreateMaterial(new Color(0.4f, 0.6f, 0.8f, 0.6f), "WindowMat");
            _roofMaterial = CreateMaterial(new Color(0.45f, 0.35f, 0.3f), "RoofMat");
            _doorMaterial = CreateMaterial(new Color(0.4f, 0.25f, 0.15f), "DoorMat");
        }

        public void GenerateBuildingsForDistrict(District district, Transform parent)
        {
            float buildingDensity = GetDensityForDistrict(district.Type);
            int buildingCount = Mathf.RoundToInt(district.Width * district.Depth * buildingDensity * 0.0001f);

            float halfWidth = district.Width * 0.45f;
            float halfDepth = district.Depth * 0.45f;

            for (int i = 0; i < buildingCount; i++)
            {
                Vector3 position = GetRandomPositionInDistrict(district, halfWidth, halfDepth);
                if (position == Vector3.zero) continue;

                BuildingType type = GetBuildingTypeForDistrict(district.Type, i);
                Vector3 scale = GetScaleForBuilding(type);
                float rotation = GetRotationForDistrict(district.Type);

                var building = new BuildingData(type, position, rotation, scale, district.Type);
                _placedBuildings.Add(building);
                _buildingCounts[type]++;

                CreateBuildingVisual(building, parent);
            }

            Debug.Log($"[BuildingPlacer] Generated {buildingCount} buildings in {district.Type}");
        }

        public void GenerateBuildingsForChunk(int chunkX, int chunkZ, List<District> districts, Transform parent)
        {
            float chunkWorldX = chunkX * _config.chunkSize;
            float chunkWorldZ = chunkZ * _config.chunkSize;
            Vector3 chunkCenter = new Vector3(chunkWorldX + _config.chunkSize * 0.5f, 0f, chunkWorldZ + _config.chunkSize * 0.5f);

            foreach (var district in districts)
            {
                if (!district.ContainsPosition(chunkCenter)) continue;

                float density = GetDensityForDistrict(district.Type);
                int count = Mathf.RoundToInt(_config.chunkSize * _config.chunkSize * density * 0.00005f);

                for (int i = 0; i < count; i++)
                {
                    float x = chunkWorldX + UnityEngine.Random.Range(5f, _config.chunkSize - 5f);
                    float z = chunkWorldZ + UnityEngine.Random.Range(5f, _config.chunkSize - 5f);
                    Vector3 position = new Vector3(x, 0f, z);

                    if (!district.ContainsPosition(position)) continue;

                    BuildingType type = GetBuildingTypeForDistrict(district.Type, i);
                    Vector3 scale = GetScaleForBuilding(type);
                    float rotation = Mathf.RoundToInt(UnityEngine.Random.Range(0f, 4f)) * 90f;

                    var building = new BuildingData(type, position, rotation, scale, district.Type);
                    _placedBuildings.Add(building);
                    _buildingCounts[type]++;

                    CreateBuildingVisual(building, parent);
                }
            }
        }

        private Vector3 GetRandomPositionInDistrict(District district, float halfWidth, float halfDepth)
        {
            for (int attempt = 0; attempt < 30; attempt++)
            {
                float x = district.Center.x + UnityEngine.Random.Range(-halfWidth, halfWidth);
                float z = district.Center.z + UnityEngine.Random.Range(-halfDepth, halfDepth);
                Vector3 pos = new Vector3(x, 0f, z);

                bool tooClose = false;
                foreach (var existing in _placedBuildings)
                {
                    if (Vector3.Distance(existing.Position, pos) < _config.minBuildingSpacing + 5f)
                    {
                        tooClose = true;
                        break;
                    }
                }

                if (!tooClose) return pos;
            }
            return Vector3.zero;
        }

        private BuildingType GetBuildingTypeForDistrict(DistrictType district, int index)
        {
            switch (district)
            {
                case DistrictType.Downtown:
                    return index % 5 == 0 ? BuildingType.Bank :
                           index % 4 == 0 ? BuildingType.Apartment :
                           index % 3 == 0 ? BuildingType.Shop :
                           BuildingType.Apartment;

                case DistrictType.Residential:
                    return index % 8 == 0 ? BuildingType.Garage :
                           index % 6 == 0 ? BuildingType.House :
                           BuildingType.House;

                case DistrictType.Industrial:
                    return index % 10 == 0 ? BuildingType.Garage :
                           index % 7 == 0 ? BuildingType.GasStation :
                           BuildingType.Garage;

                case DistrictType.Commercial:
                    return index % 6 == 0 ? BuildingType.Shop :
                           index % 5 == 0 ? BuildingType.Bank :
                           index % 4 == 0 ? BuildingType.GasStation :
                           index % 3 == 0 ? BuildingType.ParkingArea :
                           BuildingType.Shop;

                case DistrictType.Countryside:
                    return index % 12 == 0 ? BuildingType.GasStation :
                           index % 8 == 0 ? BuildingType.House :
                           BuildingType.House;

                default:
                    return BuildingType.House;
            }
        }

        private Vector3 GetScaleForBuilding(BuildingType type)
        {
            switch (type)
            {
                case BuildingType.House:
                    return new Vector3(
                        UnityEngine.Random.Range(6f, 10f),
                        UnityEngine.Random.Range(3f, 6f),
                        UnityEngine.Random.Range(6f, 10f));

                case BuildingType.Apartment:
                    return new Vector3(
                        UnityEngine.Random.Range(10f, 20f),
                        UnityEngine.Random.Range(12f, 30f),
                        UnityEngine.Random.Range(10f, 20f));

                case BuildingType.Shop:
                    return new Vector3(
                        UnityEngine.Random.Range(8f, 15f),
                        UnityEngine.Random.Range(3f, 6f),
                        UnityEngine.Random.Range(8f, 15f));

                case BuildingType.PoliceStation:
                    return new Vector3(15f, 6f, 15f);

                case BuildingType.Hospital:
                    return new Vector3(25f, 10f, 25f);

                case BuildingType.GasStation:
                    return new Vector3(12f, 4f, 12f);

                case BuildingType.Garage:
                    return new Vector3(
                        UnityEngine.Random.Range(10f, 18f),
                        UnityEngine.Random.Range(4f, 7f),
                        UnityEngine.Random.Range(10f, 18f));

                case BuildingType.Bank:
                    return new Vector3(15f, 8f, 12f);

                case BuildingType.ParkingArea:
                    return new Vector3(
                        UnityEngine.Random.Range(20f, 40f),
                        1f,
                        UnityEngine.Random.Range(20f, 40f));

                default:
                    return new Vector3(8f, 5f, 8f);
            }
        }

        private float GetRotationForDistrict(DistrictType type)
        {
            return type == DistrictType.Downtown ? Mathf.RoundToInt(UnityEngine.Random.Range(0f, 4f)) * 90f
                                                 : Mathf.RoundToInt(UnityEngine.Random.Range(0f, 4f)) * 90f;
        }

        private float GetDensityForDistrict(DistrictType type)
        {
            switch (type)
            {
                case DistrictType.Downtown: return 1.5f;
                case DistrictType.Residential: return 0.8f;
                case DistrictType.Industrial: return 0.4f;
                case DistrictType.Commercial: return 1.0f;
                case DistrictType.Countryside: return 0.3f;
                default: return 0.5f;
            }
        }

        private void CreateBuildingVisual(BuildingData data, Transform parent)
        {
            var building = GameObject.CreatePrimitive(PrimitiveType.Cube);
            building.name = $"{data.Type}_{data.Id}";
            building.transform.SetParent(parent);
            building.transform.position = data.Position + Vector3.up * (data.Scale.y * 0.5f);
            building.transform.rotation = Quaternion.Euler(0f, data.RotationY, 0f);
            building.transform.localScale = data.Scale;

            float variation = UnityEngine.Random.Range(0.85f, 1.15f);
            var mat = new Material(_buildingMaterial);
            mat.color = new Color(
                Mathf.Clamp01(_buildingMaterial.color.r * variation),
                Mathf.Clamp01(_buildingMaterial.color.g * variation),
                Mathf.Clamp01(_buildingMaterial.color.b * variation));
            building.GetComponent<Renderer>().material = mat;

            AddWindows(building.transform, data.Scale);
            AddDoor(building.transform, data.Scale);
            AddRoof(building.transform, data.Scale);
        }

        private void AddWindows(Transform parent, Vector3 scale)
        {
            int floors = Mathf.Max(1, Mathf.FloorToInt(scale.y / 3f));
            int windowsPerFloor = Mathf.Max(1, Mathf.FloorToInt(scale.x / 2.5f));
            float windowWidth = 0.8f;
            float windowHeight = 1.2f;

            for (int floor = 0; floor < floors; floor++)
            {
                for (int w = 0; w < windowsPerFloor; w++)
                {
                    float xPos = (w - (windowsPerFloor - 1) * 0.5f) * 2.5f;
                    float yPos = 1.5f + floor * 3f;

                    var window1 = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    window1.name = $"Window_{floor}_{w}";
                    window1.transform.SetParent(parent);
                    window1.transform.localPosition = new Vector3(xPos, yPos - scale.y * 0.5f, scale.z * 0.5f + 0.01f);
                    window1.transform.localScale = new Vector3(windowWidth, windowHeight, 0.05f);
                    window1.GetComponent<Renderer>().material = _windowMaterial;
                    Destroy(window1.GetComponent<Collider>());

                    var window2 = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    window2.name = $"Window_{floor}_{w}_Back";
                    window2.transform.SetParent(parent);
                    window2.transform.localPosition = new Vector3(xPos, yPos - scale.y * 0.5f, -(scale.z * 0.5f + 0.01f));
                    window2.transform.localScale = new Vector3(windowWidth, windowHeight, 0.05f);
                    window2.GetComponent<Renderer>().material = _windowMaterial;
                    Destroy(window2.GetComponent<Collider>());
                }
            }
        }

        private void AddDoor(Transform parent, Vector3 scale)
        {
            var door = GameObject.CreatePrimitive(PrimitiveType.Cube);
            door.name = "Door";
            door.transform.SetParent(parent);
            door.transform.localPosition = new Vector3(0f, -scale.y * 0.5f + 1.2f, scale.z * 0.5f + 0.02f);
            door.transform.localScale = new Vector3(1.2f, 2.4f, 0.1f);
            door.GetComponent<Renderer>().material = _doorMaterial;
        }

        private void AddRoof(Transform parent, Vector3 scale)
        {
            var roof = GameObject.CreatePrimitive(PrimitiveType.Cube);
            roof.name = "Roof";
            roof.transform.SetParent(parent);
            roof.transform.localPosition = new Vector3(0f, scale.y * 0.5f + 0.1f, 0f);
            roof.transform.localScale = new Vector3(scale.x + 0.5f, 0.2f, scale.z + 0.5f);
            roof.GetComponent<Renderer>().material = _roofMaterial;
        }

        public int GetBuildingCount(BuildingType type)
        {
            return _buildingCounts.TryGetValue(type, out int count) ? count : 0;
        }

        public void ClearBuildings()
        {
            _placedBuildings.Clear();
            foreach (var key in new List<BuildingType>(_buildingCounts.Keys))
            {
                _buildingCounts[key] = 0;
            }
        }

        private Material CreateMaterial(Color color, string name)
        {
            var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            mat.color = color;
            mat.name = name;
            return mat;
        }
    }
}
