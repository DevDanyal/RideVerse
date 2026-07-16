using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.World.Chunks
{
    public class Chunk : MonoBehaviour
    {
        public ChunkCoord Coord { get; private set; }
        public bool IsLoaded { get; private set; }
        public List<GameObject> Objects { get; } = new List<GameObject>();

        private Material _groundMaterial;

        public void Initialize(ChunkCoord coord, int chunkSize)
        {
            Coord = coord;
            gameObject.name = $"Chunk_{coord.X}_{coord.Z}";
            transform.position = coord.ToWorldPosition(chunkSize);
            IsLoaded = false;
        }

        public void Load()
        {
            if (IsLoaded) return;
            gameObject.SetActive(true);
            IsLoaded = true;
        }

        public void Unload()
        {
            if (!IsLoaded) return;
            gameObject.SetActive(false);
            IsLoaded = false;
        }

        public void AddObject(GameObject obj)
        {
            if (obj == null) return;
            obj.transform.SetParent(transform);
            Objects.Add(obj);
        }

        public void ClearObjects()
        {
            foreach (var obj in Objects)
            {
                if (obj != null)
                {
                    Destroy(obj);
                }
            }
            Objects.Clear();
        }

        public void GenerateGround(float size, Color color)
        {
            var ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
            ground.name = "Ground";
            ground.transform.SetParent(transform);
            ground.transform.localPosition = new Vector3(size * 0.5f, -0.05f, size * 0.5f);
            ground.transform.localScale = new Vector3(size, 0.1f, size);

            _groundMaterial = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            _groundMaterial.color = color;
            _groundMaterial.name = $"GroundMat_{Coord.X}_{Coord.Z}";
            ground.GetComponent<Renderer>().material = _groundMaterial;

            AddObject(ground);
        }

        public Bounds GetBounds(int chunkSize)
        {
            Vector3 center = Coord.GetWorldCenter(chunkSize);
            return new Bounds(center, new Vector3(chunkSize, 50f, chunkSize));
        }

        private void OnDestroy()
        {
            if (_groundMaterial != null)
            {
                Destroy(_groundMaterial);
            }
        }
    }
}
