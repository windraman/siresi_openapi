from fastapi.openapi.docs import get_swagger_ui_html

def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="🌴 BorneoAPI Docs",
        swagger_favicon_url="https://yourcdn.com/logo.png",  # optional favicon
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "docExpansion": "none",
            "filter": True,
        },
    )
