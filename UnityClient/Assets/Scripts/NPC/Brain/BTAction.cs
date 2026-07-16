using System;

namespace RideVerse.NPC.Brain
{
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
}
