using NUnit.Framework;
using RideVerse.Core;
using UnityEngine;

[TestFixture]
public class PlayerStateTests
{
    [SetUp]
    public void SetUp()
    {
        PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerPosX);
        PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerPosY);
        PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerPosZ);
        PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerRotY);
    }

    [TearDown]
    public void TearDown()
    {
        PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerPosX);
        PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerPosY);
        PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerPosZ);
        PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerRotY);
    }

    [Test]
    public void PlayerPrefs_PositionKeys_AreDefined()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.PlayerPrefs.PlayerPosX));
        Assert.IsFalse(string.IsNullOrEmpty(Constants.PlayerPrefs.PlayerPosY));
        Assert.IsFalse(string.IsNullOrEmpty(Constants.PlayerPrefs.PlayerPosZ));
        Assert.IsFalse(string.IsNullOrEmpty(Constants.PlayerPrefs.PlayerRotY));
    }

    [Test]
    public void PlayerPrefs_PositionKeys_AreUnique()
    {
        Assert.AreNotEqual(Constants.PlayerPrefs.PlayerPosX, Constants.PlayerPrefs.PlayerPosY);
        Assert.AreNotEqual(Constants.PlayerPrefs.PlayerPosY, Constants.PlayerPrefs.PlayerPosZ);
        Assert.AreNotEqual(Constants.PlayerPrefs.PlayerPosZ, Constants.PlayerPrefs.PlayerRotY);
    }

    [Test]
    public void PlayerPrefs_HasSavedPosition_WhenEmpty_ReturnsFalse()
    {
        bool hasPos = PlayerPrefs.HasKey(Constants.PlayerPrefs.PlayerPosX);
        Assert.IsFalse(hasPos);
    }

    [Test]
    public void PlayerPrefs_SaveAndLoadPosition_WorksCorrectly()
    {
        PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerPosX, 10f);
        PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerPosY, 5f);
        PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerPosZ, 20f);
        PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerRotY, 90f);

        float x = PlayerPrefs.GetFloat(Constants.PlayerPrefs.PlayerPosX);
        float y = PlayerPrefs.GetFloat(Constants.PlayerPrefs.PlayerPosY);
        float z = PlayerPrefs.GetFloat(Constants.PlayerPrefs.PlayerPosZ);
        float rotY = PlayerPrefs.GetFloat(Constants.PlayerPrefs.PlayerRotY);

        Assert.AreEqual(10f, x);
        Assert.AreEqual(5f, y);
        Assert.AreEqual(20f, z);
        Assert.AreEqual(90f, rotY);
    }

    [Test]
    public void PlayerPrefs_HasSavedPosition_AfterSave_ReturnsTrue()
    {
        PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerPosX, 1f);
        bool hasPos = PlayerPrefs.HasKey(Constants.PlayerPrefs.PlayerPosX);
        Assert.IsTrue(hasPos);
    }

    [Test]
    public void PlayerPrefs_ClearPosition_RemovesAllKeys()
    {
        PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerPosX, 1f);
        PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerPosY, 2f);
        PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerPosZ, 3f);
        PlayerPrefs.SetFloat(Constants.PlayerPrefs.PlayerRotY, 4f);

        PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerPosX);
        PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerPosY);
        PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerPosZ);
        PlayerPrefs.DeleteKey(Constants.PlayerPrefs.PlayerRotY);

        Assert.IsFalse(PlayerPrefs.HasKey(Constants.PlayerPrefs.PlayerPosX));
        Assert.IsFalse(PlayerPrefs.HasKey(Constants.PlayerPrefs.PlayerPosY));
        Assert.IsFalse(PlayerPrefs.HasKey(Constants.PlayerPrefs.PlayerPosZ));
        Assert.IsFalse(PlayerPrefs.HasKey(Constants.PlayerPrefs.PlayerRotY));
    }
}

[TestFixture]
public class GameManagerLogicTests
{
    [Test]
    public void GameScenes_AllAreDefined()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Scenes.Game));
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Scenes.Login));
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Scenes.MainMenu));
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Scenes.Loading));
    }

    [Test]
    public void GameScenes_GameIsDifferentFromOthers()
    {
        Assert.AreNotEqual(Constants.Scenes.Game, Constants.Scenes.Login);
        Assert.AreNotEqual(Constants.Scenes.Game, Constants.Scenes.MainMenu);
        Assert.AreNotEqual(Constants.Scenes.Game, Constants.Scenes.Loading);
    }

    [Test]
    public void Layers_Ground_IsDefined()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Layers.Ground));
    }

    [Test]
    public void Layers_Player_IsDefined()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Layers.Player));
    }

    [Test]
    public void Tags_Player_IsDefined()
    {
        Assert.IsFalse(string.IsNullOrEmpty(Constants.Tags.Player));
    }
}

[TestFixture]
public class PlayerPositionSyncModelTests
{
    [Test]
    public void SyncInterval_IsReasonable()
    {
        float syncRate = Constants.Network.SendRate;
        Assert.Greater(syncRate, 0f);
        Assert.LessOrEqual(syncRate, 60f);
    }

    [Test]
    public void WsPositionUpdate_InVehicle_FieldsWork()
    {
        var update = new RideVerse.Network.WsPositionUpdate
        {
            PositionX = 1f,
            PositionY = 2f,
            PositionZ = 3f,
            Speed = 5f,
            IsInVehicle = true,
            VehicleId = "honda_cg125"
        };

        Assert.IsTrue(update.IsInVehicle);
        Assert.AreEqual("honda_cg125", update.VehicleId);
        Assert.AreEqual(1f, update.PositionX);
        Assert.AreEqual(5f, update.Speed);
    }

    [Test]
    public void WsPositionUpdate_OnFoot_FieldsWork()
    {
        var update = new RideVerse.Network.WsPositionUpdate
        {
            PositionX = 10f,
            PositionY = 0.5f,
            PositionZ = -5f,
            Speed = 3f,
            IsInVehicle = false,
            VehicleId = null
        };

        Assert.IsFalse(update.IsInVehicle);
        Assert.IsNull(update.VehicleId);
    }
}
