namespace RideVerse.NPC.Brain
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
    }
}
