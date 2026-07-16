using UnityEngine;
using RideVerse.Traffic.Core;
using RideVerse.Traffic.Behaviors;

namespace RideVerse.Traffic.Conditions
{
    public class WeatherDrivingEffects : MonoBehaviour
    {
        private TrafficConfig _config;
        private WeatherCondition _currentWeather;
        private float _weatherTransitionProgress;
        private WeatherCondition _previousWeather;
        private float _transitionDuration = 5f;

        public WeatherCondition CurrentWeather => _currentWeather;
        public float TransitionProgress => _weatherTransitionProgress;

        public void Initialize(TrafficConfig config)
        {
            _config = config;
            _currentWeather = WeatherCondition.Clear;
            _previousWeather = WeatherCondition.Clear;
        }

        public void SetWeather(WeatherCondition weather)
        {
            if (weather == _currentWeather) return;

            _previousWeather = _currentWeather;
            _currentWeather = weather;
            _weatherTransitionProgress = 0f;
        }

        public void UpdateWeather(float deltaTime)
        {
            if (_weatherTransitionProgress < 1f)
            {
                _weatherTransitionProgress += deltaTime / _transitionDuration;
                _weatherTransitionProgress = Mathf.Clamp01(_weatherTransitionProgress);
            }
        }

        public float GetSpeedMultiplier()
        {
            float currentMult = GetMultiplierForCondition(_currentWeather);
            float prevMult = GetMultiplierForCondition(_previousWeather);

            if (_weatherTransitionProgress >= 1f)
                return currentMult;

            return Mathf.Lerp(prevMult, currentMult, _weatherTransitionProgress);
        }

        public float GetBrakeMultiplier()
        {
            float currentMult = GetBrakeForCondition(_currentWeather);
            float prevMult = GetBrakeForCondition(_previousWeather);

            if (_weatherTransitionProgress >= 1f)
                return currentMult;

            return Mathf.Lerp(prevMult, currentMult, _weatherTransitionProgress);
        }

        public float GetVisibilityRange()
        {
            switch (_currentWeather)
            {
                case WeatherCondition.Fog:
                    return _config.fogVisibilityRange;
                case WeatherCondition.Storm:
                    return _config.fogVisibilityRange * 1.5f;
                case WeatherCondition.HeavyRain:
                    return _config.fogVisibilityRange * 2f;
                case WeatherCondition.Rain:
                    return 100f;
                default:
                    return float.MaxValue;
            }
        }

        public bool ShouldUseWipers()
        {
            return _currentWeather == WeatherCondition.Rain ||
                   _currentWeather == WeatherCondition.HeavyRain ||
                   _currentWeather == WeatherCondition.Storm;
        }

        public float GetWiperSpeed()
        {
            switch (_currentWeather)
            {
                case WeatherCondition.Rain: return 1f;
                case WeatherCondition.HeavyRain: return 2f;
                case WeatherCondition.Storm: return 3f;
                default: return 0f;
            }
        }

        public bool ShouldReduceSpeed(TrafficVehicle vehicle)
        {
            float mult = GetSpeedMultiplier();
            return vehicle.CurrentSpeed > vehicle.MaxSpeed * mult;
        }

        public float GetAdjustedMaxSpeed(TrafficVehicle vehicle)
        {
            return vehicle.MaxSpeed * GetSpeedMultiplier();
        }

        public float GetBrakeDistance(float speed)
        {
            float deceleration = _config.normalDeceleration / GetBrakeMultiplier();
            return (speed * speed) / (2f * Mathf.Max(0.1f, deceleration));
        }

        public float GetTractionLossChance()
        {
            switch (_currentWeather)
            {
                case WeatherCondition.Rain: return 0.15f;
                case WeatherCondition.HeavyRain: return 0.3f;
                case WeatherCondition.Storm: return 0.45f;
                case WeatherCondition.Snow: return 0.5f;
                default: return 0f;
            }
        }

        public bool ShouldActivateFogLights()
        {
            return _currentWeather == WeatherCondition.Fog ||
                   (_currentWeather == WeatherCondition.Storm && GetVisibilityRange() < 60f);
        }

        public float GetRainIntensity()
        {
            switch (_currentWeather)
            {
                case WeatherCondition.Rain: return 0.3f;
                case WeatherCondition.HeavyRain: return 0.7f;
                case WeatherCondition.Storm: return 1f;
                default: return 0f;
            }
        }

        private float GetMultiplierForCondition(WeatherCondition condition)
        {
            switch (condition)
            {
                case WeatherCondition.Rain: return _config.rainSpeedMultiplier;
                case WeatherCondition.HeavyRain: return _config.heavyRainSpeedMultiplier;
                case WeatherCondition.Fog: return _config.fogSpeedMultiplier;
                case WeatherCondition.Storm: return _config.stormSpeedMultiplier;
                case WeatherCondition.Snow: return _config.snowSpeedMultiplier;
                default: return 1f;
            }
        }

        private float GetBrakeForCondition(WeatherCondition condition)
        {
            switch (condition)
            {
                case WeatherCondition.Rain: return _config.rainBrakeMultiplier;
                case WeatherCondition.HeavyRain: return _config.rainBrakeMultiplier * 1.3f;
                case WeatherCondition.Storm: return _config.rainBrakeMultiplier * 1.6f;
                case WeatherCondition.Snow: return _config.rainBrakeMultiplier * 1.5f;
                default: return 1f;
            }
        }
    }
}
