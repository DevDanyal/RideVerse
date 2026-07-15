using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace RideVerse.UI
{
    public class RPMGaugeUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private RectTransform rpmNeedle;
        [SerializeField] private TextMeshProUGUI rpmText;
        [SerializeField] private Image redlineZone;

        [Header("Settings")]
        [SerializeField] private float maxDisplayRPM = 10000f;
        [SerializeField] private float redlineStart = 8500f;
        [SerializeField] private float needleMinAngle = 135f;
        [SerializeField] private float needleMaxAngle = -135f;
        [SerializeField] private float needleSmoothing = 8f;
        [SerializeField] private bool showRPMText = true;

        private float currentRPM;
        private float targetRPM;
        private bool isRedlining;

        public bool IsRedlining => isRedlining;

        private void Start()
        {
            if (redlineZone != null)
            {
                float redlineNormalized = redlineStart / maxDisplayRPM;
                redlineZone.fillAmount = 1f - redlineNormalized;
            }
        }

        public void UpdateRPM(float rpm)
        {
            targetRPM = rpm;
            isRedlining = rpm >= redlineStart;
        }

        private void Update()
        {
            currentRPM = Mathf.Lerp(currentRPM, targetRPM, Time.deltaTime * needleSmoothing);
            UpdateNeedle();
            UpdateRPMText();
        }

        private void UpdateNeedle()
        {
            if (rpmNeedle == null) return;

            float normalizedRPM = Mathf.Clamp01(currentRPM / maxDisplayRPM);
            float angle = Mathf.Lerp(needleMinAngle, needleMaxAngle, normalizedRPM);
            rpmNeedle.localRotation = Quaternion.Euler(0f, 0f, angle);
        }

        private void UpdateRPMText()
        {
            if (!showRPMText || rpmText == null) return;

            rpmText.text = Mathf.RoundToInt(currentRPM / 100f).ToString("D2");

            if (isRedlining)
            {
                rpmText.color = Color.red;
            }
            else
            {
                rpmText.color = Color.white;
            }
        }

        public void SetMaxRPM(float maxRPM)
        {
            maxDisplayRPM = maxRPM;
        }

        public void SetRedline(float redline)
        {
            redlineStart = redline;
        }

        public void ResetGauge()
        {
            currentRPM = 0f;
            targetRPM = 0f;
            isRedlining = false;
            UpdateNeedle();
            UpdateRPMText();
        }
    }
}
