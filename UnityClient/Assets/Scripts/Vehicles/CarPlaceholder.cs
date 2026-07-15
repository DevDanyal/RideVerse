using UnityEngine;

namespace RideVerse.Vehicles
{
    [RequireComponent(typeof(CarController))]
    [RequireComponent(typeof(Rigidbody))]
    public class CarPlaceholder : MonoBehaviour
    {
        [Header("Build")]
        [SerializeField] private bool buildOnStart = true;

        [Header("Colors")]
        [SerializeField] private Color bodyColor = new Color(0.2f, 0.4f, 0.8f);
        [SerializeField] private Color windowColor = new Color(0.3f, 0.5f, 0.7f, 0.6f);
        [SerializeField] private Color tireColor = new Color(0.1f, 0.1f, 0.1f);
        [SerializeField] private Color metalColor = new Color(0.6f, 0.6f, 0.65f);
        [SerializeField] private Color headlightColor = new Color(1f, 0.95f, 0.8f);
        [SerializeField] private Color brakeLightColor = new Color(0.8f, 0.05f, 0.05f);
        [SerializeField] private Color interiorColor = new Color(0.15f, 0.12f, 0.1f);

        private CarController _controller;
        private WheelCollider[] _wheelColliders;

        private void Awake()
        {
            _controller = GetComponent<CarController>();
            if (buildOnStart) BuildPlaceholderCar();
        }

        public void BuildPlaceholderCar()
        {
            ClearChildren();
            BuildBody();
            BuildWindows();
            BuildWheels();
            BuildHeadlights();
            BuildBrakeLights();
            BuildIndicators();
            BuildInterior();
            BuildExhaust();
            SetupComponents();
            WireDriverReferences();
        }

        private void ClearChildren()
        {
            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                if (Application.isPlaying) Destroy(transform.GetChild(i).gameObject);
                else DestroyImmediate(transform.GetChild(i).gameObject);
            }

            var existingColliders = GetComponents<WheelCollider>();
            foreach (var col in existingColliders)
            {
                if (Application.isPlaying) Destroy(col);
                else DestroyImmediate(col);
            }
        }

        private GameObject CreatePrimitive(PrimitiveType type, string name, Vector3 localPos,
            Vector3 localScale, Color color, Transform parent = null)
        {
            GameObject go = GameObject.CreatePrimitive(type);
            go.name = name;
            go.transform.SetParent(parent != null ? parent : transform);
            go.transform.localPosition = localPos;
            go.transform.localScale = localScale;
            go.transform.localRotation = Quaternion.identity;

            var renderer = go.GetComponent<Renderer>();
            if (renderer != null)
            {
                var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                mat.color = color;
                mat.SetFloat("_Smoothness", 0.5f);
                mat.SetFloat("_Metallic", color == metalColor ? 0.8f : 0.2f);
                renderer.material = mat;
            }

            return go;
        }

        private void BuildBody()
        {
            CreatePrimitive(PrimitiveType.Cube, "Body_Main",
                new Vector3(0f, 0.5f, 0f), new Vector3(1.8f, 0.6f, 4.2f), bodyColor);

            CreatePrimitive(PrimitiveType.Cube, "Body_Front",
                new Vector3(0f, 0.55f, 1.2f), new Vector3(1.6f, 0.4f, 0.8f), bodyColor);

            CreatePrimitive(PrimitiveType.Cube, "Body_Rear",
                new Vector3(0f, 0.55f, -1.4f), new Vector3(1.6f, 0.4f, 0.6f), bodyColor);

            CreatePrimitive(PrimitiveType.Cube, "Body_Roof",
                new Vector3(0f, 0.9f, -0.2f), new Vector3(1.6f, 0.5f, 1.6f), bodyColor);

            CreatePrimitive(PrimitiveType.Cube, "Body_Bumper_Front",
                new Vector3(0f, 0.35f, 1.8f), new Vector3(1.7f, 0.25f, 0.15f), metalColor);

            CreatePrimitive(PrimitiveType.Cube, "Body_Bumper_Rear",
                new Vector3(0f, 0.35f, -1.8f), new Vector3(1.7f, 0.25f, 0.15f), metalColor);
        }

