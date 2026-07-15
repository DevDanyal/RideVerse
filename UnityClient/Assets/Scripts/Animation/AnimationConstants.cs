namespace RideVerse.Animation
{
    public static class AnimationConstants
    {
        public static class Params
        {
            public const string Speed = "Speed";
            public const string VerticalSpeed = "VerticalSpeed";
            public const string HorizontalSpeed = "HorizontalSpeed";
            public const string IsGrounded = "IsGrounded";
            public const string IsMoving = "IsMoving";
            public const string IsSprinting = "IsSprinting";
            public const string Jump = "Jump";
            public const string Land = "Land";
            public const string Interact = "Interact";
            public const string Attack = "Attack";
            public const string TakeDamage = "TakeDamage";
            public const string Die = "Die";
            public const string Wave = "Wave";
            public const string Point = "Point";
        }

        public static class States
        {
            public const string Idle = "Idle";
            public const string Walk = "Walk";
            public const string Run = "Run";
            public const string Jump = "Jump";
            public const string Fall = "Fall";
            public const string Land = "Land";
        }

        public static class Layers
        {
            public const int Base = 0;
            public const int UpperBody = 1;
            public const int Overlay = 2;
        }
    }
}
