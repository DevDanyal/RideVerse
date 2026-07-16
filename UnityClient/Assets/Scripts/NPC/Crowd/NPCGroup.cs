using System.Collections.Generic;
using UnityEngine;
using RideVerse.NPC.Core;
using RideVerse.NPC.Brain;

namespace RideVerse.NPC.Crowd
{
    public class NPCGroup
    {
        public string Id;
        public List<NPCBrain> Members;
        public Vector3 Destination;
        public bool IsActive;
        public float GroupSpeed;

        public NPCGroup()
        {
            Id = System.Guid.NewGuid().ToString("N").Substring(0, 6);
            Members = new List<NPCBrain>();
            IsActive = false;
            GroupSpeed = 1.8f;
        }

        public int MemberCount => Members.Count;

        public void AddMember(NPCBrain member)
        {
            if (!Members.Contains(member))
            {
                Members.Add(member);
            }
        }

        public void RemoveMember(NPCBrain member)
        {
            Members.Remove(member);
        }

        public void SetDestination(Vector3 destination)
        {
            Destination = destination;
            float offset = 0f;
            foreach (var member in Members)
            {
                if (member == null) continue;
                Vector3 memberDest = destination + new Vector3(
                    Random.Range(-2f, 2f), 0f, offset);
                member.SetDestination(memberDest);
                offset += 1.5f;
            }
        }
    }

    public class CrowdManager : MonoBehaviour
    {
        [SerializeField] private int _maxGroupSize = 5;
        [SerializeField] private float _groupFormationRadius = 10f;

        private List<NPCGroup> _groups = new List<NPCGroup>();
        private List<NPCBrain> _ungroupedNPCs = new List<NPCBrain>();

        public int GroupCount => _groups.Count;
        public int UngroupedCount => _ungroupedNPCs.Count;

        public NPCGroup FormGroup(List<NPCBrain> members)
        {
            if (members.Count > _maxGroupSize)
            {
                members = members.GetRange(0, _maxGroupSize);
            }

            var group = new NPCGroup();
            foreach (var member in members)
            {
                group.AddMember(member);
            }

            _groups.Add(group);
            foreach (var member in members)
            {
                _ungroupedNPCs.Remove(member);
            }

            return group;
        }

        public NPCGroup FindNearbyGroup(Vector3 position, float radius)
        {
            foreach (var group in _groups)
            {
                if (group.Members.Count == 0) continue;
                if (group.Members[0] == null) continue;

                float distance = Vector3.Distance(position, group.Members[0].transform.position);
                if (distance <= radius)
                {
                    return group;
                }
            }
            return null;
        }

        public void DisbandGroup(NPCGroup group)
        {
            if (group == null) return;
            foreach (var member in group.Members)
            {
                if (member != null)
                {
                    _ungroupedNPCs.Add(member);
                }
            }
            _groups.Remove(group);
        }

        public void RegisterUngrouped(NPCBrain npc)
        {
            if (!_ungroupedNPCs.Contains(npc))
            {
                _ungroupedNPCs.Add(npc);
            }
        }

        public void UnregisterUngrouped(NPCBrain npc)
        {
            _ungroupedNPCs.Remove(npc);
        }

        public void TryFormRandomGroups()
        {
            if (_ungroupedNPCs.Count < 2) return;

            int groupsToForm = Mathf.Min(2, _ungroupedNPCs.Count / 3);

            for (int g = 0; g < groupsToForm; g++)
            {
                if (_ungroupedNPCs.Count < 2) break;

                int groupSize = Random.Range(2, Mathf.Min(4, _ungroupedNPCs.Count + 1));
                var members = new List<NPCBrain>();

                for (int i = 0; i < groupSize; i++)
                {
                    int index = Random.Range(0, _ungroupedNPCs.Count);
                    members.Add(_ungroupedNPCs[index]);
                    _ungroupedNPCs.RemoveAt(index);
                }

                var group = FormGroup(members);
                Vector3 randomDest = members[0].transform.position + new Vector3(
                    Random.Range(-30f, 30f), 0f, Random.Range(-30f, 30f));
                group.SetDestination(randomDest);
                group.IsActive = true;
            }
        }

        public List<NPCGroup> GetAllGroups() => new List<NPCGroup>(_groups);
    }
}
