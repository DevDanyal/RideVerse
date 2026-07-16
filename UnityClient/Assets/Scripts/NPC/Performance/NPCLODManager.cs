using System.Collections.Generic;
using UnityEngine;
using RideVerse.NPC.Core;
using RideVerse.NPC.Brain;

namespace RideVerse.NPC.Performance
{
    public class NPCLODManager : MonoBehaviour
    {
        private NPCConfig _config;
        private Transform _playerTransform;
        private Dictionary<NPCBrain, NPCLODLevel> _npcLODs = new Dictionary<NPCBrain, NPCLODLevel>();
        private Dictionary<NPCBrain, float> _updateTimers = new Dictionary<NPCBrain, float>();

        public int ManagedNPCCount => _npcLODs.Count;

        public void Initialize(NPCConfig config)
        {
            _config = config;
        }

        public void SetPlayerTransform(Transform player)
        {
            _playerTransform = player;
        }

        public void RegisterNPC(NPCBrain npc)
        {
            if (!_npcLODs.ContainsKey(npc))
            {
                _npcLODs[npc] = NPCLODLevel.Full;
                _updateTimers[npc] = 0f;
            }
        }

        public void UnregisterNPC(NPCBrain npc)
        {
            _npcLODs.Remove(npc);
            _updateTimers.Remove(npc);
        }

        public NPCLODLevel GetLODLevel(NPCBrain npc)
        {
            if (_playerTransform == null || npc == null) return NPCLODLevel.Culled;
            if (!_npcLODs.ContainsKey(npc)) return NPCLODLevel.Culled;

            float distance = Vector3.Distance(_playerTransform.position, npc.transform.position);

            if (distance <= _config.lodDistanceFull)
                return NPCLODLevel.Full;
            if (distance <= _config.lodDistanceMedium)
                return NPCLODLevel.Medium;
            if (distance <= _config.lodDistanceLow)
                return NPCLODLevel.Low;
            return NPCLODLevel.Culled;
        }

        public bool ShouldUpdate(NPCBrain npc)
        {
            if (!_npcLODs.ContainsKey(npc)) return false;

            var lod = GetLODLevel(npc);
            _npcLODs[npc] = lod;

            float interval = GetUpdateInterval(lod);
            if (!_updateTimers.ContainsKey(npc))
                _updateTimers[npc] = 0f;

            _updateTimers[npc] += Time.deltaTime;
            if (_updateTimers[npc] >= interval)
            {
                _updateTimers[npc] = 0f;
                return true;
            }

            return false;
        }

        public void SetEnabled(NPCBrain npc, bool enabled)
        {
            if (npc == null) return;
            npc.gameObject.SetActive(enabled);
        }

        private float GetUpdateInterval(NPCLODLevel lod)
        {
            switch (lod)
            {
                case NPCLODLevel.Full: return _config.updateIntervalFull;
                case NPCLODLevel.Medium: return _config.updateIntervalMedium;
                case NPCLODLevel.Low: return _config.updateIntervalLow;
                case NPCLODLevel.Culled: return _config.updateIntervalCulled;
                default: return _config.updateIntervalLow;
            }
        }

        public void UpdateAllLODs()
        {
            foreach (var kvp in _npcLODs)
            {
                if (kvp.Key == null) continue;
                var lod = GetLODLevel(kvp.Key);
                _npcLODs[kvp.Key] = lod;
                SetEnabled(kvp.Key, lod != NPCLODLevel.Culled);
            }
        }

        public Dictionary<NPCBrain, NPCLODLevel> GetAllLODs() => new Dictionary<NPCBrain, NPCLODLevel>(_npcLODs);
    }

    public enum NPCLODLevel
    {
        Full,
        Medium,
        Low,
        Culled
    }
}
