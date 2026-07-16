using UnityEngine;
using RideVerse.NPC.Brain;

namespace RideVerse.NPC.States
{
    public class IdleState : INPCState
    {
        private readonly NPCBrain _brain;
        private float _idleTimer;
        private float _idleDuration;

        public IdleState(NPCBrain brain)
        {
            _brain = brain;
        }

        public void Enter()
        {
            _idleTimer = 0f;
            _idleDuration = Random.Range(2f, 6f);
        }

        public void Tick()
        {
            _idleTimer += Time.deltaTime;

            if (_idleTimer >= _idleDuration)
            {
                if (_brain.Schedule != null && _brain.Schedule.CurrentActivity != null)
                {
                    _brain.Schedule.ForceNextActivity();
                }
            }
        }

        public void Exit() { }
    }
}
