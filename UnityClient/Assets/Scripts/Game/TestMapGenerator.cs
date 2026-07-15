using UnityEngine;
using RideVerse.Core;

namespace RideVerse.Game
{
    public class TestMapGenerator : MonoBehaviour
    {
        [Header("Ground")]
        [SerializeField] private float _groundSize = 200f;
        [SerializeField] private Color _groundColor = new Color(0.3f, 0.55f, 0.25f);

        [Header("Roads")]
        [SerializeField] private float _roadWidth = 12f;
        [SerializeField] private float _mainRoadLength = 200f;
        [SerializeField] private int _sideStreetCount = 6;
        [SerializeField] private float _sideStreetSpacing = 25f;
        [SerializeField] private Color _roadColor = new Color(0.25f, 0.25f, 0.28f);
        [SerializeField] private Color _sidewalkColor = new Color(0.65f, 0.63f, 0.6f);
        [SerializeField] private float _sidewalkWidth = 2f;

        [Header("Buildings")]
        [SerializeField] private int _buildingCount = 20;
        [SerializeField] private float _minBuildingHeight = 4f;
        [SerializeField] private float _maxBuildingHeight = 15f;
        [SerializeField] private float _minBuildingSize = 4f;
        [SerializeField] private float _maxBuildingSize = 10f;

        [Header("Props")]
        [SerializeField] private int _treeCount = 15;
        [SerializeField] private int _lampPostCount = 12;
        [SerializeField] private int _benchCount = 8;

        private Material _groundMat;
        private Material _roadMat;
        private Material _sidewalkMat;
        private Material _buildingMat;

        private void Start()
        {
            CreateMaterials();
        }

        private void CreateMaterials()
        {
            _groundMat = CreateMaterial(_groundColor, "Ground");
            _roadMat = CreateMaterial(_roadColor, "Road");
            _sidewalkMat = CreateMaterial(_sidewalkColor, "Sidewalk");
            _buildingMat = CreateMaterial(new Color(0.7f, 0.68f, 0.65f), "Building");
        }

        private Material CreateMaterial(Color color, string name)
        {
            var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            mat.color = color;
            mat.name = name;
            return mat;
        }

        public void GenerateMap()
        {
            GenerateGround();
            GenerateMainRoad();
            GenerateSideStreets();
            GenerateBuildings();
            GenerateTrees();
            GenerateLampPosts();
            GenerateBenches();
            GenerateSpawnPlatform();
        }

        private void GenerateGround()
        {
            var ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
            ground.name = "Ground";
            ground.transform.position = new Vector3(0f, -0.05f, 0f);
            ground.transform.localScale = new Vector3(_groundSize, 0.1f, _groundSize);
            ground.GetComponent<Renderer>().material = _groundMat;
            ground.layer = LayerMask.NameToLayer(Constants.Layers.Ground);
        }

        private void GenerateMainRoad()
        {
            CreateRoadSegment("MainRoad", new Vector3(0f, 0.01f, 0f),
                new Vector3(_mainRoadLength, 0.02f, _roadWidth));

            CreateSidewalk("Sidewalk_North", new Vector3(0f, 0.05f, _roadWidth * 0.5f + _sidewalkWidth * 0.5f),
                new Vector3(_mainRoadLength, 0.1f, _sidewalkWidth));

            CreateSidewalk("Sidewalk_South", new Vector3(0f, 0.05f, -(_roadWidth * 0.5f + _sidewalkWidth * 0.5f)),
                new Vector3(_mainRoadLength, 0.1f, _sidewalkWidth));

            GenerateLaneMarkings();
        }

        private void GenerateLaneMarkings()
        {
            float markingLength = 3f;
            float markingGap = 3f;
            float totalLength = markingLength + markingGap;
            int markingCount = Mathf.FloorToInt(_mainRoadLength / totalLength);

            for (int i = -markingCount / 2; i < markingCount / 2; i++)
            {
                var marking = GameObject.CreatePrimitive(PrimitiveType.Cube);
                marking.name = $"LaneMarking_{i}";
                marking.transform.position = new Vector3(i * totalLength, 0.025f, 0f);
                marking.transform.localScale = new Vector3(markingLength, 0.005f, 0.15f);
                marking.GetComponent<Renderer>().material = CreateMaterial(Color.white, "LaneMarking");
                Destroy(marking.GetComponent<Collider>());
            }
        }

