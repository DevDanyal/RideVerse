using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace RideVerse.UI
{
    public class FuelGaugeUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private Slider fuelSlider;
        [SerializeField] private Image fuelFill;
        [SerializeField] private TextMeshProUGUI fuelText;
        [SerializeField] private GameObject lowFuelWarning;

        [Header("Settings")]
        [SerializeField] private float warningThreshold = 0.15f;
        [SerializeField] private float updateSmoothing = 5f;

        private float _currentFuelPercent = 1f;
        private float _targetFuelPercent = 1f;
        private bool _warningActive;

        private void Update()
        {
            _currentFuelPercent = Mathf.Lerp(_currentFuelPercent, _targetFuelPercent, Time.deltaTime * updateSmoothing);
            UpdateDisplay();
            UpdateWarning();
        }

        public void UpdateFuel(float current, float max)
        {
            _targetFuelPercent = max > 0 ? Mathf.Clamp01(current / max) : 0f;
        }

        public void UpdateFuelPercent(float percent)
        {
            _targetFuelPercent = Mathf.Clamp01(percent);
        }

        private void UpdateDisplay()
        {
            if (fuelSlider != null)
                fuelSlider.value = _currentFuelPercent;

            if (fuelFill != null)
                fuelFill.color = Color.Lerp(Color.red, Color.green, _currentFuelPercent);

            if (fuelText != null)
                fuelText.text = $"{Mathf.RoundToInt(_currentFuelPercent * 100)}%";
        }

        private void UpdateWarning()
        {
            bool shouldWarn = _currentFuelPercent <= warningThreshold;
            if (shouldWarn != _warningActive)
            {
                _warningActive = shouldWarn;
                if (lowFuelWarning != null)
                    lowFuelWarning.SetActive(_warningActive);
            }
        }

        public void SetWarningThreshold(float threshold)
        {
            warningThreshold = threshold;
        }

        public void ResetGauge()
        {
            _currentFuelPercent = 1f;
            _targetFuelPercent = 1f;
            UpdateDisplay();
            UpdateWarning();
        }
    }
}
