using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;
using RideVerse.Auth;
using RideVerse.Core;

namespace RideVerse.Network
{
    public class NetworkManager : Core.Singleton<NetworkManager>
    {
        [SerializeField] private bool _autoReconnect = true;

        private WebSocketClient _webSocket;
        private ReconnectHandler _reconnectHandler;
        private Coroutine _sendCoroutine;
        private float _lastSendTime;

        private readonly Dictionary<string, Action<WsMessage>> _eventHandlers = new Dictionary<string, Action<WsMessage>>();
        private readonly Dictionary<string, WsPositionUpdate> _remotePlayerPositions = new Dictionary<string, WsPositionUpdate>();

        public bool IsConnected => _webSocket != null && _webSocket.IsConnected;
        public float LatencyMs => _webSocket?.LatencyMs ?? 0f;
        public string PlayerId { get; private set; }
        public string DisplayName { get; private set; }
        public string ConnectionId { get; private set; }

        public event Action OnConnected;
        public event Action OnDisconnected;
        public event Action<string> OnError;
        public event Action<string, string> OnPlayerJoined;
        public event Action<string> OnPlayerLeft;
        public event Action<string, WsPositionUpdate> OnPlayerPositionUpdated;
        public event Action<WsChatMessage> OnChatMessage;
        public event Action<WsNotification> OnNotification;
        public event Action<WsRoomInfo> OnRoomInfo;
        public event Action<List<WsFriendPresence>> OnFriendsOnline;

        private string WebSocketUrl
        {
            get
            {
                string token = AuthManager.Instance?.AccessToken;
                if (string.IsNullOrEmpty(token))
                {
                    return null;
                }
                return Constants.Api.WsBaseUrl + Constants.Api.ApiPrefix + Constants.Api.Multiplayer.WsPath + token;
            }
        }

        public void Initialize()
        {
            _webSocket = new WebSocketClient();
            _reconnectHandler = new ReconnectHandler();

            _webSocket.OnConnected += HandleConnected;
            _webSocket.OnDisconnected += HandleDisconnected;
            _webSocket.OnError += HandleError;
            _webSocket.OnMessage += HandleMessage;

            _reconnectHandler.Initialize(Connect);
            _reconnectHandler.OnReconnectFailed += HandleReconnectFailed;

            RegisterDefaultHandlers();

            Debug.Log("[NetworkManager] Initialized");
        }

        private void OnDestroy()
        {
            Disconnect();

            if (_webSocket != null)
            {
                _webSocket.OnConnected -= HandleConnected;
                _webSocket.OnDisconnected -= HandleDisconnected;
                _webSocket.OnError -= HandleError;
                _webSocket.OnMessage -= HandleMessage;
                _webSocket.Dispose();
            }
        }

        public void Connect()
        {
            string url = WebSocketUrl;
            if (string.IsNullOrEmpty(url))
            {
                Debug.LogWarning("[NetworkManager] Cannot connect: no auth token");
                return;
            }

            Debug.Log("[NetworkManager] Connecting...");
            _webSocket.Connect(url);
        }

        public void Disconnect()
        {
            StopSendLoop();
            _webSocket?.Disconnect();
            _reconnectHandler?.Reset();
            _remotePlayerPositions.Clear();
        }

        public void SendEvent(string eventName, object data = null)
        {
            _webSocket?.Send(eventName, data);
        }

        public void SendPosition(WsPositionUpdate position)
        {
            SendEvent(WsEventTypes.PositionUpdate, position);
        }

        public void SendVehicleUpdate(WsVehicleUpdate vehicle)
        {
            SendEvent(WsEventTypes.VehicleUpdate, vehicle);
        }

        public void SendChat(string message, string messageType = "normal")
        {
            SendEvent(WsEventTypes.ChatSend, new { message, message_type = messageType });
        }

        public void JoinRoom(string roomId, string password = null)
        {
            SendEvent(WsEventTypes.RoomJoin, new WsJoinRoomRequest
            {
                RoomId = roomId,
                Password = password
            });
        }

