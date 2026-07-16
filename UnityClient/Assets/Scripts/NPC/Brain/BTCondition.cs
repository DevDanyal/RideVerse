using System;

namespace RideVerse.NPC.Brain
{
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
}
