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

                // Engine
                public const float EngineDisplacement = 125f;
                public const float MaxRPM = 9500f;
                public const float IdleRPM = 1300f;
                public const float RedlineRPM = 8500f;
                public const float MaxPower = 11.5f;
                public const float MaxTorque = 10.5f;
                public const float MaxSpeedKmh = 110f;

                // Transmission — 5-speed + Neutral
                public const int TotalGears = 5;
                public const int NeutralGear = 0;
                public const float FinalDriveRatio = 2.533f;

                public static readonly float[] GearRatios = new float[]
                {
                    0f,
                    2.846f,
                    1.875f,
                    1.400f,
                    1.115f,
                    0.963f
                };

                // Clutch
                public const float ClutchEngageRPM = 1500f;
                public const float ClutchSlipRange = 500f;
                public const float ClutchEngageSpeed = 5f;

                // Physical dimensions
                public const float Mass = 128f;
                public const float WheelBase = 1.24f;
                public const float FrontWheelRadius = 0.28f;
                public const float RearWheelRadius = 0.28f;
                public const float HandlebarWidth = 0.68f;

                // Steering
                public const float SteeringAngle = 45f;
                public const float SteeringSpeed = 120f;
                public const float SpeedDependentSteerFactor = 0.4f;

                // Lean
                public const float MaxLeanAngle = 40f;
                public const float LeanSpeed = 80f;
                public const float LeanRecoverySpeed = 120f;
                public const float LowSpeedLeanLimit = 25f;
                public const float LeanToSteerRatio = 0.7f;

                // Suspension
                public const float FrontSuspensionTravel = 0.13f;
                public const float RearSuspensionTravel = 0.09f;
                public const float FrontSpringForce = 35000f;
                public const float RearSpringForce = 42000f;
                public const float FrontDamperForce = 4500f;
                public const float RearDamperForce = 5000f;
                public const float SuspensionRestLength = 0.3f;

                // Braking
                public const float FrontBrakeForce = 4500f;
                public const float RearBrakeForce = 3500f;
                public const float EngineBrakeForce = 800f;
                public const float ABSActivationThreshold = 0.3f;

                // Fuel
                public const float MaxFuel = 17f;
                public const float FuelConsumptionRate = 0.04f;
                public const float FuelWarningThreshold = 3f;

                // Health / Damage
                public const float MaxHealth = 100f;
                public const float FallDamageThreshold = 3f;
                public const float FallDamageMultiplier = 15f;

                // Effects
                public const float ExhaustSmokeRate = 0.1f;
                public const float DustParticleSpeed = 2f;
            }

            public static class SportsCar
            {
                public const string VehicleId = "sports_car";
                public const string DisplayName = "Sports Car";

                // Engine
                public const float MaxRPM = 8000f;
                public const float IdleRPM = 800f;
                public const float RedlineRPM = 7500f;
                public const float MaxPower = 320f;
                public const float MaxTorque = 400f;
                public const float MaxSpeedKmh = 260f;

                // Transmission — 6-speed + Reverse
                public const int TotalGears = 6;
                public const int ReverseGear = -1;
                public const int NeutralGear = 0;
                public const float FinalDriveRatio = 3.42f;

                public static readonly float[] GearRatios = new float[]
                {
                    0f,
                    3.636f,
                    2.375f,
                    1.761f,
                    1.346f,
                    1.062f,
                    0.872f
                };

                // Physical dimensions
                public const float Mass = 1500f;
                public const float WheelBase = 2.45f;
                public const float TrackWidth = 1.55f;
                public const float FrontWheelRadius = 0.33f;
                public const float RearWheelRadius = 0.34f;

                // Steering
                public const float MaxSteerAngle = 35f;
                public const float SteeringSpeed = 150f;
                public const float SpeedDependentSteerFactor = 0.6f;

                // Suspension
                public const float FrontSuspensionTravel = 0.08f;
                public const float RearSuspensionTravel = 0.09f;
                public const float FrontSpringForce = 45000f;
                public const float RearSpringForce = 52000f;
                public const float FrontDamperForce = 5500f;
                public const float RearDamperForce = 6000f;
                public const float AntiRollBarForce = 8000f;

                // Braking
                public const float FrontBrakeForce = 5500f;
                public const float RearBrakeForce = 4500f;
                public const float EngineBrakeForce = 1200f;
                public const float ABSActivationThreshold = 0.2f;

                // Fuel
                public const float MaxFuel = 60f;
                public const float FuelConsumptionRate = 0.08f;
                public const float FuelWarningThreshold = 8f;

                // Health
                public const float MaxHealth = 100f;

                // Drift
                public const float DriftSteerAssist = 0.4f;
                public const float DriftThrottleBoost = 1.2f;
                public const float HandbrakeForce = 3500f;

                // Aerodynamics
                public const float DownforceCoefficient = 0.3f;
                public const float DragCoefficient = 0.35f;
                public const float FrontalArea = 2.2f;
            }
        }
    }
}
