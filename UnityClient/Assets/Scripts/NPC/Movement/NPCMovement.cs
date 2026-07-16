using UnityEngine;

namespace RideVerse.NPC.Movement
{
    public class NPCMovement : MonoBehaviour
    {
        private CharacterController _characterController;
        private float _speed = 2f;
        private float _rotationSpeed = 5f;
        private float _obstacleAvoidanceRadius = 1f;
        private float _stoppingDistance = 1f;
        private bool _isMoving;
        private Vector3 _velocity;

        public bool IsMoving => _isMoving;
        public float Speed => _speed;

        public void Initialize(CharacterController characterController, float speed, float rotationSpeed)
        {
            _characterController = characterController;
            _speed = speed;
            _rotationSpeed = rotationSpeed;
        }

        public void MoveTo(Vector3 destination, float stoppingDistance)
        {
            _stoppingDistance = stoppingDistance;
            Vector3 direction = (destination - transform.position);
            direction.y = 0f;
            float distance = direction.magnitude;

            if (distance <= _stoppingDistance)
            {
                _isMoving = false;
                _velocity = Vector3.zero;
                return;
            }

            _isMoving = true;
            Vector3 moveDirection = direction.normalized;

            moveDirection = AvoidObstacles(moveDirection);

            Quaternion targetRotation = Quaternion.LookRotation(moveDirection);
            transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, _rotationSpeed * Time.deltaTime);

            _velocity = moveDirection * _speed;
            _characterController.Move(_velocity * Time.deltaTime);
        }

        public void MoveDirection(Vector3 direction)
        {
            if (direction.sqrMagnitude < 0.01f)
            {
                _isMoving = false;
                return;
            }

            _isMoving = true;
            direction = AvoidObstacles(direction.normalized);

            Quaternion targetRotation = Quaternion.LookRotation(direction);
            transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, _rotationSpeed * Time.deltaTime);

            _velocity = direction * _speed;
            _characterController.Move(_velocity * Time.deltaTime);
        }

        public bool HasReachedDestination(Vector3 destination)
        {
            float distance = Vector3.Distance(
                new Vector3(transform.position.x, 0f, transform.position.z),
                new Vector3(destination.x, 0f, destination.z));
            return distance <= _stoppingDistance;
        }

        public void Stop()
        {
            _isMoving = false;
            _velocity = Vector3.zero;
        }

        public void SetSpeed(float speed)
        {
            _speed = speed;
        }

        private Vector3 AvoidObstacles(Vector3 direction)
        {
            RaycastHit hit;
            Vector3 ahead = transform.position + direction * _obstacleAvoidanceRadius * 2f;

            if (Physics.SphereCast(transform.position, _obstacleAvoidanceRadius * 0.5f, direction, out hit, _obstacleAvoidanceRadius * 2f))
            {
                Vector3 avoidDir = Vector3.Cross(hit.normal, Vector3.up);
                if (avoidDir.sqrMagnitude < 0.01f)
                {
                    avoidDir = Vector3.Cross(Vector3.forward, Vector3.up);
                }
                return Vector3.Lerp(direction, avoidDir.normalized, 0.7f).normalized;
            }

            return direction;
        }

        public void ApplyGravity()
        {
            if (_characterController != null && !_characterController.isGrounded)
            {
                _velocity.y += Physics.gravity.y * Time.deltaTime;
                _characterController.Move(_velocity * Time.deltaTime);
            }
        }
    }
}
