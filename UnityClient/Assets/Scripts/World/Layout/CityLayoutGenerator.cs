using System;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.World.Core;
using RideVerse.World.Districts;

namespace RideVerse.World.Layout
{
    public class CityLayoutGenerator : MonoBehaviour
    {
        [SerializeField] private WorldConfig _config;

        private List<RoadSegment> _roads = new List<RoadSegment>();
        private List<Intersection> _intersections = new List<Intersection>();
        private List<Bridge> _bridges = new List<Bridge>();
        private List<District> _districts = new List<District>();
        private Material _roadMaterial;
        private Material _sidewalkMaterial;
        private Material _highwayMaterial;
        private Material _intersectionMaterial;

        public IReadOnlyList<RoadSegment> Roads => _roads;
        public IReadOnlyList<Intersection> Intersections => _intersections;
        public IReadOnlyList<Bridge> Bridges => _bridges;
        public IReadOnlyList<District> Districts => _districts;

        public void Initialize(WorldConfig config)
        {
            _config = config;
            CreateMaterials();
            Debug.Log("[CityLayoutGenerator] Initialized");
        }

        private void CreateMaterials()
        {
            _roadMaterial = CreateMaterial(new Color(0.22f, 0.22f, 0.25f), "RoadMat");
            _sidewalkMaterial = CreateMaterial(new Color(0.6f, 0.58f, 0.55f), "SidewalkMat");
            _highwayMaterial = CreateMaterial(new Color(0.2f, 0.2f, 0.22f), "HighwayMat");
            _intersectionMaterial = CreateMaterial(new Color(0.24f, 0.24f, 0.26f), "IntersectionMat");
        }

        public void GenerateCityLayout(Transform parent)
        {
            GenerateDistricts();
            GenerateMainRoads(parent);
            GenerateSmallRoads(parent);
            GenerateHighways(parent);
            GenerateIntersections(parent);
            GenerateBridges(parent);

            Debug.Log($"[CityLayoutGenerator] Generated: {_roads.Count} roads, {_intersections.Count} intersections, {_bridges.Count} bridges, {_districts.Count} districts");
        }

        private void GenerateDistricts()
        {
            _districts.Clear();
            float worldCenterX = _config.worldSizeX * 0.5f;
            float worldCenterZ = _config.worldSizeZ * 0.5f;
            float districtSize = 400f;

            _districts.Add(new District(DistrictType.Downtown,
                new Vector3(worldCenterX, 0f, worldCenterZ), districtSize, districtSize));

            _districts.Add(new District(DistrictType.Residential,
                new Vector3(worldCenterX - 450f, 0f, worldCenterZ), districtSize, districtSize));

            _districts.Add(new District(DistrictType.Commercial,
                new Vector3(worldCenterX + 450f, 0f, worldCenterZ), districtSize, districtSize));

            _districts.Add(new District(DistrictType.Industrial,
                new Vector3(worldCenterX, 0f, worldCenterZ - 450f), districtSize, districtSize));

            _districts.Add(new District(DistrictType.Countryside,
                new Vector3(worldCenterX, 0f, worldCenterZ + 450f), districtSize * 1.5f, districtSize * 1.5f));
        }

        private void GenerateMainRoads(Transform parent)
        {
            float centerX = _config.worldSizeX * 0.5f;
            float centerZ = _config.worldSizeZ * 0.5f;
            float roadLength = _config.worldSizeX * 0.8f;

            var horizontalRoad = new RoadSegment(RoadType.MainRoad,
                new Vector3(centerX - roadLength * 0.5f, 0.02f, centerZ),
                new Vector3(centerX + roadLength * 0.5f, 0.02f, centerZ),
                _config.mainRoadWidth, 4);
            _roads.Add(horizontalRoad);
            CreateRoadVisual(horizontalRoad, parent);

            var verticalRoad = new RoadSegment(RoadType.MainRoad,
                new Vector3(centerX, 0.02f, centerZ - roadLength * 0.5f),
                new Vector3(centerX, 0.02f, centerZ + roadLength * 0.5f),
                _config.mainRoadWidth, 4);
            _roads.Add(verticalRoad);
            CreateRoadVisual(verticalRoad, parent);

            AddLaneMarkings(horizontalRoad, parent);
            AddLaneMarkings(verticalRoad, parent);
            AddSidewalks(horizontalRoad, parent);
            AddSidewalks(verticalRoad, parent);
        }

