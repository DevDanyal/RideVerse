using UnityEngine;

namespace RideVerse.Vehicles
{
    public class VehicleEffects : MonoBehaviour
    {
        [Header("Particle Systems")]
        [SerializeField] private ParticleSystem exhaustSmoke;
        [SerializeField] private ParticleSystem dustTrail;
        [SerializeField] private ParticleSystem skidSmoke;
        [SerializeField] private ParticleSystem sparkEffect;

        [Header("References")]
        [SerializeField] private HondaCG125Config config;
        [SerializeField] private Rigidbody bikeRigidbody;
        [SerializeField] private Transform exhaustPoint;
        [SerializeField] private Transform rearWheelPoint;

        private float dustTimer;

        private void Awake()
        {
            if (bikeRigidbody == null)
                bikeRigidbody = GetComponent<Rigidbody>();
        }

        private void Update()
        {
            UpdateDustTrail();
        }

        public void UpdateExhaust(float rpm, float throttle)
        {
            if (exhaustSmoke == null) return;

            var emission = exhaustSmoke.emission;
            float normalizedRPM = rpm / config.maxRPM;
            float rate = normalizedRPM * config.exhaustSmokeRate * 100f;

            if (throttle > 0.1f)
            {
                emission.rateOverTime = rate * 1.5f;
                if (!exhaustSmoke.isPlaying) exhaustSmoke.Play();
            }
            else
            {
                emission.rateOverTime = rate;
                if (normalizedRPM < 0.2f && exhaustSmoke.isPlaying)
                {
                    exhaustSmoke.Stop();
                }
            }

            var sizeModule = exhaustSmoke.sizeOverLifetime;
            if (sizeModule.enabled)
            {
                sizeModule.size = new ParticleSystem.MinMaxCurve(normalizedRPM * 0.3f + 0.1f);
            }
        }

        private void UpdateDustTrail()
        {
            if (dustTrail == null || rearWheelPoint == null) return;

            float speed = bikeRigidbody.linearVelocity.magnitude;

            if (speed > config.dustParticleSpeed && IsGroundedAtRear())
            {
                if (!dustTrail.isPlaying) dustTrail.Play();

                var emission = dustTrail.emission;
                emission.rateOverTime = speed * 5f;
            }
            else
            {
                if (dustTrail.isPlaying) dustTrail.Stop();
            }
        }

        public void PlaySkidEffect()
        {
            if (skidSmoke != null && !skidSmoke.isPlaying)
            {
                skidSmoke.Play();
            }
        }

        public void StopSkidEffect()
        {
            if (skidSmoke != null && skidSmoke.isPlaying)
            {
                skidSmoke.Stop();
            }
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
            if (collision.relativeVelocity.magnitude > 2f)
            {
                PlaySparkEffect(collision.contacts[0].point);

                if (exhaustSmoke != null && !exhaustSmoke.isPlaying)
                {
                    var emission = exhaustSmoke.emission;
                    emission.SetBursts(new ParticleSystem.Burst[]
                    {
                        new ParticleSystem.Burst(0f, 20)
                    });
                    exhaustSmoke.Play();
                }
            }
        }

        private bool IsGroundedAtRear()
        {
            if (rearWheelPoint == null) return true;
            return Physics.Raycast(rearWheelPoint.position, Vector3.down, 0.3f);
        }

        public void SetEngineLoad(float load)
        {
            if (exhaustSmoke == null) return;

            var velocityModule = exhaustSmoke.velocityOverLifetime;
            velocityModule.speedModifier = load * 2f;
        }
    }
}
