from src.auth.router import router

print("Rutas del router:")
for r in router.routes:
    print(f"Path: {r.path}")
    print(f"Methods: {getattr(r, 'methods', 'N/A')}")
    print(f"Name: {getattr(r, 'name', 'N/A')}")
    print("---")