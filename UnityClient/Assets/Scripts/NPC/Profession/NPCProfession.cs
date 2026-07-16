using UnityEngine;

namespace RideVerse.NPC.Profession
{
    public class NPCProfession : MonoBehaviour
    {
        private ProfessionType _type;
        private string _workPlaceName;
        private bool _isWorking;

        public ProfessionType Type => _type;
        public string WorkPlaceName => _workPlaceName;
        public bool IsWorking => _isWorking;

        public void Initialize(ProfessionType type)
        {
            _type = type;
            _workPlaceName = GetWorkPlaceName(type);
        }

        public void StartWork()
        {
            _isWorking = true;
        }

        public void StopWork()
        {
            _isWorking = false;
        }

        public float GetBaseSalary()
        {
            switch (_type)
            {
                case ProfessionType.Police: return 3000f;
                case ProfessionType.Doctor: return 5000f;
                case ProfessionType.Mechanic: return 2500f;
                case ProfessionType.Shopkeeper: return 2000f;
                case ProfessionType.TaxiDriver: return 2800f;
                case ProfessionType.BusinessOwner: return 4000f;
                case ProfessionType.Citizen: return 1500f;
                default: return 1500f;
            }
        }

        public Color GetProfessionColor()
        {
            switch (_type)
            {
                case ProfessionType.Police: return new Color(0.2f, 0.3f, 0.7f);
                case ProfessionType.Doctor: return new Color(0.9f, 0.95f, 1f);
                case ProfessionType.Mechanic: return new Color(0.6f, 0.4f, 0.2f);
                case ProfessionType.Shopkeeper: return new Color(0.8f, 0.6f, 0.2f);
                case ProfessionType.TaxiDriver: return new Color(0.9f, 0.85f, 0.1f);
                case ProfessionType.BusinessOwner: return new Color(0.3f, 0.3f, 0.4f);
                case ProfessionType.Citizen: return new Color(0.5f, 0.5f, 0.55f);
                default: return Color.gray;
            }
        }

        private string GetWorkPlaceName(ProfessionType type)
        {
            switch (type)
            {
                case ProfessionType.Police: return "Police Station";
                case ProfessionType.Doctor: return "Hospital";
                case ProfessionType.Mechanic: return "Garage";
                case ProfessionType.Shopkeeper: return "Shop";
                case ProfessionType.TaxiDriver: return "Taxi Stand";
                case ProfessionType.BusinessOwner: return "Office";
                case ProfessionType.Citizen: return "Residence";
                default: return "Unknown";
            }
        }
    }
}
