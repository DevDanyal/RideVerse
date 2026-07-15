using System;
using UnityEngine;

namespace RideVerse.Player
{
    [Serializable]
    public class PlayerProfileData
    {
        public string PlayerId;
        public string AccountId;
        public string DisplayName;
        public int Level;
        public int Experience;
        public double Cash;
        public double BankBalance;
        public int Reputation;
        public int Health;
        public int Stamina;
        public int Energy;
        public int WantedLevel;

        public static PlayerProfileData FromApiProfile(Auth.PlayerProfile api)
        {
            return new PlayerProfileData
            {
                PlayerId = api.Id,
                AccountId = api.AccountId,
                DisplayName = api.DisplayName,
                Level = api.Level,
                Experience = api.Experience,
                Cash = api.Cash,
                BankBalance = api.BankBalance,
                Reputation = api.Reputation,
                Health = api.Health,
                Stamina = api.Stamina,
                Energy = api.Energy,
                WantedLevel = api.WantedLevel
            };
        }
    }
}
