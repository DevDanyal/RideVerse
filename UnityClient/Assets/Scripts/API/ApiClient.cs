using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;
using RideVerse.Auth;
using RideVerse.Core;

namespace RideVerse.API
{
    public class ApiClient : Core.Singleton<ApiClient>
    {
        private const int MaxRetries = 2;
        private string BaseUrl => Constants.Api.BaseUrl + Constants.Api.ApiPrefix;

        private AuthManager Auth => AuthManager.Instance;

        public void Initialize()
        {
            Debug.Log("[ApiClient] Initialized");
        }

        public async Task<ApiResult<T>> GetAsync<T>(string path, CancellationToken ct = default)
        {
            return await SendRequest<T>(path, "GET", null, ct);
        }

        public async Task<ApiResult<T>> PostAsync<T>(string path, object body = null, CancellationToken ct = default)
        {
            string json = body != null ? JsonConvert.SerializeObject(body) : null;
            return await SendRequest<T>(path, "POST", json, ct);
        }

        public async Task<ApiResult<T>> PatchAsync<T>(string path, object body = null, CancellationToken ct = default)
        {
            string json = body != null ? JsonConvert.SerializeObject(body) : null;
            return await SendRequest<T>(path, "PATCH", json, ct);
        }

        public async Task<ApiResult<T>> DeleteAsync<T>(string path, CancellationToken ct = default)
        {
            return await SendRequest<T>(path, "DELETE", null, ct);
        }

        public async Task<ApiResult<object>> PostAsync(string path, object body = null, CancellationToken ct = default)
        {
            string json = body != null ? JsonConvert.SerializeObject(body) : null;
            return await SendRequest<object>(path, "POST", json, ct);
        }

        public async Task<ApiResult<object>> PatchAsync(string path, object body = null, CancellationToken ct = default)
        {
            string json = body != null ? JsonConvert.SerializeObject(body) : null;
            return await SendRequest<object>(path, "PATCH", json, ct);
        }

        public async Task<ApiResult<object>> DeleteAsync(string path, CancellationToken ct = default)
        {
            return await SendRequest<object>(path, "DELETE", null, ct);
        }

        private async Task<ApiResult<T>> SendRequest<T>(
            string path, string method, string jsonBody,
            CancellationToken ct, int retryCount = 0)
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

            string token = Auth?.AccessToken;
            if (!string.IsNullOrEmpty(token))
            {
                request.SetRequestHeader("Authorization", "Bearer " + token);
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
                    return ApiResult<T>.Fail(ApiRequestStatus.Cancelled, "Request cancelled");
                }

                return await ProcessResponse<T>(request, path, method, jsonBody, ct, retryCount);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ApiClient] {method} {path} error: {ex.Message}");
                return ApiResult<T>.Fail(ApiRequestStatus.NetworkError, ex.Message);
            }
            finally
            {
                request.Dispose();
            }
        }

        private async Task<ApiResult<T>> ProcessResponse<T>(
            UnityWebRequest request, string path, string method,
            string jsonBody, CancellationToken ct, int retryCount)
        {
            string responseText = request.downloadHandler.text;
            int statusCode = (int)request.responseCode;

            switch (statusCode)
            {
                case 200:
                case 201:
                    return ParseSuccess<T>(responseText);

                case 401:
                    if (retryCount < MaxRetries && Auth != null)
                    {
                        bool refreshed = await Auth.RefreshTokenAsync();
                        if (refreshed)
                        {
                            return await SendRequest<T>(path, method, jsonBody, ct, retryCount + 1);
                        }
                    }
                    return ApiResult<T>.Fail(ApiRequestStatus.Unauthorized, "Unauthorized");

                case 403:
                    return ApiResult<T>.Fail(ApiRequestStatus.Forbidden, "Forbidden");

                case 404:
                    return ApiResult<T>.Fail(ApiRequestStatus.NotFound, "Not found");

                case 422:
                    return ParseValidationError<T>(responseText);

                case >= 500:
                    return ApiResult<T>.Fail(ApiRequestStatus.ServerError, $"Server error: {statusCode}");

                default:
                    return ApiResult<T>.Fail(ApiRequestStatus.ServerError, $"HTTP {statusCode}: {responseText}");
            }
        }

        private ApiResult<T> ParseSuccess<T>(string responseText)
        {
            try
            {
                var envelope = JsonConvert.DeserializeObject<Auth.ApiResponseEnvelope<T>>(responseText);

                if (envelope != null && envelope.Success)
                {
                    return ApiResult<T>.Success(envelope.Data, envelope.Message);
                }

                string msg = envelope?.Message ?? "Unknown error";
                return ApiResult<T>.Fail(ApiRequestStatus.ServerError, msg, envelope?.ErrorCode);
            }
            catch (Exception ex)
            {
                return ApiResult<T>.Fail(ApiRequestStatus.ServerError, $"Parse error: {ex.Message}");
            }
        }

        private ApiResult<T> ParseValidationError<T>(string responseText)
        {
            try
            {
                var envelope = JsonConvert.DeserializeObject<Auth.ApiResponseEnvelope<T>>(responseText);
                string msg = envelope?.Message ?? "Validation error";
                return ApiResult<T>.Fail(ApiRequestStatus.ValidationError, msg, envelope?.ErrorCode);
            }
            catch
            {
                return ApiResult<T>.Fail(ApiRequestStatus.ValidationError, responseText);
            }
        }
    }
}
