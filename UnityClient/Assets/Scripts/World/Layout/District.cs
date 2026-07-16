using System;
using UnityEngine;
using RideVerse.World.Districts;

namespace RideVerse.World.Layout
{
    [Serializable]
    public class District
    {
        public string Id;
        public string Name;
        public DistrictType Type;
        public Vector3 Center;
        public float Width;
        public float Depth;
        public Color ThemeColor;

        public District() { }

        public District(DistrictType type, Vector3 center, float width, float depth)
        {
            Id = $"{type}_{center.x:F0}_{center.z:F0}";
            Type = type;
            Center = center;
            Width = width;
            Depth = depth;
            Name = type.ToString();
            ThemeColor = GetColorForType(type);
        }

        public Bounds GetBounds()
        {
            return new Bounds(Center + Vector3.up * 5f, new Vector3(Width, 10f, Depth));
        }

        public bool ContainsPosition(Vector3 position)
        {
            float halfW = Width * 0.5f;
            float halfD = Depth * 0.5f;
            return position.x >= Center.x - halfW && position.x <= Center.x + halfW &&
                   position.z >= Center.z - halfD && position.z <= Center.z + halfD;
        }

        public static Color GetColorForType(DistrictType type)
        {
            switch (type)
            {
                case DistrictType.Downtown: return new Color(0.4f, 0.4f, 0.5f);
                case DistrictType.Residential: return new Color(0.3f, 0.5f, 0.3f);
                case DistrictType.Industrial: return new Color(0.45f, 0.4f, 0.35f);
                case DistrictType.Commercial: return new Color(0.5f, 0.45f, 0.35f);
                case DistrictType.Countryside: return new Color(0.35f, 0.6f, 0.25f);
                default: return Color.gray;
            }
        }
    }
}
