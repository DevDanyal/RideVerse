using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.World.Layout
{
    [Serializable]
    public class RoadSegment
    {
        public string Id;
        public RoadType Type;
        public Vector3 Start;
        public Vector3 End;
        public float Width;
        public int Lanes;

        public Vector3 Direction => (End - Start).normalized;
        public float Length => Vector3.Distance(Start, End);
        public Vector3 Center => (Start + End) * 0.5f;

        public RoadSegment() { }

        public RoadSegment(RoadType type, Vector3 start, Vector3 end, float width, int lanes = 2)
        {
            Id = $"Road_{type}_{start.x:F0}_{start.z:F0}";
            Type = type;
            Start = start;
            End = end;
            Width = width;
            Lanes = lanes;
        }

        public Bounds GetBounds()
        {
            Vector3 center = Center;
            Vector3 size = new Vector3(Width, 1f, Length);
            return new Bounds(center, size);
        }
    }

    [Serializable]
    public class Intersection
    {
        public string Id;
        public Vector3 Position;
        public float Size;
        public int ConnectedRoadCount;
        public bool HasTrafficLight;

        public Intersection() { }

        public Intersection(Vector3 position, float size, int connectedRoads, bool trafficLight = false)
        {
            Id = $"Intersection_{position.x:F0}_{position.z:F0}";
            Position = position;
            Size = size;
            ConnectedRoadCount = connectedRoads;
            HasTrafficLight = trafficLight;
        }
    }

    [Serializable]
    public class Bridge
    {
        public string Id;
        public Vector3 Start;
        public Vector3 End;
        public float Width;
        public float Height;
        public float DeckHeight;

        public float Length => Vector3.Distance(Start, End);

        public Bridge() { }

        public Bridge(Vector3 start, Vector3 end, float width, float height, float deckHeight)
        {
            Id = $"Bridge_{start.x:F0}_{start.z:F0}";
            Start = start;
            End = end;
            Width = width;
            Height = height;
            DeckHeight = deckHeight;
        }
    }
}
