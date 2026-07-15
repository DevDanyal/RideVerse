using NUnit.Framework;
using RideVerse.Player;

[TestFixture]
public class PlayerProfileTests
{
    [Test]
    public void PlayerProfileData_DefaultValues()
    {
        var profile = new PlayerProfileData();

        Assert.IsNull(profile.PlayerId);
        Assert.IsNull(profile.AccountId);
        Assert.IsNull(profile.DisplayName);
        Assert.AreEqual(0, profile.Level);
        Assert.AreEqual(0, profile.Experience);
        Assert.AreEqual(0.0, profile.Cash);
        Assert.AreEqual(0, profile.Health);
        Assert.AreEqual(0, profile.WantedLevel);
    }

    [Test]
    public void PlayerProfileData_SetsFields()
    {
        var profile = new PlayerProfileData
        {
            PlayerId = "p_1",
            AccountId = "a_1",
            DisplayName = "TestPlayer",
            Level = 10,
            Experience = 5000,
            Cash = 10000.50,
            BankBalance = 50000.00,
            Reputation = 100,
            Health = 80,
            Stamina = 90,
            Energy = 70,
            WantedLevel = 2
        };

        Assert.AreEqual("p_1", profile.PlayerId);
        Assert.AreEqual("TestPlayer", profile.DisplayName);
        Assert.AreEqual(10, profile.Level);
        Assert.AreEqual(5000, profile.Experience);
        Assert.AreEqual(10000.50, profile.Cash);
        Assert.AreEqual(80, profile.Health);
        Assert.AreEqual(2, profile.WantedLevel);
    }

    [Test]
    public void FromApiProfile_MapsFieldsCorrectly()
    {
        var apiProfile = new Auth.PlayerProfile
        {
            Id = "id_123",
            AccountId = "acc_456",
            DisplayName = "ApiPlayer",
            Level = 5,
            Experience = 2500,
            Cash = 7500.00,
            BankBalance = 30000.00,
            Reputation = 50,
            Health = 100,
            Stamina = 80,
            Energy = 90,
            WantedLevel = 1
        };

        var profile = PlayerProfileData.FromApiProfile(apiProfile);

        Assert.AreEqual("id_123", profile.PlayerId);
        Assert.AreEqual("acc_456", profile.AccountId);
        Assert.AreEqual("ApiPlayer", profile.DisplayName);
        Assert.AreEqual(5, profile.Level);
        Assert.AreEqual(2500, profile.Experience);
        Assert.AreEqual(7500.00, profile.Cash);
        Assert.AreEqual(30000.00, profile.BankBalance);
        Assert.AreEqual(50, profile.Reputation);
        Assert.AreEqual(100, profile.Health);
        Assert.AreEqual(80, profile.Stamina);
        Assert.AreEqual(90, profile.Energy);
        Assert.AreEqual(1, profile.WantedLevel);
    }

    [Test]
    public void FromApiProfile_HandlesZeroValues()
    {
        var apiProfile = new Auth.PlayerProfile
        {
            Id = "id_0",
            AccountId = "acc_0",
            DisplayName = "NewPlayer",
            Level = 1,
            Experience = 0,
            Cash = 0,
            BankBalance = 0,
            Reputation = 0,
            Health = 100,
            Stamina = 100,
            Energy = 100,
            WantedLevel = 0
        };

        var profile = PlayerProfileData.FromApiProfile(apiProfile);

        Assert.AreEqual(1, profile.Level);
        Assert.AreEqual(0, profile.Experience);
        Assert.AreEqual(0.0, profile.Cash);
        Assert.AreEqual(0, profile.WantedLevel);
    }
}
