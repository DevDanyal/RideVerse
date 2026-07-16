using UnityEngine;

namespace RideVerse.World.Settings
{
    [CreateAssetMenu(fileName = "WorldSettings", menuName = "RideVerse/World/WorldSettings")]
    public class WorldSettings : ScriptableObject
    {
        [Header("Gravity")]
        public float gravity = -9.81f;

        [Header("Fog")]
        public bool fogEnabled = true;
        public FogMode fogMode = FogMode.ExponentialSquared;
        public float fogDensity = 0.005f;
        public float fogStartDistance = 50f;
        public float fogEndDistance = 500f;
        public Color fogColor = new Color(0.7f, 0.75f, 0.85f);

        [Header("Ambient Light")]
        public Color ambientSkyColor = new Color(0.7f, 0.75f, 0.85f);
        public Color ambientEquatorColor = new Color(0.6f, 0.6f, 0.65f);
        public Color ambientGroundColor = new Color(0.3f, 0.35f, 0.25f);
        public float ambientIntensity = 1f;
        public UnityEngine.Rendering.AmbientMode ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;

        [Header("Sun")]
        public Color sunColor = new Color(1f, 0.95f, 0.85f);
        public float sunIntensity = 1.2f;
        public float sunAngle = 50f;

        [Header("Shadows")]
        public LightShadows shadowType = LightShadows.Soft;
        public float shadowStrength = 0.8f;
        public float shadowDistance = 150f;
        public float shadowNearPlane = 0.5f;

        [Header("Skybox")]
        public Material skyboxMaterial;
        public Color skyboxTint = Color.white;
        public float skyboxExposure = 1f;
        public float skyboxRotation = 0f;

        public void Apply()
        {
            Physics.gravity = new Vector3(0f, gravity, 0f);

            RenderSettings.fog = fogEnabled;
            RenderSettings.fogMode = fogMode;
            RenderSettings.fogDensity = fogDensity;
            RenderSettings.fogStartDistance = fogStartDistance;
            RenderSettings.fogEndDistance = fogEndDistance;
            RenderSettings.fogColor = fogColor;

            RenderSettings.ambientMode = ambientMode;
            RenderSettings.ambientSkyColor = ambientSkyColor;
            RenderSettings.ambientEquatorColor = ambientEquatorColor;
            RenderSettings.ambientGroundColor = ambientGroundColor;
            RenderSettings.ambientIntensity = ambientIntensity;

            if (skyboxMaterial != null)
            {
                RenderSettings.skybox = skyboxMaterial;
                RenderSettings.skybox.SetColor("_Tint", skyboxTint);
                RenderSettings.skybox.SetFloat("_Exposure", skyboxExposure);
                RenderSettings.skybox.SetFloat("_Rotation", skyboxRotation);
            }

            QualitySettings.shadowDistance = shadowDistance;
            QualitySettings.shadowNearPlaneOffset = shadowNearPlane;

            var sun = FindFirstObjectByType<Light>();
            if (sun != null && sun.type == LightType.Directional)
            {
                sun.color = sunColor;
                sun.intensity = sunIntensity;
                sun.shadows = shadowType;
                sun.shadowStrength = shadowStrength;
                sun.transform.rotation = Quaternion.Euler(sunAngle, -30f, 0f);
            }
        }

        public Core.WorldSettingsData ToSaveData()
        {
            return new Core.WorldSettingsData
            {
                Gravity = gravity,
                FogDensity = fogDensity,
                FogStartDistance = fogStartDistance,
                FogEndDistance = fogEndDistance,
                AmbientIntensity = ambientIntensity,
                SunIntensity = sunIntensity,
                SunAngle = sunAngle
            };
        }

        public void LoadFromSaveData(Core.WorldSettingsData data)
        {
            if (data == null) return;
            gravity = data.Gravity;
            fogDensity = data.FogDensity;
            fogStartDistance = data.FogStartDistance;
            fogEndDistance = data.FogEndDistance;
            ambientIntensity = data.AmbientIntensity;
            sunIntensity = data.SunIntensity;
            sunAngle = data.SunAngle;
        }
    }
}
