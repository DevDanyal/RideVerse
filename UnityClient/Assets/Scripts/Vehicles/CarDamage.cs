using System;
using UnityEngine;

namespace RideVerse.Vehicles
{
    public class CarDamage : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private CarConfig config;
        [SerializeField] private Rigidbody carRigidbody;
        [SerializeField] private Renderer[] bodyRenderers;

        [Header("Damage Settings")]
        [SerializeField] private float collisionDamageMultiplier = 0.3f;
        [SerializeField] private float rolloverDamageMultiplier = 0.5f;

        private float _currentHealth;
        private Vector3[] _originalPositions;
        private Color[] _originalColors;
        private bool _isDestroyed;

        public float CurrentHealth => _currentHealth;
        public float HealthPercentage => config != null ? _currentHealth / config.maxHealth : 1f;
        public bool IsDestroyed => _isDestroyed;

        public event Action<float> OnHealthChanged;
        public event Action OnDestroyed;
        public event Action OnRepaired;

        private void Awake()
        {
            _currentHealth = 100f;
            if (carRigidbody == null) carRigidbody = GetComponent<Rigidbody>();
        }

        private void Start()
        {
            if (config != null) _currentHealth = config.maxHealth;
            CacheOriginalVisuals();
        }

        private void CacheOriginalVisuals()
        {
            if (bodyRenderers == null || bodyRenderers.Length == 0) return;

            _originalPositions = new Vector3[bodyRenderers.Length];
            _originalColors = new Color[bodyRenderers.Length];

            for (int i = 0; i < bodyRenderers.Length; i++)
            {
                if (bodyRenderers[i] != null)
                {
                    _originalPositions[i] = bodyRenderers[i].transform.localPosition;
                    _originalColors[i] = bodyRenderers[i].material.color;
                }
            }
        }

        private void FixedUpdate()
        {
            if (_isDestroyed || config == null) return;
            CheckRollover();
        }

        private void OnCollisionEnter(Collision collision)
        {
            if (_isDestroyed) return;

            float impactForce = collision.relativeVelocity.magnitude;
            float damage = impactForce * collisionDamageMultiplier;

            if (damage > 1f)
                TakeDamage(damage);
        }

        private void CheckRollover()
        {
            if (carRigidbody == null || config == null) return;

            float upDot = Vector3.Dot(transform.up, Vector3.up);
            if (upDot < 0.5f)
            {
                float rolloverDamage = (1f - upDot) * rolloverDamageMultiplier * config.rolloverDamageAmount;
                TakeDamage(rolloverDamage);
            }
        }

        public void TakeDamage(float damage)
        {
            if (_isDestroyed) return;

            _currentHealth -= damage;
            _currentHealth = Mathf.Max(0f, _currentHealth);

            OnHealthChanged?.Invoke(_currentHealth);
            UpdateDamageVisuals();

            if (_currentHealth <= 0f)
                DestroyVehicle();
        }

        public void TakeWheelDamage(float amount)
        {
            TakeDamage(amount * 0.2f);
        }

        public void TakeEngineDamage(float amount)
        {
            TakeDamage(amount * 0.4f);
        }

        private void DestroyVehicle()
        {
            _isDestroyed = true;
            OnDestroyed?.Invoke();
            ApplyDestroyedVisuals();
        }

        public void Repair()
        {
            if (config == null) return;
            _currentHealth = config.maxHealth;
            _isDestroyed = false;
            OnRepaired?.Invoke();
            ResetVisuals();
        }

        public void Repair(float amount)
        {
            float maxHealth = config != null ? config.maxHealth : _currentHealth > 0f ? _currentHealth : 100f;
            _currentHealth = Mathf.Min(_currentHealth + amount, maxHealth);
            OnHealthChanged?.Invoke(_currentHealth);

            if (_currentHealth > 0f)
            {
                _isDestroyed = false;
                UpdateDamageVisuals();
            }
        }

        private void UpdateDamageVisuals()
        {
            if (bodyRenderers == null) return;

            float damagePercent = 1f - HealthPercentage;

            for (int i = 0; i < bodyRenderers.Length; i++)
            {
                if (bodyRenderers[i] == null) continue;

                Color damagedColor = Color.Lerp(_originalColors[i], Color.black, damagePercent * 0.5f);
                bodyRenderers[i].material.color = damagedColor;

                float wobble = damagePercent * 0.01f;
                bodyRenderers[i].transform.localPosition = _originalPositions[i] +
                    new Vector3(
                        Mathf.Sin(Time.time * 8f + i) * wobble,
                        Mathf.Cos(Time.time * 6f + i) * wobble,
                        0f);
            }
        }

        private void ApplyDestroyedVisuals()
        {
            if (bodyRenderers == null) return;

            for (int i = 0; i < bodyRenderers.Length; i++)
            {
                if (bodyRenderers[i] != null)
                    bodyRenderers[i].material.color = new Color(0.1f, 0.1f, 0.1f);
            }
        }

        private void ResetVisuals()
        {
            if (bodyRenderers == null || _originalColors == null) return;

            for (int i = 0; i < bodyRenderers.Length; i++)
            {
                if (bodyRenderers[i] != null)
                {
                    bodyRenderers[i].material.color = _originalColors[i];
                    bodyRenderers[i].transform.localPosition = _originalPositions[i];
                }
            }
        }

        public void ResetDamage()
        {
            _currentHealth = config != null ? config.maxHealth : 100f;
            _isDestroyed = false;
            ResetVisuals();
        }

        public void SetConfig(CarConfig newConfig)
        {
            config = newConfig;
            if (newConfig != null) _currentHealth = newConfig.maxHealth;
        }
    }
}
