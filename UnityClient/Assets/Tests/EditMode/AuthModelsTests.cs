using NUnit.Framework;
using RideVerse.Auth;

[TestFixture]
public class AuthModelsTests
{
    [Test]
    public void LoginRequest_SetsFields()
    {
        var req = new LoginRequest { Email = "test@test.com", Password = "pass123" };

        Assert.AreEqual("test@test.com", req.Email);
        Assert.AreEqual("pass123", req.Password);
    }

    [Test]
    public void RegisterRequest_SetsFields()
    {
        var req = new RegisterRequest
        {
            Email = "test@test.com",
            Username = "player1",
            Password = "pass123"
        };

        Assert.AreEqual("test@test.com", req.Email);
        Assert.AreEqual("player1", req.Username);
        Assert.AreEqual("pass123", req.Password);
    }

    [Test]
    public void TokenResponse_DefaultValues()
    {
        var resp = new TokenResponse();

        Assert.IsNull(resp.AccessToken);
        Assert.IsNull(resp.RefreshToken);
        Assert.IsNull(resp.TokenType);
        Assert.AreEqual(0, resp.ExpiresIn);
    }

    [Test]
    public void AccountResponse_DefaultValues()
    {
        var resp = new AccountResponse();

        Assert.IsNull(resp.Id);
        Assert.IsNull(resp.Email);
        Assert.IsNull(resp.Username);
        Assert.IsNull(resp.Role);
        Assert.IsFalse(resp.EmailVerified);
        Assert.IsNull(resp.AccountStatus);
    }

    [Test]
    public void PlayerProfile_DefaultValues()
    {
        var profile = new PlayerProfile();

        Assert.IsNull(profile.Id);
        Assert.AreEqual(0, profile.Level);
        Assert.AreEqual(0, profile.Experience);
        Assert.AreEqual(0.0, profile.Cash);
        Assert.AreEqual(0, profile.Health);
        Assert.AreEqual(0, profile.WantedLevel);
    }

    [Test]
    public void ApiResponseEnvelope_Success()
    {
        var envelope = new ApiResponseEnvelope<TokenResponse>
        {
            Success = true,
            Message = "OK",
            Data = new TokenResponse { AccessToken = "token123" }
        };

        Assert.IsTrue(envelope.Success);
        Assert.AreEqual("OK", envelope.Message);
        Assert.IsNotNull(envelope.Data);
        Assert.AreEqual("token123", envelope.Data.AccessToken);
    }

    [Test]
    public void ApiResponseEnvelope_Error()
    {
        var envelope = new ApiResponseEnvelope<object>
        {
            Success = false,
            Message = "Invalid credentials",
            ErrorCode = "AUTH_001",
            Errors = new[]
            {
                new ApiErrorDetail { Field = "email", Message = "Invalid format" }
            }
        };

        Assert.IsFalse(envelope.Success);
        Assert.AreEqual("AUTH_001", envelope.ErrorCode);
        Assert.AreEqual(1, envelope.Errors.Length);
        Assert.AreEqual("email", envelope.Errors[0].Field);
    }

    [Test]
    public void RefreshRequest_SetsRefreshToken()
    {
        var req = new RefreshRequest { RefreshToken = "refresh_abc" };

        Assert.AreEqual("refresh_abc", req.RefreshToken);
    }

    [Test]
    public void LogoutRequest_SetsRefreshToken()
    {
        var req = new LogoutRequest { RefreshToken = "refresh_xyz" };

        Assert.AreEqual("refresh_xyz", req.RefreshToken);
    }

    [Test]
    public void PlayerStatisticsResponse_DefaultValues()
    {
        var stats = new PlayerStatisticsResponse();

        Assert.AreEqual(0, stats.TotalPlayTimeSeconds);
        Assert.AreEqual(0, stats.MissionsCompleted);
        Assert.AreEqual(0, stats.MissionsFailed);
        Assert.AreEqual(0f, stats.DistanceTraveled);
        Assert.AreEqual(0, stats.VehiclesOwned);
    }
}
