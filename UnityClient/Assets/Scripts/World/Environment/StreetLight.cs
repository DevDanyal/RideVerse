using UnityEngine;

namespace RideVerse.World.Environment
{
    [RequireComponent(typeof(Light))]
    public class StreetLight : MonoBehaviour
    {
        [SerializeField] private Light _pointLight;
        [SerializeField] private float _range = 15f;
        [SerializeField] private float _intensity = 1.5f;
        [SerializeField] private Color _lightColor = new Color(1f, 0.9f, 0.7f);

        private bool _isActive = true;

        public bool IsActive => _isActive;

        private void Awake()
        {
            if (_pointLight == null)
            {
                _pointLight = GetComponent<Light>();
            }

            if (_pointLight == null)
            {
                _pointLight = gameObject.AddComponent<Light>();
            }

            _pointLight.type = LightType.Point;
            _pointLight.range = _range;
            _pointLight.intensity = _intensity;
            _pointLight.color = _lightColor;
            _pointLight.renderMode = LightRenderMode.Auto;
            _pointLight.shadows = LightShadows.None;
        }

        public void SetActive(bool active)
        {
            _isActive = active;
            _pointLight.enabled = active;
        }

        public void SetIntensity(float intensity)
        {
            _intensity = intensity;
            if (_pointLight != null)
            {
                _pointLight.intensity = intensity;
            }
        }
    }
}
