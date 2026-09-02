![Karan, building with LLMs](assets/banner.jpg)

# Karan Manoharan

**Senior Data Engineer, London.** I build data platforms that people trust, and lately the AI layer on top of them.

Six years turning messy source systems into foundations people trust. Builder of [Pubmaxxing](https://pubmaxxing.com). These days most of my time goes where the warehouse meets language models: semantic layers, Document AI, MCP servers, agents that can be trusted with real data. I ship side projects at hackathon speed, and sometimes at hackathons.

**Follow along:** [karanmrn.github.io](https://karanmrn.github.io) · [X @karansznx](https://x.com/karansznx) · [LinkedIn](https://linkedin.com/in/karanmanoharan23) · [Medium](https://medium.com/@karanmrn) · [Linktree](https://linktr.ee/karanmrn) · karan@pubmaxxing.com

---

## What I'm building

### [Pubmaxxing](https://pubmaxxing.com) · live at pubmaxxing.com
A price aware nightlife map. A pint in London can cost eight quid and nobody tells you where it is cheaper, so I built the thing that does. Pick your drink, see which nearby pubs pour it cheapest, plan the crawl, get your mates on one route.

- 953 pubs tracked, 2,788 prices on record, all 33 London boroughs
- Nine city guides with prices and crawls: London, Manchester, Liverpool, Oxford, Durham, Glasgow, Bristol, Cambridge, Bath. Every other UK town opens the map without prices
- Drink first search: tap cocktails, rum, lager, whatever, and the map re-sorts by who pours it cheapest near you
- Crawl planner that puts the walk, the stops and the way home on one route instead of three apps
- Tonight and What's On feeds, saved pubs that turn into nights your mates can join and shape, Moments and Stories for the parts worth keeping
- Every price record names its publisher when one exists and says so plainly when none does. Nothing is dressed up as a live till price

Under the hood: a Firecrawl discovery and menu scraping pipeline, CSV data contracts with source URL, timestamp, parser version and confidence on every row, and a knowledge graph schema for the social layer.

Stack: Node.js, Firecrawl, TypeScript, CSV data contracts. [Source](https://github.com/karanmrn/pubmaxxing)

### [Councilmaxxing (CouncilGraph)](https://github.com/karanmrn/Councilmaxxing)
Turning fragmented UK council records (councillors, minutes, decisions) into a common, evidence backed structure that agents and civic apps can query safely. Bracknell Forest is the first vertical slice, served through a live MCP endpoint: [Council Gateway MCP](https://council-gateway-mcp-508695152452.europe-west1.run.app/).

- Source contracts and real data profiling before a single model is written
- DuckDB with relational bridge tables as the first graph representation. No graph DB, no vector DB, no open ended RAG until the small slice earns it
- `make verify` runs Ruff, mypy, pytest, profile freshness checks, dbt parse, dbt build and a secret scan in one go
- Explicit source rules: no scraping council sites, sanctioned APIs only, and the 37 GB meeting dump stays untouched until quality gates pass

Stack: Python 3.12, uv, DuckDB, dbt, pytest, Cloud Run.

Both projects follow the same rule I use at work: build the smallest slice that proves the data is trustworthy, then expand.

---

---

## Stack

- **Warehouse and modelling:** Snowflake (Iceberg, Dynamic Tables, Snowpipe, Cortex), Databricks, Delta Lake, DuckDB, dbt, Kimball dimensional modelling
- **Pipelines:** Airflow, Azure Data Factory, Kafka, Spark (batch and Structured Streaming), Great Expectations
- **AI systems:** Snowflake Cortex, Document AI, RAG pipelines, MCP servers, vector search, Claude Code
- **Infra:** Azure (ADLS Gen2, Synapse, Event Hubs), Docker, Terraform, GitHub Actions, Azure DevOps
- **Languages:** SQL, Python, Bash, a bit of Node when a scraper needs it

---

## How I work

- Simplicity is the hard part. Anyone can add. The skill is knowing what to remove.
- A pipeline you can explain in two sentences will outlive a clever one you can't.
- Ship the rough version on Monday. You learn more from that than a month of designing the perfect one.
- Build for the next person. Readable beats clever.

Going deeper on agent architectures and evals, MLOps on Kubernetes, and the boundary where the semantic layer meets LLMs.

---

Off the clock: hackathons whenever there's one worth losing a weekend to. Formula 1, where Lewis Hamilton is the greatest of all time and Ferrari is the team, which makes Sundays complicated. Basketball, festivals, long walks where most of the actual thinking happens. The Weeknd on repeat.

<p align="center"><img src="assets/meme-enforcers.jpg" width="420" alt="Me with my right hand enforcers at my workplace"></p>

---

**Where to find me**

- [X](https://x.com/karansznx) for daily thoughts, shipping updates and F1 opinions
- [LinkedIn](https://linkedin.com/in/karanmanoharan23) for the polished version and hackathon recaps
- [Medium](https://medium.com/@karanmrn) for longer writing on data platforms and AI
- [karan@pubmaxxing.com](mailto:karan@pubmaxxing.com), replies within a day
