using UnityEngine;
using RideVerse.Core;

namespace RideVerse.Vehicles
{
    [RequireComponent(typeof(VehicleController))]
    [RequireComponent(typeof(Rigidbody))]
    public class VehiclePlaceholder : MonoBehaviour
    {
        [Header("Build Placeholder")]
        [SerializeField] private bool _buildOnStart = true;

        [Header("Colors")]
        [SerializeField] private Color _bodyColor = new Color(0.8f, 0.1f, 0.1f);
        [SerializeField] private Color _seatColor = new Color(0.15f, 0.1f, 0.08f);
        [SerializeField] private Color _metalColor = new Color(0.6f, 0.6f, 0.65f);
        [SerializeField] private Color _tireColor = new Color(0.1f, 0.1f, 0.1f);
        [SerializeField] private Color _headlightColor = new Color(1f, 0.95f, 0.7f);

        private VehicleController _controller;

        private void Awake()
        {
            _controller = GetComponent<VehicleController>();

            if (_buildOnStart)
            {
                BuildPlaceholderBike();
            }
        }

        public void BuildPlaceholderBike()
        {
            ClearChildren();

            BuildFrame();
            BuildEngine();
            BuildFuelTank();
            BuildSeat();
            BuildHandlebars();
            BuildFrontFender();
            BuildRearFender();
            BuildExhaust();
            BuildKickstand();
            BuildLights();
            SetupWheelColliders();
            BuildWheelMeshes();
            SetupComponents();
            WireRiderReferences();
        }

        private void ClearChildren()
        {
            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                if (Application.isPlaying)
                    Destroy(transform.GetChild(i).gameObject);
                else
                    DestroyImmediate(transform.GetChild(i).gameObject);
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
                renderer.material = CreateMaterial(color);
            }

            return go;
        }

        private Material CreateMaterial(Color color)
        {
            var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            mat.color = color;
            mat.SetFloat("_Smoothness", 0.5f);
            mat.SetFloat("_Metallic", color == _metalColor ? 0.8f : 0.2f);
            return mat;
        }

        private void BuildFrame()
        {
            CreatePrimitive(PrimitiveType.Cylinder, "Frame_Main",
                new Vector3(0f, 0.55f, 0f), new Vector3(0.06f, 0.35f, 0.06f), _metalColor);

            CreatePrimitive(PrimitiveType.Cylinder, "Frame_Fork",
                new Vector3(0f, 0.7f, 0.4f), new Vector3(0.04f, 0.2f, 0.04f), _metalColor);

            CreatePrimitive(PrimitiveType.Cylinder, "Frame_SeatPost",
                new Vector3(0f, 0.75f, -0.25f), new Vector3(0.04f, 0.12f, 0.04f), _metalColor);

            CreatePrimitive(PrimitiveType.Cube, "Frame_RearSubframe",
                new Vector3(0f, 0.55f, -0.45f), new Vector3(0.05f, 0.05f, 0.3f), _metalColor);
        }

        private void BuildEngine()
        {
            CreatePrimitive(PrimitiveType.Cube, "Engine_Block",
                new Vector3(0f, 0.35f, 0.05f), new Vector3(0.2f, 0.18f, 0.2f), _metalColor);

            CreatePrimitive(PrimitiveType.Cylinder, "Engine_Cylinder",
                new Vector3(0f, 0.5f, 0.05f), new Vector3(0.1f, 0.08f, 0.1f), _metalColor);
        }

        private void BuildFuelTank()
        {
            CreatePrimitive(PrimitiveType.Cube, "FuelTank",
                new Vector3(0f, 0.68f, 0.1f), new Vector3(0.3f, 0.15f, 0.35f), _bodyColor);
        }

        private void BuildSeat()
        {
            CreatePrimitive(PrimitiveType.Cube, "Seat",
                new Vector3(0f, 0.78f, -0.2f), new Vector3(0.25f, 0.08f, 0.45f), _seatColor);
        }

        private void BuildHandlebars()
        {
            CreatePrimitive(PrimitiveType.Cube, "Handlebar_Cross",
                new Vector3(0f, 0.95f, 0.45f), new Vector3(0.5f, 0.04f, 0.04f), _metalColor);

            CreatePrimitive(PrimitiveType.Cylinder, "Handlebar_Left",
                new Vector3(-0.28f, 0.95f, 0.45f), new Vector3(0.03f, 0.06f, 0.03f), _tireColor);

            CreatePrimitive(PrimitiveType.Cylinder, "Handlebar_Right",
                new Vector3(0.28f, 0.95f, 0.45f), new Vector3(0.03f, 0.06f, 0.03f), _tireColor);

            CreatePrimitive(PrimitiveType.Cylinder, "Handlebar_Steering",
                new Vector3(0f, 0.85f, 0.42f), new Vector3(0.03f, 0.08f, 0.03f), _metalColor);
        }

        private void BuildFrontFender()
        {
            CreatePrimitive(PrimitiveType.Cube, "Fender_Front",
                new Vector3(0f, 0.42f, 0.5f), new Vector3(0.28f, 0.04f, 0.2f), _bodyColor);
        }

