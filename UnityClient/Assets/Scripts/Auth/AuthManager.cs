using System;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

namespace RideVerse.Auth
{
    public class AuthManager : Core.Singleton<AuthManager>
    {
        [SerializeField] private bool _useDependencyInjection;

        private IAuthApi _authApi;
        private ITokenStorage _tokenStorage;

        public bool IsAuthenticated => _tokenStorage != null && _tokenStorage.HasTokens;
        public string AccessToken => _tokenStorage?.GetAccessToken() ?? string.Empty;
        public string PlayerId => _tokenStorage?.GetPlayerId() ?? string.Empty;
        public string DisplayName => _tokenStorage?.GetDisplayName() ?? string.Empty;

        public event Action OnAuthenticated;
        public event Action OnLoggedOut;
        public event Action<string> OnAuthError;

        private CancellationTokenSource _cts;

        protected override void Awake()
        {
            base.Awake();
            _authApi = new AuthApi();
            _tokenStorage = new TokenStorage();
            _cts = new CancellationTokenSource();
        }

        private void OnDestroy()
        {
            _cts?.Cancel();
            _cts?.Dispose();
        }

        public async Task<bool> LoginAsync(string email, string password)
        {
            var response = await _authApi.LoginAsync(email, password, _cts.Token);

            if (response == null || !response.Success || response.Data == null)
            {
                string errorMsg = response?.Message ?? "Login failed";
                Debug.LogError($"[AuthManager] Login failed: {errorMsg}");
                OnAuthError?.Invoke(errorMsg);
                return false;
            }

            SaveAuthData(response.Data);
            OnAuthenticated?.Invoke();
            return true;
        }

        public async Task<bool> RegisterAsync(string email, string username, string password)
        {
            var response = await _authApi.RegisterAsync(email, username, password, _cts.Token);

            if (response == null || !response.Success || response.Data == null)
            {
                string errorMsg = response?.Message ?? "Registration failed";
                Debug.LogError($"[AuthManager] Register failed: {errorMsg}");
                OnAuthError?.Invoke(errorMsg);
                return false;
            }

            SaveAuthData(response.Data);
            OnAuthenticated?.Invoke();
            return true;
        }

        public async Task<bool> RefreshTokenAsync()
        {
            string refreshToken = _tokenStorage.GetRefreshToken();

            if (string.IsNullOrEmpty(refreshToken))
            {
                return false;
            }

            var response = await _authApi.RefreshTokenAsync(refreshToken, _cts.Token);

            if (response == null || !response.Success || response.Data == null)
            {
                Debug.LogWarning("[AuthManager] Token refresh failed, logging out");
                Logout();
                return false;
            }

            SaveAuthData(response.Data);
            return true;
        }

        public async Task<PlayerProfile> GetProfileAsync()
        {
            string token = _tokenStorage.GetAccessToken();

            if (string.IsNullOrEmpty(token))
            {
                return null;
            }

            var response = await _authApi.GetMeAsync(token, _cts.Token);

            if (response == null || !response.Success || response.Data == null)
            {
                Debug.LogError($"[AuthManager] GetProfile failed: {response?.Message}");
                return null;
            }

            return new PlayerProfile
            {
                Id = response.Data.Id,
                AccountId = response.Data.Id,
                DisplayName = response.Data.Username
            };
        }

        public void Logout()
        {
            string refreshToken = _tokenStorage.GetRefreshToken();

            if (!string.IsNullOrEmpty(refreshToken))
            {
                _ = _authApi.LogoutAsync(refreshToken);
            }

            _tokenStorage.ClearTokens();
            OnLoggedOut?.Invoke();
        }

        private void SaveAuthData(TokenResponse tokenData)
        {
            _tokenStorage.SaveTokens(tokenData.AccessToken, tokenData.RefreshToken);
            Debug.Log("[AuthManager] Auth tokens saved");
        }

        public void SetApi(IAuthApi authApi)
        {
            _authApi = authApi;
        }

        public void SetTokenStorage(ITokenStorage tokenStorage)
        {
            _tokenStorage = tokenStorage;
        }
    }
}
