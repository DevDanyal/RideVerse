using System;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.World.Core;

namespace RideVerse.World.Environment
{
    public class EnvironmentPlacer : MonoBehaviour
    {
        [SerializeField] private WorldConfig _config;

        private List<GameObject> _placedObjects = new List<GameObject>();
        private Material _treeTrunkMat;
        private Material _treeFoliageMat;
        private Material _grassMat;
        private Material _lampPoleMat;
        private Material _lampLightMat;
        private Material _benchMat;
        private Material _signMat;
        private Material _billboardMat;

        public int TotalPlaced => _placedObjects.Count;

        public void Initialize(WorldConfig config)
        {
            _config = config;
            CreateMaterials();
            Debug.Log("[EnvironmentPlacer] Initialized");
        }

        private void CreateMaterials()
        {
            _treeTrunkMat = CreateMat(new Color(0.4f, 0.25f, 0.1f), "TrunkMat");
            _treeFoliageMat = CreateMat(new Color(0.15f, 0.4f, 0.1f), "FoliageMat");
            _grassMat = CreateMat(new Color(0.25f, 0.5f, 0.2f), "GrassMat");
            _lampPoleMat = CreateMat(new Color(0.3f, 0.3f, 0.3f), "LampPoleMat");
            _lampLightMat = CreateMat(new Color(1f, 0.9f, 0.6f), "LampLightMat");
            _benchMat = CreateMat(new Color(0.5f, 0.3f, 0.15f), "BenchMat");
            _signMat = CreateMat(new Color(0.2f, 0.2f, 0.7f), "SignMat");
            _billboardMat = CreateMat(new Color(0.8f, 0.8f, 0.85f), "BillboardMat");
        }

        public void GenerateEnvironment(Vector3 center, float radius, Transform parent)
        {
            GenerateTrees(center, radius, parent);
            GenerateStreetLights(center, radius, parent);
            GenerateBenches(center, radius * 0.5f, parent);
            GenerateBusStops(center, radius * 0.5f, parent);
            GenerateBillboards(center, radius, parent);
            GenerateRoadSigns(center, radius, parent);

            Debug.Log($"[EnvironmentPlacer] Generated environment around {center}, radius={radius}");
        }

        public void GenerateForChunk(int chunkX, int chunkZ, Transform parent)
        {
            float chunkXPos = chunkX * _config.chunkSize;
            float chunkZPos = chunkZ * _config.chunkSize;
            Vector3 chunkCenter = new Vector3(chunkXPos + _config.chunkSize * 0.5f, 0f, chunkZPos + _config.chunkSize * 0.5f);

            int treeCount = Mathf.RoundToInt(_config.chunkSize * 0.1f);
            int lampCount = Mathf.RoundToInt(_config.chunkSize * 0.05f);
            int benchCount = Mathf.RoundToInt(_config.chunkSize * 0.02f);

            for (int i = 0; i < treeCount; i++)
            {
                float x = chunkXPos + UnityEngine.Random.Range(3f, _config.chunkSize - 3f);
                float z = chunkZPos + UnityEngine.Random.Range(3f, _config.chunkSize - 3f);
                CreateTree($"Tree_{chunkX}_{chunkZ}_{i}", new Vector3(x, 0f, z), parent);
            }

            for (int i = 0; i < lampCount; i++)
            {
                float x = chunkXPos + UnityEngine.Random.Range(3f, _config.chunkSize - 3f);
                float z = chunkZPos + UnityEngine.Random.Range(3f, _config.chunkSize - 3f);
                CreateStreetLight($"Lamp_{chunkX}_{chunkZ}_{i}", new Vector3(x, 0f, z), parent);
            }

            for (int i = 0; i < benchCount; i++)
            {
                float x = chunkXPos + UnityEngine.Random.Range(5f, _config.chunkSize - 5f);
                float z = chunkZPos + UnityEngine.Random.Range(5f, _config.chunkSize - 5f);
                CreateBench($"Bench_{chunkX}_{chunkZ}_{i}", new Vector3(x, 0f, z), parent);
            }
        }

        private void GenerateTrees(Vector3 center, float radius, Transform parent)
        {
            int count = Mathf.RoundToInt(radius * 0.3f);
            for (int i = 0; i < count; i++)
            {
                float angle = UnityEngine.Random.Range(0f, 360f) * Mathf.Deg2Rad;
                float dist = UnityEngine.Random.Range(radius * 0.3f, radius);
                Vector3 pos = center + new Vector3(Mathf.Cos(angle) * dist, 0f, Mathf.Sin(angle) * dist);
                CreateTree($"Tree_{i}", pos, parent);
            }
        }

