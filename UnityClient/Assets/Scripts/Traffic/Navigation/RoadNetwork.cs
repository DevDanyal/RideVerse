using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Traffic.Navigation
{
    [Serializable]
    public class RoadNode
    {
        public string Id;
        public Vector3 Position;
        public float SpeedLimit;
        public bool IsIntersection;
        public bool HasTrafficLight;
        public bool HasStopSign;
        public bool IsRoundabout;
        public bool IsHighway;

        [NonSerialized] public List<RoadEdge> OutgoingEdges = new List<RoadEdge>();
        [NonSerialized] public List<RoadEdge> IncomingEdges = new List<RoadEdge>();

        public RoadNode(string id, Vector3 position, float speedLimit = 50f)
        {
            Id = id;
            Position = position;
            SpeedLimit = speedLimit;
            IsIntersection = false;
            HasTrafficLight = false;
            HasStopSign = false;
            IsRoundabout = false;
            IsHighway = false;
        }

        public float DistanceTo(RoadNode other)
        {
            return Vector3.Distance(Position, other.Position);
        }

        public float DistanceTo(Vector3 position)
        {
            return Vector3.Distance(Position, position);
        }
    }

    [Serializable]
    public class RoadEdge
    {
        public RoadNode From;
        public RoadNode To;
        public float Length;
        public int LaneCount;
        public bool IsOneWay;
        public float SpeedLimit;

        public RoadEdge(RoadNode from, RoadNode to, int laneCount = 2, float speedLimit = 50f, bool isOneWay = false)
        {
            From = from;
            To = to;
            Length = Vector3.Distance(from.Position, to.Position);
            LaneCount = laneCount;
            SpeedLimit = speedLimit;
            IsOneWay = isOneWay;
        }

        public Vector3 GetDirection()
        {
            return (To.Position - From.Position).normalized;
        }

        public Vector3 GetLaneOffset(int laneIndex, float laneWidth)
        {
            Vector3 direction = GetDirection();
            Vector3 right = Vector3.Cross(Vector3.up, direction);
            float offset = (laneIndex - (LaneCount - 1) * 0.5f) * laneWidth;
            return right * offset;
        }

        public Vector3 GetLanePosition(int laneIndex, float laneWidth, float progress)
        {
            Vector3 startLanePos = From.Position + GetLaneOffset(laneIndex, laneWidth);
            Vector3 endLanePos = To.Position + GetLaneOffset(laneIndex, laneWidth);
            return Vector3.Lerp(startLanePos, endLanePos, Mathf.Clamp01(progress));
        }
    }

    public class RoadNetwork
    {
        private Dictionary<string, RoadNode> _nodes = new Dictionary<string, RoadNode>();
        private List<RoadEdge> _edges = new List<RoadEdge>();
        private int _nextNodeId;

        public int NodeCount => _nodes.Count;
        public int EdgeCount => _edges.Count;
        public IReadOnlyDictionary<string, RoadNode> Nodes => _nodes;
        public IReadOnlyList<RoadEdge> Edges => _edges;

        public RoadNode AddNode(Vector3 position, float speedLimit = 50f, bool isIntersection = false)
        {
            string id = $"RN_{_nextNodeId++}";
            var node = new RoadNode(id, position, speedLimit)
            {
                IsIntersection = isIntersection
            };
            _nodes[id] = node;
            return node;
        }

        public RoadEdge AddEdge(RoadNode from, RoadNode to, int laneCount = 2, float speedLimit = 50f, bool isOneWay = false)
        {
            var edge = new RoadEdge(from, to, laneCount, speedLimit, isOneWay);
            from.OutgoingEdges.Add(edge);
            to.IncomingEdges.Add(edge);
            _edges.Add(edge);
            return edge;
        }

        public RoadNode GetNode(string id)
        {
            _nodes.TryGetValue(id, out var node);
            return node;
        }

        public RoadNode GetNearestNode(Vector3 position)
        {
            RoadNode nearest = null;
            float nearestDistSq = float.MaxValue;

            foreach (var node in _nodes.Values)
            {
                float distSq = (node.Position - position).sqrMagnitude;
                if (distSq < nearestDistSq)
                {
                    nearestDistSq = distSq;
                    nearest = node;
                }
            }

            return nearest;
        }

        public RoadNode GetNearestNodeOnRoad(Vector3 position, float maxDistance = 50f)
        {
            RoadNode nearest = null;
            float nearestDistSq = float.MaxValue;
            float maxDistSq = maxDistance * maxDistance;

            foreach (var node in _nodes.Values)
            {
                float distSq = (node.Position - position).sqrMagnitude;
                if (distSq < maxDistSq && distSq < nearestDistSq)
                {
                    nearestDistSq = distSq;
                    nearest = node;
                }
            }

            return nearest;
        }

        public List<RoadNode> GetNodesInRadius(Vector3 center, float radius)
        {
            var result = new List<RoadNode>();
            float radiusSq = radius * radius;

            foreach (var node in _nodes.Values)
            {
                if ((node.Position - center).sqrMagnitude <= radiusSq)
                {
                    result.Add(node);
                }
            }

            return result;
        }

        public RoadEdge GetEdgeBetween(RoadNode from, RoadNode to)
        {
            foreach (var edge in from.OutgoingEdges)
            {
                if (edge.To == to) return edge;
            }
            return null;
        }

        public void GenerateGridNetwork(Vector3 center, int gridX, int gridZ, float spacing, float mainRoadSpeed, float sideRoadSpeed)
        {
            _nodes.Clear();
            _edges.Clear();
            _nextNodeId = 0;

            RoadNode[,] grid = new RoadNode[gridX + 1, gridZ + 1];

            Vector3 origin = center - new Vector3(gridX * spacing * 0.5f, 0f, gridZ * spacing * 0.5f);

            for (int x = 0; x <= gridX; x++)
            {
                for (int z = 0; z <= gridZ; z++)
                {
                    Vector3 pos = origin + new Vector3(x * spacing, 0f, z * spacing);
                    bool isMainRoad = (x % 3 == 0) || (z % 3 == 0);
                    float speed = isMainRoad ? mainRoadSpeed : sideRoadSpeed;
                    bool isIntersection = isMainRoad && ((x % 3 == 0) && (z % 3 == 0));

                    var node = AddNode(pos, speed, isIntersection);
                    grid[x, z] = node;
                }
            }

            for (int x = 0; x <= gridX; x++)
            {
                for (int z = 0; z <= gridZ; z++)
                {
                    if (x < gridX)
                    {
                        bool isMainRoad = (z % 3 == 0);
                        float speed = isMainRoad ? mainRoadSpeed : sideRoadSpeed;
                        AddEdge(grid[x, z], grid[x + 1, z], isMainRoad ? 3 : 2, speed);
                        AddEdge(grid[x + 1, z], grid[x, z], isMainRoad ? 3 : 2, speed);
                    }

                    if (z < gridZ)
                    {
                        bool isMainRoad = (x % 3 == 0);
                        float speed = isMainRoad ? mainRoadSpeed : sideRoadSpeed;
                        AddEdge(grid[x, z], grid[x, z + 1], isMainRoad ? 3 : 2, speed);
                        AddEdge(grid[x, z + 1], grid[x, z], isMainRoad ? 3 : 2, speed);
                    }
                }
            }
        }

        public void Clear()
        {
            _nodes.Clear();
            _edges.Clear();
            _nextNodeId = 0;
        }
    }
}
