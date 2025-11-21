Fix notes for 204 No Content route:

- DELETE /products/{product_id} uses status_code=204 with response_class=Response and response_model=None, and returns no body (no return or JSON).
- Verified no other routes use 204 with a body, and there is no router-level default response_model applied in app.include_router.
- This avoids FastAPI/Starlette AssertionError: "Status code 204 must not have a response body".
- Quick import check can be run with: `python quick_import_check.py`.
