using UnityEngine;
using RideVerse.NPC.Brain;
using RideVerse.NPC.Core;

namespace RideVerse.NPC.Interaction
{
    public class NPCInteraction : MonoBehaviour
    {
        [SerializeField] private float _interactionRange = 3f;
        [SerializeField] private float _greetingRange = 5f;

        private NPCBrain _brain;
        private bool _isInteracting;
        private Transform _interactionTarget;

        public bool IsInteracting => _isInteracting;

        public void Initialize(NPCBrain brain)
        {
            _brain = brain;
        }

        private void Update()
        {
            if (_brain == null) return;

            CheckForPlayer();
        }

        private void CheckForPlayer()
        {
            var player = GameObject.FindWithTag("Player");
            if (player == null) return;

            float distance = Vector3.Distance(transform.position, player.transform.position);

            if (distance <= _greetingRange && !_isInteracting)
            {
                TryGreet(player.transform);
            }

            if (distance <= _interactionRange && !_isInteracting)
            {
                TryInteract(player.transform);
            }
        }

        private void TryGreet(Transform target)
        {
            if (_brain.StateMachine.CurrentStateType != NPCStateType.Idle) return;

            float dot = Vector3.Dot(transform.forward, (target.position - transform.position).normalized);
            if (dot > 0.3f)
            {
                transform.LookAt(new Vector3(target.position.x, transform.position.y, target.position.z));
            }
        }

        private void TryInteract(Transform target)
        {
            if (_brain.StateMachine.CurrentStateType != NPCStateType.Idle) return;

            _isInteracting = true;
            _interactionTarget = target;

            _brain.StateMachine.ChangeState(NPCStateType.Talking);

            float duration = Random.Range(3f, 8f);
            Invoke(nameof(EndInteraction), duration);
        }

        private void EndInteraction()
        {
            _isInteracting = false;
            _interactionTarget = null;
        }

        public string GetGreeting()
        {
            string[] greetings = {
                "Salam!", "Hello!", "Hey!", "How are you?", "Good day!",
                "Nice weather!", "What's up?", "Assalamu Alaikum!"
            };
            return greetings[Random.Range(0, greetings.Length)];
        }

        public string GetFarewell()
        {
            string[] farewells = {
                "Goodbye!", "See you!", "Take care!", "Bye!", "Ma'a salama!"
            };
            return farewells[Random.Range(0, farewells.Length)];
        }
    }
}