        private void BuildWindows()
        {
            CreatePrimitive(PrimitiveType.Cube, "Window_Windshield",
                new Vector3(0f, 0.85f, 0.5f), new Vector3(1.4f, 0.45f, 0.05f), windowColor);

            CreatePrimitive(PrimitiveType.Cube, "Window_Rear",
                new Vector3(0f, 0.85f, -0.9f), new Vector3(1.4f, 0.35f, 0.05f), windowColor);

            CreatePrimitive(PrimitiveType.Cube, "Window_Left",
                new Vector3(-0.82f, 0.85f, -0.2f), new Vector3(0.05f, 0.35f, 1.2f), windowColor);

            CreatePrimitive(PrimitiveType.Cube, "Window_Right",
                new Vector3(0.82f, 0.85f, -0.2f), new Vector3(0.05f, 0.35f, 1.2f), windowColor);
        }

        private void BuildWheels()
        {
            float wheelRadius = 0.33f;
            float trackHalf = 0.77f;
            float frontZ = 1.15f;
            float rearZ = -1.15f;
            float wheelWidth = 0.25f;

            GameObject fl = CreatePrimitive(PrimitiveType.Cylinder, "Wheel_FL",
                new Vector3(-trackHalf, wheelRadius, frontZ), new Vector3(wheelRadius * 2, wheelWidth, wheelRadius * 2), tireColor);
            fl.transform.localRotation = Quaternion.Euler(0f, 0f, 90f);

            GameObject fr = CreatePrimitive(PrimitiveType.Cylinder, "Wheel_FR",
                new Vector3(trackHalf, wheelRadius, frontZ), new Vector3(wheelRadius * 2, wheelWidth, wheelRadius * 2), tireColor);
            fr.transform.localRotation = Quaternion.Euler(0f, 0f, 90f);

            GameObject rl = CreatePrimitive(PrimitiveType.Cylinder, "Wheel_RL",
                new Vector3(-trackHalf, wheelRadius, rearZ), new Vector3(wheelRadius * 2, wheelWidth, wheelRadius * 2), tireColor);
            rl.transform.localRotation = Quaternion.Euler(0f, 0f, 90f);

            GameObject rr = CreatePrimitive(PrimitiveType.Cylinder, "Wheel_RR",
                new Vector3(trackHalf, wheelRadius, rearZ), new Vector3(wheelRadius * 2, wheelWidth, wheelRadius * 2), tireColor);
            rr.transform.localRotation = Quaternion.Euler(0f, 0f, 90f);

            SetupWheelColliders();
        }

        private void SetupWheelColliders()
        {
            float wheelRadius = 0.33f;
            float trackHalf = 0.77f;
            float frontZ = 1.15f;
            float rearZ = -1.15f;
            float suspensionTravel = 0.08f;

            var fl = gameObject.AddComponent<WheelCollider>();
            fl.radius = wheelRadius;
            fl.suspensionDistance = suspensionTravel;
            fl.transform.localPosition = new Vector3(-trackHalf, wheelRadius, frontZ);
            ConfigureSuspension(fl, true);

            var fr = gameObject.AddComponent<WheelCollider>();
            fr.radius = wheelRadius;
            fr.suspensionDistance = suspensionTravel;
            fr.transform.localPosition = new Vector3(trackHalf, wheelRadius, frontZ);
            ConfigureSuspension(fr, true);

            var rl = gameObject.AddComponent<WheelCollider>();
            rl.radius = wheelRadius;
            rl.suspensionDistance = suspensionTravel;
            rl.transform.localPosition = new Vector3(-trackHalf, wheelRadius, rearZ);
            ConfigureSuspension(rl, false);

            var rr = gameObject.AddComponent<WheelCollider>();
            rr.radius = wheelRadius;
            rr.suspensionDistance = suspensionTravel;
            rr.transform.localPosition = new Vector3(trackHalf, wheelRadius, rearZ);
            ConfigureSuspension(rr, false);
        }

        private void ConfigureSuspension(WheelCollider wheel, bool isFront)
        {
            JointSpring spring = wheel.suspensionSpring;
            spring.spring = isFront ? 45000f : 52000f;
            spring.damper = isFront ? 5500f : 6000f;
            spring.targetPosition = 0.5f;
            wheel.suspensionSpring = spring;
        }

        private void BuildHeadlights()
        {
            CreatePrimitive(PrimitiveType.Cube, "Headlight_Left",
                new Vector3(-0.55f, 0.5f, 1.85f), new Vector3(0.25f, 0.12f, 0.05f), headlightColor);

            CreatePrimitive(PrimitiveType.Cube, "Headlight_Right",
                new Vector3(0.55f, 0.5f, 1.85f), new Vector3(0.25f, 0.12f, 0.05f), headlightColor);
        }

