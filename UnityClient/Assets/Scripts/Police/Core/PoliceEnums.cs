namespace RideVerse.Police.Core
{
    public enum PoliceState
    {
        Idle,
        Patrolling,
        RespondingToCall,
        Investigating,
        PursuingVehicle,
        PursuingOnFoot,
        SettingRoadblock,
        PlacingSpikeStrip,
        AttemptingArrest,
        EscortingToJail,
        AwaitingBackup,
        DefendingPosition,
        ReturningToStation
    }

    public enum WantedLevel
    {
        None = 0,
        MinorOffense = 1,
        TrafficViolation = 2,
        VehicleChase = 3,
        MultipleUnits = 4,
        MaximumResponse = 5,
        NationalGuard = 6
    }

    public enum CrimeType
    {
        Speeding,
        DangerousDriving,
        HitAndRun,
        VehicleTheft,
        PropertyDamage,
        WeaponPossession,
        Assault,
        Robbery,
        BusinessTheft,
        IllegalRacing,
        PoliceAssault,
        Murder
    }

    public enum PoliceUnitType
    {
        PatrolCar,
        PatrolBike,
        SUV,
        UnmarkedCar,
        SWATVan,
        SWATTeam,
        Helicopter,
        K9Unit
    }

    public enum PursuitState
    {
        None,
        Initiating,
        ActiveVehicleChase,
        ActiveFootChase,
        LostSight,
        CallingBackup,
        SettingRoadblock,
        SpikeStripDeployed,
        PursuitTerminated,
        TargetArrested
    }

    public enum DispatchPriority
    {
        Low,
        Medium,
        High,
        Critical
    }

    public enum RoadblockType
    {
        PoliceCars,
        SpikeStrip,
        Barricade,
        TrafficDiversion
    }

    public enum EvidenceType
    {
        WitnessSighting,
        CameraFootage,
        VehicleDescription,
        SpeedReading,
        DamageReport,
        WeaponReport,
        ForensicTrace,
        GPSBreadcrumb
    }

    public enum RadioMessageType
    {
        BackupRequest,
        BackupResponse,
        StatusUpdate,
        PursuitUpdate,
        RoadblockRequest,
        AllUnitsAlert,
        UnitDispatched,
        UnitOnScene,
        EvidenceLogged,
        WantedLevelChanged,
        TrafficStop,
        ClearScene,
        StandDown
    }

    public enum JailSentence
    {
        Warning = 0,
        ShortDetention = 1,
        MediumDetention = 2,
        LongDetention = 3,
        ExtendedDetention = 4
    }

    public enum FineCategory
    {
        Speeding,
        DangerousDriving,
        HitAndRun,
        VehicleTheft,
        PropertyDamage,
        WeaponViolation,
        Assault,
        Robbery,
        Racing,
        PoliceAssault,
        Murder
    }
}
