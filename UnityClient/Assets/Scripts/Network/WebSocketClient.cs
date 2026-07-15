using System;
using System.Collections.Concurrent;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using Newtonsoft.Json;
using RideVerse.Core;

namespace RideVerse.Network
{
    public class WebSocketClient : IDisposable
    {
        public enum ConnectionState
        {
            Disconnected,
            Connecting,
            Connected,
            Reconnecting
        }

        private ClientWebSocket _webSocket;
        private CancellationTokenSource _cts;
        private readonly ConcurrentQueue<string> _sendQueue = new ConcurrentQueue<string>();
        private readonly ConcurrentQueue<WsMessage> _receiveQueue = new ConcurrentQueue<WsMessage>();

        private string _url;
        private bool _shouldReconnect;
        private float _lastPingTime;
        private float _lastPongTime;
        private bool _waitingForPong;

        public ConnectionState State { get; private set; } = ConnectionState.Disconnected;
        public float LatencyMs { get; private set; }

        public event Action OnConnected;
        public event Action OnDisconnected;
        public event Action<string> OnError;
        public event Action<WsMessage> OnMessage;

        public bool IsConnected => State == ConnectionState.Connected;

        public void Connect(string url)
        {
            if (State == ConnectionState.Connecting || State == ConnectionState.Connected)
            {
                return;
            }

            _url = url;
            _shouldReconnect = true;
            _cts = new CancellationTokenSource();

            State = ConnectionState.Connecting;
            Task.Run(() => ConnectAsync(_cts.Token));
        }

        private async Task ConnectAsync(CancellationToken ct)
        {
            try
            {
                _webSocket = new ClientWebSocket();
                _webSocket.Options.KeepAliveInterval = TimeSpan.FromSeconds(Constants.Network.HeartbeatInterval);

                await _webSocket.ConnectAsync(new Uri(_url), ct);

                State = ConnectionState.Connected;
                _lastPingTime = Time.realtimeSinceStartup;
                _lastPongTime = Time.realtimeSinceStartup;
                _waitingForPong = false;

                Debug.Log("[WebSocket] Connected");
                OnConnected?.Invoke();

                _ = Task.Run(() => ReceiveLoop(ct), ct);
                _ = Task.Run(() => SendLoop(ct), ct);
                _ = Task.Run(() => HeartbeatLoop(ct), ct);
            }
            catch (OperationCanceledException)
            {
                State = ConnectionState.Disconnected;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WebSocket] Connection failed: {ex.Message}");
                State = ConnectionState.Disconnected;
                OnError?.Invoke(ex.Message);
                OnDisconnected?.Invoke();
            }
        }

        private async Task ReceiveLoop(CancellationToken ct)
        {
            var buffer = new byte[4096];

            try
            {
                while (!ct.IsCancellationRequested && _webSocket.State == WebSocketState.Open)
                {
                    var result = await _webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), ct);

                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        Debug.Log("[WebSocket] Server closed connection");
                        break;
                    }

                    if (result.MessageType == WebSocketMessageType.Text)
                    {
                        string json = Encoding.UTF8.GetString(buffer, 0, result.Count);

                        try
                        {
                            var message = JsonConvert.DeserializeObject<WsMessage>(json);
                            if (message != null)
                            {
                                _receiveQueue.Enqueue(message);
                                OnMessage?.Invoke(message);
                            }
                        }
                        catch (Exception ex)
                        {
                            Debug.LogWarning($"[WebSocket] Failed to parse message: {ex.Message}");
                        }
                    }
                }
            }
            catch (OperationCanceledException) { }
            catch (WebSocketException ex)
            {
                Debug.LogError($"[WebSocket] Receive error: {ex.Message}");
            }

            HandleDisconnect();
        }

        private async Task SendLoop(CancellationToken ct)
        {
            try
            {
                while (!ct.IsCancellationRequested && _webSocket.State == WebSocketState.Open)
                {
                    if (_sendQueue.TryDequeue(out string json))
                    {
                        byte[] bytes = Encoding.UTF8.GetBytes(json);
                        await _webSocket.SendAsync(
                            new ArraySegment<byte>(bytes),
                            WebSocketMessageType.Text,
                            true,
                            ct);
                    }
                    else
                    {
                        await Task.Delay(10, ct);
                    }
                }
            }
            catch (OperationCanceledException) { }
            catch (WebSocketException ex)
            {
                Debug.LogError($"[WebSocket] Send error: {ex.Message}");
            }
        }

        private async Task HeartbeatLoop(CancellationToken ct)
        {
            try
            {
                while (!ct.IsCancellationRequested && _webSocket.State == WebSocketState.Open)
                {
                    await Task.Delay((int)(Constants.Network.HeartbeatInterval * 1000), ct);

                    if (_waitingForPong)
                    {
                        float timeSincePong = Time.realtimeSinceStartup - _lastPongTime;
                        if (timeSincePong > Constants.Network.HeartbeatTimeout)
                        {
                            Debug.LogWarning("[WebSocket] Heartbeat timeout");
                            break;
                        }
                    }

                    var pingMsg = new WsMessage
                    {
                        Event = WsEventTypes.Ping,
                        Data = new System.Collections.Generic.Dictionary<string, object>
                        {
                            { "ts", DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() }
                        }
                    };
                    Send(pingMsg);
                    _lastPingTime = Time.realtimeSinceStartup;
                    _waitingForPong = true;
                }
            }
            catch (OperationCanceledException) { }
        }

        private void HandleDisconnect()
        {
            bool wasConnected = State == ConnectionState.Connected;
            State = ConnectionState.Disconnected;
            _waitingForPong = false;

            if (wasConnected)
            {
                Debug.Log("[WebSocket] Disconnected");
                OnDisconnected?.Invoke();
            }
        }

        public void Send(WsMessage message)
        {
            if (!IsConnected)
            {
                return;
            }

            string json = JsonConvert.SerializeObject(message);
            _sendQueue.Enqueue(json);
        }

        public void Send(string eventName, object data = null)
        {
            var message = new WsMessage
            {
                Event = eventName,
                Data = data != null
                    ? JsonConvert.DeserializeObject<System.Collections.Generic.Dictionary<string, object>>(
                        JsonConvert.SerializeObject(data))
                    : new System.Collections.Generic.Dictionary<string, object>()
            };
            Send(message);
        }

        public void HandlePong()
        {
            _waitingForPong = false;
            _lastPongTime = Time.realtimeSinceStartup;
            LatencyMs = (Time.realtimeSinceStartup - _lastPingTime) * 1000f;
        }

        public void Disconnect()
        {
            _shouldReconnect = false;
            _cts?.Cancel();

            if (_webSocket != null && _webSocket.State == WebSocketState.Open)
            {
                try
                {
                    _webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Client disconnect",
                        CancellationToken.None).Wait(TimeSpan.FromSeconds(2));
                }
                catch { }
            }

            State = ConnectionState.Disconnected;
            _waitingForPong = false;
            Debug.Log("[WebSocket] Disconnected by client");
        }

        public void Dispose()
        {
            Disconnect();
            _webSocket?.Dispose();
            _cts?.Dispose();
        }
    }
}
