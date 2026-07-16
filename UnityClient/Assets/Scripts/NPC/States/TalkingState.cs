using UnityEngine;
using RideVerse.NPC.Brain;

namespace RideVerse.NPC.States
{
    public class TalkingState : INPCState
    {
        private readonly NPCBrain _brain;
        private float _talkTimer;
        private float _talkDuration;

        public TalkingState(NPCBrain brain)
        {
            _brain = brain;
        }

        public void Enter()
        {
            _talkTimer = 0f;
            _talkDuration = Random.Range(5f, 15f);
        }

        public void Tick()
        {
            _talkTimer += Time.deltaTime;

            if (_talkTimer >= _talkDuration)
            {
                _brain.StateMachine.ChangeState(Core.NPCStateType.Idle);
            }
        }

        public void Exit() { }
    }
}
