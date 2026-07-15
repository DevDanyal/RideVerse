using UnityEngine;

namespace RideVerse.Vehicles
{
    public class MotorcycleAudioManager : MonoBehaviour
    {
        [Header("Audio Sources")]
        [SerializeField] private AudioSource engineAudioSource;
        [SerializeField] private AudioSource exhaustAudioSource;
        [SerializeField] private AudioSource hornAudioSource;

        [Header("Audio Clips")]
        [SerializeField] private AudioClip engineIdleClip;
        [SerializeField] private AudioClip engineRevClip;
        [SerializeField] private AudioClip engineStartClip;
        [SerializeField] private AudioClip engineStopClip;
        [SerializeField] private AudioClip hornClip;
        [SerializeField] private AudioClip brakeSquealClip;
        [SerializeField] private AudioClip[] gearShiftClips;
        [SerializeField] private AudioClip collisionClip;

        [Header("Settings")]
        [SerializeField] private float enginePitchMin = 0.6f;
        [SerializeField] private float enginePitchMax = 1.8f;
        [SerializeField] private float engineVolumeMin = 0.3f;
        [SerializeField] private float engineVolumeMax = 0.8f;
        [SerializeField] private float exhaustPitchMin = 0.7f;
        [SerializeField] private float exhaustPitchMax = 1.5f;

        [Header("References")]
        [SerializeField] private HondaCG125Config config;

        private float targetPitch;
        private float targetVolume;
        private bool isEngineRunning;
        private int lastGear;

        public bool IsEngineRunning => isEngineRunning;

        private void Awake()
        {
            if (config == null)
                config = Resources.Load<HondaCG125Config>("HondaCG125Config");
        }

        private void Start()
        {
            InitializeAudioSources();
            lastGear = 0;
        }

        private void InitializeAudioSources()
        {
            if (engineAudioSource != null)
            {
                engineAudioSource.clip = engineIdleClip;
                engineAudioSource.loop = true;
                engineAudioSource.playOnAwake = false;
                engineAudioSource.volume = 0f;
                engineAudioSource.pitch = enginePitchMin;
            }

            if (exhaustAudioSource != null)
            {
                exhaustAudioSource.loop = true;
                exhaustAudioSource.playOnAwake = false;
                exhaustAudioSource.volume = 0f;
            }
        }

        public void StartEngine()
        {
            if (isEngineRunning) return;

            isEngineRunning = true;

            if (engineStartClip != null && engineAudioSource != null)
            {
                engineAudioSource.PlayOneShot(engineStartClip);
            }

            if (engineAudioSource != null && engineIdleClip != null)
            {
                engineAudioSource.clip = engineIdleClip;
                engineAudioSource.Play();
            }

            if (exhaustAudioSource != null && engineIdleClip != null)
            {
                exhaustAudioSource.clip = engineIdleClip;
                exhaustAudioSource.Play();
            }
        }

        public void StopEngine()
        {
            if (!isEngineRunning) return;

            isEngineRunning = false;

            if (engineStopClip != null && engineAudioSource != null)
            {
                engineAudioSource.PlayOneShot(engineStopClip);
            }

            if (engineAudioSource != null)
            {
                engineAudioSource.Stop();
            }

            if (exhaustAudioSource != null)
            {
                exhaustAudioSource.Stop();
            }
        }

        public void UpdateEngineSound(float rpm, float throttle)
        {
            if (!isEngineRunning) return;

            float normalizedRPM = rpm / config.maxRPM;
            targetPitch = Mathf.Lerp(enginePitchMin, enginePitchMax, normalizedRPM);
            targetVolume = Mathf.Lerp(engineVolumeMin, engineVolumeMax, normalizedRPM * (0.5f + throttle * 0.5f));

            if (engineAudioSource != null)
            {
                engineAudioSource.pitch = Mathf.Lerp(engineAudioSource.pitch, targetPitch, Time.deltaTime * 10f);
                engineAudioSource.volume = Mathf.Lerp(engineAudioSource.volume, targetVolume, Time.deltaTime * 5f);
            }

            if (exhaustAudioSource != null)
            {
                float exhaustPitch = Mathf.Lerp(exhaustPitchMin, exhaustPitchMax, normalizedRPM);
                exhaustAudioSource.pitch = Mathf.Lerp(exhaustAudioSource.pitch, exhaustPitch, Time.deltaTime * 8f);
                exhaustAudioSource.volume = Mathf.Lerp(exhaustAudioSource.volume, targetVolume * 0.6f, Time.deltaTime * 5f);
            }
        }

        public void PlayGearShift(int gear)
        {
            if (gearShiftClips != null && gear > 0 && gear <= gearShiftClips.Length)
            {
                AudioClip clip = gearShiftClips[gear - 1];
                if (clip != null && engineAudioSource != null)
                {
                    engineAudioSource.PlayOneShot(clip);
                }
            }
            lastGear = gear;
        }

        public void PlayHorn()
        {
            if (hornClip != null && hornAudioSource != null)
            {
                hornAudioSource.PlayOneShot(hornClip);
            }
        }

        public void PlayBrakeSound()
        {
            if (brakeSquealClip != null && engineAudioSource != null)
            {
                engineAudioSource.PlayOneShot(brakeSquealClip, 0.5f);
            }
        }

        public void PlayCollisionSound(float impactForce)
        {
            if (collisionClip != null && engineAudioSource != null)
            {
                float volume = Mathf.Clamp01(impactForce / 10f);
                engineAudioSource.PlayOneShot(collisionClip, volume);
            }
        }

        public void SetEngineLoad(float load)
        {
            if (exhaustAudioSource != null)
            {
                exhaustAudioSource.pitch = Mathf.Lerp(exhaustPitchMin, exhaustPitchMax, load);
            }
        }

        public void UpdateDopplerEffect(float playerSpeed, float bikeSpeed)
        {
            if (engineAudioSource == null) return;

            float relativeSpeed = bikeSpeed - playerSpeed;
            float dopplerFactor = 1f + (relativeSpeed / 100f);
            dopplerFactor = Mathf.Clamp(dopplerFactor, 0.5f, 2f);

            engineAudioSource.pitch *= dopplerFactor;
        }
    }
}
