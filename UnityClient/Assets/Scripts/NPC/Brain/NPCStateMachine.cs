using System;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.NPC.Core;

namespace RideVerse.NPC.Brain
{
    public class NPCStateMachine
    {
        private NPCStateType _currentStateType;
        private INPCState _currentState;
        private readonly Dictionary<NPCStateType, INPCState> _states = new Dictionary<NPCStateType, INPCState>();

        public NPCStateType CurrentStateType => _currentStateType;
        public INPCState CurrentState => _currentState;

        public event Action<NPCStateType, NPCStateType> OnStateChanged;

        public void RegisterState(NPCStateType type, INPCState state)
        {
            _states[type] = state;
        }

        public void SetInitialState(NPCStateType type)
        {
            if (_states.TryGetValue(type, out var state))
            {
                _currentStateType = type;
                _currentState = state;
                _currentState.Enter();
            }
        }

        public void ChangeState(NPCStateType newStateType)
        {
            if (newStateType == _currentStateType) return;
            if (!_states.TryGetValue(newStateType, out var newState)) return;

            _currentState?.Exit();
            var oldState = _currentStateType;
            _currentStateType = newStateType;
            _currentState = newState;
            _currentState.Enter();

            OnStateChanged?.Invoke(oldState, newStateType);
        }

        public void Update()
        {
            _currentState?.Tick();
        }

        public void Clear()
        {
            _currentState?.Exit();
            _states.Clear();
            _currentState = null;
        }
    }

    public interface INPCState
    {
        void Enter();
        void Tick();
        void Exit();
    }
}
