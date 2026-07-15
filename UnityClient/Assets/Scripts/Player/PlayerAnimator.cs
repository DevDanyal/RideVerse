using UnityEngine;
using RideVerse.Core;

namespace RideVerse.Player
{
    [RequireComponent(typeof(Animator))]
    public class PlayerAnimator : MonoBehaviour
    {
        private Animator _animator;
        private PlayerController _controller;

        private int _speedHash;
        private int _verticalSpeedHash;
        private int _isGroundedHash;
        private int _isMovingHash;
        private int _jumpHash;
        private int _landHash;
        private int _takeDamageHash;

        private float _currentSpeed;
        private float _speedDampVelocity;

        private void Awake()
        {
            _animator = GetComponent<Animator>();
            _controller = GetComponent<PlayerController>();

            CacheHashes();
        }

        private void CacheHashes()
        {
            _speedHash = Animator.StringToHash(Animation.AnimationConstants.Params.Speed);
            _verticalSpeedHash = Animator.StringToHash(Animation.AnimationConstants.Params.VerticalSpeed);
            _isGroundedHash = Animator.StringToHash(Animation.AnimationConstants.Params.IsGrounded);
            _isMovingHash = Animator.StringToHash(Animation.AnimationConstants.Params.IsMoving);
            _jumpHash = Animator.StringToHash(Animation.AnimationConstants.Params.Jump);
            _landHash = Animator.StringToHash(Animation.AnimationConstants.Params.Land);
            _takeDamageHash = Animator.StringToHash(Animation.AnimationConstants.Params.TakeDamage);
        }

        private void Update()
        {
            if (_animator == null || _controller == null) return;

            UpdateLocomotion();
        }

        private void UpdateLocomotion()
        {
            float targetSpeed = _controller.IsMoving ? _controller.CurrentSpeed : 0f;
            _currentSpeed = Mathf.SmoothDamp(_currentSpeed, targetSpeed, ref _speedDampVelocity, 0.15f);

            _animator.SetFloat(_speedHash, _currentSpeed);
            _animator.SetBool(_isGroundedHash, _controller.IsGrounded);
            _animator.SetBool(_isMovingHash, _controller.IsMoving);
        }

        public void SetMovementSpeed(float normalizedSpeed)
        {
            if (_animator != null)
            {
                _animator.SetFloat(_speedHash, normalizedSpeed);
            }
        }

        public void TriggerJump()
        {
            if (_animator != null)
            {
                _animator.SetTrigger(_jumpHash);
            }
        }

        public void TriggerLand()
        {
            if (_animator != null)
            {
                _animator.SetTrigger(_landHash);
            }
        }

        public void TriggerTakeDamage()
        {
            if (_animator != null)
            {
                _animator.SetTrigger(_takeDamageHash);
            }
        }

        public void SetLayerWeight(int layerIndex, float weight)
        {
            if (_animator != null && layerIndex < _animator.layerCount)
            {
                _animator.SetLayerWeight(layerIndex, weight);
            }
        }

        public void PlayAnimation(string stateName, int layer = 0, float normalizedTime = 0f)
        {
            if (_animator != null)
            {
                _animator.Play(stateName, layer, normalizedTime);
            }
        }

        public void SetBool(string parameter, bool value)
        {
            if (_animator != null)
            {
                _animator.SetBool(parameter, value);
            }
        }

        public void SetFloat(string parameter, float value)
        {
            if (_animator != null)
            {
                _animator.SetFloat(parameter, value);
            }
        }

        public void SetTrigger(string parameter)
        {
            if (_animator != null)
            {
                _animator.SetTrigger(parameter);
            }
        }
    }
}
