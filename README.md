# Shinigami

Backend API code generation agent. Generates full working backend projects across 5 tech stacks using templates + LLM.

## Install

```bash
pip install shinigami-cli
```

## Usage

```bash
# List all available built-in project specs
shinigami list

# Show project details
shinigami info <name>

# Generate a project (requires API key)
export ANTHROPIC_API_KEY=sk-...
shinigami generate <name>

# Use OpenAI instead
export OPENAI_API_KEY=sk-...
shinigami generate <name> --provider openai

# Use Gemini instead
export GOOGLE_API_KEY=...
shinigami generate <name> --provider gemini

# Create a spec interactively
shinigami create

# Generate from your own spec
shinigami generate myproject --spec ./my-specs/my-project.yaml
```

## Stacks

| Stack | Framework |
|-------|-----------|
| TypeScript | Express + Prisma |
| Python | FastAPI + SQLAlchemy |
| Go | Gin |
| Rust | Actix-web + SQLx |
| C++ | Drogon |

Ships with a set of built-in specs across real-world, fintech, and agentic-AI categories — run `shinigami list` to see them, or write your own with `shinigami create`.

## Config

Set via environment or `shinigami.config.yaml`:

```yaml
provider: claude          # claude | openai | gemini
claude_model: claude-sonnet-4-6
openai_model: gpt-4o
gemini_model: gemini-2.5-pro
output_dir: ../backend
```

## Tests

```bash
pytest -v
```
