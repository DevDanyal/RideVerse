using System;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using RideVerse.Auth;
using RideVerse.Core;

namespace RideVerse.UI
{
    public class LoginUI : MonoBehaviour
    {
        [Header("Login Panel")]
        [SerializeField] private GameObject _loginPanel;
        [SerializeField] private TMP_InputField _emailInput;
        [SerializeField] private TMP_InputField _passwordInput;
        [SerializeField] private Button _loginButton;
        [SerializeField] private Button _togglePasswordButton;
        [SerializeField] private Toggle _rememberMeToggle;

        [Header("Register Panel")]
        [SerializeField] private GameObject _registerPanel;
        [SerializeField] private TMP_InputField _regEmailInput;
        [SerializeField] private TMP_InputField _regUsernameInput;
        [SerializeField] private TMP_InputField _regPasswordInput;
        [SerializeField] private TMP_InputField _regConfirmPasswordInput;
        [SerializeField] private Button _registerButton;
        [SerializeField] private Button _backToLoginButton;

        [Header("Navigation")]
        [SerializeField] private Button _goToRegisterButton;
        [SerializeField] private Button _goToLoginButton;

        [Header("Status")]
        [SerializeField] private GameObject _loadingIndicator;
        [SerializeField] private TextMeshProUGUI _errorText;
        [SerializeField] private TextMeshProUGUI _statusText;

        [Header("Configuration")]
        [SerializeField] private float _errorDisplayDuration = 5f;

        private AuthManager _authManager;
        private CancellationTokenSource _cts;
        private bool _isPasswordVisible;

        private void Awake()
        {
            _authManager = AuthManager.Instance;
            _cts = new CancellationTokenSource();
        }

        private void Start()
        {
            ShowLoginPanel();
            BindButtons();
            LoadRememberedEmail();
            HideError();
            SetLoading(false);
        }

        private void OnDestroy()
        {
            _cts?.Cancel();
            _cts?.Dispose();
        }

        private void BindButtons()
        {
            _loginButton?.onClick.AddListener(OnLoginClicked);
            _registerButton?.onClick.AddListener(OnRegisterClicked);
            _goToRegisterButton?.onClick.AddListener(ShowRegisterPanel);
            _goToLoginButton?.onClick.AddListener(ShowLoginPanel);
            _backToLoginButton?.onClick.AddListener(ShowLoginPanel);
            _togglePasswordButton?.onClick.AddListener(TogglePasswordVisibility);

            if (_emailInput != null)
                _emailInput.onSubmit.AddListener(_ => OnLoginClicked());
            if (_passwordInput != null)
                _passwordInput.onSubmit.AddListener(_ => OnLoginClicked());
        }

        private void ShowLoginPanel()
        {
            if (_loginPanel != null) _loginPanel.SetActive(true);
            if (_registerPanel != null) _registerPanel.SetActive(false);
            HideError();
        }

        private void ShowRegisterPanel()
        {
            if (_loginPanel != null) _loginPanel.SetActive(false);
            if (_registerPanel != null) _registerPanel.SetActive(true);
            HideError();
        }

        private async void OnLoginClicked()
        {
            string email = _emailInput?.text?.Trim();
            string password = _passwordInput?.text;

            if (string.IsNullOrEmpty(email) || string.IsNullOrEmpty(password))
            {
                ShowError("Please enter email and password");
                return;
            }

            SetLoading(true);
            HideError();

            bool success = await _authManager.LoginAsync(email, password);

            if (_cts.Token.IsCancellationRequested) return;

            SetLoading(false);

            if (success)
            {
                if (_rememberMeToggle != null && _rememberMeToggle.isOn)
                {
                    PlayerPrefs.SetString(Constants.PlayerPrefs.RememberEmail, email);
                    PlayerPrefs.Save();
                }

                Debug.Log("[LoginUI] Login successful");
                Core.AppManager.Instance?.LoadScene(Constants.Scenes.MainMenu);
            }
            else
            {
                ShowError("Invalid email or password");
            }
        }

        private async void OnRegisterClicked()
        {
            string email = _regEmailInput?.text?.Trim();
            string username = _regUsernameInput?.text?.Trim();
            string password = _regPasswordInput?.text;
            string confirmPassword = _regConfirmPasswordInput?.text;

            if (string.IsNullOrEmpty(email) || string.IsNullOrEmpty(username) ||
                string.IsNullOrEmpty(password))
            {
                ShowError("Please fill in all fields");
                return;
            }

            if (password != confirmPassword)
            {
                ShowError("Passwords do not match");
                return;
            }

            if (password.Length < 8)
            {
                ShowError("Password must be at least 8 characters");
                return;
            }

            SetLoading(true);
            HideError();

            bool success = await _authManager.RegisterAsync(email, username, password);

            if (_cts.Token.IsCancellationRequested) return;

            SetLoading(false);

            if (success)
            {
                Debug.Log("[LoginUI] Registration successful");
                Core.AppManager.Instance?.LoadScene(Constants.Scenes.MainMenu);
            }
            else
            {
                ShowError("Registration failed. Email or username may already be taken.");
            }
        }

        private void TogglePasswordVisibility()
        {
            _isPasswordVisible = !_isPasswordVisible;
            if (_passwordInput != null)
            {
                _passwordInput.contentType = _isPasswordVisible
                    ? TMP_InputField.ContentType.Standard
                    : TMP_InputField.ContentType.Password;
                _passwordInput.ForceLabelUpdate();
            }
        }

        private void LoadRememberedEmail()
        {
            string rememberedEmail = PlayerPrefs.GetString(Constants.PlayerPrefs.RememberEmail, "");
            if (!string.IsNullOrEmpty(rememberedEmail) && _emailInput != null)
            {
                _emailInput.text = rememberedEmail;
                if (_rememberMeToggle != null)
                    _rememberMeToggle.isOn = true;
            }
        }

        private void SetLoading(bool loading)
        {
            if (_loadingIndicator != null)
                _loadingIndicator.SetActive(loading);

            if (_loginButton != null)
                _loginButton.interactable = !loading;
            if (_registerButton != null)
                _registerButton.interactable = !loading;

            if (_emailInput != null) _emailInput.interactable = !loading;
            if (_passwordInput != null) _passwordInput.interactable = !loading;
            if (_regEmailInput != null) _regEmailInput.interactable = !loading;
            if (_regUsernameInput != null) _regUsernameInput.interactable = !loading;
            if (_regPasswordInput != null) _regPasswordInput.interactable = !loading;
            if (_regConfirmPasswordInput != null) _regConfirmPasswordInput.interactable = !loading;
        }

        private void ShowError(string message)
        {
            if (_errorText != null)
            {
                _errorText.text = message;
                _errorText.gameObject.SetActive(true);
                Invoke(nameof(HideError), _errorDisplayDuration);
            }
        }

        private void HideError()
        {
            CancelInvoke(nameof(HideError));
            if (_errorText != null)
                _errorText.gameObject.SetActive(false);
        }
    }
}
