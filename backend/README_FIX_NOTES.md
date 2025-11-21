Fix notes for 204 No Content route:

- DELETE /products/{product_id} now uses status_code=204 with response_class=Response and returns no body (no return statement).
- This avoids FastAPI/Starlette AssertionError for 204 responses having a body.
- Quick import check can be run with: `python quick_import_check.py`.