        private void GenerateStreetLights(Vector3 center, float radius, Transform parent)
        {
            int count = Mathf.RoundToInt(radius * 0.1f);
            for (int i = 0; i < count; i++)
            {
                float angle = UnityEngine.Random.Range(0f, 360f) * Mathf.Deg2Rad;
                float dist = UnityEngine.Random.Range(radius * 0.2f, radius);
                Vector3 pos = center + new Vector3(Mathf.Cos(angle) * dist, 0f, Mathf.Sin(angle) * dist);
                CreateStreetLight($"StreetLight_{i}", pos, parent);
            }
        }

        private void GenerateBenches(Vector3 center, float radius, Transform parent)
        {
            int count = Mathf.RoundToInt(radius * 0.05f);
            for (int i = 0; i < count; i++)
            {
                float angle = UnityEngine.Random.Range(0f, 360f) * Mathf.Deg2Rad;
                float dist = UnityEngine.Random.Range(2f, radius);
                Vector3 pos = center + new Vector3(Mathf.Cos(angle) * dist, 0f, Mathf.Sin(angle) * dist);
                CreateBench($"Bench_{i}", pos, parent);
            }
        }

        private void GenerateBusStops(Vector3 center, float radius, Transform parent)
        {
            int count = Mathf.RoundToInt(radius * 0.02f);
            for (int i = 0; i < count; i++)
            {
                float angle = UnityEngine.Random.Range(0f, 360f) * Mathf.Deg2Rad;
                float dist = UnityEngine.Random.Range(5f, radius * 0.8f);
                Vector3 pos = center + new Vector3(Mathf.Cos(angle) * dist, 0f, Mathf.Sin(angle) * dist);
                CreateBusStop($"BusStop_{i}", pos, parent);
            }
        }

        private void GenerateBillboards(Vector3 center, float radius, Transform parent)
        {
            int count = Mathf.RoundToInt(radius * 0.01f);
            for (int i = 0; i < count; i++)
            {
                float angle = UnityEngine.Random.Range(0f, 360f) * Mathf.Deg2Rad;
                float dist = UnityEngine.Random.Range(radius * 0.5f, radius);
                Vector3 pos = center + new Vector3(Mathf.Cos(angle) * dist, 0f, Mathf.Sin(angle) * dist);
                CreateBillboard($"Billboard_{i}", pos, parent);
            }
        }

        private void GenerateRoadSigns(Vector3 center, float radius, Transform parent)
        {
            int count = Mathf.RoundToInt(radius * 0.03f);
            for (int i = 0; i < count; i++)
            {
                float angle = UnityEngine.Random.Range(0f, 360f) * Mathf.Deg2Rad;
                float dist = UnityEngine.Random.Range(3f, radius * 0.7f);
                Vector3 pos = center + new Vector3(Mathf.Cos(angle) * dist, 0f, Mathf.Sin(angle) * dist);
                CreateRoadSign($"RoadSign_{i}", pos, parent);
            }
        }

        private void CreateTree(string name, Vector3 position, Transform parent)
        {
            var trunk = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            trunk.name = $"{name}_Trunk";
            trunk.transform.SetParent(parent);
            trunk.transform.position = position + Vector3.up * 1f;
            trunk.transform.localScale = new Vector3(0.3f, 1f, 0.3f);
            trunk.GetComponent<Renderer>().material = _treeTrunkMat;
            _placedObjects.Add(trunk);

            var foliage = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            foliage.name = $"{name}_Foliage";
            foliage.transform.SetParent(parent);
            foliage.transform.position = position + Vector3.up * 3f;
            foliage.transform.localScale = new Vector3(2f, 2.5f, 2f);
            var fmat = new Material(_treeFoliageMat);
            fmat.color = new Color(
                0.15f + UnityEngine.Random.Range(0f, 0.1f),
                0.4f + UnityEngine.Random.Range(0f, 0.15f),
                0.1f);
            foliage.GetComponent<Renderer>().material = fmat;
            _placedObjects.Add(foliage);
        }

