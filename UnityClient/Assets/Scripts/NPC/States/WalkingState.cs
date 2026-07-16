using UnityEngine;
using RideVerse.NPC.Brain;
using RideVerse.NPC.Movement;

namespace RideVerse.NPC.States
{
    public class WalkingState : INPCState
    {
        private readonly NPCBrain _brain;
        private NPCMovement _movement;

        public WalkingState(NPCBrain brain)
        {
            _brain = brain;
        }

        public void Enter()
        {
            _movement = _brain.GetComponent<NPCMovement>();
            if (_movement == null)
            {
                _movement = _brain.gameObject.AddComponent<NPCMovement>();
            }

            float speed = _brain.StateMachine.CurrentStateType == Core.NPCStateType.Running
                ? _brain.Config.runSpeed
                : _brain.Config.walkSpeed;

            _movement.Initialize(_brain.CharacterController, speed, 5f);
            _brain.SetSpeed(speed);
        }

        public void Tick()
        {
            if (!_brain.HasDestination)
            {
                _brain.StateMachine.ChangeState(Core.NPCStateType.Idle);
                return;
            }

            _movement.MoveTo(_brain.CurrentDestination, _brain.Config.stoppingDistance);

            if (_movement.HasReachedDestination(_brain.CurrentDestination))
            {
                _movement.Stop();
                _brain.ClearDestination();
                _brain.StateMachine.ChangeState(Core.NPCStateType.Idle);
            }
        }

        public void Exit()
        {
            _movement?.Stop();
        }
    }
}