        private void BuildBrakeLights()
        {
            CreatePrimitive(PrimitiveType.Cube, "BrakeLight_Left",
                new Vector3(-0.6f, 0.5f, -1.85f), new Vector3(0.2f, 0.1f, 0.05f), brakeLightColor);

            CreatePrimitive(PrimitiveType.Cube, "BrakeLight_Right",
                new Vector3(0.6f, 0.5f, -1.85f), new Vector3(0.2f, 0.1f, 0.05f), brakeLightColor);
        }

        private void BuildIndicators()
        {
            Color indicatorColor = new Color(1f, 0.5f, 0f);

            CreatePrimitive(PrimitiveType.Cube, "Indicator_LF",
                new Vector3(-0.8f, 0.45f, 1.8f), new Vector3(0.08f, 0.08f, 0.03f), indicatorColor);
            CreatePrimitive(PrimitiveType.Cube, "Indicator_RF",
                new Vector3(0.8f, 0.45f, 1.8f), new Vector3(0.08f, 0.08f, 0.03f), indicatorColor);
            CreatePrimitive(PrimitiveType.Cube, "Indicator_LR",
                new Vector3(-0.8f, 0.45f, -1.8f), new Vector3(0.08f, 0.08f, 0.03f), indicatorColor);
            CreatePrimitive(PrimitiveType.Cube, "Indicator_RR",
                new Vector3(0.8f, 0.45f, -1.8f), new Vector3(0.08f, 0.08f, 0.03f), indicatorColor);
        }

        private void BuildInterior()
        {
            CreatePrimitive(PrimitiveType.Cube, "Dashboard",
                new Vector3(0f, 0.65f, 0.7f), new Vector3(1.4f, 0.15f, 0.3f), interiorColor);

            CreatePrimitive(PrimitiveType.Cube, "SteeringWheel",
                new Vector3(0f, 0.75f, 0.55f), new Vector3(0.3f, 0.3f, 0.05f), metalColor);

            CreatePrimitive(PrimitiveType.Cube, "Seat_Driver",
                new Vector3(-0.3f, 0.65f, -0.1f), new Vector3(0.45f, 0.15f, 0.5f), interiorColor);

            CreatePrimitive(PrimitiveType.Cube, "Seat_Passenger",
                new Vector3(0.3f, 0.65f, -0.1f), new Vector3(0.45f, 0.15f, 0.5f), interiorColor);
        }

        private void BuildExhaust()
        {
            CreatePrimitive(PrimitiveType.Cylinder, "Exhaust_Pipe",
                new Vector3(0.6f, 0.25f, -1.7f), new Vector3(0.08f, 0.15f, 0.08f), metalColor);
        }

        private void SetupComponents()
        {
            if (GetComponent<CarPhysics>() == null) gameObject.AddComponent<CarPhysics>();
            if (GetComponent<CarDriftController>() == null) gameObject.AddComponent<CarDriftController>();
            if (GetComponent<CarDamage>() == null) gameObject.AddComponent<CarDamage>();
            if (GetComponent<CarEffects>() == null) gameObject.AddComponent<CarEffects>();
            if (GetComponent<CarLights>() == null) gameObject.AddComponent<CarLights>();
            if (GetComponent<CarAudioManager>() == null) gameObject.AddComponent<CarAudioManager>();
            if (GetComponent<CarSuspension>() == null) gameObject.AddComponent<CarSuspension>();
        }

        private void WireDriverReferences()
        {
            var seatPoint = new GameObject("DriverSeat_Point");
            seatPoint.transform.SetParent(transform);
            seatPoint.transform.localPosition = new Vector3(-0.3f, 0.85f, -0.1f);
            seatPoint.transform.localRotation = Quaternion.identity;

            var wheelPoint = new GameObject("SteeringWheel_Point");
            wheelPoint.transform.SetParent(transform);
            wheelPoint.transform.localPosition = new Vector3(0f, 0.75f, 0.55f);
            wheelPoint.transform.localRotation = Quaternion.identity;

            if (_controller != null)
                _controller.SetDriverReferences(seatPoint.transform, wheelPoint.transform);
        }
    }
}