        private void GenerateSideStreets()
        {
            for (int i = 0; i < _sideStreetCount; i++)
            {
                float z = -_mainRoadLength * 0.5f + (i + 1) * _sideStreetSpacing;
                if (z > _mainRoadLength * 0.5f) break;

                string suffix = i % 2 == 0 ? "N" : "S";
                float direction = i % 2 == 0 ? 1f : -1f;

                CreateRoadSegment($"SideStreet_{suffix}{i}",
                    new Vector3(0f, 0.01f, z),
                    new Vector3(_roadWidth, 0.02f, _mainRoadLength * 0.4f));
            }
        }

        private void CreateRoadSegment(string name, Vector3 position, Vector3 scale)
        {
            var road = GameObject.CreatePrimitive(PrimitiveType.Cube);
            road.name = name;
            road.transform.position = position;
            road.transform.localScale = scale;
            road.GetComponent<Renderer>().material = _roadMat;
        }

        private void CreateSidewalk(string name, Vector3 position, Vector3 scale)
        {
            var sidewalk = GameObject.CreatePrimitive(PrimitiveType.Cube);
            sidewalk.name = name;
            sidewalk.transform.position = position;
            sidewalk.transform.localScale = scale;
            sidewalk.GetComponent<Renderer>().material = _sidewalkMat;
        }

        private void GenerateBuildings()
        {
            float halfSize = _mainRoadLength * 0.4f;

            for (int i = 0; i < _buildingCount; i++)
            {
                Vector3 position = GetRandomBuildingPosition(halfSize);
                if (position == Vector3.zero) continue;

                float width = Random.Range(_minBuildingSize, _maxBuildingSize);
                float depth = Random.Range(_minBuildingSize, _maxBuildingSize);
                float height = Random.Range(_minBuildingHeight, _maxBuildingHeight);

                CreateBuilding($"Building_{i}", position, width, height, depth);
            }
        }

        private Vector3 GetRandomBuildingPosition(float halfSize)
        {
            for (int attempt = 0; attempt < 20; attempt++)
            {
                float x = Random.Range(-halfSize, halfSize);
                float z = Random.Range(-halfSize, halfSize);

                if (Mathf.Abs(z) < _roadWidth * 0.5f + _sidewalkWidth + 2f) continue;

                Vector3 pos = new Vector3(x, 0f, z);
                bool tooClose = false;

                var existingBuildings = GameObject.FindGameObjectsWithTag("Untagged");
                foreach (var b in existingBuildings)
                {
                    if (b.name.StartsWith("Building") && Vector3.Distance(b.transform.position, pos) < _maxBuildingSize + 2f)
                    {
                        tooClose = true;
                        break;
                    }
                }

                if (!tooClose) return pos;
            }

            return Vector3.zero;
        }

        private void CreateBuilding(string name, Vector3 position, float width, float height, float depth)
        {
            var building = GameObject.CreatePrimitive(PrimitiveType.Cube);
            building.name = name;
            building.transform.position = position + Vector3.up * (height * 0.5f);
            building.transform.localScale = new Vector3(width, height, depth);

            var renderer = building.GetComponent<Renderer>();
            float variation = Random.Range(0.85f, 1.15f);
            var mat = new Material(_buildingMat);
            mat.color = new Color(
                Mathf.Clamp01(_buildingMat.color.r * variation),
                Mathf.Clamp01(_buildingMat.color.g * variation),
                Mathf.Clamp01(_buildingMat.color.b * variation));
            renderer.material = mat;

            CreateWindows(building.transform, width, height, depth);
        }

        private void CreateWindows(Transform parent, float width, float height, float depth)
        {
            int floors = Mathf.FloorToInt(height / 3f);
            int windowsPerFloor = Mathf.FloorToInt(width / 2.5f);

            Material windowMat = CreateMaterial(new Color(0.4f, 0.6f, 0.8f, 0.6f), "Window");

            for (int floor = 0; floor < floors; floor++)
            {
                for (int w = 0; w < windowsPerFloor; w++)
                {
                    float windowWidth = 0.8f;
                    float windowHeight = 1.2f;

                    float xPos = (w - (windowsPerFloor - 1) * 0.5f) * 2.5f;
                    float yPos = 1.5f + floor * 3f;

                    var windowObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    windowObj.name = $"Window_F{floor}_W{w}";
                    windowObj.transform.SetParent(parent);
                    windowObj.transform.localPosition = new Vector3(xPos, yPos - height * 0.5f, depth * 0.5f + 0.01f);
                    windowObj.transform.localScale = new Vector3(windowWidth, windowHeight, 0.05f);
                    windowObj.GetComponent<Renderer>().material = windowMat;
                    Destroy(windowObj.GetComponent<Collider>());

                    var windowObj2 = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    windowObj2.name = $"Window_F{floor}_W{w}_Back";
                    windowObj2.transform.SetParent(parent);
                    windowObj2.transform.localPosition = new Vector3(xPos, yPos - height * 0.5f, -(depth * 0.5f + 0.01f));
                    windowObj2.transform.localScale = new Vector3(windowWidth, windowHeight, 0.05f);
                    windowObj2.GetComponent<Renderer>().material = windowMat;
                    Destroy(windowObj2.GetComponent<Collider>());
                }
            }
        }

