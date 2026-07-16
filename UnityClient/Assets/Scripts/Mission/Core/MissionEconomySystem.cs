using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.Mission.Core
{
    public class MissionEconomySystem
    {
        private readonly MissionConfig _config;
        private double _cash;
        private double _bankBalance;
        private int _totalCashEarned;
        private int _totalCashSpent;

        public double Cash => _cash;
        public double BankBalance => _bankBalance;
        public int TotalCashEarned => _totalCashEarned;
        public int TotalCashSpent => _totalCashSpent;

        public event Action<double> OnCashChanged;
        public event Action<double> OnBankChanged;
        public event Action<int> OnCashEarned;
        public event Action<int> OnCashSpent;
        public event Action<string, int> OnMissionRewardReceived;

        public MissionEconomySystem(MissionConfig config)
        {
            _config = config;
        }

        public void Initialize(double startingCash, double startingBank)
        {
            _cash = startingCash;
            _bankBalance = startingBank;
        }

        public bool AddCash(int amount, string source = "")
        {
            if (amount <= 0) return false;

            _cash += amount;
            _totalCashEarned += amount;

            OnCashChanged?.Invoke(_cash);
            OnCashEarned?.Invoke(amount);

            if (!string.IsNullOrEmpty(source))
            {
                OnMissionRewardReceived?.Invoke(source, amount);
            }

            return true;
        }

        public bool SpendCash(int amount, string reason = "")
        {
            if (amount <= 0 || _cash < amount) return false;

            _cash -= amount;
            _totalCashSpent += amount;

            OnCashChanged?.Invoke(_cash);
            OnCashSpent?.Invoke(amount);

            return true;
        }

        public bool CanAfford(int amount)
        {
            return _cash >= amount;
        }

        public void DepositToBank(int amount)
        {
            if (amount <= 0 || _cash < amount) return;

            _cash -= amount;
            _bankBalance += amount;

            OnCashChanged?.Invoke(_cash);
            OnBankChanged?.Invoke(_bankBalance);
        }

        public void WithdrawFromBank(int amount)
        {
            if (amount <= 0 || _bankBalance < amount) return;

            _bankBalance -= amount;
            _cash += amount;

            OnCashChanged?.Invoke(_cash);
            OnBankChanged?.Invoke(_bankBalance);
        }

        public void GrantMissionRewards(string missionId, List<MissionRewardEntry> rewards)
        {
            if (rewards == null) return;

            foreach (var reward in rewards)
            {
                switch (reward.Type)
                {
                    case RewardType.Cash:
                        AddCash(reward.Amount, missionId);
                        break;
                }
            }
        }

        public void SetCash(double amount)
        {
            _cash = Mathf.Max(0f, (float)amount);
            OnCashChanged?.Invoke(_cash);
        }

        public void SetBankBalance(double amount)
        {
            _bankBalance = Mathf.Max(0f, (float)amount);
            OnBankChanged?.Invoke(_bankBalance);
        }

        public double GetNetWorth()
        {
            return _cash + _bankBalance;
        }

        public void ClearAll()
        {
            _cash = 0;
            _bankBalance = 0;
            _totalCashEarned = 0;
            _totalCashSpent = 0;
        }
    }
}
