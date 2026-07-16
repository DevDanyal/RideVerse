using UnityEngine;
using RideVerse.NPC.Brain;
using RideVerse.NPC.Core;
using RideVerse.NPC.Movement;

namespace RideVerse.NPC.Vehicle
{
    public class NPCVehicleDriver : MonoBehaviour
    {
        private NPCBrain _brain;
        private NPCMovement _movement;
        private bool _isInVehicle;
        private float _driveSpeed;
        private Vector3 _driveDestination;

        public bool IsInVehicle => _isInVehicle;

        public void Initialize(NPCBrain brain)
        {
            _brain = brain;
        }

        public void EnterVehicle(Vector3 vehiclePosition, float vehicleRotation)
        {
            _isInVehicle = true;
            transform.position = vehiclePosition + Vector3.up * 0.5f;
            transform.rotation = Quaternion.Euler(0f, vehicleRotation, 0f);
            _driveSpeed = _brain.Config.vehicleSpeed;
            _brain.StateMachine.ChangeState(NPCStateType.Driving);
        }

        public void DriveTo(Vector3 destination)
        {
            _driveDestination = destination;
        }

        public void ExitVehicle()
        {
            _isInVehicle = false;
            transform.position += transform.right * 2f;
            _brain.StateMachine.ChangeState(NPCStateType.Idle);
        }

        public void ParkVehicle()
        {
            ExitVehicle();
        }
    }
}
