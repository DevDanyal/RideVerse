using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.World.Core;

namespace RideVerse.World.Chunks
{
    public class ChunkManager : MonoBehaviour
    {
        [SerializeField] private WorldConfig _config;

        private Dictionary<ChunkCoord, Chunk> _chunks = new Dictionary<ChunkCoord, Chunk>();
        private ChunkCoord _lastPlayerChunk;
        private bool _isInitialized;

        public event Action<Chunk> OnChunkLoaded;
        public event Action<Chunk> OnChunkUnloaded;
        public int ActiveChunkCount { get; private set; }

        public void Initialize(WorldConfig config)
        {
            _config = config;
            _chunks.Clear();
            _isInitialized = true;
            Debug.Log($"[ChunkManager] Initialized: {config.ChunkCountX}x{config.ChunkCountZ} chunks, size={config.chunkSize}");
        }

        public void UpdatePlayerPosition(Vector3 playerPosition)
        {
            if (!_isInitialized || _config == null) return;

            ChunkCoord currentChunk = ChunkCoord.FromWorldPosition(playerPosition, _config.chunkSize);

            if (currentChunk.Equals(_lastPlayerChunk)) return;

            _lastPlayerChunk = currentChunk;
            UpdateVisibleChunks(currentChunk);
        }

        private void UpdateVisibleChunks(ChunkCoord playerChunk)
        {
            int loadRadius = _config.loadRadius;
            int unloadRadius = _config.unloadRadius;

            HashSet<ChunkCoord> chunksToLoad = new HashSet<ChunkCoord>();

            for (int x = -loadRadius; x <= loadRadius; x++)
            {
                for (int z = -loadRadius; z <= loadRadius; z++)
                {
                    ChunkCoord coord = new ChunkCoord(playerChunk.X + x, playerChunk.Z + z);
                    if (IsChunkInBounds(coord))
                    {
                        chunksToLoad.Add(coord);
                    }
                }
            }

            foreach (var coord in chunksToLoad)
            {
                if (!_chunks.TryGetValue(coord, out Chunk chunk))
                {
                    chunk = CreateChunk(coord);
                }

                if (!chunk.IsLoaded)
                {
                    chunk.Load();
                    ActiveChunkCount++;
                    OnChunkLoaded?.Invoke(chunk);
                }
            }

            List<ChunkCoord> toUnload = new List<ChunkCoord>();
            foreach (var kvp in _chunks)
            {
                if (!kvp.Value.IsLoaded) continue;
                if (kvp.Key.DistanceTo(playerChunk) > unloadRadius)
                {
                    toUnload.Add(kvp.Key);
                }
            }

            foreach (var coord in toUnload)
            {
                if (_chunks.TryGetValue(coord, out Chunk chunk))
                {
                    chunk.Unload();
                    ActiveChunkCount--;
                    OnChunkUnloaded?.Invoke(chunk);
                }
            }

            Debug.Log($"[ChunkManager] Active chunks: {ActiveChunkCount}");
        }

        private Chunk CreateChunk(ChunkCoord coord)
        {
            var go = new GameObject($"Chunk_{coord.X}_{coord.Z}");
            go.transform.SetParent(transform);
            var chunk = go.AddComponent<Chunk>();
            chunk.Initialize(coord, _config.chunkSize);

            Color groundColor = GetGroundColorForChunk(coord);
            chunk.GenerateGround(_config.chunkSize, groundColor);

            _chunks[coord] = chunk;
            return chunk;
        }

        private Color GetGroundColorForChunk(ChunkCoord coord)
        {
            float noise = Mathf.PerlinNoise(coord.X * 0.1f, coord.Z * 0.1f);
            return Color.Lerp(
                new Color(0.25f, 0.45f, 0.2f),
                new Color(0.35f, 0.55f, 0.25f),
                noise);
        }

        public bool IsChunkInBounds(ChunkCoord coord)
        {
            return coord.X >= 0 && coord.X < _config.ChunkCountX &&
                   coord.Z >= 0 && coord.Z < _config.ChunkCountZ;
        }

        public Chunk GetChunk(ChunkCoord coord)
        {
            _chunks.TryGetValue(coord, out Chunk chunk);
            return chunk;
        }

        public Chunk GetChunkAtWorldPosition(Vector3 worldPos)
        {
            if (_config == null) return null;
            ChunkCoord coord = ChunkCoord.FromWorldPosition(worldPos, _config.chunkSize);
            return GetChunk(coord);
        }

        public List<Chunk> GetLoadedChunks()
        {
            var loaded = new List<Chunk>();
            foreach (var kvp in _chunks)
            {
                if (kvp.Value.IsLoaded)
                {
                    loaded.Add(kvp.Value);
                }
            }
            return loaded;
        }

        public List<Chunk> GetChunksInRange(Vector3 center, float range)
        {
            var result = new List<Chunk>();
            float rangeSq = range * range;

            foreach (var kvp in _chunks)
            {
                Vector3 chunkCenter = kvp.Key.GetWorldCenter(_config.chunkSize);
                float distSq = (chunkCenter - center).sqrMagnitude;
                if (distSq <= rangeSq)
                {
                    result.Add(kvp.Value);
                }
            }
            return result;
        }

        public void ClearAllChunks()
        {
            foreach (var kvp in _chunks)
            {
                if (kvp.Value != null)
                {
                    kvp.Value.ClearObjects();
                    Destroy(kvp.Value.gameObject);
                }
            }
            _chunks.Clear();
            ActiveChunkCount = 0;
        }

        public int GetChunkCount() => _chunks.Count;
    }
}
