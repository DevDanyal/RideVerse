using System;
using Newtonsoft.Json;

namespace RideVerse.Auth
{
    [Serializable]
    public class LoginRequest
    {
        [JsonProperty("email")] public string Email;
        [JsonProperty("password")] public string Password;
    }

    [Serializable]
    public class RegisterRequest
    {
        [JsonProperty("email")] public string Email;
        [JsonProperty("username")] public string Username;
        [JsonProperty("password")] public string Password;
    }

    [Serializable]
    public class RefreshRequest
    {
        [JsonProperty("refresh_token")] public string RefreshToken;
    }

    [Serializable]
    public class LogoutRequest
    {
        [JsonProperty("refresh_token")] public string RefreshToken;
    }

    [Serializable]
    public class TokenResponse
    {
        [JsonProperty("access_token")] public string AccessToken;
        [JsonProperty("refresh_token")] public string RefreshToken;
        [JsonProperty("token_type")] public string TokenType;
        [JsonProperty("expires_in")] public int ExpiresIn;
    }

    [Serializable]
    public class AccountResponse
    {
        [JsonProperty("id")] public string Id;
        [JsonProperty("email")] public string Email;
        [JsonProperty("username")] public string Username;
        [JsonProperty("role")] public string Role;
        [JsonProperty("email_verified")] public bool EmailVerified;
        [JsonProperty("account_status")] public string AccountStatus;
        [JsonProperty("created_at")] public string CreatedAt;
    }

    [Serializable]
    public class PlayerProfile
    {
        [JsonProperty("id")] public string Id;
        [JsonProperty("account_id")] public string AccountId;
        [JsonProperty("display_name")] public string DisplayName;
        [JsonProperty("level")] public int Level;
        [JsonProperty("experience")] public int Experience;
        [JsonProperty("cash")] public double Cash;
        [JsonProperty("bank_balance")] public double BankBalance;
        [JsonProperty("reputation")] public int Reputation;
        [JsonProperty("health")] public int Health;
        [JsonProperty("stamina")] public int Stamina;
        [JsonProperty("energy")] public int Energy;
        [JsonProperty("wanted_level")] public int WantedLevel;
        [JsonProperty("current_server")] public string CurrentServer;
        [JsonProperty("current_region")] public string CurrentRegion;
        [JsonProperty("created_at")] public string CreatedAt;
    }

    [Serializable]
    public class PlayerStatisticsResponse
    {
        [JsonProperty("total_play_time_seconds")] public int TotalPlayTimeSeconds;
        [JsonProperty("missions_completed")] public int MissionsCompleted;
        [JsonProperty("missions_failed")] public int MissionsFailed;
        [JsonProperty("distance_traveled")] public float DistanceTraveled;
        [JsonProperty("vehicles_owned")] public int VehiclesOwned;
        [JsonProperty("weapons_owned")] public int WeaponsOwned;
        [JsonProperty("total_earned")] public double TotalEarned;
        [JsonProperty("total_spent")] public double TotalSpent;
    }

    [Serializable]
    public class ApiResponseEnvelope<T>
    {
        [JsonProperty("success")] public bool Success;
        [JsonProperty("message")] public string Message;
        [JsonProperty("data")] public T Data;
        [JsonProperty("error_code")] public string ErrorCode;
        [JsonProperty("errors")] public ApiErrorDetail[] Errors;
    }

    [Serializable]
    public class ApiErrorDetail
    {
        [JsonProperty("field")] public string Field;
        [JsonProperty("message")] public string Message;
    }
}
