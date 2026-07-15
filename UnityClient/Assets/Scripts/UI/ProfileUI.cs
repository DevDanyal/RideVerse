using UnityEngine;
using UnityEngine.UI;
using TMPro;
using RideVerse.API;
using RideVerse.Auth;
using RideVerse.Core;

namespace RideVerse.UI
{
    public class ProfileUI : MonoBehaviour
    {
        [Header("Profile Display")]
        [SerializeField] private TextMeshProUGUI _displayNameText;
        [SerializeField] private TextMeshProUGUI _levelText;
        [SerializeField] private TextMeshProUGUI _emailText;
        [SerializeField] private Slider _experienceBar;
        [SerializeField] private TextMeshProUGUI _experienceText;

        [Header("Stats")]
        [SerializeField] private TextMeshProUGUI _healthText;
        [SerializeField] private TextMeshProUGUI _staminaText;
        [SerializeField] private TextMeshProUGUI _energyText;
        [SerializeField] private TextMeshProUGUI _reputationText;
        [SerializeField] private TextMeshProUGUI _wantedLevelText;

        [Header("Economy")]
        [SerializeField] private TextMeshProUGUI _cashText;
        [SerializeField] private TextMeshProUGUI _bankText;

        [Header("Game Stats")]
        [SerializeField] private TextMeshProUGUI _missionsCompletedText;
        [SerializeField] private TextMeshProUGUI _distanceTraveledText;
        [SerializeField] private TextMeshProUGUI _totalEarnedText;
        [SerializeField] private TextMeshProUGUI _playTimeText;

        [Header("Buttons")]
        [SerializeField] private Button _refreshButton;
        [SerializeField] private Button _closeButton;

        private void Start()
        {
            _refreshButton?.onClick.AddListener(LoadProfile);
            _closeButton?.onClick.AddListener(Hide);
        }

        public async void LoadProfile()
        {
            var auth = AuthManager.Instance;
            if (auth == null || !auth.IsAuthenticated) return;

            var api = new PlayerApi(ApiClient.Instance);
            var profileResult = await api.GetProfileAsync();
            var statsResult = await api.GetStatisticsAsync();

            if (profileResult.IsSuccess && profileResult.Data != null)
            {
                var p = profileResult.Data;
                SetText(_displayNameText, p.DisplayName);
                SetText(_levelText, $"Level {p.Level}");
                SetText(_emailText, "");
                SetText(_healthText, $"{p.Health}/100");
                SetText(_staminaText, $"{p.Stamina}/100");
                SetText(_energyText, $"{p.Energy}/100");
                SetText(_reputationText, $"Rep: {p.Reputation}");
                SetText(_wantedLevelText, $"Wanted: {p.WantedLevel}");
                SetText(_cashText, $"${p.Cash:N0}");
                SetText(_bankText, $"${p.BankBalance:N0}");

                if (_experienceBar != null)
                {
                    int xpForNext = p.Level * 1000;
                    _experienceBar.value = xpForNext > 0 ? (float)p.Experience / xpForNext : 0f;
                }
                SetText(_experienceText, $"XP: {p.Experience}");
            }

            if (statsResult.IsSuccess && statsResult.Data != null)
            {
                var s = statsResult.Data;
                SetText(_missionsCompletedText, $"Missions: {s.MissionsCompleted}");
                SetText(_distanceTraveledText, $"Distance: {s.DistanceTraveled:F0}m");
                SetText(_totalEarnedText, $"Total Earned: ${s.TotalEarned:N0}");
                SetText(_playTimeText, FormatPlayTime(s.TotalPlayTimeSeconds));
            }
        }

        public void Show()
        {
            gameObject.SetActive(true);
            LoadProfile();
        }

        public void Hide()
        {
            gameObject.SetActive(false);
        }

        private void SetText(TextMeshProUGUI tmp, string value)
        {
            if (tmp != null)
                tmp.text = value;
        }

        private string FormatPlayTime(int totalSeconds)
        {
            int hours = totalSeconds / 3600;
            int minutes = (totalSeconds % 3600) / 60;
            return $"{hours}h {minutes}m";
        }
    }
}
