using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class RoadblockSystem
    {
        private readonly PoliceConfig _config;
        private readonly List<RoadblockData> _activeRoadblocks;

        public int ActiveRoadblockCount => _activeRoadblocks.Count;
        public IReadOnlyList<RoadblockData> ActiveRoadblocks => _activeRoadblocks;

        public event Action<RoadblockData> OnRoadblockDeployed;
        public event Action<RoadblockData> OnRoadblockRemoved;

        public RoadblockSystem(PoliceConfig config)
        {
            _config = config;
            _activeRoadblocks = new List<RoadblockData>();
        }

        public void Update(float deltaTime)
        {
            for (int i = _activeRoadblocks.Count - 1; i >= 0; i--)
            {
                var rb = _activeRoadblocks[i];

                if (rb.IsReady && rb.IsExpired())
                {
                    RemoveRoadblock(rb.RoadblockId);
                    continue;
                }

                if (!rb.IsReady)
                {
                    rb.SetupProgress += deltaTime / _config.roadblockSetupTime;
                    if (rb.SetupProgress >= 1f)
                    {
                        rb.IsReady = true;
                        rb.Activate();
                    }
                }
            }
        }

        public RoadblockData CreateRoadblock(RoadblockType type, Vector3 position, float rotation)
        {
            if (_activeRoadblocks.Count >= _config.maxActiveRoadblocks)
            {
                return null;
            }

            var roadblock = new RoadblockData(type, position, rotation);
            _activeRoadblocks.Add(roadblock);
            OnRoadblockDeployed?.Invoke(roadblock);
            return roadblock;
        }

        public RoadblockData CreateSpikeStrip(Vector3 position, float rotation)
        {
            return CreateRoadblock(RoadblockType.SpikeStrip, position, rotation);
        }

        public RoadblockData CreatePoliceCarRoadblock(Vector3 position, float rotation)
        {
            return CreateRoadblock(RoadblockType.PoliceCars, position, rotation);
        }

        public void RemoveRoadblock(string roadblockId)
        {
            for (int i = _activeRoadblocks.Count - 1; i >= 0; i--)
            {
                if (_activeRoadblocks[i].RoadblockId == roadblockId)
                {
                    var rb = _activeRoadblocks[i];
                    _activeRoadblocks.RemoveAt(i);
                    OnRoadblockRemoved?.Invoke(rb);
                    return;
                }
            }
        }

        public void AssignUnit(string roadblockId, string unitId)
        {
            var rb = FindRoadblock(roadblockId);
            if (rb != null && !rb.AssignedUnitIds.Contains(unitId))
            {
                rb.AssignedUnitIds.Add(unitId);
            }
        }

        public bool IsRoadblockReady(string roadblockId)
        {
            var rb = FindRoadblock(roadblockId);
            return rb != null && rb.IsReady;
        }

        public bool HasActiveRoadblocks()
        {
            return _activeRoadblocks.Count > 0;
        }

        public RoadblockData FindRoadblock(string roadblockId)
        {
            for (int i = 0; i < _activeRoadblocks.Count; i++)
            {
                if (_activeRoadblocks[i].RoadblockId == roadblockId)
                    return _activeRoadblocks[i];
            }
            return null;
        }

        public RoadblockData GetRoadblockBlockingPath(Vector3 from, Vector3 to)
        {
            Vector3 direction = (to - from).normalized;
            float pathLength = Vector3.Distance(from, to);

            for (int i = 0; i < _activeRoadblocks.Count; i++)
            {
                var rb = _activeRoadblocks[i];
                if (!rb.IsReady || !rb.IsActive) continue;

                Vector3 toRoadblock = rb.Position - from;
                float forwardDist = Vector3.Dot(toRoadblock, direction);
                float perpDist = Vector3.Cross(direction, toRoadblock).magnitude;

                if (forwardDist > 0 && forwardDist < pathLength && perpDist < rb.GetEffectiveWidth())
                {
                    return rb;
                }
            }

            return null;
        }

        public Vector3 CalculateRoadblockPosition(Vector3 targetPosition, Vector3 targetDirection, float distanceAhead)
        {
            Vector3 aheadPos = targetPosition + targetDirection.normalized * distanceAhead;
            aheadPos.y = 0f;
            return aheadPos;
        }

        public Vector3 CalculateSpikeStripPosition(Vector3 targetPosition, Vector3 targetDirection, float distanceAhead)
        {
            Vector3 pos = targetPosition + targetDirection.normalized * distanceAhead;
            pos.y = 0f;
            return pos;
        }

        public bool IsPositionInRoadblock(Vector3 position)
        {
            for (int i = 0; i < _activeRoadblocks.Count; i++)
            {
                var rb = _activeRoadblocks[i];
                if (!rb.IsReady || !rb.IsActive) continue;

                float distance = Vector3.Distance(position, rb.Position);
                if (distance < rb.GetEffectiveWidth() * 0.5f)
                {
                    return true;
                }
            }
            return false;
        }

        public float GetSpikeStripDamage(Vector3 position)
        {
            for (int i = 0; i < _activeRoadblocks.Count; i++)
            {
                var rb = _activeRoadblocks[i];
                if (rb.Type != RoadblockType.SpikeStrip || !rb.IsReady || !rb.IsActive) continue;

                float distance = Vector3.Distance(position, rb.Position);
                if (distance < _config.spikeStripLength * 0.5f)
                {
                    return _config.spikeStripDamageAmount;
                }
            }
            return 0f;
        }

        public float GetSpikeStripSlowdownFactor(Vector3 position)
        {
            for (int i = 0; i < _activeRoadblocks.Count; i++)
            {
                var rb = _activeRoadblocks[i];
                if (rb.Type != RoadblockType.SpikeStrip || !rb.IsReady || !rb.IsActive) continue;

                float distance = Vector3.Distance(position, rb.Position);
                if (distance < _config.spikeStripLength * 0.5f)
                {
                    return _config.pursuitSpikeStripSlowdown;
                }
            }
            return 1f;
        }

        public int GetRequiredUnitsForRoadblock(RoadblockType type)
        {
            return type switch
            {
                RoadblockType.PoliceCars => _config.roadblockMinUnitsRequired,
                RoadblockType.SpikeStrip => 1,
                RoadblockType.Barricade => _config.roadblockMinUnitsRequired,
                RoadblockType.TrafficDiversion => 1,
                _ => 1
            };
        }

        public void ClearAll()
        {
            for (int i = _activeRoadblocks.Count - 1; i >= 0; i--)
            {
                OnRoadblockRemoved?.Invoke(_activeRoadblocks[i]);
            }
            _activeRoadblocks.Clear();
        }
    }
}
