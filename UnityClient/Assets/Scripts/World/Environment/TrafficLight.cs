using System;
using UnityEngine;

namespace RideVerse.World.Environment
{
    public enum TrafficLightState
    {
        Red,
        Yellow,
        Green
    }

    public class TrafficLight : MonoBehaviour
    {
        [SerializeField] private float _greenDuration = 10f;
        [SerializeField] private float _yellowDuration = 3f;
        [SerializeField] private float _redDuration = 10f;

        [SerializeField] private Renderer _redRenderer;
        [SerializeField] private Renderer _yellowRenderer;
        [SerializeField] private Renderer _greenRenderer;

        private TrafficLightState _currentState = TrafficLightState.Red;
        private float _timer;
        private bool _isActive = true;

        public TrafficLightState CurrentState => _currentState;
        public bool IsActive => _isActive;
        public event Action<TrafficLightState> OnStateChanged;

        private void Start()
        {
            _timer = UnityEngine.Random.Range(0f, _greenDuration + _yellowDuration + _redDuration);
            UpdateVisual();
        }

        private void Update()
        {
            if (!_isActive) return;

            _timer += Time.deltaTime;
            float cycleDuration = _greenDuration + _yellowDuration + _redDuration;
            float cycleTime = _timer % cycleDuration;

            TrafficLightState newState;

            if (cycleTime < _greenDuration)
            {
                newState = TrafficLightState.Green;
            }
            else if (cycleTime < _greenDuration + _yellowDuration)
            {
                newState = TrafficLightState.Yellow;
            }
            else
            {
                newState = TrafficLightState.Red;
            }

            if (newState != _currentState)
            {
                _currentState = newState;
                UpdateVisual();
                OnStateChanged?.Invoke(_currentState);
            }
        }

        private void UpdateVisual()
        {
            if (_redRenderer != null)
                _redRenderer.material.SetColor("_EmissionColor", _currentState == TrafficLightState.Red ? Color.red * 2f : Color.black);

            if (_yellowRenderer != null)
                _yellowRenderer.material.SetColor("_EmissionColor", _currentState == TrafficLightState.Yellow ? Color.yellow * 2f : Color.black);

            if (_greenRenderer != null)
                _greenRenderer.material.SetColor("_EmissionColor", _currentState == TrafficLightState.Green ? Color.green * 2f : Color.black);
        }

        public void SetActive(bool active)
        {
            _isActive = active;
        }

        public void SetDurations(float green, float yellow, float red)
        {
            _greenDuration = green;
            _yellowDuration = yellow;
            _redDuration = red;
        }

        public bool IsGreen => _currentState == TrafficLightState.Green;
        public bool IsRed => _currentState == TrafficLightState.Red;
        public bool IsYellow => _currentState == TrafficLightState.Yellow;
    }
}
