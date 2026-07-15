using UnityEngine;
using UnityEngine.InputSystem;
using RideVerse.Core;

namespace RideVerse.Player
{
    [RequireComponent(typeof(CharacterController))]
    public class PlayerController : MonoBehaviour
    {
        [Header("Movement")]
        [SerializeField] private float _walkSpeed = Constants.Player.WalkSpeed;
        [SerializeField] private float _sprintSpeed = Constants.Player.SprintSpeed;
        [SerializeField] private float _jumpForce = Constants.Player.JumpForce;
        [SerializeField] private float _gravity = Constants.Player.Gravity;
        [SerializeField] private float _rotationSpeed = Constants.Player.RotationSpeed;

        [Header("Ground Check")]
        [SerializeField] private float _groundCheckRadius = 0.2f;
        [SerializeField] private float _groundCheckDistance = Constants.Player.GroundCheckDistance;
        [SerializeField] private LayerMask _groundMask;

        private CharacterController _characterController;
        private PlayerAnimator _animator;

        private Vector2 _moveInput;
        private Vector3 _velocity;
        private bool _isGrounded;
        private bool _isSprinting;
        private bool _isJumping;
        private float _currentSpeed;

        public bool IsGrounded => _isGrounded;
        public float CurrentSpeed => _currentSpeed;
        public bool IsMoving => _moveInput.sqrMagnitude > 0.01f;

        private InputActions _inputActions;

        private void Awake()
        {
            _characterController = GetComponent<CharacterController>();
            _animator = GetComponent<PlayerAnimator>();

            _inputActions = new InputActions();

            _inputActions.Player.Move.performed += ctx => _moveInput = ctx.ReadValue<Vector2>();
            _inputActions.Player.Move.canceled += ctx => _moveInput = Vector2.zero;

            _inputActions.Player.Jump.performed += ctx => OnJump();

            _inputActions.Player.Sprint.performed += ctx => _isSprinting = true;
            _inputActions.Player.Sprint.canceled += ctx => _isSprinting = false;
        }

        private void OnEnable()
        {
            _inputActions?.Player.Enable();
        }

        private void OnDisable()
        {
            _inputActions?.Player.Disable();
        }

        private void Update()
        {
            CheckGround();
            HandleMovement();
            HandleGravity();
            ApplyMovement();
        }

        private void CheckGround()
        {
            Vector3 spherePos = transform.position + Vector3.down * _groundCheckRadius;
            _isGrounded = Physics.CheckSphere(
                spherePos, _groundCheckRadius, _groundMask,
                QueryTriggerInteraction.Ignore);

            if (_isGrounded && _velocity.y < 0)
            {
                _velocity.y = -2f;
            }
        }

        private void HandleMovement()
        {
            float targetSpeed = _isSprinting ? _sprintSpeed : _walkSpeed;
            Vector3 moveDir = new Vector3(_moveInput.x, 0f, _moveInput.y).normalized;

            if (moveDir.sqrMagnitude > 0.01f)
            {
                Quaternion targetRotation = Quaternion.LookRotation(moveDir);
                transform.rotation = Quaternion.Slerp(
                    transform.rotation, targetRotation, _rotationSpeed * Time.deltaTime);
            }

            _currentSpeed = Mathf.Lerp(_currentSpeed,
                moveDir.sqrMagnitude > 0.01f ? targetSpeed : 0f,
                Time.deltaTime * 10f);

            _animator?.SetMovementSpeed(_currentSpeed / _sprintSpeed);
        }

        private void HandleGravity()
        {
            if (_isGrounded && _velocity.y < 0)
            {
                _velocity.y = -2f;
            }

            _velocity.y += _gravity * Time.deltaTime;
        }

        private void HandleJump()
        {
            if (_isGrounded)
            {
                _velocity.y = _jumpForce;
                _isJumping = true;
                _animator?.TriggerJump();
            }
        }

        private void ApplyMovement()
        {
            Vector3 move = transform.forward * (_currentSpeed * Time.deltaTime);
            _characterController.Move(move + _velocity * Time.deltaTime);

            if (_isGrounded && _isJumping)
            {
                _isJumping = false;
            }
        }

        private void OnJump()
        {
            HandleJump();
        }

        public void SetInputEnabled(bool enabled)
        {
            if (enabled)
                _inputActions?.Player.Enable();
            else
                _inputActions?.Player.Disable();
        }

        public void Teleport(Vector3 position)
        {
            _characterController.enabled = false;
            transform.position = position;
            _characterController.enabled = true;
        }
    }
}
