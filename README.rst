================================
Django Function Caching
================================

A function wrapper that helps with caching techniques which have been battle-tested with millions of users. 2 main features are as following:

1) Utilizing redis locks to limit cache recalculation to a single thread
2) Allow serving somewhat stale data to keep the server going

To understand the design decisions you can read the following blog posts where I justify the need for these cases.

https://eralpbayraktar.com/blog/django/2020/caching-with-django

https://eralpbayraktar.com/blog/django/2020/caching-with-django-part-II


1) Cache calculation mutex
==========================
If you have a cold cache and 1000 requests hit the endpoint, you don't want all your gunicorn workers to calculate this exact same function. With this functionality, 1 worker will calculate and the other 999 have basically 2 options. They can either error out and release worker resources, which is healthy for the remaining endpoints, or they can serve somewhat old value if it's available. This brings us to the next point.

2) Allow serving kind of old data
=================================
This is not ideal but sometimes it's better to serve old cache values instead of erroring out or block all your workers. With django-function-caching you can set 2 timeout values for a given function. One is the grand **timeout**, that's nothing new, after this many seconds the cache will be invalidated, and the other is **freshness_timeout**. This is the interesting one. One example is setting the **timeout** to 24 hours and **freshness_timeout** to 1 hour. This means workers will try to serve a cache value fresher than 1 hour, but if they cannot, then they are allowed to serve a value that's maximum 24 hours old. This flexibility or relaxation gives us the chance to keep the server healthy. You can set the maximum even to 1 month, in ideal conditions **freshness_timeout** should decide the behavior. **timeout** is only used in extreme cases, and you should be glad when it's used because that means it has saved you from something worse or catastrophic. If only 1 request comes and the cache value is older than **freshness_timeout** that worker will recalculate and update the cache.

Getting It
============
::

    $ pip install django-function-caching

Settings
============
**django-function-caching** will use "default" cache backend and it should be redis. Check out how to setup **django-redis** (our dependency)

Usage
=====

::

    from functioncaching import cached_function

    @cached_function(timeout=24*60*60, freshness_timeout=60*60)
    def _get_top_book_ids(self):
        time.sleep(5)  # make the calculation slower for the sake of argument
        return list(Book.objects.order_by('-purchase_count').values_list('id', flat=True)[:10])

    # or

    @cached_function(timeout=24*60*60, freshness_timeout=60*60, prefix='Author')
    def _get_top_book_ids(self):
        time.sleep(5)  # make the calculation slower for the sake of argument
        return list(Book.objects.order_by('-purchase_count').values_list('id', flat=True)[:10])

"prefix" is used to prefix the cache key.

How is the cache key calculated?
==================================
The cache_key is calculated based on the function name + string representation of all the arguments and keyword arguments. This means if you pass classes/complex objects to the function, it might not behave correctly. So I'd advise you to pass simple parameters (like making functions class methods or static methods and passing object IDs, instead of using self), the same idea when you schedule celery tasks, the simpler the parameters the better, and no unnecessary parameters since they will create additional cache keys. Because the library cannot know if they change the behavior or not.
Prefix is good when you have the same function names in multiple places/classes/modules, it is optional.

Things to keep in mind
======================

    AttributeError: 'LocMemCache' object has no attribute 'ttl'

This means your default cache is not redis, check django-redis installation and configurations.


    I'm getting ColdCacheException

Good! The library saved you from worker clogging. This means multiple requests came to the endpoint yet you don't even have an old/stale cache value in your cache database to serve as a back-up. Increase your **timeout** parameter to protect against this.