        public void LeaveRoom(string roomId = null)
        {
            SendEvent(WsEventTypes.RoomLeave, roomId != null ? new { room_id = roomId } : null);
        }

        public void CreateRoom(WsCreateRoomRequest request)
        {
            SendEvent(WsEventTypes.RoomCreate, request);
        }

        public void ListRooms(string roomType = null, string region = null, int page = 1, int perPage = 20)
        {
            SendEvent(WsEventTypes.RoomList, new
            {
                room_type = roomType,
                region = region,
                page,
                per_page = perPage
            });
        }

        public void SendNotificationAck(string notificationId)
        {
            SendEvent(WsEventTypes.NotificationAck, new { notification_id = notificationId });
        }

        public WsPositionUpdate GetRemotePlayerPosition(string playerId)
        {
            _remotePlayerPositions.TryGetValue(playerId, out var pos);
            return pos;
        }

        public Dictionary<string, WsPositionUpdate> GetAllRemotePositions()
        {
            return new Dictionary<string, WsPositionUpdate>(_remotePlayerPositions);
        }

        public void RegisterHandler(string eventName, Action<WsMessage> handler)
        {
            if (_eventHandlers.ContainsKey(eventName))
            {
                _eventHandlers[eventName] += handler;
            }
            else
            {
                _eventHandlers[eventName] = handler;
            }
        }

        public void UnregisterHandler(string eventName, Action<WsMessage> handler)
        {
            if (_eventHandlers.ContainsKey(eventName))
            {
                _eventHandlers[eventName] -= handler;
            }
        }

        private void RegisterDefaultHandlers()
        {
            RegisterHandler(WsEventTypes.AuthSuccess, HandleAuthSuccess);
            RegisterHandler(WsEventTypes.Pong, HandlePong);
            RegisterHandler(WsEventTypes.PositionBroadcast, HandlePositionBroadcast);
            RegisterHandler(WsEventTypes.VehicleBroadcast, HandleVehicleBroadcast);
            RegisterHandler(WsEventTypes.ChatMessage, HandleChatMessage);
            RegisterHandler(WsEventTypes.PlayerJoined, HandlePlayerJoined);
            RegisterHandler(WsEventTypes.PlayerLeft, HandlePlayerLeft);
            RegisterHandler(WsEventTypes.Notification, HandleNotification);
            RegisterHandler(WsEventTypes.RoomInfo, HandleRoomInfo);
            RegisterHandler(WsEventTypes.RoomUpdate, HandleRoomInfo);
            RegisterHandler(WsEventTypes.FriendsOnline, HandleFriendsOnline);
            RegisterHandler(WsEventTypes.Error, HandleServerError);
        }

        private void HandleConnected()
        {
            _reconnectHandler.OnConnected();
            StartSendLoop();
            OnConnected?.Invoke();
        }

        private void HandleDisconnected()
        {
            StopSendLoop();
            OnDisconnected?.Invoke();

            if (_autoReconnect && AuthManager.Instance.IsAuthenticated)
            {
                string url = WebSocketUrl;
                if (!string.IsNullOrEmpty(url))
                {
                    StartCoroutine(_reconnectHandler.ReconnectCoroutine(url));
                }
            }
        }

        private void HandleError(string error)
        {
            Debug.LogError($"[NetworkManager] Error: {error}");
            OnError?.Invoke(error);
        }

        private void HandleReconnectFailed()
        {
            Debug.LogError("[NetworkManager] Reconnection failed");
        }

        private void HandleMessage(WsMessage message)
        {
            if (string.IsNullOrEmpty(message.Event))
            {
                return;
            }

            if (_eventHandlers.TryGetValue(message.Event, out var handler))
            {
                try
                {
                    handler.Invoke(message);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[NetworkManager] Handler error for {message.Event}: {ex.Message}");
                }
            }
        }

