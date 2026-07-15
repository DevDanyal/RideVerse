using System;
using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;
using RideVerse.Auth;
using RideVerse.Network;

namespace RideVerse.Core
{
    public class AppManager : Singleton<AppManager>
    {
        [Header("Configuration")]
        [SerializeField] private bool _autoConnect = true;
        [SerializeField] private bool _skipLoadingScreen;

        public bool IsInitialized { get; private set; }
        public string CurrentScene { get; private set; }

        public event Action OnStartupComplete;
        public event Action<string> OnSceneTransitioning;

        private void Start()
        {
            Application.targetFrameRate = 60;
            Screen.sleepTimeout = SleepTimeout.NeverSleep;

            StartCoroutine(StartupSequence());
        }

        private IEnumerator StartupSequence()
        {
            yield return StartCoroutine(InitializeSystems());

            IsInitialized = true;
            OnStartupComplete?.Invoke();
            GameEvents.TriggerGameInitialized();

            if (AuthManager.Instance.IsAuthenticated)
            {
                if (_autoConnect)
                {
                    NetworkManager.Instance.Connect();
                }

                LoadScene(Constants.Scenes.MainMenu);
            }
            else
            {
                LoadScene(Constants.Scenes.Login);
            }
        }

        private IEnumerator InitializeSystems()
        {
            AuthManager authManager = AuthManager.Instance;
            yield return null;

            ApiClient.Instance.Initialize();
            yield return null;

            NetworkManager.Instance.Initialize();
            yield return null;
        }

        public void LoadScene(string sceneName)
        {
            OnSceneTransitioning?.Invoke(sceneName);
            StartCoroutine(LoadSceneAsync(sceneName));
        }

        private IEnumerator LoadSceneAsync(string sceneName)
        {
            GameEvents.TriggerSceneLoadStarted();

            if (!_skipLoadingScreen && CurrentScene != null && CurrentScene != sceneName)
            {
                yield return SceneManager.LoadSceneAsync(Constants.Scenes.Loading);
            }

            AsyncOperation asyncLoad = SceneManager.LoadSceneAsync(sceneName);

            while (asyncLoad != null && !asyncLoad.isDone)
            {
                yield return null;
            }

            CurrentScene = sceneName;
            GameEvents.TriggerSceneLoadCompleted(sceneName);
        }

        public void OnApplicationPause(bool paused)
        {
            if (paused)
            {
                GameEvents.TriggerApplicationPaused();
            }
            else
            {
                GameEvents.TriggerApplicationResumed();
            }
        }

        public void QuitApplication()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }
    }
}
