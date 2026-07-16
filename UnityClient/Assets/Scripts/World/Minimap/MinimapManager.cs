using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.World.Minimap
{
    public class MinimapManager : MonoBehaviour
    {
        [SerializeField] private Camera _minimapCamera;
        [SerializeField] private RenderTexture _minimapTexture;
        [SerializeField] private float _minimapSize = 200f;
        [SerializeField] private float _minimapHeight = 150f;
        [SerializeField] private bool _followPlayer = true;

        private Transform _playerTransform;
        private List<MinimapIconEntry> _icons = new List<MinimapIconEntry>();

        public bool IsVisible { get; private set; } = true;

        public void Initialize(Camera minimapCamera, RenderTexture texture)
        {
            _minimapCamera = minimapCamera;
            _minimapTexture = texture;

            if (_minimapCamera != null)
            {
                _minimapCamera.orthographic = true;
                _minimapCamera.orthographicSize = _minimapSize;
                _minimapCamera.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
                _minimapCamera.transform.position = new Vector3(0f, _minimapHeight, 0f);
                _minimapCamera.clearFlags = CameraClearFlags.SolidColor;
                _minimapCamera.backgroundColor = new Color(0.15f, 0.2f, 0.15f, 0.9f);
                _minimapCamera.cullingMask = LayerMask.GetMask("Default");
            }

            Debug.Log("[MinimapManager] Initialized");
        }

        public void SetPlayerTransform(Transform player)
        {
            _playerTransform = player;
        }

        private void LateUpdate()
        {
            if (_minimapCamera == null || !_followPlayer || _playerTransform == null) return;

            Vector3 pos = _playerTransform.position;
            _minimapCamera.transform.position = new Vector3(pos.x, _minimapHeight, pos.z);
        }

        public void AddIcon(string id, MinimapIconType type, Vector3 worldPosition, Color color)
        {
            var entry = new MinimapIconEntry
            {
                Id = id,
                Type = type,
                WorldPosition = worldPosition,
                Color = color
            };
            _icons.Add(entry);
        }

        public void RemoveIcon(string id)
        {
            _icons.RemoveAll(icon => icon.Id == id);
        }

        public void UpdateIconPosition(string id, Vector3 newPosition)
        {
            for (int i = 0; i < _icons.Count; i++)
            {
                if (_icons[i].Id == id)
                {
                    var entry = _icons[i];
                    entry.WorldPosition = newPosition;
                    _icons[i] = entry;
                }
            }
        }

        public void SetVisible(bool visible)
        {
            IsVisible = visible;
            if (_minimapCamera != null)
            {
                _minimapCamera.enabled = visible;
            }
        }

        public void SetZoom(float size)
        {
            _minimapSize = size;
            if (_minimapCamera != null)
            {
                _minimapCamera.orthographicSize = size;
            }
        }

        public Vector2 WorldToMinimapPosition(Vector3 worldPosition)
        {
            if (_minimapCamera == null) return Vector2.zero;

            Vector3 viewportPos = _minimapCamera.WorldToViewportPoint(worldPosition);
            return new Vector2(viewportPos.x, viewportPos.y);
        }

        public List<MinimapIconEntry> GetIcons() => new List<MinimapIconEntry>(_icons);
        public int IconCount => _icons.Count;

        public void ClearIcons()
        {
            _icons.Clear();
        }
    }

    [Serializable]
    public struct MinimapIconEntry
    {
        public string Id;
        public MinimapIconType Type;
        public Vector3 WorldPosition;
        public Color Color;
    }
}
