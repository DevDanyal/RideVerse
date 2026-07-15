using UnityEngine;
using UnityEngine.UI;
using TMPro;
using RideVerse.Network;
using RideVerse.Core;

namespace RideVerse.UI
{
    public class HUDUI : MonoBehaviour
    {
        [Header("Health")]
        [SerializeField] private Slider _healthBar;
        [SerializeField] private Image _healthFill;
        [SerializeField] private TextMeshProUGUI _healthText;

        [Header("Stamina")]
        [SerializeField] private Slider _staminaBar;
        [SerializeField] private Image _staminaFill;

        [Header("Money")]
        [SerializeField] private TextMeshProUGUI _cashText;
        [SerializeField] private TextMeshProUGUI _bankText;

        [Header("Fuel")]
        [SerializeField] private Slider _fuelBar;
        [SerializeField] private Image _fuelFill;
        [SerializeField] private GameObject _fuelPanel;

        [Header("Wanted Level")]
        [SerializeField] private GameObject _wantedPanel;
        [SerializeField] private Image[] _wantedStars;

        [Header("Minimap Placeholder")]
        [SerializeField] private RawImage _minimapImage;
        [SerializeField] private RectTransform _minimapPlayerMarker;
        [SerializeField] private Camera _minimapCamera;

        [Header("Network")]
        [SerializeField] private TextMeshProUGUI _connectionIndicator;
        [SerializeField] private TextMeshProUGUI _latencyText;

        [Header("Player Count")]
        [SerializeField] private TextMeshProUGUI _playerCountText;

        [Header("Chat")]
        [SerializeField] private GameObject _chatPanel;
        [SerializeField] private TMP_InputField _chatInput;
        [SerializeField] private Button _chatSendButton;
        [SerializeField] private TextMeshProUGUI _chatMessagesText;
        [SerializeField] private ScrollRect _chatScrollRect;
        [SerializeField] private int _maxChatMessages = 50;

        private int _currentHealth = 100;
        private int _maxHealth = 100;
        private int _currentStamina = 100;
        private int _maxStamina = 100;
        private float _currentFuel = 100f;
        private float _maxFuel = 100f;
        private int _wantedLevel;
        private int _chatMessageCount;

        private void Start()
        {
            BindChat();
            SubscribeEvents();
            UpdateAll();
        }

        private void OnDestroy()
        {
            UnsubscribeEvents();
        }

        private void Update()
        {
            UpdateConnectionInfo();
        }

        private void BindChat()
        {
            _chatSendButton?.onClick.AddListener(OnChatSend);
            if (_chatInput != null)
                _chatInput.onSubmit.AddListener(_ => OnChatSend());
        }

        private void SubscribeEvents()
        {
            if (NetworkManager.Instance != null)
            {
                NetworkManager.Instance.OnChatMessage += HandleChatMessage;
                NetworkManager.Instance.OnConnected += HandleConnected;
                NetworkManager.Instance.OnDisconnected += HandleDisconnected;
            }
        }

        private void UnsubscribeEvents()
        {
            if (NetworkManager.Instance != null)
            {
                NetworkManager.Instance.OnChatMessage -= HandleChatMessage;
                NetworkManager.Instance.OnConnected -= HandleConnected;
                NetworkManager.Instance.OnDisconnected -= HandleDisconnected;
            }
        }

        public void UpdateHealth(int current, int max)
        {
            _currentHealth = current;
            _maxHealth = max;

            if (_healthBar != null)
                _healthBar.value = (float)current / max;

            if (_healthText != null)
                _healthText.text = $"{current}/{max}";

            if (_healthFill != null)
                _healthFill.color = Color.Lerp(Color.red, Color.green, (float)current / max);
        }

        public void UpdateStamina(int current, int max)
        {
            _currentStamina = current;
            _maxStamina = max;

            if (_staminaBar != null)
                _staminaBar.value = (float)current / max;

            if (_staminaFill != null)
                _staminaFill.color = Color.Lerp(Color.yellow, Color.cyan, (float)current / max);
        }

