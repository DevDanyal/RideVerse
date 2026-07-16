namespace RideVerse.Traffic.Core
{
    public enum TrafficVehicleType
    {
        Motorcycle,
        Scooter,
        Sedan,
        SUV,
        PickupTruck,
        SportsCar,
        Supercar,
        LuxuryCar,
        Bus,
        DeliveryVan,
        CargoTruck,
        FuelTanker,
        Taxi
    }

    public enum TrafficAIBehaviorState
    {
        Idle,
        FollowingLane,
        ApproachingLight,
        StoppingAtLight,
        WaitingAtLight,
        ApproachingStopSign,
        StoppedAtStopSign,
        LaneChanging,
        Overtaking,
        ApproachingRoundabout,
        NavigatingRoundabout,
        Parking,
        Unparking,
        YieldingToEmergency,
        EmergencyBraking,
        FollowingTraffic,
        Cruising
    }

    public enum LanePosition
    {
        Left,
        Center,
        Right
    }

    public enum TrafficLightPhase
    {
        Green,
        Yellow,
        Red
    }

    public enum StopSignAction
    {
        None,
        Decelerate,
        Stopped,
        Proceeding
    }

    public enum RoundaboutEntry
    {
        None,
        Yielding,
        Entering,
        Circulating,
        Exiting
    }

    public enum ParkingState
    {
        None,
        Searching,
        Approaching,
        Maneuvering,
        Parked,
        Exiting
    }

    public enum EmergencyType
    {
        None,
        Police,
        Ambulance,
        FireTruck
    }

    public enum TrafficDensityLevel
    {
        VeryLow,
        Low,
        Medium,
        High,
        VeryHigh,
        RushHour
    }

    public enum WeatherCondition
    {
        Clear,
        Rain,
        HeavyRain,
        Fog,
        Storm,
        Snow
    }

    public enum TimeOfDay
    {
        Dawn,
        Morning,
        Midday,
        Afternoon,
        Dusk,
        Night
    }

    public enum IncidentType
    {
        MinorCrash,
        MajorCrash,
        VehicleBreakdown,
        TrafficJam,
        RoadClosure,
        Construction
    }

    public enum TrafficVehicleLOD
    {
        Full,
        Simplified,
        Culled
    }

    public enum Direction
    {
        North,
        South,
        East,
        West
    }
}
