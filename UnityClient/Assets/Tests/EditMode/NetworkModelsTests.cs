using NUnit.Framework;
using RideVerse.Network;
using System.Collections.Generic;

[TestFixture]
public class NetworkModelsTests
{
    [Test]
    public void WsMessage_DefaultValues()
    {
        var msg = new WsMessage();

        Assert.IsNull(msg.Event);
        Assert.IsNull(msg.Data);
    }

    [Test]
    public void WsMessage_WithEventAndData()
    {
        var msg = new WsMessage
        {
            Event = "ping",
            Data = new Dictionary<string, object> { { "ts", 12345 } }
        };

        Assert.AreEqual("ping", msg.Event);
        Assert.IsNotNull(msg.Data);
        Assert.AreEqual(12345, msg.Data["ts"]);
    }

    [Test]
    public void WsPositionUpdate_DefaultValues()
    {
        var pos = new WsPositionUpdate();

        Assert.AreEqual(0f, pos.PositionX);
        Assert.AreEqual(0f, pos.PositionY);
        Assert.AreEqual(0f, pos.PositionZ);
        Assert.AreEqual(0f, pos.Speed);
        Assert.IsFalse(pos.IsInVehicle);
        Assert.IsNull(pos.VehicleId);
    }

    [Test]
    public void WsPositionUpdate_SetsAllFields()
    {
        var pos = new WsPositionUpdate
        {
            PositionX = 1.0f, PositionY = 2.0f, PositionZ = 3.0f,
            RotationX = 10f, RotationY = 20f, RotationZ = 30f,
            VelocityX = 0.1f, VelocityY = 0.2f, VelocityZ = 0.3f,
            Speed = 5.5f,
            IsInVehicle = true,
            VehicleId = "v_123"
        };

        Assert.AreEqual(1.0f, pos.PositionX);
        Assert.AreEqual(2.0f, pos.PositionY);
        Assert.AreEqual(3.0f, pos.PositionZ);
        Assert.AreEqual(5.5f, pos.Speed);
        Assert.IsTrue(pos.IsInVehicle);
        Assert.AreEqual("v_123", pos.VehicleId);
    }

    [Test]
    public void WsVehicleUpdate_DefaultValues()
    {
        var v = new WsVehicleUpdate();

        Assert.AreEqual(0f, v.Speed);
        Assert.AreEqual(0f, v.Health);
        Assert.AreEqual(0f, v.Fuel);
        Assert.AreEqual(0, v.CurrentGear);
        Assert.AreEqual(0f, v.Rpm);
    }

    [Test]
    public void WsChatMessage_SetsFields()
    {
        var chat = new WsChatMessage
        {
            MessageId = "msg_1",
            PlayerId = "p_1",
            DisplayName = "Player1",
            Message = "Hello",
            MessageType = "normal",
            RoomId = "room_1",
            Timestamp = "2025-01-01T00:00:00Z"
        };

        Assert.AreEqual("msg_1", chat.MessageId);
        Assert.AreEqual("Player1", chat.DisplayName);
        Assert.AreEqual("Hello", chat.Message);
        Assert.AreEqual("normal", chat.MessageType);
    }

    [Test]
    public void WsAuthSuccess_SetsFields()
    {
        var auth = new WsAuthSuccess
        {
            PlayerId = "p_1",
            DisplayName = "TestUser",
            ConnectionId = "conn_1"
        };

        Assert.AreEqual("p_1", auth.PlayerId);
        Assert.AreEqual("TestUser", auth.DisplayName);
        Assert.AreEqual("conn_1", auth.ConnectionId);
    }

    [Test]
    public void WsRoomInfo_DefaultValues()
    {
        var room = new WsRoomInfo();

        Assert.IsNull(room.RoomId);
        Assert.IsNull(room.RoomName);
        Assert.IsNull(room.RoomType);
        Assert.AreEqual(0, room.MaxPlayers);
        Assert.AreEqual(0, room.CurrentPlayers);
        Assert.IsNull(room.Members);
    }

