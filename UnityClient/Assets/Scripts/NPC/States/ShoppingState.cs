using UnityEngine;
using RideVerse.NPC.Brain;

namespace RideVerse.NPC.States
{
    public class ShoppingState : INPCState
    {
        private readonly NPCBrain _brain;
        private float _shopTimer;
        private float _shopDuration;

        public ShoppingState(NPCBrain brain)
        {
            _brain = brain;
        }

        public void Enter()
        {
            _shopTimer = 0f;
            _shopDuration = Random.Range(8f, 20f);
        }

        public void Tick()
        {
            _shopTimer += Time.deltaTime;

            if (_shopTimer >= _shopDuration)
            {
                _brain.StateMachine.ChangeState(Core.NPCStateType.Idle);
            }
        }

        public void Exit() { }
    }
}
