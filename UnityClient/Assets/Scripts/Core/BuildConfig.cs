using UnityEngine;

namespace RideVerse.Core
{
    [CreateAssetMenu(fileName = "BuildConfig", menuName = "RideVerse/Build Configuration")]
    public class BuildConfig : ScriptableObject
    {
        [Header("Build Settings")]
        public string CompanyName = "RideVerse";
        public string ProductName = "RideVerse";
        public string BundleVersion = "1.0.0";

        [Header("Android")]
        public string AndroidBundleVersionCode = "1";
        public string AndroidMinSdkVersion = "26";
        public string AndroidTargetSdkVersion = "34";
        public string AndroidKeystorePath = "";
        public string AndroidKeystorePassword = "";
        public string AndroidKeyAlias = "";
        public string AndroidKeyAliasPassword = "";

        [Header("Server")]
        public string ApiBaseUrl = "http://localhost:8000";
        public string WsBaseUrl = "ws://localhost:8000";

        [Header("Debug")]
        public bool EnableDebugLogs = true;
        public bool EnablePerformanceOverlay;

        private static BuildConfig _instance;

        public static BuildConfig Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = Resources.Load<BuildConfig>("BuildConfig");
                }
                return _instance;
            }
        }

        public void ApplyToPlayerPrefs()
        {
            PlayerPrefs.SetString(Constants.Api.BaseUrlKey, ApiBaseUrl);
            PlayerPrefs.SetString(Constants.Api.WsBaseUrlKey, WsBaseUrl);
            PlayerPrefs.Save();
        }
    }
}
