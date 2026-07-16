using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class PoliceUnit : MonoBehaviour
    {
        [SerializeField] private PoliceConfig _config;

        private PoliceAIBrain _brain;
        private PoliceUnitData _data;
        private string _unitId;
        private bool _isInitialized;
        private float _health;
        private bool _isInVehicle;
        private bool _hasSiren;
        private bool _sirenActive;
        private bool _hasLightsOn;
        private PoliceUnitLOD _lodLevel;

        public string UnitId => _unitId;
        public PoliceUnitData Data => _data;
        public PoliceAIBrain Brain => _brain;
        public bool IsInitialized => _isInitialized;
        public float Health => _health;
        public bool IsInVehicle => _isInVehicle;
        public bool SirenActive => _sirenActive;
        public PoliceUnitLOD LODLevel => _lodLevel;

        public event Action<PoliceUnit, float> OnHealthChanged;
        public event Action<PoliceUnit> OnUnitDestroyed;

        private void Awake()
        {
            _brain = gameObject.AddComponent<PoliceAIBrain>();
        }

        public void Initialize(PoliceConfig config, PoliceUnitData data, Vector3 homePosition)
        {
            _config = config;
            _data = data;
            _unitId = data.UnitId;
            _health = data.MaxHealth;
            _isInVehicle = data.IsInVehicle;
            _hasSiren = data.UnitType == PoliceUnitType.PatrolCar ||
                        data.UnitType == PoliceUnitType.SUV ||
                        data.UnitType == PoliceUnitType.SWATVan;
            _lodLevel = PoliceUnitLOD.Full;

            transform.position = data.SpawnPosition;
            transform.rotation = Quaternion.Euler(0f, data.SpawnRotation, 0f);

            _brain.Initialize(config, data, homePosition);

            _isInitialized = true;
        }

        private void Update()
        {
            if (!_isInitialized) return;

            UpdateLOD();
            UpdateSiren();
        }

        private void UpdateLOD()
        {
            var player = GameObject.FindGameObjectWithTag("Player");
            if (player == null)
            {
                _lodLevel = PoliceUnitLOD.Full;
                return;
            }

            float distance = Vector3.Distance(transform.position, player.transform.position);

            if (distance <= _config.lodDistanceFull)
                _lodLevel = PoliceUnitLOD.Full;
            else if (distance <= _config.lodDistanceSimplified)
                _lodLevel = PoliceUnitLOD.Simplified;
            else
                _lodLevel = PoliceUnitLOD.Culled;
        }

        private void UpdateSiren()
        {
            if (!_hasSiren) return;

            if (_brain.CurrentState == PoliceState.PursuingVehicle ||
                _brain.CurrentState == PoliceState.RespondingToCall ||
                _brain.CurrentState == PoliceState.PursuingOnFoot)
            {
                _sirenActive = true;
            }
            else
            {
                _sirenActive = false;
            }
        }

        public void TakeDamage(float amount)
        {
            _health -= amount;
            _health = Mathf.Max(0f, _health);
            OnHealthChanged?.Invoke(this, amount);

            if (_health <= 0f)
            {
                OnUnitDestroyed?.Invoke(this);
                Destroy(gameObject);
            }
        }

        public void Heal(float amount)
        {
            _health = Mathf.Min(_health + amount, _data.MaxHealth);
        }

        public void EnterVehicle()
        {
            _isInVehicle = true;
            _data.IsInVehicle = true;
            _brain.SetInVehicle(true);
        }

        public void ExitVehicle()
        {
            _isInVehicle = false;
            _data.IsInVehicle = false;
            _brain.SetInVehicle(false);
        }

        public void SetSiren(bool active)
        {
            _sirenActive = active && _hasSiren;
        }

        public void SetLightsOn(bool on)
        {
            _hasLightsOn = on;
        }

        public float DistanceTo(Vector3 position)
        {
            return Vector3.Distance(transform.position, position);
        }

        public Vector3 DirectionTo(Vector3 position)
        {
            Vector3 dir = (position - transform.position).normalized;
            dir.y = 0f;
            return dir;
        }

        public bool IsWithinRange(Vector3 position, float range)
        {
            return Vector3.Distance(transform.position, position) <= range;
        }

        public void FacePosition(Vector3 position)
        {
            Vector3 dir = (position - transform.position).normalized;
            dir.y = 0f;
            if (dir.sqrMagnitude > 0.01f)
            {
                transform.rotation = Quaternion.LookRotation(dir);
            }
        }

        public bool IsAlive()
        {
            return _health > 0f;
        }
    }

    public enum PoliceUnitLOD
    {
        Full,
        Simplified,
        Culled
    }
}
