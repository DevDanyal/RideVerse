using UnityEngine;

namespace RideVerse.NPC.Movement
{
    public class NPCTrafficInteraction : MonoBehaviour
    {
        private float _waitTimer;
        private bool _isWaitingAtLight;
        private bool _isCrossingRoad;

        public bool IsWaitingAtLight => _isWaitingAtLight;
        public bool IsCrossingRoad => _isCrossingRoad;

        public void CheckTrafficLight(Vector3 position, float checkRadius)
        {
            Collider[] hits = Physics.OverlapSphere(position, checkRadius, LayerMask.GetMask("Default"));

            foreach (var hit in hits)
            {
                var trafficLight = hit.GetComponent<Environment.TrafficLight>();
                if (trafficLight != null && trafficLight.IsRed)
                {
                    _isWaitingAtLight = true;
                    _waitTimer = 0f;
                    return;
                }
            }

            _isWaitingAtLight = false;
        }

        public bool ShouldWaitAtLight()
        {
            return _isWaitingAtLight;
        }

        public void StartCrossingRoad()
        {
            _isCrossingRoad = true;
            _waitTimer = 0f;
        }

        public bool IsFinishedCrossing(float crossingTime)
        {
            _waitTimer += Time.deltaTime;
            if (_waitTimer >= crossingTime)
            {
                _isCrossingRoad = false;
                _waitTimer = 0f;
                return true;
            }
            return false;
        }

        public void Reset()
        {
            _isWaitingAtLight = false;
            _isCrossingRoad = false;
            _waitTimer = 0f;
        }
    }
}
