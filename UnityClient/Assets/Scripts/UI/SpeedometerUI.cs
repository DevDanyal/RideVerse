using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace RideVerse.UI
{
    public class SpeedometerUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private RectTransform speedNeedle;
        [SerializeField] private TextMeshProUGUI speedText;
        [SerializeField] private TextMeshProUGUI unitText;

        [Header("Settings")]
        [SerializeField] private float maxDisplaySpeed = 140f;
        [SerializeField] private float needleMinAngle = 135f;
        [SerializeField] private float needleMaxAngle = -135f;
        [SerializeField] private float needleSmoothing = 5f;
        [SerializeField] private bool showDigitalSpeed = true;
        [SerializeField] private bool useMPH = false;

        private float currentSpeed;
        private float targetSpeed;

        private void Start()
        {
            if (unitText != null)
            {
                unitText.text = useMPH ? "MPH" : "KM/H";
            }
        }

        public void UpdateSpeed(float speedKmh)
        {
            targetSpeed = useMPH ? speedKmh * 0.621371f : speedKmh;
        }

        private void Update()
        {
            currentSpeed = Mathf.Lerp(currentSpeed, targetSpeed, Time.deltaTime * needleSmoothing);
            UpdateNeedle();
            UpdateDigitalDisplay();
        }

        private void UpdateNeedle()
        {
            if (speedNeedle == null) return;

            float normalizedSpeed = Mathf.Clamp01(currentSpeed / maxDisplaySpeed);
            float angle = Mathf.Lerp(needleMinAngle, needleMaxAngle, normalizedSpeed);
            speedNeedle.localRotation = Quaternion.Euler(0f, 0f, angle);
        }

        private void UpdateDigitalDisplay()
        {
            if (!showDigitalSpeed || speedText == null) return;
            speedText.text = Mathf.RoundToInt(currentSpeed).ToString();
        }

        public void SetMaxSpeed(float maxSpeed)
        {
            maxDisplaySpeed = maxSpeed;
        }

        public void ResetGauge()
        {
            currentSpeed = 0f;
            targetSpeed = 0f;
            UpdateNeedle();
            UpdateDigitalDisplay();
        }
    }
}
