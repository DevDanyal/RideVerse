using UnityEngine;

namespace RideVerse.Vehicles
{
    public class CarAudioManager : MonoBehaviour
    {
        [Header("Audio Sources")]
        [SerializeField] private AudioSource engineAudioSource;
        [SerializeField] private AudioSource exhaustAudioSource;
        [SerializeField] private AudioSource hornAudioSource;
        [SerializeField] private AudioSource tireScreechSource;
        [SerializeField] private AudioSource windAudioSource;

        [Header("Engine Audio")]
        [SerializeField] private AudioClip engineIdleClip;
        [SerializeField] private AudioClip engineRevClip;
        [SerializeField] private AudioClip engineStartClip;
        [SerializeField] private AudioClip engineStopClip;

        [Header("Other Audio")]
        [SerializeField] private AudioClip hornClip;
        [SerializeField] private AudioClip brakeSquealClip;
        [SerializeField] private AudioClip[] gearShiftClips;
        [SerializeField] private AudioClip collisionClip;
        [SerializeField] private AudioClip[] tireScreechClips;
        [SerializeField] private AudioClip turboWhistleClip;

        [Header("Settings")]
        [SerializeField] private float enginePitchMin = 0.5f;
        [SerializeField] private float enginePitchMax = 2.0f;
        [SerializeField] private float engineVolumeMin = 0.2f;
        [SerializeField] private float engineVolumeMax = 0.9f;

        private bool _isEngineRunning;
        private float _targetPitch;
        private float _targetVolume;

        public bool IsEngineRunning => _isEngineRunning;

        public void StartEngine()
        {
            if (_isEngineRunning) return;
            _isEngineRunning = true;

            if (engineStartClip != null && engineAudioSource != null)
                engineAudioSource.PlayOneShot(engineStartClip);

            if (engineAudioSource != null && engineIdleClip != null)
            {
                engineAudioSource.clip = engineIdleClip;
                engineAudioSource.loop = true;
                engineAudioSource.Play();
            }

            if (exhaustAudioSource != null && engineIdleClip != null)
            {
                exhaustAudioSource.clip = engineIdleClip;
                exhaustAudioSource.loop = true;
                exhaustAudioSource.Play();
            }
        }

        public void StopEngine()
        {
            if (!_isEngineRunning) return;
            _isEngineRunning = false;

            if (engineStopClip != null && engineAudioSource != null)
                engineAudioSource.PlayOneShot(engineStopClip);

            engineAudioSource?.Stop();
            exhaustAudioSource?.Stop();
        }

        public void UpdateEngineSound(float rpm, float throttle)
        {
            if (!_isEngineRunning) return;

            float normalizedRPM = rpm / 8000f;
            _targetPitch = Mathf.Lerp(enginePitchMin, enginePitchMax, normalizedRPM);
            _targetVolume = Mathf.Lerp(engineVolumeMin, engineVolumeMax, normalizedRPM * (0.5f + Mathf.Abs(throttle) * 0.5f));

            if (engineAudioSource != null)
            {
                engineAudioSource.pitch = Mathf.Lerp(engineAudioSource.pitch, _targetPitch, Time.deltaTime * 10f);
                engineAudioSource.volume = Mathf.Lerp(engineAudioSource.volume, _targetVolume, Time.deltaTime * 5f);
            }

            if (exhaustAudioSource != null)
            {
                exhaustAudioSource.pitch = Mathf.Lerp(exhaustAudioSource.pitch, _targetPitch * 0.9f, Time.deltaTime * 8f);
                exhaustAudioSource.volume = Mathf.Lerp(exhaustAudioSource.volume, _targetVolume * 0.6f, Time.deltaTime * 5f);
            }
        }

        public void PlayGearShift(int gear)
        {
            if (gearShiftClips != null && gear > 0 && gear <= gearShiftClips.Length)
            {
                AudioClip clip = gearShiftClips[gear - 1];
                if (clip != null && engineAudioSource != null)
                    engineAudioSource.PlayOneShot(clip);
            }
        }

        public void PlayHorn()
        {
            if (hornClip != null && hornAudioSource != null)
                hornAudioSource.PlayOneShot(hornClip);
        }

        public void PlayBrakeSqueal()
        {
            if (brakeSquealClip != null && tireScreechSource != null)
                tireScreechSource.PlayOneShot(brakeSquealClip, 0.6f);
        }

        public void PlayTireScreech(float intensity = 1f)
        {
            if (tireScreechClips != null && tireScreechClips.Length > 0 && tireScreechSource != null)
            {
                int index = Random.Range(0, tireScreechClips.Length);
                if (tireScreechClips[index] != null)
                    tireScreechSource.PlayOneShot(tireScreechClips[index], Mathf.Clamp01(intensity));
            }
        }

        public void PlayCollision(float force)
        {
            if (collisionClip != null && engineAudioSource != null)
                engineAudioSource.PlayOneShot(collisionClip, Mathf.Clamp01(force / 15f));
        }

        public void UpdateWindNoise(float speedKmh)
        {
            if (windAudioSource == null) return;

            float normalizedSpeed = Mathf.Clamp01(speedKmh / 200f);
            windAudioSource.volume = Mathf.Lerp(0f, 0.4f, normalizedSpeed);
            windAudioSource.pitch = Mathf.Lerp(0.8f, 1.5f, normalizedSpeed);
        }

        public void StopAllSounds()
        {
            engineAudioSource?.Stop();
            exhaustAudioSource?.Stop();
            hornAudioSource?.Stop();
            tireScreechSource?.Stop();
            windAudioSource?.Stop();
        }
    }
}
