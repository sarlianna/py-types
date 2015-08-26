The following is information on profiling and load testing a real web app using py-types v0.1.0a.
The project is unfortunately closed-source;
actual application logic functions in the profile has been changed to `<application logic>(function)`.

Localhost profiling:

```
PATH: '/predictions/flights/'
         49019 function calls (45349 primitive calls) in 1.062 seconds
   Ordered by: internal time, call count
   List reduced from 831 to 30 due to restriction <30>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
       10    0.355    0.036    0.355    0.036 {method 'recv_into' of '_socket.socket' objects}
        4    0.227    0.057    0.227    0.057 {method 'recv' of '_socket.socket' objects}
        1    0.116    0.116    0.116    0.116 {method 'connect' of '_socket.socket' objects}
        1    0.101    0.101    0.101    0.101 {built-in method getaddrinfo}
   107/27    0.041    0.000    0.145    0.005 /usr/local/lib/python3.4/dist-packages/py_types/runtime/schema.py:128(_check_values_dict)
10724/9604    0.030    0.000    0.058    0.000 {built-in method isinstance}
     2337    0.018    0.000    0.031    0.000 /usr/lib/python3.4/copy.py:67(copy)
 1683/594    0.010    0.000    0.022    0.000 /usr/lib/python3.4/json/encoder.py:325(_iterencode_dict)
     1764    0.010    0.000    0.016    0.000 <application_logic>(function)
   488/63    0.009    0.000    0.152    0.002 /usr/local/lib/python3.4/dist-packages/py_types/runtime/schema.py:69(_format_asserts)
     2257    0.008    0.000    0.008    0.000 /usr/lib/python3.4/copy.py:125(_copy_with_constructor)
      986    0.007    0.000    0.012    0.000 /usr/lib/python3.4/abc.py:178(__instancecheck__)
      560    0.007    0.000    0.024    0.000 /usr/local/lib/python3.4/dist-packages/py_types/type_defs/base.py:64(__instancecheck__)
     2825    0.007    0.000    0.008    0.000 /usr/local/lib/python3.4/dist-packages/py_types/runtime/schema.py:236(_assert_or_raise)
     3068    0.007    0.000    0.007    0.000 {method 'get' of 'dict' objects}
 1095/588    0.006    0.000    0.018    0.000 /usr/lib/python3.4/json/encoder.py:269(_iterencode_list)
     2732    0.006    0.000    0.006    0.000 {method 'append' of 'list' objects}
3012/3011    0.005    0.000    0.005    0.000 {built-in method len}
     1358    0.004    0.000    0.004    0.000 /usr/lib/python3.4/_weakrefset.py:70(__contains__)
     2015    0.004    0.000    0.004    0.000 {method 'split' of 'str' objects}
       42    0.004    0.000    0.020    0.000 <application logic>(<listcomp>)
      594    0.003    0.000    0.025    0.000 /usr/lib/python3.4/json/encoder.py:404(_iterencode)
      560    0.003    0.000    0.004    0.000 <application logic>(function)
      560    0.003    0.000    0.006    0.000 /usr/local/lib/python3.4/dist-packages/py_types/type_defs/base.py:70(<listcomp>)
      560    0.002    0.000    0.009    0.000 /usr/local/lib/python3.4/dist-packages/py_types/type_defs/base.py:69(<listcomp>)
      209    0.002    0.000    0.002    0.000 {method 'format' of 'str' objects}
     92/3    0.002    0.000    0.993    0.331 /usr/local/lib/python3.4/dist-packages/py_types/runtime/asserts.py:11(wrapper)
        3    0.002    0.001    0.027    0.009 /usr/lib/python3.4/json/encoder.py:175(encode)
    28/19    0.001    0.000    0.016    0.001 /usr/lib/python3.4/_collections_abc.py:562(update)
        1    0.001    0.001    0.002    0.002 <application logic>(function)
```

My takeaway from this is that network functions were about 800ms of the response time,
py-types was about 0.150 of it,
and actual logic was around 0.110 of it.

So, performance overhead is a bit worse than 2x in this case.

That 0.993 cumtime in the typecheck decorator looks worrying, but I'm fairly sure it's because the top-level app logic
is wrapped in this. (Schema decorator should have similar numbers if it were in top 30 tottime.)

Load tested the server running this and it seems it doesn't really degrade gracefully.
With just logic (and type checking) running, we get pretty high spikes and about 2/3rds the performance.  Here's the numbers:

No type-checking, 40 concurrent across 10 t2.mediums:
```
most are 0.2- 0.4, some decently common spikes up to 1.5 ish

Transactions:               3515 hits
Availability:             100.00 %
Elapsed time:              79.08 secs
Data transferred:          19.13 MB
Response time:              0.38 secs
Transaction rate:          44.45 trans/sec
Throughput:             0.24 MB/sec
Concurrency:               16.95
Successful transactions:        3515
Failed transactions:               0
Longest transaction:            5.43
Shortest transaction:           0.24
```

With type-checking, 40 concurrent across 10 t2.mediums:
```
Mostly in the range of 0.5-0.7, with a long period of 1-2 before coming back down

Transactions:               4146 hits
Availability:             100.00 %
Elapsed time:             129.72 secs
Data transferred:          22.50 MB
Response time:              0.76 secs
Transaction rate:          31.96 trans/sec
Throughput:             0.17 MB/sec
Concurrency:               24.16
Successful transactions:        4146
Failed transactions:               0
Longest transaction:            7.13
Shortest transaction:           0.28
```

As you can see, transaction rate is about 29.5% lower with type checking, and
max response time increased by about 31%.

Up at 80 concurrent, we have more results for non-type checking:
```
                          Low Case         High Case
Transactions:            10049 hits       12971 hits
Availability:            99.99 %          100.00%
Elapsed time:            281.90 secs      175.13 secs
Data transferred:        54.90 MB         70.83 MB
Response time:           1.73 secs        0.57 secs
Transaction rate:        35.65 trans/sec  73.99 trans/sec
Throughput:              0.19 MB/sec      0.40 MB/sec
Concurrency:             61.57            42.19
Successful transactions: 10049            12971
Failed transactions:     1                0
Longest transaction:     11.06            6.0
Shortest transaction:    0.28             0.25
```

As you can see, performance was pretty variable, though I have no real indicator what the difference between tests was.

with type-checking, 2 tests, at 80:
```
Transactions:            12679 hits
Availability:            99.99 %
Elapsed time:            366.83 secs
Data transferred:        68.84 MB
Response time:           1.75 secs
Transaction rate:        34.56 trans/sec
Throughput:              0.19 MB/sec
Concurrency:             60.60
Successful transactions: 12679
Failed transactions:     1
Longest transaction:     13.92
Shortest transaction:    0.36
```
```
Transactions:            11060 hits
Availability:            99.99 %
Elapsed time:            209.47 secs
Data transferred:        60.03 MB
Response time:           1.01 secs
Transaction rate:        52.80 trans/sec
Throughput:              0.29 MB/sec
Concurrency:             53.20
Successful transactions: 11060
Failed transactions:     1
Longest transaction:     22.09
Shortest transaction:    0.28
```

Notice really terrible max response time even on the better throughput test.
