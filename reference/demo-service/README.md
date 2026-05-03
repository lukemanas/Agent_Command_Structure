# demo-service

A tiny stdlib-only HTTP service that AgentCS workers operate on. Used as the target codebase for the reference implementation's example OAP.

```
demo-service/
  service.py            # the service. Routes live in ROUTES.
  tests/
    test_service.py     # tests call handle() directly, no live server needed
```

Run live (optional):
```
python3 service.py 8000
curl http://127.0.0.1:8000/health   # → ok
```

Run tests:
```
python3 -m unittest discover demo-service/tests
```

The example OAP (`examples/oap.json`) asks the worker to add a `/hello` route here and a corresponding test.
