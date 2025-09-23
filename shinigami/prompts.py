from shinigami.models import ProjectSpec, RouteGroup


def build_system_prompt(spec: ProjectSpec) -> str:
    stack = spec.stack
    parts = [
        f"You are a senior backend engineer. Generate production-grade {stack.language} code.",
        f"Framework: {stack.framework}. Database: {stack.database}.",
    ]
    if stack.orm:
        parts.append(f"ORM: {stack.orm}.")
    if stack.cache:
        parts.append(f"Cache: {stack.cache}.")
    if stack.auth:
        parts.append(f"Auth: {stack.auth}.")
    parts.append("Output ONLY code. No explanations, no markdown fences unless the output is a single file.")
    parts.append("Include proper error handling, input validation, and types.")
    return " ".join(parts)


def build_models_prompt(spec: ProjectSpec) -> str:
    model_list = ", ".join(spec.models)
    lines = [
        f"Generate database models/schemas for: {model_list}.",
        f"Project: {spec.display_name} — {spec.description}.",
        "Include: relations between models, indexes, timestamps (created_at, updated_at).",
        "Features context: " + "; ".join(spec.features),
    ]
    if spec.stack.orm == "prisma":
        lines.append("Output a complete Prisma schema file (schema.prisma).")
    elif spec.stack.language == "python":
        lines.append("Output SQLAlchemy 2.0 declarative models.")
    elif spec.stack.language == "go":
        lines.append("Output Go structs with GORM tags.")
    elif spec.stack.language == "rust":
        lines.append("Output Rust structs with SQLx FromRow derives.")
    elif spec.stack.language == "cpp":
        lines.append("Output Drogon ORM model definitions.")
    return "\n".join(lines)


def build_routes_prompt(spec: ProjectSpec, route: RouteGroup) -> str:
    endpoints = ", ".join(route.endpoints)
    lines = [
        f"Generate route handlers for prefix: {route.prefix}",
        f"Endpoints: {endpoints}",
        f"Project: {spec.display_name} — {spec.description}",
        "Include: request validation, error responses, proper HTTP status codes.",
        "Use the models defined in the models file. Import them.",
    ]
    if spec.stack.auth == "jwt" and route.prefix != "/auth":
        lines.append("Protect these routes with JWT auth middleware.")
    return "\n".join(lines)


def build_middleware_prompt(spec: ProjectSpec) -> str:
    lines = [
        f"Generate middleware for {spec.display_name}.",
        "Include: error handler middleware, request logger.",
    ]
    if spec.stack.auth == "jwt":
        lines.append("Include: JWT authentication middleware that verifies tokens and attaches user to request.")
    if spec.stack.cache == "redis":
        lines.append("Include: rate limiter middleware using Redis.")
    return "\n".join(lines)


def build_tests_prompt(spec: ProjectSpec) -> str:
    route_summary = "; ".join(f"{r.prefix}: {', '.join(r.endpoints)}" for r in spec.api_routes)
    lines = [
        f"Generate test suite for {spec.display_name}.",
        f"Routes to test: {route_summary}",
        f"Models: {', '.join(spec.models)}",
        "Include: unit tests for each endpoint, edge cases, auth tests if applicable.",
        "Use the standard test framework for the language.",
    ]
    return "\n".join(lines)
