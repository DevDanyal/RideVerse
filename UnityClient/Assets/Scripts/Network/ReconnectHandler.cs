using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.Core;

namespace RideVerse.Network
{
    public class ReconnectHandler
    {
        private int _attemptCount;
        private float _currentDelay;
        private bool _isReconnecting;
        private Action<string> _connectAction;

        public bool IsReconnecting => _isReconnecting;
        public int AttemptCount => _attemptCount;

        public event Action<int> OnReconnectAttempt;
        public event Action OnReconnectFailed;
        public event Action OnReconnectSucceeded;

        public void Initialize(Action<string> connectAction)
        {
            _connectAction = connectAction;
            _attemptCount = 0;
            _currentDelay = Constants.Network.ReconnectMinDelay;
            _isReconnecting = false;
        }

        public void Reset()
        {
            _attemptCount = 0;
            _currentDelay = Constants.Network.ReconnectMinDelay;
            _isReconnecting = false;
        }

        public IEnumerator ReconnectCoroutine(string url)
        {
            if (_isReconnecting)
            {
                yield break;
            }

            _isReconnecting = true;

            while (_attemptCount < Constants.Network.MaxReconnectAttempts)
            {
                _attemptCount++;
                OnReconnectAttempt?.Invoke(_attemptCount);

                Debug.Log($"[Reconnect] Attempt {_attemptCount}, waiting {_currentDelay:F1}s");
                yield return new WaitForSeconds(_currentDelay);

                _connectAction?.Invoke(url);

                float waitStart = Time.realtimeSinceStartup;
                float maxWait = 5f;

                while (Time.realtimeSinceStartup - waitStart < maxWait)
                {
                    yield return new WaitForSeconds(0.2f);
                }

                _currentDelay = Mathf.Min(
                    _currentDelay * Constants.Network.ReconnectMultiplier,
                    Constants.Network.ReconnectMaxDelay);
            }

            Debug.LogError($"[Reconnect] Failed after {_attemptCount} attempts");
            _isReconnecting = false;
            OnReconnectFailed?.Invoke();
        }

        public void OnConnected()
        {
            if (_isReconnecting)
            {
                Debug.Log("[Reconnect] Connected successfully");
                OnReconnectSucceeded?.Invoke();
            }

            Reset();
        }
    }
}
