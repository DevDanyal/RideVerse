using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Traffic.AI
{
    public enum BTNodeStatus
    {
        Success,
        Failure,
        Running
    }

    public abstract class BTNode
    {
        public abstract BTNodeStatus Evaluate();
        public virtual void Reset() { }
        public virtual void Abort() { }
    }

    public class BTCondition : BTNode
    {
        private readonly Func<bool> _condition;

        public BTCondition(Func<bool> condition)
        {
            _condition = condition;
        }

        public override BTNodeStatus Evaluate()
        {
            return _condition() ? BTNodeStatus.Success : BTNodeStatus.Failure;
        }
    }

    public class BTAction : BTNode
    {
        private readonly Func<BTNodeStatus> _action;

        public BTAction(Func<BTNodeStatus> action)
        {
            _action = action;
        }

        public override BTNodeStatus Evaluate()
        {
            return _action();
        }
    }

    public class BTSequence : BTNode
    {
        private readonly BTNode[] _children;
        private int _currentIndex;

        public BTSequence(params BTNode[] children)
        {
            _children = children;
        }

        public override BTNodeStatus Evaluate()
        {
            for (; _currentIndex < _children.Length; _currentIndex++)
            {
                var status = _children[_currentIndex].Evaluate();
                if (status != BTNodeStatus.Success)
                    return status;
            }
            return BTNodeStatus.Success;
        }

        public override void Reset()
        {
            _currentIndex = 0;
            foreach (var child in _children)
                child.Reset();
        }
    }

    public class BTSelector : BTNode
    {
        private readonly BTNode[] _children;
        private int _currentIndex;

        public BTSelector(params BTNode[] children)
        {
            _children = children;
        }

        public override BTNodeStatus Evaluate()
        {
            for (; _currentIndex < _children.Length; _currentIndex++)
            {
                var status = _children[_currentIndex].Evaluate();
                if (status != BTNodeStatus.Failure)
                    return status;
            }
            return BTNodeStatus.Failure;
        }

        public override void Reset()
        {
            _currentIndex = 0;
            foreach (var child in _children)
                child.Reset();
        }
    }

    public class BTRepeater : BTNode
    {
        private readonly BTNode _child;
        private readonly int _maxRepeats;
        private int _count;

        public BTRepeater(BTNode child, int maxRepeats = -1)
        {
            _child = child;
            _maxRepeats = maxRepeats;
        }

        public override BTNodeStatus Evaluate()
        {
            if (_maxRepeats > 0 && _count >= _maxRepeats)
                return BTNodeStatus.Success;

            var status = _child.Evaluate();
            _count++;

            if (status == BTNodeStatus.Running)
                return BTNodeStatus.Running;

            return BTNodeStatus.Success;
        }

        public override void Reset()
        {
            _count = 0;
            _child.Reset();
        }
    }

    public class BTCooldown : BTNode
    {
        private readonly BTNode _child;
        private readonly float _cooldownTime;
        private float _lastExecuteTime;

        public BTCooldown(BTNode child, float cooldownTime)
        {
            _child = child;
            _cooldownTime = cooldownTime;
        }

        public override BTNodeStatus Evaluate()
        {
            if (Time.time - _lastExecuteTime < _cooldownTime)
                return BTNodeStatus.Failure;

            var status = _child.Evaluate();
            if (status == BTNodeStatus.Success)
                _lastExecuteTime = Time.time;

            return status;
        }

        public override void Reset()
        {
            _lastExecuteTime = 0f;
        }
    }
}
