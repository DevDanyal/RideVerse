using UnityEngine;
using RideVerse.NPC.Brain;

namespace RideVerse.NPC.States
{
    public class RestingState : INPCState
    {
        private readonly NPCBrain _brain;
        private float _restTimer;
        private float _restDuration;

        public RestingState(NPCBrain brain)
        {
            _brain = brain;
        }

        public void Enter()
        {
            _restTimer = 0f;
            _restDuration = Random.Range(15f, 30f);
        }

        public void Tick()
        {
            _restTimer += Time.deltaTime;

            if (_restTimer >= _restDuration)
            {
                _brain.StateMachine.ChangeState(Core.NPCStateType.Idle);
            }
        }

        public void Exit() { }
    }
}
