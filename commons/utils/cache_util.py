from django.core.cache import cache


class Cache:

    def __init__(self, time_out):
        self.time_out = time_out

    def cache_set(self, k, v):
        original_key = "19026"
        real_key = cache.make_key(original_key)
        cache.set(original_key, {'name': 123, 'age': 321})
        a = cache.get(original_key)
        print(f"实际存储键名: {real_key}")
        print(f'{type(a)}, {a}')
        cache.set(k, v, self.time_out)

    def cache_get(self, k):
        cache.get(k)
