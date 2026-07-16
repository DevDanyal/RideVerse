using System.Collections.Generic;
using UnityEngine;
using RideVerse.Traffic.Core;
using RideVerse.Traffic.Behaviors;

namespace RideVerse.Traffic.PublicTransport
{
    public enum TaxiState
    {
        Idle,
        Cruising,
        HeadingToPassenger,
        WithPassenger,
        HeadingToDestination,
        WaitingForPassenger
    }

    public class TaxiAI : MonoBehaviour
    {
        private TrafficConfig _config;
        private TrafficVehicle _vehicle;
        private TaxiState _taxiState;
        private Vector3 _cruiseDestination;
        private Vector3 _passengerPickup;
        private Vector3 _passengerDestination;
        private float _waitTimer;
        private float _cruiseTimer;

        public TaxiState State => _taxiState;
        public Vector3 PassengerDestination => _passengerDestination;

        public void Initialize(TrafficConfig config, TrafficVehicle vehicle)
        {
            _config = config;
            _vehicle = vehicle;
            _taxiState = TaxiState.Idle;
            SetNewCruiseDestination();
        }

        public void UpdateTaxi(float deltaTime)
        {
            if (_vehicle == null || !_vehicle.IsActive) return;

            switch (_taxiState)
            {
                case TaxiState.Idle:
                    UpdateIdle(deltaTime);
                    break;
                case TaxiState.Cruising:
                    UpdateCruising(deltaTime);
                    break;
                case TaxiState.HeadingToPassenger:
                    UpdateHeadingToPassenger(deltaTime);
                    break;
                case TaxiState.WithPassenger:
                    UpdateWithPassenger(deltaTime);
                    break;
                case TaxiState.HeadingToDestination:
                    UpdateHeadingToDestination(deltaTime);
                    break;
                case TaxiState.WaitingForPassenger:
                    UpdateWaiting(deltaTime);
                    break;
            }
        }

        private void UpdateIdle(float deltaTime)
        {
            _vehicle.Stop();
            _waitTimer += deltaTime;

            if (_waitTimer > 3f)
            {
                _waitTimer = 0f;
                TrySpawnPassenger();
                if (_taxiState == TaxiState.Idle)
                {
                    _taxiState = TaxiState.Cruising;
                    SetNewCruiseDestination();
                }
            }
        }

        private void UpdateCruising(float deltaTime)
        {
            _cruiseTimer += deltaTime;

            float distance = Vector3.Distance(_vehicle.Position, _cruiseDestination);

            if (distance < 5f || _cruiseTimer > 30f)
            {
                SetNewCruiseDestination();
                _cruiseTimer = 0f;
                TrySpawnPassenger();
                return;
            }

            MoveToward(_cruiseDestination, _config.taxiCruiseSpeed, deltaTime);
        }

        private void UpdateHeadingToPassenger(float deltaTime)
        {
            float distance = Vector3.Distance(_vehicle.Position, _passengerPickup);

            if (distance < 3f)
            {
                _vehicle.Stop();
                _taxiState = TaxiState.WaitingForPassenger;
                _waitTimer = 0f;
                return;
            }

            MoveToward(_passengerPickup, _config.taxiCruiseSpeed, deltaTime);
        }

        private void UpdateWithPassenger(float deltaTime)
        {
            _taxiState = TaxiState.HeadingToDestination;
        }

        private void UpdateHeadingToDestination(float deltaTime)
        {
            float distance = Vector3.Distance(_vehicle.Position, _passengerDestination);

            if (distance < 5f)
            {
                _vehicle.Stop();
                _taxiState = TaxiState.Idle;
                _waitTimer = 0f;
                return;
            }

            MoveToward(_passengerDestination, _config.taxiCruiseSpeed, deltaTime);
        }

        private void UpdateWaiting(float deltaTime)
        {
            _vehicle.Stop();
            _waitTimer += deltaTime;

            if (_waitTimer > 10f)
            {
                _taxiState = TaxiState.Cruising;
                _waitTimer = 0f;
                SetNewCruiseDestination();
            }
        }

        private void MoveToward(Vector3 target, float speed, float deltaTime)
        {
            Vector3 direction = (target - _vehicle.Position).normalized;
            direction.y = 0f;

            float distance = Vector3.Distance(_vehicle.Position, target);
            float adjustedSpeed = Mathf.Min(speed, distance * 2f);

            _vehicle.SetTargetSpeed(adjustedSpeed);
            _vehicle.ApplyMovement(direction, _vehicle.CurrentSpeed, deltaTime);
        }

        public void SetPassengerDestination(Vector3 pickup, Vector3 destination)
        {
            _passengerPickup = pickup;
            _passengerDestination = destination;
            _taxiState = TaxiState.HeadingToPassenger;
        }

        public void PickupPassenger()
        {
            _taxiState = TaxiState.WithPassenger;
        }

        private void SetNewCruiseDestination()
        {
            float angle = Random.Range(0f, 360f) * Mathf.Deg2Rad;
            float distance = Random.Range(20f, _config.taxiSearchRadius);
            _cruiseDestination = _vehicle.Position + new Vector3(Mathf.Cos(angle) * distance, 0f, Mathf.Sin(angle) * distance);
            _cruiseDestination.y = 0f;
        }

        private void TrySpawnPassenger()
        {
            if (Random.value < 0.1f)
            {
                Vector3 pickup = _vehicle.Position + new Vector3(
                    Random.Range(-30f, 30f), 0f, Random.Range(-30f, 30f));
                Vector3 destination = pickup + new Vector3(
                    Random.Range(-50f, 50f), 0f, Random.Range(-50f, 50f));

                SetPassengerDestination(pickup, destination);
            }
        }

        public void CancelTrip()
        {
            _taxiState = TaxiState.Cruising;
            SetNewCruiseDestination();
        }
    }
}
