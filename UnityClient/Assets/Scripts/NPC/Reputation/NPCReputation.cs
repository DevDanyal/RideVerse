using UnityEngine;

namespace RideVerse.NPC.Reputation
{
    public class NPCReputation : MonoBehaviour
    {
        private ReputationLevel _level;
        private float _trust;
        private float _fear;
        private float _friendliness;

        public ReputationLevel Level => _level;
        public float Trust => _trust;
        public float Fear => _fear;
        public float Friendliness => _friendliness;

        public void Initialize()
        {
            _level = ReputationLevel.Neutral;
            _trust = 50f;
            _fear = 0f;
            _friendliness = 50f;
        }

        public void Initialize(ReputationLevel level)
        {
            _level = level;
            switch (level)
            {
                case ReputationLevel.Friendly:
                    _trust = 80f;
                    _fear = 0f;
                    _friendliness = 80f;
                    break;
                case ReputationLevel.Neutral:
                    _trust = 50f;
                    _fear = 0f;
                    _friendliness = 50f;
                    break;
                case ReputationLevel.Hostile:
                    _trust = 20f;
                    _fear = 10f;
                    _friendliness = 20f;
                    break;
                case ReputationLevel.Fear:
                    _trust = 10f;
                    _fear = 80f;
                    _friendliness = 30f;
                    break;
            }
        }

        public void ModifyTrust(float amount)
        {
            _trust = Mathf.Clamp(_trust + amount, 0f, 100f);
            UpdateLevel();
        }

        public void ModifyFear(float amount)
        {
            _fear = Mathf.Clamp(_fear + amount, 0f, 100f);
            UpdateLevel();
        }

        public void ModifyFriendliness(float amount)
        {
            _friendliness = Mathf.Clamp(_friendliness + amount, 0f, 100f);
            UpdateLevel();
        }

        private void UpdateLevel()
        {
            if (_fear > 60f)
            {
                _level = ReputationLevel.Fear;
            }
            else if (_friendliness > 65f)
            {
                _level = ReputationLevel.Friendly;
            }
            else if (_friendliness < 30f || _trust < 30f)
            {
                _level = ReputationLevel.Hostile;
            }
            else
            {
                _level = ReputationLevel.Neutral;
            }
        }

        public string GetLevelEmoji()
        {
            switch (_level)
            {
                case ReputationLevel.Friendly: return ":)";
                case ReputationLevel.Hostile: return ">:(";
                case ReputationLevel.Fear: return "O_O";
                default: return "|";
            }
        }
    }
}
