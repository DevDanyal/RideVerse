using System.Collections.Generic;
using UnityEngine;
using RideVerse.NPC.Core;
using RideVerse.NPC.Brain;
using RideVerse.NPC.Profession;
using RideVerse.NPC.Reputation;
using RideVerse.NPC.Performance;

namespace RideVerse.NPC.Diagnostics
{
    public class NPCDebugTools : MonoBehaviour
    {
        private NPCManager _npcManager;
        private bool _showDebugInfo;
        private bool _showGizmos = true;
        private GUIStyle _labelStyle;
        private GUIStyle _boxStyle;

        public bool ShowDebugInfo => _showDebugInfo;
        public bool ShowGizmos => _showGizmos;

        public void Initialize(NPCManager npcManager)
        {
            _npcManager = npcManager;
        }

        public void ToggleDebugInfo()
        {
            _showDebugInfo = !_showDebugInfo;
        }

        public void ToggleGizmos()
        {
            _showGizmos = !_showGizmos;
        }

        private void OnGUI()
        {
            if (!_showDebugInfo || _npcManager == null) return;

            if (_labelStyle == null)
            {
                _labelStyle = new GUIStyle(GUI.skin.label)
                {
                    fontSize = 12,
                    normal = { textColor = Color.white }
                };
            }

            if (_boxStyle == null)
            {
                _boxStyle = new GUIStyle(GUI.skin.box)
                {
                    alignment = TextAnchor.UpperLeft,
                    padding = new RectOffset(5, 5, 5, 5)
                };
            }

            float x = 10f;
            float y = 10f;
            float width = 300f;
            float lineHeight = 18f;

            int activeCount = _npcManager.ActiveNPCCount;
            int totalCount = _npcManager.TotalNPCCount;

            GUI.Box(new Rect(x, y, width, 200f), "NPC Debug Info");
            y += 5f;

            GUI.Label(new Rect(x + 5f, y, width, lineHeight), $"Active NPCs: {activeCount}/{totalCount}");
            y += lineHeight;

            var lodManager = _npcManager.GetLODManager();
            if (lodManager != null)
            {
                GUI.Label(new Rect(x + 5f, y, width, lineHeight), $"LOD Managed: {lodManager.ManagedNPCCount}");
                y += lineHeight;
            }

            var crowdManager = _npcManager.GetCrowdManager();
            if (crowdManager != null)
            {
                GUI.Label(new Rect(x + 5f, y, width, lineHeight), $"Groups: {crowdManager.GroupCount}");
                y += lineHeight;
                GUI.Label(new Rect(x + 5f, y, width, lineHeight), $"Ungrouped: {crowdManager.UngroupedCount}");
                y += lineHeight;
            }

            y += 5f;

            var allNPCs = _npcManager.GetAllNPCs();
            int shown = 0;
            foreach (var npc in allNPCs)
            {
                if (npc == null || shown >= 8) break;

                string profession = npc.Profession != null ? npc.Profession.Type.ToString() : "Unknown";
                string state = npc.StateMachine.CurrentStateType.ToString();
                string rep = npc.Reputation != null ? npc.Reputation.Level.ToString() : "Neutral";

                GUI.Label(new Rect(x + 5f, y, width, lineHeight),
                    $"> {npc.Data.DisplayName} [{profession}] {state} ({rep})");
                y += lineHeight;
                shown++;
            }
        }

        public void DrawGizmosForNPC(NPCBrain npc)
        {
            if (!_showGizmos || npc == null) return;

            Gizmos.color = GetStateColor(npc.StateMachine.CurrentStateType);
            Gizmos.DrawWireSphere(npc.transform.position + Vector3.up * 2f, 0.5f);

            if (npc.HasDestination)
            {
                Gizmos.color = Color.yellow;
                Gizmos.DrawLine(npc.transform.position + Vector3.up, npc.CurrentDestination + Vector3.up);
                Gizmos.DrawWireSphere(npc.CurrentDestination, 0.3f);
            }

            if (npc.Reputation != null)
            {
                Gizmos.color = GetReputationColor(npc.Reputation.Level);
                Gizmos.DrawWireSphere(npc.transform.position + Vector3.up * 3f, 0.3f);
            }
        }

        private Color GetStateColor(Core.NPCStateType state)
        {
            switch (state)
            {
                case Core.NPCStateType.Idle: return Color.gray;
                case Core.NPCStateType.Walking: return Color.green;
                case Core.NPCStateType.Running: return Color.yellow;
                case Core.NPCStateType.Driving: return Color.blue;
                case Core.NPCStateType.Working: return Color.cyan;
                case Core.NPCStateType.Talking: return Color.magenta;
                case Core.NPCStateType.Shopping: return new Color(1f, 0.5f, 0f);
                case Core.NPCStateType.Resting: return new Color(0.5f, 0.5f, 1f);
                case Core.NPCStateType.Fleeing: return Color.red;
                default: return Color.white;
            }
        }

        private Color GetReputationColor(ReputationLevel level)
        {
            switch (level)
            {
                case ReputationLevel.Friendly: return Color.green;
                case ReputationLevel.Neutral: return Color.yellow;
                case ReputationLevel.Hostile: return Color.red;
                case ReputationLevel.Fear: return new Color(1f, 0.5f, 0f);
                default: return Color.white;
            }
        }

        public NPCDebugInfo GetDebugInfo()
        {
            var info = new NPCDebugInfo();
            if (_npcManager == null) return info;

            info.TotalNPCs = _npcManager.TotalNPCCount;
            info.ActiveNPCs = _npcManager.ActiveNPCCount;

            var allNPCs = _npcManager.GetAllNPCs();
            foreach (var npc in allNPCs)
            {
                if (npc == null) continue;
                info.StateCounts[npc.StateMachine.CurrentStateType] =
                    info.StateCounts.GetValueOrDefault(npc.StateMachine.CurrentStateType, 0) + 1;

                if (npc.Profession != null)
                {
                    info.ProfessionCounts[npc.Profession.Type] =
                        info.ProfessionCounts.GetValueOrDefault(npc.Profession.Type, 0) + 1;
                }
            }

            return info;
        }
    }

    public class NPCDebugInfo
    {
        public int TotalNPCs;
        public int ActiveNPCs;
        public Dictionary<Core.NPCStateType, int> StateCounts = new Dictionary<Core.NPCStateType, int>();
        public Dictionary<ProfessionType, int> ProfessionCounts = new Dictionary<ProfessionType, int>();
    }
}
