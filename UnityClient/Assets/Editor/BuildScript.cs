using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;
using System.Linq;

namespace RideVerse.Editor
{
    public static class BuildScript
    {
        private const string BuildPath = "Builds";

        [MenuItem("RideVerse/Build/Android")]
        public static void BuildAndroid()
        {
            string[] scenes = GetScenes();

            PlayerSettings.Android.bundleVersionCode =
                int.TryParse(PlayerSettings.Android.bundleVersionCode.ToString(), out int code) ? code + 1 : 1;

            var buildOptions = new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = $"{BuildPath}/Android/RideVerse.apk",
                target = BuildTarget.Android,
                options = BuildOptions.None
            };

            BuildReport report = BuildPipeline.BuildPlayer(buildOptions);
            BuildSummary summary = report.summary;

            if (summary.result == BuildResult.Succeeded)
            {
                Debug.Log($"[Build] Android APK built: {summary.totalSize} bytes");
            }
            else
            {
                Debug.LogError($"[Build] Android build failed: {summary.result}");
            }
        }

        [MenuItem("RideVerse/Build/Android AAB")]
        public static void BuildAndroidAAB()
        {
            string[] scenes = GetScenes();

            EditorUserBuildSettings.buildAppBundle = true;

            var buildOptions = new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = $"{BuildPath}/Android/RideVerse.aab",
                target = BuildTarget.Android,
                options = BuildOptions.None
            };

            BuildReport report = BuildPipeline.BuildPlayer(buildOptions);
            EditorUserBuildSettings.buildAppBundle = false;

            if (report.summary.result == BuildResult.Succeeded)
            {
                Debug.Log($"[Build] Android AAB built: {report.summary.totalSize} bytes");
            }
            else
            {
                Debug.LogError($"[Build] Android AAB build failed: {report.summary.result}");
            }
        }

        [MenuItem("RideVerse/Build/Windows")]
        public static void BuildWindows()
        {
            string[] scenes = GetScenes();

            var buildOptions = new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = $"{BuildPath}/Windows/RideVerse.exe",
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None
            };

            BuildReport report = BuildPipeline.BuildPlayer(buildOptions);

            if (report.summary.result == BuildResult.Succeeded)
            {
                Debug.Log($"[Build] Windows build succeeded: {report.summary.totalSize} bytes");
            }
            else
            {
                Debug.LogError($"[Build] Windows build failed: {report.summary.result}");
            }
        }

        private static string[] GetScenes()
        {
            return EditorBuildSettings.scenes
                .Where(s => s.enabled)
                .Select(s => s.path)
                .ToArray();
        }
    }
}