        public void UpdateMoney(double cash, double bank)
        {
            if (_cashText != null)
                _cashText.text = $"${cash:N0}";
            if (_bankText != null)
                _bankText.text = $"${bank:N0}";
        }

        public void UpdateFuel(float current, float max)
        {
            _currentFuel = current;
            _maxFuel = max;

            if (_fuelBar != null)
                _fuelBar.value = current / max;

            if (_fuelFill != null)
                _fuelFill.color = Color.Lerp(Color.red, Color.green, current / max);

            if (_fuelPanel != null)
                _fuelPanel.SetActive(max > 0);
        }

        public void UpdateWantedLevel(int level)
        {
            _wantedLevel = Mathf.Clamp(level, 0, 5);

            if (_wantedPanel != null)
                _wantedPanel.SetActive(_wantedLevel > 0);

            if (_wantedStars != null)
            {
                for (int i = 0; i < _wantedStars.Length; i++)
                {
                    if (_wantedStars[i] != null)
                        _wantedStars[i].enabled = i < _wantedLevel;
                }
            }
        }

        public void UpdatePlayerCount(int count)
        {
            if (_playerCountText != null)
                _playerCountText.text = $"Players: {count}";
        }

        private void UpdateConnectionInfo()
        {
            if (NetworkManager.Instance == null) return;

            if (_connectionIndicator != null)
            {
                bool connected = NetworkManager.Instance.IsConnected;
                _connectionIndicator.text = connected ? "●" : "○";
                _connectionIndicator.color = connected ? Color.green : Color.red;
            }

            if (_latencyText != null)
            {
                float latency = NetworkManager.Instance.LatencyMs;
                _latencyText.text = latency > 0 ? $"{latency:F0}ms" : "";
            }
        }

        private void UpdateAll()
        {
            UpdateHealth(_currentHealth, _maxHealth);
            UpdateStamina(_currentStamina, _maxStamina);
            UpdateMoney(0, 0);
            UpdateFuel(_currentFuel, _maxFuel);
            UpdateWantedLevel(_wantedLevel);
            UpdateConnectionInfo();
        }

        private void OnChatSend()
        {
            if (_chatInput == null) return;

            string message = _chatInput.text.Trim();
            if (string.IsNullOrEmpty(message)) return;

            NetworkManager.Instance?.SendChat(message);
            _chatInput.text = "";
            _chatInput.ActivateInputField();
        }

        private void HandleChatMessage(WsChatMessage chat)
        {
            if (_chatMessagesText == null) return;

            string formattedMsg = $"<b>{chat.DisplayName}</b>: {chat.Message}";
            _chatMessagesText.text += formattedMsg + "\n";
            _chatMessageCount++;

            if (_chatMessageCount > _maxChatMessages)
            {
                string text = _chatMessagesText.text;
                int firstNewline = text.IndexOf('\n');
                if (firstNewline >= 0)
                {
                    _chatMessagesText.text = text.Substring(firstNewline + 1);
                }
                _chatMessageCount--;
            }

            if (_chatScrollRect != null)
            {
                Canvas.ForceUpdateCanvases();
                _chatScrollRect.verticalNormalizedPosition = 0f;
            }
        }

        private void HandleConnected()
        {
            if (_chatMessagesText != null)
            {
                _chatMessagesText.text += "<i>Connected to server</i>\n";
            }
        }

        private void HandleDisconnected()
        {
            if (_chatMessagesText != null)
            {
                _chatMessagesText.text += "<i>Disconnected from server</i>\n";
            }
        }

        public void ToggleChat()
        {
            if (_chatPanel != null)
                _chatPanel.SetActive(!_chatPanel.activeSelf);
        }

        public void SetHUDVisible(bool visible)
        {
            gameObject.SetActive(visible);
        }
    }
}
