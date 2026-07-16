using System;
using UnityEngine;

namespace RideVerse.World.Chunks
{
    [Serializable]
    public struct ChunkCoord : IEquatable<ChunkCoord>
    {
        public int X;
        public int Z;

        public ChunkCoord(int x, int z)
        {
            X = x;
            Z = z;
        }

        public static ChunkCoord FromWorldPosition(Vector3 worldPos, int chunkSize)
        {
            int x = Mathf.FloorToInt(worldPos.x / chunkSize);
            int z = Mathf.FloorToInt(worldPos.z / chunkSize);
            return new ChunkCoord(x, z);
        }

        public Vector3 ToWorldPosition(int chunkSize)
        {
            return new Vector3(X * chunkSize, 0f, Z * chunkSize);
        }

        public Vector3 GetWorldCenter(int chunkSize)
        {
            return new Vector3(X * chunkSize + chunkSize * 0.5f, 0f, Z * chunkSize + chunkSize * 0.5f);
        }

        public float DistanceTo(ChunkCoord other)
        {
            float dx = X - other.X;
            float dz = Z - other.Z;
            return Mathf.Sqrt(dx * dx + dz * dz);
        }

        public int ManhattanDistanceTo(ChunkCoord other)
        {
            return Mathf.Abs(X - other.X) + Mathf.Abs(Z - other.Z);
        }

        public bool Equals(ChunkCoord other)
        {
            return X == other.X && Z == other.Z;
        }

        public override bool Equals(object obj)
        {
            return obj is ChunkCoord other && Equals(other);
        }

        public override int GetHashCode()
        {
            return X * 397 ^ Z;
        }

        public override string ToString()
        {
            return $"({X}, {Z})";
        }

        public static bool operator ==(ChunkCoord a, ChunkCoord b) => a.Equals(b);
        public static bool operator !=(ChunkCoord a, ChunkCoord b) => !a.Equals(b);
    }
}