        private void BuildRearFender()
        {
            CreatePrimitive(PrimitiveType.Cube, "Fender_Rear",
                new Vector3(0f, 0.42f, -0.5f), new Vector3(0.28f, 0.04f, 0.3f), _bodyColor);
        }

        private void BuildExhaust()
        {
            CreatePrimitive(PrimitiveType.Cylinder, "Exhaust_Pipe",
                new Vector3(0.18f, 0.3f, -0.1f), new Vector3(0.05f, 0.25f, 0.05f), _metalColor);

            CreatePrimitive(PrimitiveType.Cylinder, "Exhaust_Muffler",
                new Vector3(0.18f, 0.3f, -0.5f), new Vector3(0.07f, 0.12f, 0.07f), _metalColor);
        }

        private void BuildKickstand()
        {
            CreatePrimitive(PrimitiveType.Cylinder, "Kickstand",
                new Vector3(-0.18f, 0.15f, -0.1f), new Vector3(0.02f, 0.18f, 0.02f), _metalColor);
        }

        private void BuildLights()
        {
            CreatePrimitive(PrimitiveType.Sphere, "Headlight",
                new Vector3(0f, 0.8f, 0.55f), new Vector3(0.12f, 0.1f, 0.06f), _headlightColor);

            CreatePrimitive(PrimitiveType.Cube, "BrakeLight_Left",
                new Vector3(-0.1f, 0.6f, -0.68f), new Vector3(0.06f, 0.06f, 0.03f),
                new Color(0.8f, 0.05f, 0.05f));

            CreatePrimitive(PrimitiveType.Cube, "BrakeLight_Right",
                new Vector3(0.1f, 0.6f, -0.68f), new Vector3(0.06f, 0.06f, 0.03f),
                new Color(0.8f, 0.05f, 0.05f));

            CreatePrimitive(PrimitiveType.Cube, "Indicator_Left",
                new Vector3(-0.2f, 0.65f, 0.45f), new Vector3(0.04f, 0.04f, 0.02f),
                new Color(1f, 0.5f, 0f));

            CreatePrimitive(PrimitiveType.Cube, "Indicator_Right",
                new Vector3(0.2f, 0.65f, 0.45f), new Vector3(0.04f, 0.04f, 0.02f),
                new Color(1f, 0.5f, 0f));
        }

        private void SetupWheelColliders()
        {
            var frontCollider = gameObject.AddComponent<WheelCollider>();
            frontCollider.radius = 0.28f;
            frontCollider.suspensionDistance = 0.13f;
            frontCollider.transform.localPosition = new Vector3(0f, 0.28f, 0.55f);

            var rearCollider = gameObject.AddComponent<WheelCollider>();
            rearCollider.radius = 0.28f;
            rearCollider.suspensionDistance = 0.09f;
            rearCollider.transform.localPosition = new Vector3(0f, 0.28f, -0.55f);
        }

        private void BuildWheelMeshes()
        {
            GameObject frontWheel = CreatePrimitive(PrimitiveType.Cylinder, "Wheel_Front_Mesh",
                new Vector3(0f, 0.28f, 0.55f), new Vector3(0.35f, 0.06f, 0.35f), _tireColor);
            frontWheel.transform.localRotation = Quaternion.Euler(0f, 0f, 90f);

            GameObject rearWheel = CreatePrimitive(PrimitiveType.Cylinder, "Wheel_Rear_Mesh",
                new Vector3(0f, 0.28f, -0.55f), new Vector3(0.35f, 0.06f, 0.35f), _tireColor);
            rearWheel.transform.localRotation = Quaternion.Euler(0f, 0f, 90f);
        }

        private void SetupComponents()
        {
            if (GetComponent<MotorcyclePhysics>() == null)
                gameObject.AddComponent<MotorcyclePhysics>();

            if (GetComponent<VehicleLights>() == null)
                gameObject.AddComponent<VehicleLights>();

            if (GetComponent<VehicleDamage>() == null)
                gameObject.AddComponent<VehicleDamage>();

            if (GetComponent<VehicleEffects>() == null)
                gameObject.AddComponent<VehicleEffects>();

            if (GetComponent<MotorcycleAudioManager>() == null)
                gameObject.AddComponent<MotorcycleAudioManager>();
        }

        private void WireRiderReferences()
        {
            var seatPoint = new GameObject("RiderSeat_Point");
            seatPoint.transform.SetParent(transform);
            seatPoint.transform.localPosition = new Vector3(0f, 0.85f, -0.15f);
            seatPoint.transform.localRotation = Quaternion.identity;

            var gripPoint = new GameObject("HandlebarGrip_Point");
            gripPoint.transform.SetParent(transform);
            gripPoint.transform.localPosition = new Vector3(0f, 0.95f, 0.45f);
            gripPoint.transform.localRotation = Quaternion.identity;

            if (_controller != null)
            {
                _controller.SetRiderReferences(seatPoint.transform, gripPoint.transform);
            }
        }
    }
}
