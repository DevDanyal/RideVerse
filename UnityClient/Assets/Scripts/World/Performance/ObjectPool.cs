using System;
using System.Collections.Generic;
using UnityEngine;

namespace RideVerse.World.Performance
{
    public class ObjectPool<T> where T : Component
    {
        private readonly Queue<T> _available = new Queue<T>();
        private readonly List<T> _allObjects = new List<T>();
        private readonly T _prefab;
        private readonly Transform _parent;
        private readonly int _initialSize;

        public int AvailableCount => _available.Count;
        public int TotalCount => _allObjects.Count;
        public int ActiveCount => _allObjects.Count - _available.Count;

        public ObjectPool(T prefab, Transform parent, int initialSize = 10)
        {
            _prefab = prefab;
            _parent = parent;
            _initialSize = initialSize;

            Prewarm(initialSize);
        }

        public void Prewarm(int count)
        {
            for (int i = 0; i < count; i++)
            {
                var obj = UnityEngine.Object.Instantiate(_prefab, _parent);
                obj.gameObject.SetActive(false);
                _available.Enqueue(obj);
                _allObjects.Add(obj);
            }
        }

        public T Get()
        {
            T obj;

            if (_available.Count > 0)
            {
                obj = _available.Dequeue();
            }
            else
            {
                obj = UnityEngine.Object.Instantiate(_prefab, _parent);
                _allObjects.Add(obj);
            }

            obj.gameObject.SetActive(true);
            return obj;
        }

        public T Get(Vector3 position, Quaternion rotation)
        {
            T obj = Get();
            obj.transform.position = position;
            obj.transform.rotation = rotation;
            return obj;
        }

        public void Return(T obj)
        {
            if (obj == null) return;
            obj.gameObject.SetActive(false);
            obj.transform.SetParent(_parent);
            _available.Enqueue(obj);
        }

        public void ReturnAll()
        {
            foreach (var obj in _allObjects)
            {
                if (obj != null)
                {
                    obj.gameObject.SetActive(false);
                    _available.Enqueue(obj);
                }
            }
        }

        public void Clear()
        {
            foreach (var obj in _allObjects)
            {
                if (obj != null)
                {
                    UnityEngine.Object.Destroy(obj.gameObject);
                }
            }
            _allObjects.Clear();
            _available.Clear();
        }
    }

    public class GameObjectPool
    {
        private readonly Queue<GameObject> _available = new Queue<GameObject>();
        private readonly List<GameObject> _allObjects = new List<GameObject>();
        private readonly GameObject _prefab;
        private readonly Transform _parent;

        public int AvailableCount => _available.Count;
        public int TotalCount => _allObjects.Count;
        public int ActiveCount => _allObjects.Count - _available.Count;

        public GameObjectPool(GameObject prefab, Transform parent, int initialSize = 10)
        {
            _prefab = prefab;
            _parent = parent;

            for (int i = 0; i < initialSize; i++)
            {
                var obj = UnityEngine.Object.Instantiate(_prefab, _parent);
                obj.SetActive(false);
                _available.Enqueue(obj);
                _allObjects.Add(obj);
            }
        }

        public GameObject Get()
        {
            GameObject obj;

            if (_available.Count > 0)
            {
                obj = _available.Dequeue();
            }
            else
            {
                obj = UnityEngine.Object.Instantiate(_prefab, _parent);
                _allObjects.Add(obj);
            }

            obj.SetActive(true);
            return obj;
        }

        public GameObject Get(Vector3 position, Quaternion rotation)
        {
            GameObject obj = Get();
            obj.transform.position = position;
            obj.transform.rotation = rotation;
            return obj;
        }

        public void Return(GameObject obj)
        {
            if (obj == null) return;
            obj.SetActive(false);
            _available.Enqueue(obj);
        }

        public void ReturnAll()
        {
            foreach (var obj in _allObjects)
            {
                if (obj != null)
                {
                    obj.SetActive(false);
                    _available.Enqueue(obj);
                }
            }
        }
    }
}
