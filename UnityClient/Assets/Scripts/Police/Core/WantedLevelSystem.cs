using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Police.Core
{
    public class WantedLevelSystem
    {
        private readonly PoliceConfig _config;
        private float _currentWantedLevel;
        private float _decayTimer;
        private float _lastIncreaseTime;
        private readonly Dictionary<string, float> _playerCrimeScores;
        private readonly Dictionary<string, float> _playerDecayTimers;

        public float CurrentWantedLevel => _currentWantedLevel;
        public int CurrentStars => Mathf.FloorToInt(_currentWantedLevel);
        public bool IsWanted => _currentWantedLevel > 0f;

        public event Action<int> OnWantedLevelChanged;
        public event Action<int, int> OnStarsChanged;

        public WantedLevelSystem(PoliceConfig config)
        {
            _config = config;
            _currentWantedLevel = 0f;
            _decayTimer = 0f;
            _lastIncreaseTime = 0f;
            _playerCrimeScores = new Dictionary<string, float>();
            _playerDecayTimers = new Dictionary<string, float>();
        }

        public void AddCrime(string playerId, CrimeRecord crime)
        {
            if (!_playerCrimeScores.ContainsKey(playerId))
            {
                _playerCrimeScores[playerId] = 0f;
                _playerDecayTimers[playerId] = 0f;
            }

            float contribution = crime.GetWantedLevelContribution();
            _playerCrimeScores[playerId] += contribution;

            int oldStars = GetPlayerStars(playerId);
            int newStars = CalculateStars(_playerCrimeScores[playerId]);

            if (newStars != oldStars)
            {
                OnStarsChanged?.Invoke(oldStars, newStars);
            }

            if (playerId == GetMainPlayerId())
            {
                IncreaseWantedLevel(contribution);
            }
        }

        private void IncreaseWantedLevel(float amount)
        {
            if (Time.time - _lastIncreaseTime < _config.wantedLevelIncreaseCooldown)
                return;

            float oldLevel = _currentWantedLevel;
            _currentWantedLevel = Mathf.Min(_currentWantedLevel + amount, _config.maxWantedLevel);
            _decayTimer = 0f;
            _lastIncreaseTime = Time.time;

            int oldStars = Mathf.FloorToInt(oldLevel);
            int newStars = Mathf.FloorToInt(_currentWantedLevel);

            if (newStars != oldStars)
            {
                OnStarsChanged?.Invoke(oldStars, newStars);
                OnWantedLevelChanged?.Invoke(newStars);
            }
        }

        public void Update(float deltaTime)
        {
            UpdateDecay(deltaTime);
            UpdatePlayerDecay(deltaTime);
        }

        private void UpdateDecay(float deltaTime)
        {
            if (_currentWantedLevel <= 0f) return;

            _decayTimer += deltaTime;
            if (_decayTimer >= _config.wantedLevelDecayTime)
            {
                float oldLevel = _currentWantedLevel;
                _currentWantedLevel -= _config.wantedLevelDecayMultiplier * deltaTime;

                if (_currentWantedLevel < 0f)
                    _currentWantedLevel = 0f;

                int oldStars = Mathf.FloorToInt(oldLevel);
                int newStars = Mathf.FloorToInt(_currentWantedLevel);

                if (newStars != oldStars)
                {
                    OnStarsChanged?.Invoke(oldStars, newStars);
                    OnWantedLevelChanged?.Invoke(newStars);
                }
            }
        }

        private void UpdatePlayerDecay(float deltaTime)
        {
            List<string> toRemove = new List<string>();

            foreach (var kvp in _playerCrimeScores)
            {
                _playerDecayTimers[kvp.Key] += deltaTime;

                if (_playerDecayTimers[kvp.Key] >= _config.wantedLevelDecayTime)
                {
                    _playerCrimeScores[kvp.Key] -= _config.wantedLevelDecayMultiplier * deltaTime * 5f;
                    if (_playerCrimeScores[kvp.Key] <= 0f)
                    {
                        toRemove.Add(kvp.Key);
                    }
                }
            }

            foreach (var id in toRemove)
            {
                _playerCrimeScores.Remove(id);
                _playerDecayTimers.Remove(id);
            }
        }

        public void ClearWantedLevel(string playerId)
        {
            _playerCrimeScores.Remove(playerId);
            _playerDecayTimers.Remove(playerId);

            if (playerId == GetMainPlayerId())
            {
                int oldStars = CurrentStars;
                _currentWantedLevel = 0f;
                _decayTimer = 0f;

                if (oldStars != 0)
                {
                    OnStarsChanged?.Invoke(oldStars, 0);
                    OnWantedLevelChanged?.Invoke(0);
                }
            }
        }

        public void SetWantedLevel(string playerId, int stars)
        {
            if (playerId == GetMainPlayerId())
            {
                int oldStars = CurrentStars;
                _currentWantedLevel = Mathf.Clamp(stars, 0, _config.maxWantedLevel);

                if (_currentWantedLevel != oldStars)
                {
                    OnStarsChanged?.Invoke(oldStars, Mathf.FloorToInt(_currentWantedLevel));
                    OnWantedLevelChanged?.Invoke(Mathf.FloorToInt(_currentWantedLevel));
                }
            }
        }

        public int GetPlayerStars(string playerId)
        {
            if (_playerCrimeScores.TryGetValue(playerId, out float score))
            {
                return CalculateStars(score);
            }
            return 0;
        }

        private int CalculateStars(float crimeScore)
        {
            for (int i = _config.wantedLevelCrimeThresholds.Length - 1; i >= 0; i--)
            {
                if (crimeScore >= _config.wantedLevelCrimeThresholds[i])
                {
                    return Mathf.Min(i + 1, _config.maxWantedLevel);
                }
            }
            return 0;
        }

        public float GetCrimeScore(string playerId)
        {
            _playerCrimeScores.TryGetValue(playerId, out float score);
            return score;
        }

        public DispatchPriority GetDispatchPriority()
        {
            int stars = CurrentStars;
            return stars switch
            {
                0 => DispatchPriority.Low,
                1 => DispatchPriority.Low,
                2 => DispatchPriority.Medium,
                3 => DispatchPriority.High,
                4 => DispatchPriority.High,
                5 => DispatchPriority.Critical,
                6 => DispatchPriority.Critical,
                _ => DispatchPriority.Low
            };
        }

        public bool ShouldDeploySWAT()
        {
            return CurrentStars >= _config.swatMinWantedLevel;
        }

        public bool ShouldDeployHelicopter()
        {
            return CurrentStars >= _config.helicopterMinWantedLevel;
        }

        public int GetRequiredPursuitUnits()
        {
            int stars = CurrentStars;
            return stars switch
            {
                0 => 0,
                1 => 1,
                2 => 1,
                3 => 2,
                4 => 3,
                5 => 4,
                6 => 5,
                _ => 1
            };
        }

        public float GetMaxPursuitSpeed()
        {
            int stars = CurrentStars;
            return stars switch
            {
                0 => 0f,
                1 => _config.patrolCarMaxSpeed,
                2 => _config.patrolCarMaxSpeed * 1.1f,
                3 => _config.pursuitMaxSpeed,
                4 => _config.pursuitMaxSpeed * 1.1f,
                5 => _config.pursuitCatchUpSpeed,
                6 => _config.pursuitCatchUpSpeed * 1.2f,
                _ => _config.pursuitMaxSpeed
            };
        }

        public JailSentence GetJailSentence()
        {
            int stars = CurrentStars;
            return stars switch
            {
                0 => JailSentence.Warning,
                1 => JailSentence.Warning,
                2 => JailSentence.ShortDetention,
                3 => JailSentence.MediumDetention,
                4 => JailSentence.LongDetention,
                5 => JailSentence.ExtendedDetention,
                6 => JailSentence.ExtendedDetention,
                _ => JailSentence.Warning
            };
        }

        private string GetMainPlayerId()
        {
            return "local_player";
        }

        public void Reset()
        {
            _currentWantedLevel = 0f;
            _decayTimer = 0f;
            _playerCrimeScores.Clear();
            _playerDecayTimers.Clear();
            OnWantedLevelChanged?.Invoke(0);
            OnStarsChanged?.Invoke(CurrentStars, 0);
        }
    }
}
