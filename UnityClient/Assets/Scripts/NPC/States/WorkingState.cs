using UnityEngine;
using RideVerse.NPC.Brain;

namespace RideVerse.NPC.States
{
    public class WorkingState : INPCState
    {
        private readonly NPCBrain _brain;
        private float _workTimer;
        private float _workDuration;

        public WorkingState(NPCBrain brain)
        {
            _brain = brain;
        }

        public void Enter()
        {
            _workTimer = 0f;
            _workDuration = Random.Range(20f, 40f);
        }

        public void Tick()
        {
            _workTimer += Time.deltaTime;

            if (_workTimer >= _workDuration)
            {
                _brain.StateMachine.ChangeState(Core.NPCStateType.Idle);
            }
        }

        public void Exit() { }
    }
}
