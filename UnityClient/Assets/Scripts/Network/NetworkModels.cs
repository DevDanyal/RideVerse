using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace RideVerse.Network
{
    [Serializable]
    public class WsMessage
    {
        [JsonProperty("event")] public string Event;
        [JsonProperty("data")] public Dictionary<string, object> Data;
    }

    [Serializable]
    public class WsPositionUpdate
    {
        [JsonProperty("position_x")] public float PositionX;
        [JsonProperty("position_y")] public float PositionY;
        [JsonProperty("position_z")] public float PositionZ;
        [JsonProperty("rotation_x")] public float RotationX;
        [JsonProperty("rotation_y")] public float RotationY;
        [JsonProperty("rotation_z")] public float RotationZ;
        [JsonProperty("velocity_x")] public float VelocityX;
        [JsonProperty("velocity_y")] public float VelocityY;
        [JsonProperty("velocity_z")] public float VelocityZ;
        [JsonProperty("speed")] public float Speed;
        [JsonProperty("is_in_vehicle")] public bool IsInVehicle;
        [JsonProperty("vehicle_id")] public string VehicleId;
    }

    [Serializable]
    public class WsVehicleUpdate
    {
        [JsonProperty("vehicle_id")] public string VehicleId;
        [JsonProperty("position_x")] public float PositionX;
        [JsonProperty("position_y")] public float PositionY;
        [JsonProperty("position_z")] public float PositionZ;
        [JsonProperty("rotation_x")] public float RotationX;
        [JsonProperty("rotation_y")] public float RotationY;
        [JsonProperty("rotation_z")] public float RotationZ;
        [JsonProperty("velocity_x")] public float VelocityX;
        [JsonProperty("velocity_y")] public float VelocityY;
        [JsonProperty("velocity_z")] public float VelocityZ;
        [JsonProperty("speed")] public float Speed;
        [JsonProperty("health")] public float Health;
        [JsonProperty("fuel")] public float Fuel;
        [JsonProperty("current_gear")] public int CurrentGear;
        [JsonProperty("rpm")] public float Rpm;
    }

    [Serializable]
    public class WsChatMessage
    {
        [JsonProperty("message_id")] public string MessageId;
        [JsonProperty("player_id")] public string PlayerId;
        [JsonProperty("display_name")] public string DisplayName;
        [JsonProperty("message")] public string Message;
        [JsonProperty("message_type")] public string MessageType;
        [JsonProperty("room_id")] public string RoomId;
        [JsonProperty("timestamp")] public string Timestamp;
    }

    [Serializable]
    public class WsRoomInfo
    {
        [JsonProperty("room_id")] public string RoomId;
        [JsonProperty("room_name")] public string RoomName;
        [JsonProperty("room_type")] public string RoomType;
        [JsonProperty("room_status")] public string RoomStatus;
        [JsonProperty("max_players")] public int MaxPlayers;
        [JsonProperty("current_players")] public int CurrentPlayers;
        [JsonProperty("region")] public string Region;
        [JsonProperty("map_name")] public string MapName;
        [JsonProperty("members")] public List<WsRoomMember> Members;
    }

    [Serializable]
    public class WsRoomMember
    {
        [JsonProperty("player_id")] public string PlayerId;
        [JsonProperty("display_name")] public string DisplayName;
        [JsonProperty("joined_at")] public string JoinedAt;
    }

    [Serializable]
    public class WsAuthSuccess
    {
        [JsonProperty("player_id")] public string PlayerId;
        [JsonProperty("display_name")] public string DisplayName;
        [JsonProperty("connection_id")] public string ConnectionId;
    }

    [Serializable]
    public class WsNotification
    {
        [JsonProperty("notification_id")] public string NotificationId;
        [JsonProperty("title")] public string Title;
        [JsonProperty("message")] public string Message;
        [JsonProperty("notification_type")] public string NotificationType;
        [JsonProperty("data")] public Dictionary<string, object> Data;
        [JsonProperty("timestamp")] public string Timestamp;
    }

    [Serializable]
    public class WsFriendPresence
    {
        [JsonProperty("friend_player_id")] public string FriendPlayerId;
        [JsonProperty("display_name")] public string DisplayName;
        [JsonProperty("status")] public string Status;
        [JsonProperty("current_room_id")] public string CurrentRoomId;
    }

    [Serializable]
    public class WsCreateRoomRequest
    {
        [JsonProperty("room_name")] public string RoomName;
        [JsonProperty("room_type")] public string RoomType = "free_roam";
        [JsonProperty("max_players")] public int MaxPlayers = 10;
        [JsonProperty("region")] public string Region = "global";
        [JsonProperty("password")] public string Password;
        [JsonProperty("map_name")] public string MapName;
    }

    [Serializable]
    public class WsJoinRoomRequest
    {
        [JsonProperty("room_id")] public string RoomId;
        [JsonProperty("password")] public string Password;
    }

    public static class WsEventTypes
    {
        public const string AuthSuccess = "auth_success";
        public const string AuthFailure = "auth_failure";
        public const string Ping = "ping";
        public const string Pong = "pong";
        public const string PositionUpdate = "position_update";
        public const string PositionBroadcast = "position_broadcast";
        public const string VehicleUpdate = "vehicle_update";
        public const string VehicleBroadcast = "vehicle_broadcast";
        public const string ChatSend = "chat_send";
        public const string ChatMessage = "chat_message";
        public const string RoomCreate = "room_create";
        public const string RoomJoin = "room_join";
        public const string RoomLeave = "room_leave";
        public const string RoomList = "room_list";
        public const string RoomInfo = "room_info";
        public const string RoomUpdate = "room_update";
        public const string RoomDestroy = "room_destroy";
        public const string PlayerJoined = "player_joined";
        public const string PlayerLeft = "player_left";
        public const string PresenceUpdate = "presence_update";
        public const string FriendsOnline = "friends_online";
        public const string Notification = "notification";
        public const string NotificationAck = "notification_ack";
        public const string Error = "error";
        public const string RateLimited = "rate_limited";
    }
}