        private void GenerateSmallRoads(Transform parent)
        {
            float centerX = _config.worldSizeX * 0.5f;
            float centerZ = _config.worldSizeZ * 0.5f;
            float gridSpacing = 100f;
            float extent = 400f;

            for (float offset = gridSpacing; offset <= extent; offset += gridSpacing)
            {
                var roadPos = new RoadSegment(RoadType.SmallRoad,
                    new Vector3(centerX - extent, 0.01f, centerZ + offset),
                    new Vector3(centerX + extent, 0.01f, centerZ + offset),
                    _config.smallRoadWidth, 2);
                _roads.Add(roadPos);
                CreateRoadVisual(roadPos, parent);

                var roadNeg = new RoadSegment(RoadType.SmallRoad,
                    new Vector3(centerX - extent, 0.01f, centerZ - offset),
                    new Vector3(centerX + extent, 0.01f, centerZ - offset),
                    _config.smallRoadWidth, 2);
                _roads.Add(roadNeg);
                CreateRoadVisual(roadNeg, parent);

                var roadLeft = new RoadSegment(RoadType.SmallRoad,
                    new Vector3(centerX + offset, 0.01f, centerZ - extent),
                    new Vector3(centerX + offset, 0.01f, centerZ + extent),
                    _config.smallRoadWidth, 2);
                _roads.Add(roadLeft);
                CreateRoadVisual(roadLeft, parent);

                var roadRight = new RoadSegment(RoadType.SmallRoad,
                    new Vector3(centerX - offset, 0.01f, centerZ - extent),
                    new Vector3(centerX - offset, 0.01f, centerZ + extent),
                    _config.smallRoadWidth, 2);
                _roads.Add(roadRight);
                CreateRoadVisual(roadRight, parent);
            }
        }

        private void GenerateHighways(Transform parent)
        {
            float highwayZ1 = _config.worldSizeZ * 0.15f;
            float highwayZ2 = _config.worldSizeZ * 0.85f;

            var highway1 = new RoadSegment(RoadType.Highway,
                new Vector3(0f, 0.03f, highwayZ1),
                new Vector3(_config.worldSizeX, 0.03f, highwayZ1),
                _config.highwayWidth, 6);
            _roads.Add(highway1);
            CreateHighwayVisual(highway1, parent);

            var highway2 = new RoadSegment(RoadType.Highway,
                new Vector3(0f, 0.03f, highwayZ2),
                new Vector3(_config.worldSizeX, 0.03f, highwayZ2),
                _config.highwayWidth, 6);
            _roads.Add(highway2);
            CreateHighwayVisual(highway2, parent);
        }

        private void GenerateIntersections(Transform parent)
        {
            HashSet<string> processed = new HashSet<string>();

            foreach (var road1 in _roads)
            {
                foreach (var road2 in _roads)
                {
                    if (road1 == road2) continue;

                    Vector3? intersection = GetRoadIntersection(road1, road2);
                    if (intersection.HasValue)
                    {
                        string key = $"{intersection.Value.x:F0}_{intersection.Value.z:F0}";
                        if (!processed.Contains(key))
                        {
                            processed.Add(key);
                            var inter = new Intersection(intersection.Value, road1.Width, 2, true);
                            _intersections.Add(inter);
                            CreateIntersectionVisual(inter, parent);
                        }
                    }
                }
            }
        }

        private void GenerateBridges(Transform parent)
        {
            float bridgeX = _config.worldSizeX * 0.5f;
            float bridgeLength = 60f;

            var bridge = new Bridge(
                new Vector3(bridgeX - bridgeLength * 0.5f, 2f, _config.worldSizeZ * 0.15f),
                new Vector3(bridgeX + bridgeLength * 0.5f, 2f, _config.worldSizeZ * 0.15f),
                _config.highwayWidth, 4f, 3f);
            _bridges.Add(bridge);
            CreateBridgeVisual(bridge, parent);
        }

        private Vector3? GetRoadIntersection(RoadSegment a, RoadSegment b)
        {
            Vector2 p = a.Start;
            Vector2 r = a.End - a.Start;
            Vector2 q = b.Start;
            Vector2 s = b.End - b.Start;

            float rxs = r.x * s.y - r.y * s.x;
            if (Mathf.Abs(rxs) < 0.001f) return null;

            Vector2 qp = q - p;
            float t = (qp.x * s.y - qp.y * s.x) / rxs;
            float u = (qp.x * r.y - qp.y * r.x) / rxs;

            if (t >= 0f && t <= 1f && u >= 0f && u <= 1f)
            {
                Vector3 hitPoint = p + r * t;
                return new Vector3(hitPoint.x, 0.02f, hitPoint.y);
            }

            return null;
        }

        private void CreateRoadVisual(RoadSegment road, Transform parent)
        {
            Vector3 center = road.Center;
            Vector3 direction = road.Direction;
            float angle = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg;

            var roadObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            roadObj.name = road.Id;
            roadObj.transform.SetParent(parent);
            roadObj.transform.position = center + Vector3.up * 0.01f;
            roadObj.transform.rotation = Quaternion.Euler(0f, angle, 0f);
            roadObj.transform.localScale = new Vector3(road.Width, 0.02f, road.Length);
            roadObj.GetComponent<Renderer>().material = _roadMaterial;
        }

        private void CreateHighwayVisual(RoadSegment road, Transform parent)
        {
            Vector3 center = road.Center;
            Vector3 direction = road.Direction;
            float angle = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg;

            var roadObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            roadObj.name = road.Id;
            roadObj.transform.SetParent(parent);
            roadObj.transform.position = center + Vector3.up * 0.03f;
            roadObj.transform.rotation = Quaternion.Euler(0f, angle, 0f);
            roadObj.transform.localScale = new Vector3(road.Width, 0.03f, road.Length);
            roadObj.GetComponent<Renderer>().material = _highwayMaterial;

            AddLaneMarkings(road, parent);
        }

