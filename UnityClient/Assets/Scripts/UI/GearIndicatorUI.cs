using UnityEngine;
using TMPro;

namespace RideVerse.UI
{
    public class GearIndicatorUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TextMeshProUGUI gearText;
        [SerializeField] private TextMeshProUGUI gearNameText;

        [Header("Settings")]
        [SerializeField] private float gearChangeSmoothing = 5f;

        private int _displayedGear;
        private int _targetGear;

        public void UpdateGear(int gear, bool isReversing = false)
        {
            _targetGear = gear;
        }

        private void Update()
        {
            if (_displayedGear != _targetGear)
            {
                _displayedGear = Mathf.RoundToInt(Mathf.Lerp(_displayedGear, _targetGear, Time.deltaTime * gearChangeSmoothing));
                if (Mathf.Abs(_displayedGear - _targetGear) < 0.1f) _displayedGear = _targetGear;
                UpdateDisplay();
            }
        }

        private void UpdateDisplay()
        {
            if (gearText != null)
            {
                if (_displayedGear == 0)
                    gearText.text = "N";
                else if (_displayedGear < 0)
                    gearText.text = "R";
                else
                    gearText.text = _displayedGear.ToString();
            }

            if (gearNameText != null)
            {
                if (_displayedGear == 0)
                    gearNameText.text = "Neutral";
                else if (_displayedGear < 0)
                    gearNameText.text = "Reverse";
                else
                    gearNameText.text = $"Gear {_displayedGear}";
            }
        }

        public void ResetDisplay()
        {
            _displayedGear = 0;
            _targetGear = 0;
            UpdateDisplay();
        }
    }
}
