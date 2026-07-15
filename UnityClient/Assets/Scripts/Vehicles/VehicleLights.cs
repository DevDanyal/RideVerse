using UnityEngine;

namespace RideVerse.Vehicles
{
    public class VehicleLights : MonoBehaviour
    {
        [Header("Light References")]
        [SerializeField] private Light headlight;
        [SerializeField] private Light brakeLightLeft;
        [SerializeField] private Light brakeLightRight;
        [SerializeField] private Light indicatorLeft;
        [SerializeField] private Light indicatorRight;

        [Header("Settings")]
        [SerializeField] private float headlightIntensity = 2f;
        [SerializeField] private float brakeLightIntensity = 4f;
        [SerializeField] private float indicatorBlinkRate = 1.5f;

        private bool headlightOn;
        private bool brakeActive;
        private bool leftIndicatorOn;
        private bool rightIndicatorOn;
        private bool hazardLightsOn;
        private float indicatorTimer;

        public bool HeadlightOn => headlightOn;
        public bool BrakeActive => brakeActive;
        public bool LeftIndicatorOn => leftIndicatorOn;
        public bool RightIndicatorOn => rightIndicatorOn;

        private void Update()
        {
            UpdateIndicatorBlink();
            UpdateBrakeLight();
        }

        public void ToggleHeadlight()
        {
            headlightOn = !headlightOn;
            if (headlight != null)
            {
                headlight.enabled = headlightOn;
                headlight.intensity = headlightOn ? headlightIntensity : 0f;
            }
        }

        public void SetBrake(bool active)
        {
            brakeActive = active;
        }

        private void UpdateBrakeLight()
        {
            float intensity = brakeActive ? brakeLightIntensity : 0f;
            if (brakeLightLeft != null)
            {
                brakeLightLeft.intensity = intensity;
                brakeLightLeft.enabled = brakeActive;
            }
            if (brakeLightRight != null)
            {
                brakeLightRight.intensity = intensity;
                brakeLightRight.enabled = brakeActive;
            }
        }

        public void ToggleLeftIndicator()
        {
            if (hazardLightsOn) return;
            leftIndicatorOn = !leftIndicatorOn;
            rightIndicatorOn = false;
        }

        public void ToggleRightIndicator()
        {
            if (hazardLightsOn) return;
            rightIndicatorOn = !rightIndicatorOn;
            leftIndicatorOn = false;
        }

        public void ToggleHazardLights()
        {
            hazardLightsOn = !hazardLightsOn;
            leftIndicatorOn = hazardLightsOn;
            rightIndicatorOn = hazardLightsOn;
        }

        public void CancelIndicators()
        {
            leftIndicatorOn = false;
            rightIndicatorOn = false;
            hazardLightsOn = false;
        }

        private void UpdateIndicatorBlink()
        {
            indicatorTimer += Time.deltaTime * indicatorBlinkRate;
            bool blinkState = Mathf.Sin(indicatorTimer * Mathf.PI * 2f) > 0f;

            if (indicatorLeft != null)
            {
                indicatorLeft.enabled = leftIndicatorOn && blinkState;
            }
            if (indicatorRight != null)
            {
                indicatorRight.enabled = rightIndicatorOn && blinkState;
            }
        }

        public void SetAllLights(bool isNight)
        {
            if (isNight)
            {
                if (!headlightOn) ToggleHeadlight();
            }
            else
            {
                if (headlightOn) ToggleHeadlight();
            }
        }
    }
}
