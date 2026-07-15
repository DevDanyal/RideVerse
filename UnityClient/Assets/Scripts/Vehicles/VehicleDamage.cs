using System;
using UnityEngine;

namespace RideVerse.Vehicles
{
    public class VehicleDamage : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private HondaCG125Config config;

        [Header("Damage Settings")]
        [SerializeField] private float collisionDamageMultiplier = 0.5f;
        [SerializeField] private Renderer bodyRenderer;

        private float currentHealth;
        private float previousSpeed;
        private Vector3 originalBodyPosition;
        private Color originalBodyColor;
        private bool isDestroyed;

        public float CurrentHealth => currentHealth;
        public float HealthPercentage => currentHealth / config.maxHealth;
        public bool IsDestroyed => isDestroyed;

        public event Action<float> OnHealthChanged;
        public event Action OnDestroyed;
        public event Action OnRepaired;

        private void Awake()
        {
            if (config == null)
                config = Resources.Load<HondaCG125Config>("HondaCG125Config");

            currentHealth = config.maxHealth;
        }

        private void Start()
        {
            if (bodyRenderer != null)
            {
                originalBodyColor = bodyRenderer.material.color;
                originalBodyPosition = bodyRenderer.transform.localPosition;
            }
        }

        private void FixedUpdate()
        {
            previousSpeed = GetComponent<Rigidbody>().linearVelocity.magnitude * 3.6f;
        }

        private void OnCollisionEnter(Collision collision)
        {
            if (isDestroyed) return;

            float impactForce = collision.relativeVelocity.magnitude;
            float damage = impactForce * collisionDamageMultiplier;

            if (damage > 1f)
            {
                TakeDamage(damage);
            }
        }

        public void TakeDamage(float damage)
        {
            if (isDestroyed) return;

            currentHealth -= damage;
            currentHealth = Mathf.Max(0f, currentHealth);

            OnHealthChanged?.Invoke(currentHealth);
            UpdateDamageVisuals();

            if (currentHealth <= 0f)
            {
                Destroy();
            }
        }

        public void TakeFallDamage(float fallSpeed)
        {
            if (fallSpeed > config.fallDamageThreshold)
            {
                float damage = (fallSpeed - config.fallDamageThreshold) * config.fallDamageMultiplier;
                TakeDamage(damage);
            }
        }

        private void Destroy()
        {
            isDestroyed = true;
            OnDestroyed?.Invoke();
            ApplyDestroyedVisuals();
        }

        public void Repair()
        {
            currentHealth = config.maxHealth;
            isDestroyed = false;
            OnRepaired?.Invoke();
            ResetVisuals();
        }

        public void Repair(float amount)
        {
            currentHealth = Mathf.Min(currentHealth + amount, config.maxHealth);
            OnHealthChanged?.Invoke(currentHealth);

            if (currentHealth > 0f)
            {
                isDestroyed = false;
                UpdateDamageVisuals();
            }
        }

        private void UpdateDamageVisuals()
        {
            if (bodyRenderer == null) return;

            float damagePercent = 1f - HealthPercentage;
            Color damagedColor = Color.Lerp(originalBodyColor, Color.black, damagePercent * 0.5f);
            bodyRenderer.material.color = damagedColor;

            float wobble = damagePercent * 0.02f;
            bodyRenderer.transform.localPosition = originalBodyPosition +
                new Vector3(
                    Mathf.Sin(Time.time * 10f) * wobble,
                    Mathf.Cos(Time.time * 8f) * wobble,
                    0f);
        }

        private void ApplyDestroyedVisuals()
        {
            if (bodyRenderer == null) return;

            bodyRenderer.material.color = new Color(0.1f, 0.1f, 0.1f);

            ParticleSystem smoke = GetComponentInChildren<ParticleSystem>();
            if (smoke != null)
            {
                var emission = smoke.emission;
                emission.rateOverTime = 10f;
                smoke.Play();
            }
        }

        private void ResetVisuals()
        {
            if (bodyRenderer != null)
            {
                bodyRenderer.material.color = originalBodyColor;
                bodyRenderer.transform.localPosition = originalBodyPosition;
            }
        }

        public void ResetDamage()
        {
            currentHealth = config.maxHealth;
            isDestroyed = false;
            ResetVisuals();
        }
    }
}
