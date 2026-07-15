namespace RideVerse.Core
{
    public static class Constants
    {
        public const string GameName = "RideVerse";
        const string LocalHost = "http://localhost:8000";
        const string LocalHostWs = "ws://localhost:8000";

        const string StagingHost = "https://staging-api.rideverse.game";
        const string StagingHostWs = "wss://staging-api.rideverse.game";

        const string ProductionHost = "https://api.rideverse.game";
        const string ProductionHostWs = "wss://api.rideverse.game";

        public static class Api
        {
            public const string BaseUrlKey = "api_base_url";
            public const string WsBaseUrlKey = "ws_base_url";

            public static string BaseUrl => PlayerPrefs.GetString(BaseUrlKey, LocalHost);
            public static string WsBaseUrl => PlayerPrefs.GetString(WsBaseUrlKey, LocalHostWs);

            public const string ApiPrefix = "/api/v1";

            public static class Auth
            {
                public const string Register = "/auth/register";
                public const string Login = "/auth/login";
                public const string Refresh = "/auth/refresh";
                public const string Logout = "/auth/logout";
                public const string Me = "/auth/me";
            }

            public static class Players
            {
                public const string Me = "/players/me";
                public const string MeStatistics = "/players/me/statistics";
                public const string MeSettings = "/players/me/settings";
                public const string MeCharacters = "/players/me/characters";
                public const string MeInventory = "/players/me/inventory";
                public const string MeEconomy = "/players/me/economy";
                public const string MeWallet = "/players/me/economy/wallet";
                public const string MeAchievements = "/players/me/achievements";
            }

            public static class Multiplayer
            {
                public const string Rooms = "/multiplayer/rooms";
                public const string Sessions = "/multiplayer/sessions";
                public const string Stats = "/multiplayer/stats";
                public const string WsPath = "/multiplayer/ws/";
            }
        }

        public static class Scenes
        {
            public const string Loading = "LoadingScene";
            public const string Login = "LoginScene";
            public const string MainMenu = "MainMenuScene";
            public const string Game = "GameScene";
        }

        public static class Tags
        {
            public const string Player = "Player";
            public const string MainCamera = "MainCamera";
            public const string GameManagers = "GameManagers";
        }

        public static class Layers
        {
            public const string Player = "Player";
            public const string Ground = "Ground";
            public const string UI = "UI";
        }

        public static class PlayerPrefs
        {
            public const string AccessToken = "rv_access_token";
            public const string RefreshToken = "rv_refresh_token";
            public const string PlayerId = "rv_player_id";
            public const string DisplayName = "rv_display_name";
            public const string RememberEmail = "rv_remember_email";
            public const string PlayerPosX = "rv_player_pos_x";
            public const string PlayerPosY = "rv_player_pos_y";
            public const string PlayerPosZ = "rv_player_pos_z";
            public const string PlayerRotY = "rv_player_rot_y";
        }

        public static class Network
        {
            public const float ReconnectMinDelay = 1f;
            public const float ReconnectMaxDelay = 30f;
            public const float ReconnectMultiplier = 2f;
            public const int MaxReconnectAttempts = 10;
            public const float HeartbeatInterval = 15f;
            public const float HeartbeatTimeout = 5f;
            public const float SendRate = 30f;
        }

        public static class Player
        {
            public const float WalkSpeed = 3.5f;
            public const float SprintSpeed = 6f;
            public const float JumpForce = 7f;
            public const float Gravity = -20f;
            public const float GroundCheckDistance = 0.3f;
            public const float RotationSpeed = 10f;
            public const float CameraDistance = 4f;
            public const float CameraHeight = 2f;
            public const float CameraSmoothness = 10f;
        }

        public static class Vehicle
        {
            public const float InteractionRange = 3f;
            public const string InteractionPrompt = "Press F to enter";
            public const string ExitPrompt = "Press F to exit";
            public const float PositionSaveInterval = 5f;

            public static class HondaCG125
            {
                public const string VehicleId = "honda_cg125";
                public const string DisplayName = "Honda CG125";

                public const float MaxSpeed = 12f;
                public const float Acceleration = 8f;
                public const float BrakingForce = 16f;
                public const float SteeringSpeed = 120f;
                public const float MaxLeanAngle = 35f;
                public const float LeanSpeed = 80f;
                public const float Mass = 130f;
                public const float MaxFuel = 100f;
                public const float FuelConsumptionRate = 0.5f;
                public const float MaxHealth = 100f;
                public const int MaxGear = 4;

                public static float[] GearRatios => new float[]
                {
                    0f,
                    0.25f,
                    0.45f,
                    0.7f,
                    1f
                };
            }
        }
    }
}
