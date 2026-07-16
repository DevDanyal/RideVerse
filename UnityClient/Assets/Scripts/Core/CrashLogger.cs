using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;

namespace RideVerse.Core
{
    public class CrashLogger : MonoBehaviour
    {
        private static CrashLogger _instance;
        private readonly List<LogEntry> _logBuffer = new List<LogEntry>();
        private readonly StringBuilder _crashReport = new StringBuilder();
        private string _logDirectory;
        private int _maxLogEntries = 500;
        private bool _isInitialized;

        public static CrashLogger Instance => _instance;

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }

            _instance = this;
            DontDestroyOnLoad(gameObject);
            Initialize();
        }

        private void Initialize()
        {
            _logDirectory = Path.Combine(Application.persistentDataPath, "Logs");
            if (!Directory.Exists(_logDirectory))
            {
                Directory.CreateDirectory(_logDirectory);
            }

            Application.logMessageReceived += HandleLog;
            Application.quitting += HandleQuitting;

            _isInitialized = true;
            Debug.Log($"[CrashLogger] Initialized. Logs directory: {_logDirectory}");
        }

        private void HandleLog(string condition, string stackTrace, LogType type)
        {
            if (!_isInitialized) return;

            var entry = new LogEntry
            {
                Timestamp = DateTime.UtcNow,
                Message = condition,
                StackTrace = stackTrace,
                Type = type
            };

            _logBuffer.Add(entry);

            if (_logBuffer.Count > _maxLogEntries)
            {
                _logBuffer.RemoveAt(0);
            }

            if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert)
            {
                WriteErrorLog(entry);
            }
        }

        private void WriteErrorLog(LogEntry entry)
        {
            try
            {
                string filename = $"error_{DateTime.UtcNow:yyyyMMdd_HHmmss}.log";
                string filepath = Path.Combine(_logDirectory, filename);

                var sb = new StringBuilder();
                sb.AppendLine("=== RideVerse Error Log ===");
                sb.AppendLine($"Timestamp: {entry.Timestamp:O}");
                sb.AppendLine($"Type: {entry.Type}");
                sb.AppendLine($"Platform: {Application.platform}");
                sb.AppendLine($"Version: {Application.version}");
                sb.AppendLine($"Unity Version: {Application.unityVersion}");
                sb.AppendLine($"Device: {SystemInfo.deviceModel}");
                sb.AppendLine($"OS: {SystemInfo.operatingSystem}");
                sb.AppendLine($"Memory: {SystemInfo.systemMemorySize}MB");
                sb.AppendLine($"Graphics: {SystemInfo.graphicsDeviceName}");
                sb.AppendLine($"---");
                sb.AppendLine($"Message: {entry.Message}");
                sb.AppendLine($"---");
                sb.AppendLine($"Stack Trace:");
                sb.AppendLine(entry.StackTrace);
                sb.AppendLine($"---");

                File.WriteAllText(filepath, sb.ToString());
                Debug.Log($"[CrashLogger] Error log written: {filepath}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[CrashLogger] Failed to write error log: {ex.Message}");
            }
        }

        private void HandleQuitting()
        {
            WriteSessionLog();
            Application.logMessageReceived -= HandleLog;
        }

        private void WriteSessionLog()
        {
            try
            {
                string filename = $"session_{DateTime.UtcNow:yyyyMMdd_HHmmss}.log";
                string filepath = Path.Combine(_logDirectory, filename);

                var sb = new StringBuilder();
                sb.AppendLine("=== RideVerse Session Log ===");
                sb.AppendLine($"Session End: {DateTime.UtcNow:O}");
                sb.AppendLine($"Platform: {Application.platform}");
                sb.AppendLine($"Version: {Application.version}");
                sb.AppendLine($"Device: {SystemInfo.deviceModel}");
                sb.AppendLine($"OS: {SystemInfo.operatingSystem}");
                sb.AppendLine($"System Memory: {SystemInfo.systemMemorySize}MB");
                sb.AppendLine($"---");
                sb.AppendLine($"Total Log Entries: {_logBuffer.Count}");

                int errorCount = 0;
                int warningCount = 0;
                foreach (var entry in _logBuffer)
                {
                    if (entry.Type == LogType.Error || entry.Type == LogType.Exception) errorCount++;
                    else if (entry.Type == LogType.Warning) warningCount++;
                }

                sb.AppendLine($"Errors: {errorCount}");
                sb.AppendLine($"Warnings: {warningCount}");
                sb.AppendLine($"---");

                sb.AppendLine("Recent Errors:");
                foreach (var entry in _logBuffer)
                {
                    if (entry.Type == LogType.Error || entry.Type == LogType.Exception)
                    {
                        sb.AppendLine($"[{entry.Timestamp:HH:mm:ss}] {entry.Message}");
                    }
                }

                File.WriteAllText(filepath, sb.ToString());
            }
            catch (Exception ex)
            {
                Debug.LogError($"[CrashLogger] Failed to write session log: {ex.Message}");
            }
        }

        public string GetCrashReport()
        {
            _crashReport.Clear();
            _crashReport.AppendLine("=== RideVerse Crash Report ===");
            _crashReport.AppendLine($"Time: {DateTime.UtcNow:O}");
            _crashReport.AppendLine($"Platform: {Application.platform}");
            _crashReport.AppendLine($"Version: {Application.version}");
            _crashReport.AppendLine($"Device: {SystemInfo.deviceModel}");
            _crashReport.AppendLine($"OS: {SystemInfo.operatingSystem}");
            _crashReport.AppendLine($"Memory: {SystemInfo.systemMemorySize}MB");
            _crashReport.AppendLine($"Graphics: {SystemInfo.graphicsDeviceName}");
            _crashReport.AppendLine("---");
            _crashReport.AppendLine("Recent Log:");
            int start = Mathf.Max(0, _logBuffer.Count - 50);
            for (int i = start; i < _logBuffer.Count; i++)
            {
                var e = _logBuffer[i];
                _crashReport.AppendLine($"[{e.Type}] [{e.Timestamp:HH:mm:ss}] {e.Message}");
            }

            return _crashReport.ToString();
        }

        public List<LogEntry> GetRecentErrors(int count = 10)
        {
            var errors = new List<LogEntry>();
            for (int i = _logBuffer.Count - 1; i >= 0 && errors.Count < count; i--)
            {
                if (_logBuffer[i].Type == LogType.Error || _logBuffer[i].Type == LogType.Exception)
                {
                    errors.Add(_logBuffer[i]);
                }
            }
            return errors;
        }

        public void SetMaxLogEntries(int max)
        {
            _maxLogEntries = max;
            while (_logBuffer.Count > _maxLogEntries)
            {
                _logBuffer.RemoveAt(0);
            }
        }

        public string GetLogDirectory() => _logDirectory;
        public int GetLogCount() => _logBuffer.Count;
        public int GetErrorCount()
        {
            int count = 0;
            foreach (var e in _logBuffer)
            {
                if (e.Type == LogType.Error || e.Type == LogType.Exception) count++;
            }
            return count;
        }

        private void OnDestroy()
        {
            Application.logMessageReceived -= HandleLog;
            Application.quitting -= HandleQuitting;
        }
    }

    [Serializable]
    public class LogEntry
    {
        public DateTime Timestamp;
        public string Message;
        public string StackTrace;
        public LogType Type;
    }
}
