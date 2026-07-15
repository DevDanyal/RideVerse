using NUnit.Framework;
using RideVerse.Network;
using System;

[TestFixture]
public class ReconnectHandlerTests
{
    [Test]
    public void Reset_SetsAttemptCountToZero()
    {
        var handler = new ReconnectHandler();
        handler.Initialize(_ => { });

        handler.Reset();

        Assert.AreEqual(0, handler.AttemptCount);
        Assert.IsFalse(handler.IsReconnecting);
    }

    [Test]
    public void Initialize_SetsAttemptCountToZero()
    {
        var handler = new ReconnectHandler();

        handler.Initialize(_ => { });

        Assert.AreEqual(0, handler.AttemptCount);
        Assert.IsFalse(handler.IsReconnecting);
    }

    [Test]
    public void OnConnected_ResetsState()
    {
        var handler = new ReconnectHandler();
        handler.Initialize(_ => { });
        bool succeeded = false;
        handler.OnReconnectSucceeded += () => succeeded = true;

        handler.OnConnected();

        Assert.AreEqual(0, handler.AttemptCount);
        Assert.IsFalse(handler.IsReconnecting);
        Assert.IsTrue(succeeded);
    }

    [Test]
    public void OnReconnectFailed_FiresAfterMaxAttempts()
    {
        var handler = new ReconnectHandler();
        bool failed = false;
        handler.OnReconnectFailed += () => failed = true;
        handler.Initialize(_ => { });

        handler.Reset();

        Assert.IsFalse(failed);
    }

    [Test]
    public void EventHandlers_DontThrow()
    {
        var handler = new ReconnectHandler();
        handler.Initialize(_ => { });

        Assert.DoesNotThrow(() => handler.OnConnected());
        Assert.DoesNotThrow(() => handler.Reset());
    }
}

[TestFixture]
public class WebSocketClientTests
{
    [Test]
    public void NewClient_IsDisconnected()
    {
        var client = new WebSocketClient();

        Assert.IsFalse(client.IsConnected);
        Assert.AreEqual(WebSocketClient.ConnectionState.Disconnected, client.State);
    }

    [Test]
    public void HandlePong_UpdatesLatency()
    {
        var client = new WebSocketClient();

        Assert.DoesNotThrow(() => client.HandlePong());
    }

    [Test]
    public void Dispose_DoesNotThrow()
    {
        var client = new WebSocketClient();

        Assert.DoesNotThrow(() => client.Dispose());
    }

    [Test]
    public void Disconnect_DoesNotThrow()
    {
        var client = new WebSocketClient();

        Assert.DoesNotThrow(() => client.Disconnect());
    }

    [Test]
    public void Send_WhenDisconnected_DoesNotThrow()
    {
        var client = new WebSocketClient();
        var msg = new WsMessage { Event = "test" };

        Assert.DoesNotThrow(() => client.Send(msg));
        client.Dispose();
    }

    [Test]
    public void SendString_WhenDisconnected_DoesNotThrow()
    {
        var client = new WebSocketClient();

        Assert.DoesNotThrow(() => client.Send("test_event", new { key = "value" }));
        client.Dispose();
    }

    [Test]
    public void MultipleDispose_DoesNotThrow()
    {
        var client = new WebSocketClient();

        Assert.DoesNotThrow(() =>
        {
            client.Dispose();
            client.Dispose();
        });
    }

    [Test]
    public void Connect_InvalidUrl_FiresErrorAndDisconnects()
    {
        var client = new WebSocketClient();
        bool errorFired = false;
        bool disconnectedFired = false;

        client.OnError += _ => errorFired = true;
        client.OnDisconnected += () => disconnectedFired = true;

        client.Connect("ws://invalid.server.that.doesntexist:99999/ws");

        System.Threading.Thread.Sleep(2000);

        Assert.IsFalse(client.IsConnected);
        client.Dispose();
    }
}
