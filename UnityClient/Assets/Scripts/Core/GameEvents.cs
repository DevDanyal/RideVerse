using System;
using UnityEngine;

namespace RideVerse.Core
{
    public static class GameEvents
    {
        public static event Action OnGameInitialized;
        public static event Action OnSceneLoadStarted;
        public static event Action<string> OnSceneLoadCompleted;
        public static event Action OnApplicationPaused;
        public static event Action OnApplicationResumed;

        public static void TriggerGameInitialized() => OnGameInitialized?.Invoke();
        public static void TriggerSceneLoadStarted() => OnSceneLoadStarted?.Invoke();
        public static void TriggerSceneLoadCompleted(string sceneName) => OnSceneLoadCompleted?.Invoke(sceneName);
        public static void TriggerApplicationPaused() => OnApplicationPaused?.Invoke();
        public static void TriggerApplicationResumed() => OnApplicationResumed?.Invoke();

        public static void ClearAll()
        {
            OnGameInitialized = null;
            OnSceneLoadStarted = null;
            OnSceneLoadCompleted = null;
            OnApplicationPaused = null;
            OnApplicationResumed = null;
        }
    }
}