        private void HandleAuthSuccess(WsMessage message)
        {
            var data = JsonConvert.DeserializeObject<WsAuthSuccess>(
                JsonConvert.SerializeObject(message.Data));

            if (data != null)
            {
                PlayerId = data.PlayerId;
                DisplayName = data.DisplayName;
                ConnectionId = data.ConnectionId;

                var tokenStorage = new TokenStorage();
                tokenStorage.SavePlayerId(data.PlayerId);
                tokenStorage.SaveDisplayName(data.DisplayName);

                Debug.Log($"[NetworkManager] Authenticated as {data.DisplayName} ({data.PlayerId})");
            }
        }

        private void HandlePong(WsMessage message)
        {
            _webSocket?.HandlePong();
        }

        private void HandlePositionBroadcast(WsMessage message)
        {
            var pos = JsonConvert.DeserializeObject<WsPositionUpdate>(
                JsonConvert.SerializeObject(message.Data));

            if (pos != null && message.Data.ContainsKey("player_id"))
            {
                string playerId = message.Data["player_id"].ToString();
                _remotePlayerPositions[playerId] = pos;
                OnPlayerPositionUpdated?.Invoke(playerId, pos);
            }
        }

        private void HandleVehicleBroadcast(WsMessage message)
        {
        }

        private void HandleChatMessage(WsMessage message)
        {
            var chat = JsonConvert.DeserializeObject<WsChatMessage>(
                JsonConvert.SerializeObject(message.Data));

            if (chat != null)
            {
                OnChatMessage?.Invoke(chat);
            }
        }

        private void HandlePlayerJoined(WsMessage message)
        {
            if (message.Data != null && message.Data.ContainsKey("player_id"))
            {
                string playerId = message.Data["player_id"].ToString();
                string displayName = message.Data.ContainsKey("display_name")
                    ? message.Data["display_name"].ToString() : "Unknown";
                OnPlayerJoined?.Invoke(playerId, displayName);
            }
        }

        private void HandlePlayerLeft(WsMessage message)
        {
            if (message.Data != null && message.Data.ContainsKey("player_id"))
            {
                string playerId = message.Data["player_id"].ToString();
                _remotePlayerPositions.Remove(playerId);
                OnPlayerLeft?.Invoke(playerId);
            }
        }

        private void HandleNotification(WsMessage message)
        {
            var notif = JsonConvert.DeserializeObject<WsNotification>(
                JsonConvert.SerializeObject(message.Data));

            if (notif != null)
            {
                OnNotification?.Invoke(notif);
            }
        }

        private void HandleRoomInfo(WsMessage message)
        {
            var room = JsonConvert.DeserializeObject<WsRoomInfo>(
                JsonConvert.SerializeObject(message.Data));

            if (room != null)
            {
                OnRoomInfo?.Invoke(room);
            }
        }

        private void HandleFriendsOnline(WsMessage message)
        {
            if (message.Data != null && message.Data.ContainsKey("friends"))
            {
                var friendsJson = JsonConvert.SerializeObject(message.Data["friends"]);
                var friends = JsonConvert.DeserializeObject<List<WsFriendPresence>>(friendsJson);
                if (friends != null)
                {
                    OnFriendsOnline?.Invoke(friends);
                }
            }
        }

        private void HandleServerError(WsMessage message)
        {
            string errorMsg = message.Data?.ContainsKey("message") == true
                ? message.Data["message"].ToString() : "Unknown server error";
            Debug.LogError($"[NetworkManager] Server error: {errorMsg}");
            OnError?.Invoke(errorMsg);
        }

        private void StartSendLoop()
        {
            if (_sendCoroutine == null)
            {
                _sendCoroutine = StartCoroutine(SendLoopCoroutine());
            }
        }

        private void StopSendLoop()
        {
            if (_sendCoroutine != null)
            {
                StopCoroutine(_sendCoroutine);
                _sendCoroutine = null;
            }
        }

        private IEnumerator SendLoopCoroutine()
        {
            while (IsConnected)
            {
                yield return new WaitForSeconds(1f / Constants.Network.SendRate);
            }
        }
    }
}