        private void GenerateTrees()
        {
            float halfSize = _mainRoadLength * 0.35f;

            for (int i = 0; i < _treeCount; i++)
            {
                float x = Random.Range(-halfSize, halfSize);
                float z = Random.Range(-halfSize, halfSize);

                if (Mathf.Abs(z) < _roadWidth * 0.5f + 1f) continue;

                CreateTree($"Tree_{i}", new Vector3(x, 0f, z));
            }
        }

        private void CreateTree(string name, Vector3 position)
        {
            var trunk = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            trunk.name = $"{name}_Trunk";
            trunk.transform.position = position + Vector3.up * 1f;
            trunk.transform.localScale = new Vector3(0.3f, 1f, 0.3f);
            trunk.GetComponent<Renderer>().material = CreateMaterial(new Color(0.4f, 0.25f, 0.1f), "Trunk");

            var foliage = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            foliage.name = $"{name}_Foliage";
            foliage.transform.position = position + Vector3.up * 3f;
            foliage.transform.localScale = new Vector3(2f, 2.5f, 2f);
            foliage.GetComponent<Renderer>().material = CreateMaterial(
                new Color(0.15f + Random.Range(0f, 0.1f), 0.4f + Random.Range(0f, 0.15f), 0.1f), "Foliage");
        }

        private void GenerateLampPosts()
        {
            float halfLength = _mainRoadLength * 0.45f;
            float spacing = _mainRoadLength / _lampPostCount;

            for (int i = 0; i < _lampPostCount; i++)
            {
                float x = -halfLength + i * spacing;
                CreateLampPost($"LampPost_{i}",
                    new Vector3(x, 0f, _roadWidth * 0.5f + _sidewalkWidth + 0.5f));
            }
        }

        private void CreateLampPost(string name, Vector3 position)
        {
            var pole = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            pole.name = $"{name}_Pole";
            pole.transform.position = position + Vector3.up * 2.5f;
            pole.transform.localScale = new Vector3(0.1f, 2.5f, 0.1f);
            pole.GetComponent<Renderer>().material = CreateMaterial(new Color(0.3f, 0.3f, 0.3f), "LampPole");

            var lamp = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            lamp.name = $"{name}_Light";
            lamp.transform.position = position + Vector3.up * 5.2f;
            lamp.transform.localScale = new Vector3(0.4f, 0.2f, 0.4f);
            lamp.GetComponent<Renderer>().material = CreateMaterial(
                new Color(1f, 0.9f, 0.6f), "LampLight");
        }

        private void GenerateBenches()
        {
            float halfLength = _mainRoadLength * 0.3f;

            for (int i = 0; i < _benchCount; i++)
            {
                float x = Random.Range(-halfLength, halfLength);
                float side = i % 2 == 0 ? 1f : -1f;
                float z = side * (_roadWidth * 0.5f + _sidewalkWidth + 1f);

                CreateBench($"Bench_{i}", new Vector3(x, 0f, z));
            }
        }

        private void CreateBench(string name, Vector3 position)
        {
            var seat = GameObject.CreatePrimitive(PrimitiveType.Cube);
            seat.name = $"{name}_Seat";
            seat.transform.position = position + Vector3.up * 0.4f;
            seat.transform.localScale = new Vector3(1.5f, 0.08f, 0.5f);
            seat.GetComponent<Renderer>().material = CreateMaterial(new Color(0.5f, 0.3f, 0.15f), "BenchSeat");

            var back = GameObject.CreatePrimitive(PrimitiveType.Cube);
            back.name = $"{name}_Back";
            back.transform.position = position + Vector3.up * 0.7f + Vector3.forward * -0.2f;
            back.transform.localScale = new Vector3(1.5f, 0.5f, 0.06f);
            back.GetComponent<Renderer>().material = CreateMaterial(new Color(0.5f, 0.3f, 0.15f), "BenchBack");
        }

        private void GenerateSpawnPlatform()
        {
            var platform = GameObject.CreatePrimitive(PrimitiveType.Cube);
            platform.name = "SpawnPlatform";
            platform.transform.position = new Vector3(0f, 0.05f, 15f);
            platform.transform.localScale = new Vector3(6f, 0.1f, 6f);
            platform.GetComponent<Renderer>().material = CreateMaterial(new Color(0.6f, 0.6f, 0.65f), "SpawnPlatform");
        }
    }
}