    [Test]
    public void WsNotification_SetsFields()
    {
        var notif = new WsNotification
        {
            NotificationId = "n_1",
            Title = "Test",
            Message = "Notification",
            NotificationType = "info"
        };

        Assert.AreEqual("n_1", notif.NotificationId);
        Assert.AreEqual("Test", notif.Title);
        Assert.AreEqual("info", notif.NotificationType);
    }

    [Test]
    public void WsEventTypes_ContainsAllExpectedEvents()
    {
        Assert.AreEqual("auth_success", WsEventTypes.AuthSuccess);
        Assert.AreEqual("auth_failure", WsEventTypes.AuthFailure);
        Assert.AreEqual("ping", WsEventTypes.Ping);
        Assert.AreEqual("pong", WsEventTypes.Pong);
        Assert.AreEqual("position_update", WsEventTypes.PositionUpdate);
        Assert.AreEqual("position_broadcast", WsEventTypes.PositionBroadcast);
        Assert.AreEqual("vehicle_update", WsEventTypes.VehicleUpdate);
        Assert.AreEqual("vehicle_broadcast", WsEventTypes.VehicleBroadcast);
        Assert.AreEqual("chat_send", WsEventTypes.ChatSend);
        Assert.AreEqual("chat_message", WsEventTypes.ChatMessage);
        Assert.AreEqual("room_create", WsEventTypes.RoomCreate);
        Assert.AreEqual("room_join", WsEventTypes.RoomJoin);
        Assert.AreEqual("room_leave", WsEventTypes.RoomLeave);
        Assert.AreEqual("room_list", WsEventTypes.RoomList);
        Assert.AreEqual("room_info", WsEventTypes.RoomInfo);
        Assert.AreEqual("room_update", WsEventTypes.RoomUpdate);
        Assert.AreEqual("room_destroy", WsEventTypes.RoomDestroy);
        Assert.AreEqual("player_joined", WsEventTypes.PlayerJoined);
        Assert.AreEqual("player_left", WsEventTypes.PlayerLeft);
        Assert.AreEqual("presence_update", WsEventTypes.PresenceUpdate);
        Assert.AreEqual("friends_online", WsEventTypes.FriendsOnline);
        Assert.AreEqual("notification", WsEventTypes.Notification);
        Assert.AreEqual("notification_ack", WsEventTypes.NotificationAck);
        Assert.AreEqual("error", WsEventTypes.Error);
        Assert.AreEqual("rate_limited", WsEventTypes.RateLimited);
    }

    [Test]
    public void WsCreateRoomRequest_DefaultValues()
    {
        var req = new WsCreateRoomRequest();

        Assert.IsNull(req.RoomName);
        Assert.AreEqual("free_roam", req.RoomType);
        Assert.AreEqual(10, req.MaxPlayers);
        Assert.AreEqual("global", req.Region);
        Assert.IsNull(req.Password);
        Assert.IsNull(req.MapName);
    }

    [Test]
    public void WsJoinRoomRequest_SetsFields()
    {
        var req = new WsJoinRoomRequest
        {
            RoomId = "room_abc",
            Password = "secret"
        };

        Assert.AreEqual("room_abc", req.RoomId);
        Assert.AreEqual("secret", req.Password);
    }

    [Test]
    public void WsFriendPresence_SetsFields()
    {
        var friend = new WsFriendPresence
        {
            FriendPlayerId = "f_1",
            DisplayName = "Friend1",
            Status = "online",
            CurrentRoomId = "room_1"
        };

        Assert.AreEqual("f_1", friend.FriendPlayerId);
        Assert.AreEqual("online", friend.Status);
        Assert.AreEqual("room_1", friend.CurrentRoomId);
    }

    [Test]
    public void WsRoomMember_SetsFields()
    {
        var member = new WsRoomMember
        {
            PlayerId = "p_1",
            DisplayName = "Player1",
            JoinedAt = "2025-01-01T00:00:00Z"
        };

        Assert.AreEqual("p_1", member.PlayerId);
        Assert.AreEqual("Player1", member.DisplayName);
    }
}
