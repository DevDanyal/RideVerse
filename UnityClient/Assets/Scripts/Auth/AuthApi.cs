using System;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;
using RideVerse.Core;

namespace RideVerse.Auth
{
    public interface IAuthApi
    {
        Task<ApiResponseEnvelope<TokenResponse>> LoginAsync(string email, string password, CancellationToken ct = default);
        Task<ApiResponseEnvelope<TokenResponse>> RegisterAsync(string email, string username, string password, CancellationToken ct = default);
        Task<ApiResponseEnvelope<TokenResponse>> RefreshTokenAsync(string refreshToken, CancellationToken ct = default);
        Task<ApiResponseEnvelope<object>> LogoutAsync(string refreshToken, CancellationToken ct = default);
        Task<ApiResponseEnvelope<AccountResponse>> GetMeAsync(string accessToken, CancellationToken ct = default);
    }

    public class AuthApi : IAuthApi
    {
        private string BaseUrl => Constants.Api.BaseUrl + Constants.Api.ApiPrefix;

        public async Task<ApiResponseEnvelope<TokenResponse>> LoginAsync(
            string email, string password, CancellationToken ct = default)
        {
            var body = JsonConvert.SerializeObject(new LoginRequest { Email = email, Password = password });
            return await SendRequest<TokenResponse>(Constants.Api.Auth.Login, "POST", body, ct);
        }

        public async Task<ApiResponseEnvelope<TokenResponse>> RegisterAsync(
            string email, string username, string password, CancellationToken ct = default)
        {
            var body = JsonConvert.SerializeObject(new RegisterRequest
            {
                Email = email,
                Username = username,
                Password = password
            });
            return await SendRequest<TokenResponse>(Constants.Api.Auth.Register, "POST", body, ct);
        }

        public async Task<ApiResponseEnvelope<TokenResponse>> RefreshTokenAsync(
            string refreshToken, CancellationToken ct = default)
        {
            var body = JsonConvert.SerializeObject(new RefreshRequest { RefreshToken = refreshToken });
            return await SendRequest<TokenResponse>(Constants.Api.Auth.Refresh, "POST", body, ct);
        }

        public async Task<ApiResponseEnvelope<object>> LogoutAsync(
            string refreshToken, CancellationToken ct = default)
        {
            var body = JsonConvert.SerializeObject(new LogoutRequest { RefreshToken = refreshToken });
            return await SendRequest<object>(Constants.Api.Auth.Logout, "POST", body, ct);
        }

        public async Task<ApiResponseEnvelope<AccountResponse>> GetMeAsync(
            string accessToken, CancellationToken ct = default)
        {
            return await SendRequest<AccountResponse>(
                Constants.Api.Auth.Me, "GET", null, ct, accessToken);
        }

        private async Task<ApiResponseEnvelope<T>> SendRequest<T>(
            string path, string method, string jsonBody,
            CancellationToken ct, string bearerToken = null)
        {
            string url = BaseUrl + path;

            using var request = new UnityWebRequest(url, method);

            if (!string.IsNullOrEmpty(jsonBody))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonBody);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            }

            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            if (!string.IsNullOrEmpty(bearerToken))
            {
                request.SetRequestHeader("Authorization", "Bearer " + bearerToken);
            }

            try
            {
                var operation = request.SendWebRequest();

                while (!operation.isDone && !ct.IsCancellationRequested)
                {
                    await Task.Yield();
                }

                if (ct.IsCancellationRequested)
                {
                    request.Abort();
                    return new ApiResponseEnvelope<T>
                    {
                        Success = false,
                        Message = "Request cancelled"
                    };
                }

                string responseText = request.downloadHandler.text;
                var envelope = JsonConvert.DeserializeObject<ApiResponseEnvelope<T>>(responseText);

                if (envelope == null)
                {
                    return new ApiResponseEnvelope<T>
                    {
                        Success = false,
                        Message = $"Failed to parse response: {responseText}"
                    };
                }

                return envelope;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[AuthApi] {method} {path} failed: {ex.Message}");
                return new ApiResponseEnvelope<T>
                {
                    Success = false,
                    Message = ex.Message
                };
            }
            finally
            {
                request.Dispose();
            }
        }
    }
}
