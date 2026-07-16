using UnityEngine;
using RideVerse.NPC.Brain;

namespace RideVerse.NPC.States
{
    public class DrivingState : INPCState
    {
        private readonly NPCBrain _brain;
        private float _driveTimer;
        private float _driveDuration;

        public DrivingState(NPCBrain brain)
        {
            _brain = brain;
        }

        public void Enter()
        {
            _driveTimer = 0f;
            _driveDuration = Random.Range(10f, 30f);
        }

        public void Tick()
        {
            _driveTimer += Time.deltaTime;

            if (_driveTimer >= _driveDuration || !_brain.HasDestination)
            {
                _brain.StateMachine.ChangeState(Core.NPCStateType.Idle);
            }
        }

        public void Exit() { }
    }
}