        private void CreateStreetLight(string name, Vector3 position, Transform parent)
        {
            var pole = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            pole.name = $"{name}_Pole";
            pole.transform.SetParent(parent);
            pole.transform.position = position + Vector3.up * 2.5f;
            pole.transform.localScale = new Vector3(0.1f, 2.5f, 0.1f);
            pole.GetComponent<Renderer>().material = _lampPoleMat;
            _placedObjects.Add(pole);

            var lamp = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            lamp.name = $"{name}_Light";
            lamp.transform.SetParent(parent);
            lamp.transform.position = position + Vector3.up * 5.2f;
            lamp.transform.localScale = new Vector3(0.4f, 0.2f, 0.4f);
            lamp.GetComponent<Renderer>().material = _lampLightMat;
            _placedObjects.Add(lamp);
        }

        private void CreateBench(string name, Vector3 position, Transform parent)
        {
            var seat = GameObject.CreatePrimitive(PrimitiveType.Cube);
            seat.name = $"{name}_Seat";
            seat.transform.SetParent(parent);
            seat.transform.position = position + Vector3.up * 0.4f;
            seat.transform.localScale = new Vector3(1.5f, 0.08f, 0.5f);
            seat.GetComponent<Renderer>().material = _benchMat;
            _placedObjects.Add(seat);

            var back = GameObject.CreatePrimitive(PrimitiveType.Cube);
            back.name = $"{name}_Back";
            back.transform.SetParent(parent);
            back.transform.position = position + Vector3.up * 0.7f + Vector3.forward * -0.2f;
            back.transform.localScale = new Vector3(1.5f, 0.5f, 0.06f);
            back.GetComponent<Renderer>().material = _benchMat;
            _placedObjects.Add(back);
        }

        private void CreateBusStop(string name, Vector3 position, Transform parent)
        {
            var roof = GameObject.CreatePrimitive(PrimitiveType.Cube);
            roof.name = $"{name}_Roof";
            roof.transform.SetParent(parent);
            roof.transform.position = position + Vector3.up * 2.5f;
            roof.transform.localScale = new Vector3(4f, 0.15f, 1.5f);
            roof.GetComponent<Renderer>().material = _signMat;
            _placedObjects.Add(roof);

            for (int i = 0; i < 2; i++)
            {
                float xOffset = i == 0 ? -1.8f : 1.8f;
                var pole = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                pole.name = $"{name}_Pole_{i}";
                pole.transform.SetParent(parent);
                pole.transform.position = position + Vector3.up * 1.25f + Vector3.right * xOffset;
                pole.transform.localScale = new Vector3(0.08f, 1.25f, 0.08f);
                pole.GetComponent<Renderer>().material = _lampPoleMat;
                _placedObjects.Add(pole);
            }
        }

        private void CreateBillboard(string name, Vector3 position, Transform parent)
        {
            var board = GameObject.CreatePrimitive(PrimitiveType.Cube);
            board.name = $"{name}_Board";
            board.transform.SetParent(parent);
            board.transform.position = position + Vector3.up * 3.5f;
            board.transform.localScale = new Vector3(6f, 3f, 0.2f);
            board.GetComponent<Renderer>().material = _billboardMat;
            _placedObjects.Add(board);

            var support = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            support.name = $"{name}_Support";
            support.transform.SetParent(parent);
            support.transform.position = position + Vector3.up * 1.5f;
            support.transform.localScale = new Vector3(0.15f, 1.5f, 0.15f);
            support.GetComponent<Renderer>().material = _lampPoleMat;
            _placedObjects.Add(support);
        }

        private void CreateRoadSign(string name, Vector3 position, Transform parent)
        {
            var sign = GameObject.CreatePrimitive(PrimitiveType.Cube);
            sign.name = $"{name}_Sign";
            sign.transform.SetParent(parent);
            sign.transform.position = position + Vector3.up * 2.5f;
            sign.transform.localScale = new Vector3(1f, 0.6f, 0.05f);
            sign.GetComponent<Renderer>().material = _signMat;
            _placedObjects.Add(sign);

            var pole = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            pole.name = $"{name}_Pole";
            pole.transform.SetParent(parent);
            pole.transform.position = position + Vector3.up * 1.25f;
            pole.transform.localScale = new Vector3(0.06f, 1.25f, 0.06f);
            pole.GetComponent<Renderer>().material = _lampPoleMat;
            _placedObjects.Add(pole);
        }

        public void ClearEnvironment()
        {
            foreach (var obj in _placedObjects)
            {
                if (obj != null) Destroy(obj);
            }
            _placedObjects.Clear();
        }

        private Material CreateMat(Color color, string name)
        {
            var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            mat.color = color;
            mat.name = name;
            return mat;
        }
    }
}
