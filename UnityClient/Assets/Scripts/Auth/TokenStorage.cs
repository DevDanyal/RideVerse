using UnityEngine;

namespace RideVerse.Auth
{
    public interface ITokenStorage
    {
        void SaveTokens(string accessToken, string refreshToken);
        string GetAccessToken();
        string GetRefreshToken();
        void ClearTokens();
        bool HasTokens { get; }
        void SavePlayerId(string playerId);
        string GetPlayerId();
        void SaveDisplayName(string displayName);
        string GetDisplayName();
    }

    public class TokenStorage : ITokenStorage
    {
        public void SaveTokens(string accessToken, string refreshToken)
        {
            PlayerPrefs.SetString(Constants.PlayerPrefs.AccessToken, accessToken);
            PlayerPrefs.SetString(Constants.PlayerPrefs.RefreshToken, refreshToken);
            PlayerPrefs.Save();
        }

        public string GetAccessToken()
        {
            return PlayerPrefs.GetString(Constants.PlayerPrefs.AccessToken, string.Empty);
        }

        public string GetRefreshToken()
        {
            return PlayerPrefs.GetString(Constants.PlayerPrefs.RefreshToken, string.Empty);
        }

        public void ClearTokens()
        {
            PlayerPrefs.DeleteKey(Constants.PlayerPrefs.AccessToken);
            PlayerPrefs.DeleteKey(Constants.PlayerPrefs.RefreshToken);
            PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerId);
            PlayerPrefs.DeleteKey(Constants.PlayerPrefs.DisplayName);
            PlayerPrefs.Save();
        }

        public bool HasTokens => !string.IsNullOrEmpty(GetRefreshToken());

        public void SavePlayerId(string playerId)
        {
            PlayerPrefs.SetString(Constants.PlayerPrefs.PlayerId, playerId);
            PlayerPrefs.Save();
        }

        public string GetPlayerId()
        {
            return PlayerPrefs.GetString(Constants.PlayerPrefs.PlayerId, string.Empty);
        }

        public void SaveDisplayName(string displayName)
        {
            PlayerPrefs.SetString(Constants.PlayerPrefs.DisplayName, displayName);
            PlayerPrefs.Save();
        }

        public string GetDisplayName()
        {
            return PlayerPrefs.GetString(Constants.PlayerPrefs.DisplayName, string.Empty);
        }
    }
}
