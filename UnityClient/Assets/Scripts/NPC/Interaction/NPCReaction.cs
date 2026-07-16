using UnityEngine;
using RideVerse.NPC.Brain;
using RideVerse.NPC.Core;
using RideVerse.NPC.Reputation;

namespace RideVerse.NPC.Interaction
{
    public class NPCReaction : MonoBehaviour
    {
        private NPCBrain _brain;
        private NPCReputation _reputation;

        public void Initialize(NPCBrain brain)
        {
            _brain = brain;
            _reputation = brain.GetComponent<NPCReputation>();
        }

        public void ReactToPlayer(Transform player, string playerAction)
        {
            if (_brain == null || _reputation == null) return;

            float distance = Vector3.Distance(transform.position, player.position);
            if (distance > _brain.Config.playerReactionRange) return;

            switch (playerAction)
            {
                case "DriveBy":
                    if (_reputation.Fear > 50f)
                    {
                        _brain.StateMachine.ChangeState(NPCStateType.Fleeing);
                    }
                    break;

                case "Nearby":
                    if (_reputation.Friendliness > 60f)
                    {
                        _brain.StateMachine.ChangeState(NPCStateType.Talking);
                    }
                    break;

                case "Threaten":
                    _reputation.ModifyFear(20f);
                    _reputation.ModifyFriendliness(-15f);
                    _brain.StateMachine.ChangeState(NPCStateType.Fleeing);
                    break;

                case "Help":
                    _reputation.ModifyTrust(15f);
                    _reputation.ModifyFriendliness(20f);
                    _reputation.ModifyFear(-10f);
                    break;

                case "Attack":
                    _reputation.ModifyFear(40f);
                    _reputation.ModifyFriendliness(-30f);
                    _reputation.ModifyTrust(-20f);
                    _brain.StateMachine.ChangeState(NPCStateType.Fleeing);
                    break;
            }
        }

        public void ReactToVehicle(float vehicleSpeed)
        {
            if (vehicleSpeed > 20f)
            {
                float reactionChance = _reputation.Fear / 100f;
                if (Random.value < reactionChance)
                {
                    _brain.StateMachine.ChangeState(NPCStateType.Fleeing);
                }
            }
        }

        public void ReactToWeather(string weather)
        {
            switch (weather)
            {
                case "Rain":
                    _brain.SetDestination(transform.position + new Vector3(
                        Random.Range(-10f, 10f), 0f, Random.Range(-10f, 10f)));
                    _brain.StateMachine.ChangeState(NPCStateType.Walking);
                    break;

                case "Storm":
                    _brain.StateMachine.ChangeState(NPCStateType.Resting);
                    break;
            }
        }

        public void ReactToTimeOfDay(float hour)
        {
            if (hour >= 22f || hour < 6f)
            {
                if (_brain.StateMachine.CurrentStateType == NPCStateType.Walking)
                {
                    _brain.SetDestination(_brain.Data.GetSpawnPosition());
                }
            }
        }
    }
}
