using System.Collections.Generic;

namespace RideVerse.NPC.Brain
{
    public class BTSequence : BTNode
    {
        private readonly List<BTNode> _children = new List<BTNode>();
        private int _currentIndex;

        public BTSequence(params BTNode[] children)
        {
            _children.AddRange(children);
        }

        public void AddChild(BTNode child)
        {
            _children.Add(child);
        }

        public override BTNodeStatus Evaluate()
        {
            while (_currentIndex < _children.Count)
            {
                var status = _children[_currentIndex].Evaluate();

                if (status == BTNodeStatus.Running)
                {
                    return BTNodeStatus.Running;
                }

                if (status == BTNodeStatus.Failure)
                {
                    _currentIndex = 0;
                    return BTNodeStatus.Failure;
                }

                _currentIndex++;
            }

            _currentIndex = 0;
            return BTNodeStatus.Success;
        }

        public override void Reset()
        {
            _currentIndex = 0;
            foreach (var child in _children)
            {
                child.Reset();
            }
        }
    }
}
