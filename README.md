# Shinigami

Backend API code generation agent. Generates full working backend projects across 5 tech stacks using templates + LLM.

## Install

```bash
pip install -e .
```

## Usage

```bash
# List all available projects
shinigami list

# Show project details
shinigami info taskflow

# Generate a project (requires API key)
export ANTHROPIC_API_KEY=sk-...
shinigami generate taskflow

# Use OpenAI instead
export OPENAI_API_KEY=sk-...
shinigami generate taskflow --provider openai
```

## Stacks

| Stack | Framework | Projects |
|-------|-----------|----------|
| TypeScript | Express + Prisma | 7 |
| Python | FastAPI + SQLAlchemy | 10 |
| Go | Gin | 4 |
| Rust | Actix-web + SQLx | 4 |
| C++ | Drogon | 1 |

## Projects (32)

### Real-World
TaskFlow, WeatherHub, TalentForge, BookEase, CollabInk, MarketSphere, Pulse, VoteSphere, StreamForge, QuickBite, SplitWiseX

### Trading & Fintech
CorePay, CoinForge, Kaido, TaxForge, OpenBank, CrossWire, InsureIt, SquareOne, TradeFlow, PipSmith, Mercury, EdenGate

### Agentic AI
CodeForge, ArchGen, DocBrain, TradeGPT, LogSense, DeployAI, APIWise, QueryPilot, AgentHub

## Config

Set via environment or `shinigami.config.yaml`:

```yaml
provider: claude          # or openai
claude_model: claude-sonnet-4-6
openai_model: gpt-4o
output_dir: ../backend
```

## Tests

```bash
pytest -v
```