        private void CreateIntersectionVisual(Intersection intersection, Transform parent)
        {
            var obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obj.name = intersection.Id;
            obj.transform.SetParent(parent);
            obj.transform.position = intersection.Position + Vector3.up * 0.015f;
            obj.transform.localScale = new Vector3(intersection.Size, 0.02f, intersection.Size);
            obj.GetComponent<Renderer>().material = _intersectionMaterial;
        }

        private void CreateBridgeVisual(Bridge bridge, Transform parent)
        {
            Vector3 center = (bridge.Start + bridge.End) * 0.5f;
            float length = bridge.Length;
            Vector3 direction = (bridge.End - bridge.Start).normalized;
            float angle = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg;

            var deck = GameObject.CreatePrimitive(PrimitiveType.Cube);
            deck.name = bridge.Id;
            deck.transform.SetParent(parent);
            deck.transform.position = center + Vector3.up * bridge.DeckHeight;
            deck.transform.rotation = Quaternion.Euler(0f, angle, 0f);
            deck.transform.localScale = new Vector3(bridge.Width, 0.3f, length);
            deck.GetComponent<Renderer>().material = _roadMaterial;

            float pillarSpacing = 15f;
            int pillarCount = Mathf.Max(2, Mathf.FloorToInt(length / pillarSpacing));
            Material pillarMat = CreateMaterial(new Color(0.5f, 0.5f, 0.5f), "PillarMat");

            for (int i = 0; i < pillarCount; i++)
            {
                float t = (i + 0.5f) / pillarCount;
                Vector3 pillarPos = Vector3.Lerp(bridge.Start, bridge.End, t);

                var pillar = GameObject.CreatePrimitive(PrimitiveType.Cube);
                pillar.name = $"{bridge.Id}_Pillar_{i}";
                pillar.transform.SetParent(parent);
                pillar.transform.position = pillarPos + Vector3.up * (bridge.DeckHeight * 0.5f);
                pillar.transform.localScale = new Vector3(2f, bridge.DeckHeight, 2f);
                pillar.GetComponent<Renderer>().material = pillarMat;
            }
        }

        private void AddLaneMarkings(RoadSegment road, Transform parent)
        {
            float markingLength = 3f;
            float markingGap = 3f;
            float totalSpacing = markingLength + markingGap;
            int markingCount = Mathf.FloorToInt(road.Length / totalSpacing);
            Vector3 direction = road.Direction;
            float angle = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg;

            Material markingMat = CreateMaterial(Color.white, "LaneMarking");

            for (int i = -markingCount / 2; i < markingCount / 2; i++)
            {
                var marking = GameObject.CreatePrimitive(PrimitiveType.Cube);
                marking.name = $"Marking_{road.Id}_{i}";
                marking.transform.SetParent(parent);
                marking.transform.position = road.Start + direction * (i * totalSpacing) + Vector3.up * 0.025f;
                marking.transform.rotation = Quaternion.Euler(0f, angle, 0f);
                marking.transform.localScale = new Vector3(0.15f, 0.005f, markingLength);
                marking.GetComponent<Renderer>().material = markingMat;
                Destroy(marking.GetComponent<Collider>());
            }
        }

        private void AddSidewalks(RoadSegment road, Transform parent)
        {
            float halfWidth = road.Width * 0.5f;
            Vector3 direction = road.Direction;
            Vector3 perpendicular = new Vector3(-direction.z, 0f, direction.x);

            for (int side = -1; side <= 1; side += 2)
            {
                Vector3 offset = perpendicular * (halfWidth + _config.sidewalkWidth * 0.5f) * side;
                Vector3 center = road.Center + offset;

                var sidewalk = GameObject.CreatePrimitive(PrimitiveType.Cube);
                sidewalk.name = $"Sidewalk_{road.Id}_{side}";
                sidewalk.transform.SetParent(parent);
                sidewalk.transform.position = center + Vector3.up * (_config.sidewalkHeight * 0.5f);
                float angle = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg;
                sidewalk.transform.rotation = Quaternion.Euler(0f, angle, 0f);
                sidewalk.transform.localScale = new Vector3(_config.sidewalkWidth, _config.sidewalkHeight, road.Length);
                sidewalk.GetComponent<Renderer>().material = _sidewalkMaterial;
            }
        }

        private Material CreateMaterial(Color color, string name)
        {
            var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            mat.color = color;
            mat.name = name;
            return mat;
        }

        public District GetDistrictAtPosition(Vector3 position)
        {
            foreach (var district in _districts)
            {
                if (district.ContainsPosition(position))
                {
                    return district;
                }
            }
            return null;
        }

        public void ClearLayout()
        {
            _roads.Clear();
            _intersections.Clear();
            _bridges.Clear();
            _districts.Clear();
        }
    }
}
