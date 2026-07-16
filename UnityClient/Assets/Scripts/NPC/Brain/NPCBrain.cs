using UnityEngine;
using RideVerse.NPC.Core;
using RideVerse.NPC.States;
using RideVerse.NPC.Schedule;
using RideVerse.NPC.Profession;
using RideVerse.NPC.Reputation;

namespace RideVerse.NPC.Brain
{
    [RequireComponent(typeof(CharacterController))]
    public class NPCBrain : MonoBehaviour
    {
        [SerializeField] private NPCConfig _config;

        private NPCStateMachine _stateMachine;
        private NPCData _data;
        private CharacterController _characterController;
        private NPCSchedule _schedule;
        private NPCProfession _profession;
        private NPCReputation _reputation;

        private float _currentSpeed;
        private Vector3 _currentDestination;
        private bool _hasDestination;
        private float _updateTimer;
        private float _aiUpdateInterval = 0.5f;

        public NPCData Data => _data;
        public NPCStateMachine StateMachine => _stateMachine;
        public NPCSchedule Schedule => _schedule;
        public NPCProfession Profession => _profession;
        public NPCReputation Reputation => _reputation;
        public NPCConfig Config => _config;
        public CharacterController CharacterController => _characterController;
        public float CurrentSpeed => _currentSpeed;
        public Vector3 CurrentDestination => _currentDestination;
        public bool HasDestination => _hasDestination;

        public void Initialize(NPCData data, NPCConfig config)
        {
            _data = data;
            _config = config;
            _characterController = GetComponent<CharacterController>();

            _schedule = gameObject.AddComponent<NPCSchedule>();
            _profession = gameObject.AddComponent<NPCProfession>();
            _reputation = gameObject.AddComponent<NPCReputation>();

            _schedule.Initialize(config);
            _profession.Initialize((ProfessionType)data.ProfessionTypeIndex);
            _reputation.Initialize();

            SetupStateMachine();
            RegisterScheduleCallbacks();

            transform.position = data.GetSpawnPosition();
            transform.rotation = Quaternion.Euler(0f, data.SpawnRotationY, 0f);

            _stateMachine.SetInitialState(NPCStateType.Idle);

            Debug.Log($"[NPCBrain] {data.DisplayName} ({_profession.Type}) initialized at {transform.position}");
        }

        private void SetupStateMachine()
        {
            _stateMachine = new NPCStateMachine();

            _stateMachine.RegisterState(NPCStateType.Idle, new IdleState(this));
            _stateMachine.RegisterState(NPCStateType.Walking, new WalkingState(this));
            _stateMachine.RegisterState(NPCStateType.Running, new WalkingState(this));
            _stateMachine.RegisterState(NPCStateType.Driving, new DrivingState(this));
            _stateMachine.RegisterState(NPCStateType.Working, new WorkingState(this));
            _stateMachine.RegisterState(NPCStateType.Talking, new TalkingState(this));
            _stateMachine.RegisterState(NPCStateType.Shopping, new ShoppingState(this));
            _stateMachine.RegisterState(NPCStateType.Resting, new RestingState(this));
            _stateMachine.RegisterState(NPCStateType.WaitingAtLight, new IdleState(this));
            _stateMachine.RegisterState(NPCStateType.CrossingRoad, new WalkingState(this));
            _stateMachine.RegisterState(NPCStateType.Fleeing, new WalkingState(this));
        }

        private void RegisterScheduleCallbacks()
        {
            _schedule.OnActivityChanged += HandleActivityChanged;
        }

        private void HandleActivityChanged(string activityName)
        {
            switch (activityName)
            {
                case "Sleep":
                    _stateMachine.ChangeState(NPCStateType.Resting);
                    break;
                case "WakeUp":
                    _stateMachine.ChangeState(NPCStateType.Idle);
                    break;
                case "GoToWork":
                    SetDestination(GetWorkPosition());
                    _stateMachine.ChangeState(NPCStateType.Walking);
                    break;
                case "Work":
                    _stateMachine.ChangeState(NPCStateType.Working);
                    break;
                case "Lunch":
                    SetDestination(GetShopPosition());
                    _stateMachine.ChangeState(NPCStateType.Walking);
                    break;
                case "GoHome":
                    SetDestination(_data.GetSpawnPosition());
                    _stateMachine.ChangeState(NPCStateType.Walking);
                    break;
                case "Shop":
                    SetDestination(GetShopPosition());
                    _stateMachine.ChangeState(NPCStateType.Walking);
                    break;
                case "Rest":
                    _stateMachine.ChangeState(NPCStateType.Resting);
                    break;
            }
        }

        private Vector3 GetWorkPosition()
        {
            return _data.GetSpawnPosition() + new Vector3(
                Random.Range(-20f, 20f), 0f, Random.Range(-20f, 20f));
        }

        private Vector3 GetShopPosition()
        {
            return _data.GetSpawnPosition() + new Vector3(
                Random.Range(-30f, 30f), 0f, Random.Range(-30f, 30f));
        }

        public void SetDestination(Vector3 destination)
        {
            _currentDestination = destination;
            _hasDestination = true;
        }

        public void ClearDestination()
        {
            _hasDestination = false;
            _currentDestination = Vector3.zero;
        }

        public void SetSpeed(float speed)
        {
            _currentSpeed = speed;
        }

        private void Update()
        {
            _updateTimer += Time.deltaTime;
            if (_updateTimer < _aiUpdateInterval) return;
            _updateTimer = 0f;

            _schedule?.UpdateTime(Time.deltaTime * _config.timeScale);
            _stateMachine?.Update();
        }

        private void OnDisable()
        {
            if (_schedule != null)
            {
                _schedule.OnActivityChanged -= HandleActivityChanged;
            }
        }
    }
}
