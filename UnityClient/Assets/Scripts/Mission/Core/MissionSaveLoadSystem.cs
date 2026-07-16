using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionSaveLoadSystem
    {
        private readonly MissionConfig _config;
        private MissionSaveData _saveData;
        private float _autoSaveTimer;
        private bool _isDirty;

        public MissionSaveData SaveData => _saveData;
        public bool IsDirty => _isDirty;

        public event Action<MissionSaveData> OnDataLoaded;
        public event Action<MissionSaveData> OnDataSaved;

        public MissionSaveLoadSystem(MissionConfig config)
        {
            _config = config;
            _saveData = new MissionSaveData();
        }

        public void Initialize(string playerId)
        {
            _saveData.PlayerId = playerId;
            Load(playerId);
        }

        public void Update(float deltaTime)
        {
            if (!_isDirty || _config == null) return;

            _autoSaveTimer += deltaTime;
            if (_autoSaveTimer >= _config.autoSaveInterval)
            {
                _autoSaveTimer = 0f;
                Save(_saveData.PlayerId);
            }
        }

        public void Save(string playerId)
        {
            try
            {
                _saveData.LastSaveTime = DateTime.UtcNow;
                string json = JsonUtility.ToJson(_saveData, true);
                string path = GetSavePath(playerId);

                string directory = Path.GetDirectoryName(path);
                if (!Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                File.WriteAllText(path, json);
                _isDirty = false;
                OnDataSaved?.Invoke(_saveData);
                Debug.Log($"[MissionSaveLoad] Data saved for player {playerId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[MissionSaveLoad] Failed to save: {ex.Message}");
            }
        }

        public void Load(string playerId)
        {
            try
            {
                string path = GetSavePath(playerId);
                if (File.Exists(path))
                {
                    string json = File.ReadAllText(path);
                    _saveData = JsonUtility.FromJson<MissionSaveData>(json);
                    Debug.Log($"[MissionSaveLoad] Data loaded for player {playerId}");
                }
                else
                {
                    _saveData = new MissionSaveData { PlayerId = playerId };
                    Debug.Log($"[MissionSaveLoad] No save found, creating new for player {playerId}");
                }

                OnDataLoaded?.Invoke(_saveData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[MissionSaveLoad] Failed to load: {ex.Message}");
                _saveData = new MissionSaveData { PlayerId = playerId };
            }
        }

        public void MarkDirty()
        {
            _isDirty = true;
        }

        public void AddActiveMission(MissionData mission)
        {
            _saveData.ActiveMissions.Add(mission);
            MarkDirty();
        }

        public void RemoveActiveMission(string missionId)
        {
            _saveData.ActiveMissions.RemoveAll(m => m.MissionId == missionId);
            MarkDirty();
        }

        public void AddCompletedMission(MissionData mission)
        {
            _saveData.CompletedMissions.Add(mission);
            _saveData.TotalMissionsCompleted++;
            MarkDirty();
        }

        public void AddFailedMission(MissionData mission)
        {
            _saveData.FailedMissions.Add(mission);
            _saveData.TotalMissionsFailed++;
            MarkDirty();
        }

        public MissionData GetActiveMission(string missionId)
        {
            return _saveData.ActiveMissions.Find(m => m.MissionId == missionId);
        }

        public bool HasActiveMission(string missionId)
        {
            return _saveData.ActiveMissions.Exists(m => m.MissionId == missionId);
        }

        public bool HasCompletedMission(string missionId)
        {
            return _saveData.CompletedMissions.Exists(m => m.MissionId == missionId);
        }

        public int GetCompletedMissionCount()
        {
            return _saveData.TotalMissionsCompleted;
        }

        public int GetFailedMissionCount()
        {
            return _saveData.TotalMissionsFailed;
        }

        public void UpdateMissionProgress(MissionData mission)
        {
            for (int i = 0; i < _saveData.ActiveMissions.Count; i++)
            {
                if (_saveData.ActiveMissions[i].MissionId == mission.MissionId)
                {
                    _saveData.ActiveMissions[i] = mission;
                    MarkDirty();
                    return;
                }
            }
        }

        public void RecordDailyStreak(int streak)
        {
            _saveData.DailyStreak = streak;
            _saveData.LastDailyResetDate = DateTime.UtcNow.ToString("yyyy-MM-dd");
            MarkDirty();
        }

        public bool ShouldResetDaily()
        {
            if (string.IsNullOrEmpty(_saveData.LastDailyResetDate)) return true;

            DateTime lastReset = DateTime.Parse(_saveData.LastDailyResetDate);
            return DateTime.UtcNow.Date > lastReset.Date;
        }

        public List<MissionData> GetAllActiveMissions()
        {
            return new List<MissionData>(_saveData.ActiveMissions);
        }

        public List<MissionData> GetActiveMissionsByType(MissionType type)
        {
            return _saveData.ActiveMissions.FindAll(m => m.Type == type);
        }

        public void DeleteSave(string playerId)
        {
            try
            {
                string path = GetSavePath(playerId);
                if (File.Exists(path))
                {
                    File.Delete(path);
                }
                _saveData = new MissionSaveData { PlayerId = playerId };
                Debug.Log($"[MissionSaveLoad] Save deleted for player {playerId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[MissionSaveLoad] Failed to delete save: {ex.Message}");
            }
        }

        public string GetSavePath(string playerId)
        {
            return Path.Combine(Application.persistentDataPath, "Missions", $"{playerId}_missions.json");
        }

        public void ClearAll()
        {
            _saveData = new MissionSaveData();
            _isDirty = false;
            _autoSaveTimer = 0f;
        }
    }
}
