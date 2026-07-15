using UnityEngine;

namespace RideVerse.Vehicles
{
    public class CarEffects : MonoBehaviour
    {
        [Header("Particle Systems")]
        [SerializeField] private ParticleSystem exhaustSmoke;
        [SerializeField] private ParticleSystem tireSmoke;
        [SerializeField] private ParticleSystem burnoutSmoke;
        [SerializeField] private ParticleSystem dustTrail;
        [SerializeField] private ParticleSystem sparkEffect;

        [Header("References")]
        [SerializeField] private CarConfig config;
        [SerializeField] private Rigidbody carRigidbody;
        [SerializeField] private Transform[] wheelTransforms;

        private void Awake()
        {
            if (carRigidbody == null) carRigidbody = GetComponent<Rigidbody>();
        }

        private void Update()
        {
            UpdateDustTrail();
        }

        public void UpdateExhaust(float rpm, float throttle)
        {
            if (exhaustSmoke == null || config == null) return;

            var emission = exhaustSmoke.emission;
            float normalizedRPM = rpm / config.maxRPM;
            float rate = normalizedRPM * config.exhaustSmokeRate * 100f;

            if (Mathf.Abs(throttle) > 0.1f)
            {
                emission.rateOverTime = rate * 1.5f;
                if (!exhaustSmoke.isPlaying) exhaustSmoke.Play();
            }
            else
            {
                emission.rateOverTime = rate;
                if (normalizedRPM < 0.15f && exhaustSmoke.isPlaying)
                    exhaustSmoke.Stop();
            }
        }

        public void PlaySkidEffect()
        {
            if (tireSmoke != null && !tireSmoke.isPlaying)
                tireSmoke.Play();
        }

        public void StopSkidEffect()
        {
            if (tireSmoke != null && tireSmoke.isPlaying)
                tireSmoke.Stop();
        }

        public void PlayBurnoutSmoke()
        {
            if (burnoutSmoke != null && !burnoutSmoke.isPlaying)
                burnoutSmoke.Play();
        }

        public void StopBurnoutSmoke()
        {
            if (burnoutSmoke != null && burnoutSmoke.isPlaying)
                burnoutSmoke.Stop();
        }

        public void PlaySparkEffect(Vector3 contactPoint)
        {
            if (sparkEffect != null)
            {
                sparkEffect.transform.position = contactPoint;
                sparkEffect.Play();
            }
        }

        public void PlayCollisionEffect(Collision collision)
        {
            if (collision.relativeVelocity.magnitude > 3f)
                PlaySparkEffect(collision.contacts[0].point);
        }

        private void UpdateDustTrail()
        {
            if (dustTrail == null || carRigidbody == null) return;

            float speed = carRigidbody.linearVelocity.magnitude;
            if (speed > (config != null ? config.dustParticleSpeed : 5f))
            {
                if (!dustTrail.isPlaying) dustTrail.Play();
                var emission = dustTrail.emission;
                emission.rateOverTime = speed * 3f;
            }
            else
            {
                if (dustTrail.isPlaying) dustTrail.Stop();
            }
        }

        public void SetExhaustIntensity(float intensity)
        {
            if (exhaustSmoke == null) return;
            var velocityModule = exhaustSmoke.velocityOverLifetime;
            velocityModule.speedModifier = intensity * 2f;
        }
    }
}
