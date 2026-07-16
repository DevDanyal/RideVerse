using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.World.Core;
using RideVerse.World.Chunks;

namespace RideVerse.World.Streaming
{
    public class WorldStreamer : MonoBehaviour
    {
        [SerializeField] private WorldConfig _config;
        [SerializeField] private ChunkManager _chunkManager;
        [SerializeField] private float _updateInterval = 0.5f;
        [SerializeField] private int _maxChunksPerFrame = 2;

        private Transform _playerTransform;
        private float _lastUpdateTime;
        private Queue<ChunkCoord> _loadQueue = new Queue<ChunkCoord>();
        private Queue<ChunkCoord> _unloadQueue = new Queue<ChunkCoord>();
        private bool _isStreaming;

        public int LoadedChunkCount => _chunkManager != null ? _chunkManager.ActiveChunkCount : 0;
        public bool IsStreaming => _isStreaming;

        public event Action<ChunkCoord> OnChunkLoadRequested;
        public event Action<ChunkCoord> OnChunkUnloadRequested;

        public void Initialize(WorldConfig config, ChunkManager chunkManager)
        {
            _config = config;
            _chunkManager = chunkManager;
            _updateInterval = _config.streamingUpdateInterval;
            _maxChunksPerFrame = _config.maxChunksPerFrame;
            Debug.Log($"[WorldStreamer] Initialized: interval={_updateInterval}s, maxPerFrame={_maxChunksPerFrame}");
        }

        public void SetPlayerTransform(Transform player)
        {
            _playerTransform = player;
        }

        private void Update()
        {
            if (_playerTransform == null || _chunkManager == null) return;

            if (Time.time - _lastUpdateTime < _updateInterval) return;
            _lastUpdateTime = Time.time;

            UpdateStreaming();
        }

        private void UpdateStreaming()
        {
            Vector3 playerPos = _playerTransform.position;
            ChunkCoord playerChunk = ChunkCoord.FromWorldPosition(playerPos, _config.chunkSize);

            UpdateLoadQueue(playerChunk);
            ProcessQueues();
        }

        private void UpdateLoadQueue(ChunkCoord playerChunk)
        {
            _loadQueue.Clear();
            _unloadQueue.Clear();

            int loadRadius = _config.loadRadius;
            int unloadRadius = _config.unloadRadius;

            List<ChunkCoord> desiredChunks = new List<ChunkCoord>();
            for (int x = -loadRadius; x <= loadRadius; x++)
            {
                for (int z = -loadRadius; z <= loadRadius; z++)
                {
                    ChunkCoord coord = new ChunkCoord(playerChunk.X + x, playerChunk.Z + z);
                    if (_chunkManager.IsChunkInBounds(coord))
                    {
                        desiredChunks.Add(coord);
                        var chunk = _chunkManager.GetChunk(coord);
                        if (chunk == null || !chunk.IsLoaded)
                        {
                            _loadQueue.Enqueue(coord);
                        }
                    }
                }
            }

            var loadedChunks = _chunkManager.GetLoadedChunks();
            foreach (var chunk in loadedChunks)
            {
                if (chunk.Coord.DistanceTo(playerChunk) > unloadRadius)
                {
                    _unloadQueue.Enqueue(chunk.Coord);
                }
            }
        }

        private void ProcessQueues()
        {
            int loadedThisFrame = 0;
            while (_loadQueue.Count > 0 && loadedThisFrame < _maxChunksPerFrame)
            {
                ChunkCoord coord = _loadQueue.Dequeue();
                OnChunkLoadRequested?.Invoke(coord);
                loadedThisFrame++;
            }

            int unloadedThisFrame = 0;
            while (_unloadQueue.Count > 0 && unloadedThisFrame < _maxChunksPerFrame)
            {
                ChunkCoord coord = _unloadQueue.Dequeue();
                OnChunkUnloadRequested?.Invoke(coord);
                unloadedThisFrame++;
            }
        }

        public void ForceLoadAll()
        {
            for (int x = 0; x < _config.ChunkCountX; x++)
            {
                for (int z = 0; z < _config.ChunkCountZ; z++)
                {
                    _loadQueue.Enqueue(new ChunkCoord(x, z));
                }
            }
            ProcessQueues();
        }

        public void ForceUnloadAll()
        {
            var loaded = _chunkManager.GetLoadedChunks();
            foreach (var chunk in loaded)
            {
                _unloadQueue.Enqueue(chunk.Coord);
            }
            ProcessQueues();
        }

        public List<ChunkCoord> GetLoadedChunkCoords()
        {
            var result = new List<ChunkCoord>();
            var loaded = _chunkManager.GetLoadedChunks();
            foreach (var chunk in loaded)
            {
                result.Add(chunk.Coord);
            }
            return result;
        }
    }
}
