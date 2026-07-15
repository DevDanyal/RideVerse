using NUnit.Framework;
using RideVerse.Auth;

[TestFixture]
public class TokenStorageTests
{
    private TokenStorage _storage;

    [SetUp]
    public void SetUp()
    {
        _storage = new TokenStorage();
        _storage.ClearTokens();
    }

    [TearDown]
    public void TearDown()
    {
        _storage.ClearTokens();
    }

    [Test]
    public void HasTokens_WhenEmpty_ReturnsFalse()
    {
        Assert.IsFalse(_storage.HasTokens);
    }

    [Test]
    public void SaveTokens_ThenGetAccessToken_ReturnsSavedToken()
    {
        _storage.SaveTokens("test_access", "test_refresh");

        Assert.AreEqual("test_access", _storage.GetAccessToken());
    }

    [Test]
    public void SaveTokens_ThenGetRefreshToken_ReturnsSavedToken()
    {
        _storage.SaveTokens("test_access", "test_refresh");

        Assert.AreEqual("test_refresh", _storage.GetRefreshToken());
    }

    [Test]
    public void HasTokens_AfterSave_ReturnsTrue()
    {
        _storage.SaveTokens("access", "refresh");

        Assert.IsTrue(_storage.HasTokens);
    }

    [Test]
    public void ClearTokens_RemovesAllTokens()
    {
        _storage.SaveTokens("access", "refresh");
        _storage.ClearTokens();

        Assert.IsFalse(_storage.HasTokens);
        Assert.AreEqual(string.Empty, _storage.GetAccessToken());
        Assert.AreEqual(string.Empty, _storage.GetRefreshToken());
    }

    [Test]
    public void SavePlayerId_ThenGetPlayerId_ReturnsSavedId()
    {
        _storage.SavePlayerId("player_123");

        Assert.AreEqual("player_123", _storage.GetPlayerId());
    }

    [Test]
    public void SaveDisplayName_ThenGetDisplayName_ReturnsSavedName()
    {
        _storage.SaveDisplayName("TestPlayer");

        Assert.AreEqual("TestPlayer", _storage.GetDisplayName());
    }

    [Test]
    public void ClearTokens_RemovesPlayerIdAndDisplayName()
    {
        _storage.SavePlayerId("p1");
        _storage.SaveDisplayName("Name");
        _storage.ClearTokens();

        Assert.AreEqual(string.Empty, _storage.GetPlayerId());
        Assert.AreEqual(string.Empty, _storage.GetDisplayName());
    }

    [Test]
    public void SaveTokens_OverwritesExistingTokens()
    {
        _storage.SaveTokens("old_access", "old_refresh");
        _storage.SaveTokens("new_access", "new_refresh");

        Assert.AreEqual("new_access", _storage.GetAccessToken());
        Assert.AreEqual("new_refresh", _storage.GetRefreshToken());
    }

    [Test]
    public void GetPlayerId_WhenEmpty_ReturnsEmptyString()
    {
        Assert.AreEqual(string.Empty, _storage.GetPlayerId());
    }
}
