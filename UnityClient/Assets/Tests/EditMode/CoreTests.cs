using NUnit.Framework;
using RideVerse.Core;

[TestFixture]
public class ApiResponseTests
{
    [Test]
    public void ApiResult_Success()
    {
        var result = ApiResult<string>.Success("data", "OK");

        Assert.IsTrue(result.IsSuccess);
        Assert.AreEqual("data", result.Data);
        Assert.AreEqual("OK", result.Message);
        Assert.AreEqual(ApiRequestStatus.Success, result.Status);
    }

    [Test]
    public void ApiResult_Fail()
    {
        var result = ApiResult<int>.Fail(ApiRequestStatus.Unauthorized, "Not authed", "ERR_01");

        Assert.IsFalse(result.IsSuccess);
        Assert.AreEqual(0, result.Data);
        Assert.AreEqual("Not authed", result.Message);
        Assert.AreEqual("ERR_01", result.ErrorCode);
        Assert.AreEqual(ApiRequestStatus.Unauthorized, result.Status);
    }

    [Test]
    public void ApiResult_IsSuccess_OnlyTrueForSuccessStatus()
    {
        Assert.IsTrue(ApiResult<object>.Success(null).IsSuccess);
        Assert.IsFalse(ApiResult<object>.Fail(ApiRequestStatus.Unauthorized, "").IsSuccess);
        Assert.IsFalse(ApiResult<object>.Fail(ApiRequestStatus.Forbidden, "").IsSuccess);
        Assert.IsFalse(ApiResult<object>.Fail(ApiRequestStatus.NotFound, "").IsSuccess);
        Assert.IsFalse(ApiResult<object>.Fail(ApiRequestStatus.ValidationError, "").IsSuccess);
        Assert.IsFalse(ApiResult<object>.Fail(ApiRequestStatus.ServerError, "").IsSuccess);
        Assert.IsFalse(ApiResult<object>.Fail(ApiRequestStatus.NetworkError, "").IsSuccess);
        Assert.IsFalse(ApiResult<object>.Fail(ApiRequestStatus.Cancelled, "").IsSuccess);
    }

    [Test]
    public void ApiResult_NullData()
    {
        var result = ApiResult<object>.Success(null);

        Assert.IsTrue(result.IsSuccess);
        Assert.IsNull(result.Data);
    }
}

[TestFixture]
public class ConstantsTests
{
    [Test]
    public void ApiPaths_StartWithSlash()
    {
        Assert.IsTrue(Constants.Api.Auth.Login.StartsWith("/"));
        Assert.IsTrue(Constants.Api.Auth.Register.StartsWith("/"));
        Assert.IsTrue(Constants.Api.Auth.Refresh.StartsWith("/"));
        Assert.IsTrue(Constants.Api.Auth.Logout.StartsWith("/"));
        Assert.IsTrue(Constants.Api.Auth.Me.StartsWith("/"));
        Assert.IsTrue(Constants.Api.Players.Me.StartsWith("/"));
        Assert.IsTrue(Constants.Api.Multiplayer.Rooms.StartsWith("/"));
    }

    [Test]
    public void NetworkConstants_HaveReasonableValues()
    {
        Assert.Greater(Constants.Network.HeartbeatInterval, 0f);
        Assert.Greater(Constants.Network.HeartbeatTimeout, 0f);
        Assert.Greater(Constants.Network.MaxReconnectAttempts, 0);
        Assert.Greater(Constants.Network.SendRate, 0f);
        Assert.Greater(Constants.Network.ReconnectMinDelay, 0f);
        Assert.Greater(Constants.Network.ReconnectMaxDelay, Constants.Network.ReconnectMinDelay);
    }

    [Test]
    public void PlayerConstants_HaveReasonableValues()
    {
        Assert.Greater(Constants.Player.WalkSpeed, 0f);
        Assert.Greater(Constants.Player.SprintSpeed, Constants.Player.WalkSpeed);
        Assert.Greater(Constants.Player.JumpForce, 0f);
        Assert.Less(Constants.Player.Gravity, 0f);
        Assert.Greater(Constants.Player.RotationSpeed, 0f);
    }

    [Test]
    public void SceneNames_AreNotEmpty()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Scenes.Loading));
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Scenes.Login));
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Scenes.MainMenu));
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Scenes.Game));
    }

    [Test]
    public void Tags_AreNotEmpty()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Tags.Player));
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Tags.MainCamera));
    }
}

[TestFixture]
public class GameEventsTests
{
    [SetUp]
    public void SetUp()
    {
        GameEvents.ClearAll();
    }

    [TearDown]
    public void TearDown()
    {
        GameEvents.ClearAll();
    }

    [Test]
    public void OnGameInitialized_FiresCorrectly()
    {
        bool fired = false;
        GameEvents.OnGameInitialized += () => fired = true;

        GameEvents.TriggerGameInitialized();

        Assert.IsTrue(fired);
    }

    [Test]
    public void OnSceneLoadCompleted_FiresWithCorrectSceneName()
    {
        string receivedScene = null;
        GameEvents.OnSceneLoadCompleted += scene => receivedScene = scene;

        GameEvents.TriggerSceneLoadCompleted("TestScene");

        Assert.AreEqual("TestScene", receivedScene);
    }

    [Test]
    public void OnSceneLoadStarted_FiresCorrectly()
    {
        bool fired = false;
        GameEvents.OnSceneLoadStarted += () => fired = true;

        GameEvents.TriggerSceneLoadStarted();

        Assert.IsTrue(fired);
    }

    [Test]
    public void ClearAll_RemovesAllHandlers()
    {
        bool fired1 = false, fired2 = false;
        GameEvents.OnGameInitialized += () => fired1 = true;
        GameEvents.OnSceneLoadStarted += () => fired2 = true;

        GameEvents.ClearAll();
        GameEvents.TriggerGameInitialized();
        GameEvents.TriggerSceneLoadStarted();

        Assert.IsFalse(fired1);
        Assert.IsFalse(fired2);
    }

    [Test]
    public void MultipleHandlers_AllFire()
    {
        int count = 0;
        GameEvents.OnGameInitialized += () => count++;
        GameEvents.OnGameInitialized += () => count++;
        GameEvents.OnGameInitialized += () => count++;

        GameEvents.TriggerGameInitialized();

        Assert.AreEqual(3, count);
    }
}
