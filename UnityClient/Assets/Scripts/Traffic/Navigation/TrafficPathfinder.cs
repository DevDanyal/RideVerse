using System.Collections.Generic;
using UnityEngine;
using RideVerse.Traffic.Navigation;

namespace RideVerse.Traffic.Navigation
{
    public class TrafficPathfinder
    {
        private readonly RoadNetwork _network;

        public TrafficPathfinder(RoadNetwork network)
        {
            _network = network;
        }

        public List<Vector3> FindPath(Vector3 start, Vector3 end)
        {
            var startNode = _network.GetNearestNode(start);
            var endNode = _network.GetNearestNode(end);

            if (startNode == null || endNode == null)
                return CreateDirectPath(start, end);

            var nodePath = AStar(startNode, endNode);
            if (nodePath == null || nodePath.Count == 0)
                return CreateDirectPath(start, end);

            return SmoothPath(nodePath, start, end);
        }

        public List<RoadNode> FindNodePath(Vector3 start, Vector3 end)
        {
            var startNode = _network.GetNearestNode(start);
            var endNode = _network.GetNearestNode(end);

            if (startNode == null || endNode == null)
                return null;

            return AStar(startNode, endNode);
        }

        private List<RoadNode> AStar(RoadNode start, RoadNode goal)
        {
            var openSet = new List<RoadNode> { start };
            var cameFrom = new Dictionary<string, RoadNode>();
            var gScore = new Dictionary<string, float> { { start.Id, 0f } };
            var fScore = new Dictionary<string, float> { { start.Id, Heuristic(start, goal) } };
            var closedSet = new HashSet<string>();

            while (openSet.Count > 0)
            {
                RoadNode current = GetLowestF(openSet, fScore);
                if (current.Id == goal.Id)
                    return ReconstructPath(cameFrom, current);

                openSet.Remove(current);
                closedSet.Add(current.Id);

                foreach (var edge in current.OutgoingEdges)
                {
                    RoadNode neighbor = edge.To;
                    if (closedSet.Contains(neighbor.Id)) continue;

                    float tentativeG = gScore[current.Id] + edge.Length;
                    float currentG;
                    gScore.TryGetValue(neighbor.Id, out currentG);

                    if (!gScore.ContainsKey(neighbor.Id) || tentativeG < currentG)
                    {
                        cameFrom[neighbor.Id] = current;
                        gScore[neighbor.Id] = tentativeG;
                        fScore[neighbor.Id] = tentativeG + Heuristic(neighbor, goal);

                        if (!openSet.Contains(neighbor))
                            openSet.Add(neighbor);
                    }
                }
            }

            return null;
        }

        private float Heuristic(RoadNode a, RoadNode b)
        {
            return Vector3.Distance(a.Position, b.Position);
        }

        private RoadNode GetLowestF(List<RoadNode> openSet, Dictionary<string, float> fScore)
        {
            RoadNode lowest = openSet[0];
            float lowestF = float.MaxValue;

            foreach (var node in openSet)
            {
                float f;
                if (fScore.TryGetValue(node.Id, out f) && f < lowestF)
                {
                    lowestF = f;
                    lowest = node;
                }
            }

            return lowest;
        }

        private List<RoadNode> ReconstructPath(Dictionary<string, RoadNode> cameFrom, RoadNode current)
        {
            var path = new List<RoadNode> { current };
            while (cameFrom.ContainsKey(current.Id))
            {
                current = cameFrom[current.Id];
                path.Insert(0, current);
            }
            return path;
        }

        private List<Vector3> SmoothPath(List<RoadNode> nodePath, Vector3 startPos, Vector3 endPos)
        {
            var path = new List<Vector3>();

            if (nodePath.Count == 0)
            {
                path.Add(startPos);
                path.Add(endPos);
                return path;
            }

            path.Add(startPos);

            foreach (var node in nodePath)
            {
                if (path.Count > 1)
                {
                    Vector3 prev = path[path.Count - 1];
                    if (Vector3.Distance(prev, node.Position) > 2f)
                    {
                        path.Add(node.Position);
                    }
                }
                else
                {
                    path.Add(node.Position);
                }
            }

            if (Vector3.Distance(path[path.Count - 1], endPos) > 1f)
            {
                path.Add(endPos);
            }

            return path;
        }

        private List<Vector3> CreateDirectPath(Vector3 start, Vector3 end)
        {
            return new List<Vector3> { start, end };
        }

        public RoadNode GetNextIntersection(Vector3 position, Vector3 direction)
        {
            RoadNode nearest = _network.GetNearestNodeOnRoad(position, 30f);
            if (nearest == null) return null;

            RoadNode best = null;
            float bestScore = float.MinValue;

            foreach (var edge in nearest.OutgoingEdges)
            {
                Vector3 edgeDir = edge.GetDirection();
                float dot = Vector3.Dot(direction, edgeDir);

                if (dot > 0.3f && edge.To.IsIntersection)
                {
                    float score = dot / Mathf.Max(1f, edge.Length);
                    if (score > bestScore)
                    {
                        bestScore = score;
                        best = edge.To;
                    }
                }
            }

            return best ?? nearest;
        }

        public RoadEdge GetCurrentEdge(Vector3 position, float maxSearchRange = 20f)
        {
            RoadEdge closestEdge = null;
            float closestDist = maxSearchRange;

            foreach (var edge in _network.Edges)
            {
                Vector3 closestPoint = GetClosestPointOnSegment(edge.From.Position, edge.To.Position, position);
                float dist = Vector3.Distance(position, closestPoint);

                if (dist < closestDist)
                {
                    closestDist = dist;
                    closestEdge = edge;
                }
            }

            return closestEdge;
        }

        private Vector3 GetClosestPointOnSegment(Vector3 a, Vector3 b, Vector3 point)
        {
            Vector3 ab = b - a;
            float t = Mathf.Clamp01(Vector3.Dot(point - a, ab) / Vector3.Dot(ab, ab));
            return a + ab * t;
        }
    }
}
