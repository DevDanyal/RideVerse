using UnityEngine;

namespace RideVerse.World.Performance
{
    public class AndroidOptimizer : MonoBehaviour
    {
        [Header("Performance Targets")]
        [SerializeField] private int _targetFrameRate = 60;
        [SerializeField] private int _maxTextureSize = 1024;
        [SerializeField] private bool _enableOcclusionCulling = true;
        [SerializeField] private bool _enableStaticBatching = true;
        [SerializeField] private bool _enableDynamicBatching = false;

        [Header("Quality Settings")]
        [SerializeField] private int _pixelLightCount = 2;
        [SerializeField] private int _shadowResolution = 1;
        [SerializeField] private float _shadowDistance = 80f;
        [SerializeField] private int _antiAliasing = 0;
        [SerializeField] private bool _softParticles = false;

        [Header("Memory")]
        [SerializeField] private int _maxActiveObjects = 300;
        [SerializeField] private float _gcInterval = 30f;



        public bool IsAndroid => Application.platform == RuntimePlatform.Android;
        public int MaxActiveObjects => _maxActiveObjects;

        public void Initialize()
        {
            if (!IsAndroid)
            {
                Debug.Log("[AndroidOptimizer] Running on non-Android platform, skipping optimization");
                return;
            }

            ApplyFrameRate();
            ApplyQualitySettings();
            ApplyMemorySettings();
            Debug.Log("[AndroidOptimizer] Android optimizations applied");
        }

        private void ApplyFrameRate()
        {
            Application.targetFrameRate = _targetFrameRate;
            QualitySettings.vSyncCount = 0;
        }

        private void ApplyQualitySettings()
        {
            QualitySettings.pixelLightCount = _pixelLightCount;
            QualitySettings.shadowResolution = (ShadowResolution)_shadowResolution;
            QualitySettings.shadowDistance = _shadowDistance;
            QualitySettings.antiAliasing = _antiAliasing;
            QualitySettings.softParticles = _softParticles;
            QualitySettings.shadowCascades = 2;
            QualitySettings.shadowCascade2Split = 0.33f;

            QualitySettings.masterTextureLimit = _maxTextureSize <= 512 ? 2 : _maxTextureSize <= 1024 ? 1 : 0;

#if UNITY_EDITOR
            if (_enableStaticBatching)
            {
                UnityEditor.PlayerSettings.staticBatching = true;
            }

            if (_enableDynamicBatching)
            {
                UnityEditor.PlayerSettings.dynamicBatching = true;
            }
#endif
        }

        private void ApplyMemorySettings()
        {
        }

        private void Update()
        {
        }

        public void SetTargetFrameRate(int fps)
        {
            _targetFrameRate = fps;
            Application.targetFrameRate = fps;
        }

        public void SetShadowDistance(float distance)
        {
            _shadowDistance = distance;
            QualitySettings.shadowDistance = distance;
        }

        public PerformanceStats GetStats()
        {
            return new PerformanceStats
            {
                FrameRate = Mathf.RoundToInt(1f / Time.unscaledDeltaTime),
                MemoryUsed = System.GC.GetTotalMemory(false) / (1024 * 1024),
                ActiveObjects = FindObjectsByType<GameObject>(FindObjectsSortMode.None).Length
            };
        }
    }

    public struct PerformanceStats
    {
        public int FrameRate;
        public long MemoryUsed;
        public int ActiveObjects;
    }
}
