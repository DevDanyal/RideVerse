using System;
using System.Collections.Generic;
using UnityEngine;
using RideVerse.Traffic.Core;

namespace RideVerse.Traffic.PublicTransport
{
    [Serializable]
    public class BusStop
    {
        public string Id;
        public Vector3 Position;
        public string Name;
        public float DwellTime;

        public BusStop(string id, Vector3 position, string name, float dwellTime = 8f)
        {
            Id = id;
            Position = position;
            Name = name;
            DwellTime = dwellTime;
        }
    }

    [Serializable]
    public class BusRoute
    {
        public string Id;
        public string RouteName;
        public List<BusStop> Stops;
        public Color RouteColor;
        public float Frequency;

        public BusRoute(string id, string routeName, float frequency = 120f)
        {
            Id = id;
            RouteName = routeName;
            Stops = new List<BusStop>();
            RouteColor = Color.blue;
            Frequency = frequency;
        }

        public void AddStop(BusStop stop)
        {
            Stops.Add(stop);
        }

        public BusStop GetNextStop(int currentIndex)
        {
            if (Stops.Count == 0) return null;
            return Stops[(currentIndex + 1) % Stops.Count];
        }

        public float GetTotalRouteLength()
        {
            float total = 0f;
            for (int i = 0; i < Stops.Count; i++)
            {
                int next = (i + 1) % Stops.Count;
                total += Vector3.Distance(Stops[i].Position, Stops[next].Position);
            }
            return total;
        }
    }

    public class BusRouteSystem : MonoBehaviour
    {
        private TrafficConfig _config;
        private List<BusRoute> _routes = new List<BusRoute>();
        private List<TrafficVehicle> _activeBuses = new List<TrafficVehicle>();
        private Dictionary<TrafficVehicle, BusRouteState> _busStates = new Dictionary<TrafficVehicle, BusRouteState>();

        public int ActiveBusCount => _activeBuses.Count;
        public int RouteCount => _routes.Count;

        public void Initialize(TrafficConfig config)
        {
            _config = config;
            GenerateDefaultRoutes();
        }

        public void SpawnBus(BusRoute route, Vector3 spawnPosition)
        {
            if (_activeBuses.Count >= _config.maxBuses) return;

            if (TrafficManager.Instance == null) return;

            TrafficVehicle bus = TrafficManager.Instance.SpawnVehicle(
                TrafficVehicleType.Bus,
                spawnPosition,
                0f,
                40f);

            if (bus != null)
            {
                _activeBuses.Add(bus);
                var state = new BusRouteState
                {
                    Route = route,
                    CurrentStopIndex = 0,
                    IsAtStop = false,
                    DwellTimer = 0f
                };
                _busStates[bus] = state;
            }
        }

        public void UpdateBuses(float deltaTime)
        {
            List<TrafficVehicle> toRemove = new List<TrafficVehicle>();

            foreach (var bus in _activeBuses)
            {
                if (bus == null)
                {
                    toRemove.Add(bus);
                    continue;
                }

                if (!_busStates.ContainsKey(bus)) continue;

                var state = _busStates[bus];
                UpdateBus(bus, state, deltaTime);
            }

            foreach (var bus in toRemove)
            {
                _activeBuses.Remove(bus);
                _busStates.Remove(bus);
            }
        }

        private void UpdateBus(TrafficVehicle bus, BusRouteState state, float deltaTime)
        {
            if (state.Route.Stops.Count == 0) return;

            BusStop currentStop = state.Route.Stops[state.CurrentStopIndex];

            if (state.IsAtStop)
            {
                state.DwellTimer += deltaTime;
                bus.Stop();

                if (state.DwellTimer >= currentStop.DwellTime)
                {
                    state.IsAtStop = false;
                    state.DwellTimer = 0f;
                    state.CurrentStopIndex = (state.CurrentStopIndex + 1) % state.Route.Stops.Count;
                }
                return;
            }

            BusStop nextStop = state.Route.Stops[state.CurrentStopIndex];
            float distance = Vector3.Distance(bus.Position, nextStop.Position);

            if (distance < 3f)
            {
                state.IsAtStop = true;
                state.DwellTimer = 0f;
                return;
            }

            Vector3 direction = (nextStop.Position - bus.Position).normalized;
            direction.y = 0f;

            float speed = Mathf.Min(bus.MaxSpeed, 40f);
            if (distance < 15f)
                speed = Mathf.Lerp(5f, bus.MaxSpeed, distance / 15f);

            bus.SetTargetSpeed(speed);
            bus.ApplyMovement(direction, bus.CurrentSpeed, deltaTime);
        }

        public void RemoveBus(TrafficVehicle bus)
        {
            _activeBuses.Remove(bus);
            _busStates.Remove(bus);
        }

        private void GenerateDefaultRoutes()
        {
            _routes.Clear();

            var route1 = new BusRoute("R001", "Downtown Loop", 120f);
            route1.AddStop(new BusStop("S001", new Vector3(50f, 0f, 50f), "Main Square", 8f));
            route1.AddStop(new BusStop("S002", new Vector3(100f, 0f, 50f), "Market Street", 6f));
            route1.AddStop(new BusStop("S003", new Vector3(100f, 0f, 100f), "City Center", 10f));
            route1.AddStop(new BusStop("S004", new Vector3(50f, 0f, 100f), "Park Avenue", 6f));
            route1.RouteColor = Color.blue;
            _routes.Add(route1);

            var route2 = new BusRoute("R002", "Suburban Express", 180f);
            route2.AddStop(new BusStop("S005", new Vector3(-50f, 0f, -50f), "Suburb North", 8f));
            route2.AddStop(new BusStop("S006", new Vector3(0f, 0f, -50f), "Highway Junction", 5f));
            route2.AddStop(new BusStop("S007", new Vector3(50f, 0f, -50f), "Industrial Area", 6f));
            route2.AddStop(new BusStop("S008", new Vector3(50f, 0f, 0f), "Shopping Mall", 10f));
            route2.RouteColor = Color.green;
            _routes.Add(route2);

            var route3 = new BusRoute("R003", "Beach Route", 150f);
            route3.AddStop(new BusStop("S009", new Vector3(-100f, 0f, 0f), "West Terminal", 8f));
            route3.AddStop(new BusStop("S010", new Vector3(-50f, 0f, 50f), "Riverside", 6f));
            route3.AddStop(new BusStop("S011", new Vector3(0f, 0f, 100f), "Beach Front", 12f));
            route3.RouteColor = Color.cyan;
            _routes.Add(route3);
        }

        public BusRoute GetRoute(string routeId)
        {
            return _routes.Find(r => r.Id == routeId);
        }

        public List<BusRoute> GetAllRoutes() => new List<BusRoute>(_routes);

        public BusStop FindNearestBusStop(Vector3 position)
        {
            BusStop nearest = null;
            float nearestDist = float.MaxValue;

            foreach (var route in _routes)
            {
                foreach (var stop in route.Stops)
                {
                    float dist = Vector3.Distance(position, stop.Position);
                    if (dist < nearestDist)
                    {
                        nearestDist = dist;
                        nearest = stop;
                    }
                }
            }

            return nearest;
        }
    }

    public class BusRouteState
    {
        public BusRoute Route;
        public int CurrentStopIndex;
        public bool IsAtStop;
        public float DwellTimer;
    }
}
