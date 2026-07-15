using UnityEngine;
using UnityEngine.UI;
using TMPro;
using RideVerse.Core;

namespace RideVerse.UI
{
    public class LoadingUI : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private Slider _progressBar;
        [SerializeField] private TextMeshProUGUI _statusText;
        [SerializeField] private TextMeshProUGUI _versionText;
        [SerializeField] private CanvasGroup _canvasGroup;

        [Header("Configuration")]
        [SerializeField] private float _fadeInDuration = 0.3f;
        [SerializeField] private string[] _loadingTips;

        private float _targetProgress;
        private float _currentProgress;

        private void Start()
        {
            if (_canvasGroup != null)
            {
                _canvasGroup.alpha = 0f;
                LeanFadeIn();
            }

            if (_versionText != null)
            {
                _versionText.text = $"v{Application.version}";
            }

            if (_loadingTips != null && _loadingTips.Length > 0 && _statusText != null)
            {
                int tipIndex = Random.Range(0, _loadingTips.Length);
                _statusText.text = _loadingTips[tipIndex];
            }
        }

        private void Update()
        {
            if (_currentProgress < _targetProgress)
            {
                _currentProgress = Mathf.MoveTowards(
                    _currentProgress, _targetProgress, Time.deltaTime * 2f);

                if (_progressBar != null)
                {
                    _progressBar.value = _currentProgress;
                }
            }
        }

        public void SetProgress(float progress, string statusText = null)
        {
            _targetProgress = Mathf.Clamp01(progress);

            if (statusText != null && _statusText != null)
            {
                _statusText.text = statusText;
            }
        }

        private void LeanFadeIn()
        {
            if (_canvasGroup != null)
            {
                _canvasGroup.alpha = 1f;
            }
        }
    }
}
