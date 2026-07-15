using UnityEngine;

namespace RideVerse.Vehicles
{
    public class CarLights : MonoBehaviour
    {
        [Header("Headlights")]
        [SerializeField] private Light headlightLeft;
        [SerializeField] private Light headlightRight;
        [SerializeField] private float headlightIntensity = 2f;

        [Header("Brake Lights")]
        [SerializeField] private Light brakeLightLeft;
        [SerializeField] private Light brakeLightRight;
        [SerializeField] private float brakeLightIntensity = 4f;

        [Header("Reverse Lights")]
        [SerializeField] private Light reverseLightLeft;
        [SerializeField] private Light reverseLightRight;
        [SerializeField] private float reverseLightIntensity = 1.5f;

        [Header("Indicators")]
        [SerializeField] private Light indicatorLeftFront;
        [SerializeField] private Light indicatorLeftRear;
        [SerializeField] private Light indicatorRightFront;
        [SerializeField] private Light indicatorRightRear;
        [SerializeField] private float indicatorBlinkRate = 1.5f;

        private bool _headlightOn;
        private bool _brakeActive;
        private bool _reverseActive;
        private bool _leftIndicatorOn;
        private bool _rightIndicatorOn;
        private bool _hazardLightsOn;
        private float _indicatorTimer;

        public bool HeadlightOn => _headlightOn;
        public bool BrakeActive => _brakeActive;
        public bool ReverseActive => _reverseActive;
        public bool LeftIndicatorOn => _leftIndicatorOn;
        public bool RightIndicatorOn => _rightIndicatorOn;

        private void Update()
        {
            UpdateIndicatorBlink();
            UpdateBrakeLights();
            UpdateReverseLights();
        }

        public void ToggleHeadlight()
        {
            _headlightOn = !_headlightOn;
            SetHeadlights(_headlightOn);
        }

        public void SetHeadlights(bool on)
        {
            _headlightOn = on;
            float intensity = on ? headlightIntensity : 0f;
            SetLight(headlightLeft, on, intensity);
            SetLight(headlightRight, on, intensity);
        }

        public void SetBrake(bool active)
        {
            _brakeActive = active;
        }

        private void UpdateBrakeLights()
        {
            float intensity = _brakeActive ? brakeLightIntensity : 0f;
            SetLight(brakeLightLeft, _brakeActive, intensity);
            SetLight(brakeLightRight, _brakeActive, intensity);
        }

        public void SetReverse(bool active)
        {
            _reverseActive = active;
        }

        private void UpdateReverseLights()
        {
            float intensity = _reverseActive ? reverseLightIntensity : 0f;
            SetLight(reverseLightLeft, _reverseActive, intensity);
            SetLight(reverseLightRight, _reverseActive, intensity);
        }

        public void ToggleLeftIndicator()
        {
            if (_hazardLightsOn) return;
            _leftIndicatorOn = !_leftIndicatorOn;
            _rightIndicatorOn = false;
        }

        public void ToggleRightIndicator()
        {
            if (_hazardLightsOn) return;
            _rightIndicatorOn = !_rightIndicatorOn;
            _leftIndicatorOn = false;
        }

        public void ToggleHazardLights()
        {
            _hazardLightsOn = !_hazardLightsOn;
            _leftIndicatorOn = _hazardLightsOn;
            _rightIndicatorOn = _hazardLightsOn;
        }

        public void CancelIndicators()
        {
            _leftIndicatorOn = false;
            _rightIndicatorOn = false;
            _hazardLightsOn = false;
        }

        private void UpdateIndicatorBlink()
        {
            _indicatorTimer += Time.deltaTime * indicatorBlinkRate;
            bool blinkState = Mathf.Sin(_indicatorTimer * Mathf.PI * 2f) > 0f;

            SetLight(indicatorLeftFront, _leftIndicatorOn && blinkState, _leftIndicatorOn ? 1f : 0f);
            SetLight(indicatorLeftRear, _leftIndicatorOn && blinkState, _leftIndicatorOn ? 1f : 0f);
            SetLight(indicatorRightFront, _rightIndicatorOn && blinkState, _rightIndicatorOn ? 1f : 0f);
            SetLight(indicatorRightRear, _rightIndicatorOn && blinkState, _rightIndicatorOn ? 1f : 0f);
        }

        public void SetAllLights(bool isNight)
        {
            SetHeadlights(isNight);
        }

        private void SetLight(Light light, bool enabled, float intensity)
        {
            if (light == null) return;
            light.enabled = enabled;
            light.intensity = intensity;
        }
    }
}
