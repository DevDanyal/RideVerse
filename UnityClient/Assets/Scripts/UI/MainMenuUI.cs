using UnityEngine;
using UnityEngine.UI;
using TMPro;
using RideVerse.Auth;
using RideVerse.Core;
using RideVerse.Network;

namespace RideVerse.UI
{
    public class MainMenuUI : MonoBehaviour
    {
        [Header("Panels")]
        [SerializeField] private GameObject _mainPanel;
        [SerializeField] private GameObject _profilePanel;
        [SerializeField] private GameObject _settingsPanel;

        [Header("Main Panel")]
        [SerializeField] private Button _playButton;
        [SerializeField] private Button _profileButton;
        [SerializeField] private Button _settingsButton;
        [SerializeField] private Button _logoutButton;
        [SerializeField] private TextMeshProUGUI _welcomeText;

        [Header("Profile Panel")]
        [SerializeField] private TextMeshProUGUI _profileDisplayName;
        [SerializeField] private TextMeshProUGUI _profileLevel;
        [SerializeField] private TextMeshProUGUI _profileCash;
        [SerializeField] private TextMeshProUGUI _profileBank;
        [SerializeField] private TextMeshProUGUI _profileReputation;
        [SerializeField] private TextMeshProUGUI _profilePlayTime;
        [SerializeField] private Button _profileBackButton;

        [Header("Settings Panel")]
        [SerializeField] private Slider _musicVolumeSlider;
        [SerializeField] private Slider _sfxVolumeSlider;
        [SerializeField] private TMP_Dropdown _qualityDropdown;
        [SerializeField] private TMP_Dropdown _resolutionDropdown;
        [SerializeField] private Toggle _fullscreenToggle;
        [SerializeField] private Button _settingsBackButton;

        [Header("Status")]
        [SerializeField] private TextMeshProUGUI _connectionStatusText;
        [SerializeField] private TextMeshProUGUI _latencyText;

        private void Start()
        {
            BindButtons();
            ShowMainPanel();
            UpdateWelcomeText();
            UpdateConnectionStatus();
        }

        private void Update()
        {
            UpdateConnectionStatus();
        }

        private void BindButtons()
        {
            _playButton?.onClick.AddListener(OnPlayClicked);
            _profileButton?.onClick.AddListener(ShowProfilePanel);
            _settingsButton?.onClick.AddListener(ShowSettingsPanel);
            _logoutButton?.onClick.AddListener(OnLogoutClicked);
            _profileBackButton?.onClick.AddListener(ShowMainPanel);
            _settingsBackButton?.onClick.AddListener(ShowMainPanel);

            _fullscreenToggle?.onValueChanged.AddListener(OnFullscreenChanged);
            _qualityDropdown?.onValueChanged.AddListener(OnQualityChanged);
        }

        private void ShowMainPanel()
        {
            SetPanelActive(_mainPanel);
        }

        private void ShowProfilePanel()
        {
            SetPanelActive(_profilePanel);
            LoadProfileData();
        }

        private void ShowSettingsPanel()
        {
            SetPanelActive(_settingsPanel);
            LoadSettings();
        }

        private void SetPanelActive(GameObject panel)
        {
            _mainPanel?.SetActive(false);
            _profilePanel?.SetActive(false);
            _settingsPanel?.SetActive(false);
            panel?.SetActive(true);
        }

        private void UpdateWelcomeText()
        {
            if (_welcomeText != null)
            {
                string name = AuthManager.Instance.DisplayName;
                _welcomeText.text = string.IsNullOrEmpty(name) ? "Welcome" : $"Welcome, {name}";
            }
        }

        private void UpdateConnectionStatus()
        {
            if (_connectionStatusText != null)
            {
                bool connected = NetworkManager.Instance != null && NetworkManager.Instance.IsConnected;
                _connectionStatusText.text = connected ? "Online" : "Offline";
                _connectionStatusText.color = connected ? Color.green : Color.red;
            }

            if (_latencyText != null && NetworkManager.Instance != null)
            {
                float latency = NetworkManager.Instance.LatencyMs;
                _latencyText.text = latency > 0 ? $"{latency:F0}ms" : "";
            }
        }

        private async void LoadProfileData()
        {
            var api = new PlayerApi(ApiClient.Instance);
            var result = await api.GetProfileAsync();

            if (result.IsSuccess && result.Data != null)
            {
                if (_profileDisplayName != null)
                    _profileDisplayName.text = result.Data.DisplayName;
                if (_profileLevel != null)
                    _profileLevel.text = $"Level {result.Data.Level}";
                if (_profileCash != null)
                    _profileCash.text = $"${result.Data.Cash:N0}";
                if (_profileBank != null)
                    _profileBank.text = $"${result.Data.BankBalance:N0}";
                if (_profileReputation != null)
                    _profileReputation.text = $"Rep: {result.Data.Reputation}";
            }
        }

        private void LoadSettings()
        {
            if (_qualityDropdown != null)
            {
                _qualityDropdown.ClearOptions();
                var options = new System.Collections.Generic.List<string>(QualitySettings.names);
                _qualityDropdown.AddOptions(options);
                _qualityDropdown.value = QualitySettings.GetQualityLevel();
            }

            if (_fullscreenToggle != null)
                _fullscreenToggle.isOn = Screen.fullScreen;
        }

        private void OnPlayClicked()
        {
            Core.AppManager.Instance?.LoadScene(Constants.Scenes.Game);
        }

        private void OnLogoutClicked()
        {
            NetworkManager.Instance?.Disconnect();
            AuthManager.Instance?.Logout();
            Core.AppManager.Instance?.LoadScene(Constants.Scenes.Login);
        }

        private void OnFullscreenChanged(bool isFullscreen)
        {
            Screen.fullScreen = isFullscreen;
        }

        private void OnQualityChanged(int index)
        {
            QualitySettings.SetQualityLevel(index);
        }
    }
}
