# Claude UCO Test Project

This project integrates PayloadsAllTheThings with Graphiti and the Unified Cyber Ontology (UCO) to create a comprehensive cybersecurity knowledge graph.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+
- Git

### Starting Neo4j

1. Navigate to the docker directory:
```bash
cd docker
```

2. Start the Neo4j container:
```bash
docker-compose up -d
```

3. Verify the container is running:
```bash
docker-compose ps
```

4. Check Neo4j health:
```bash
docker-compose logs neo4j
```

### Accessing Neo4j

- **Neo4j Browser**: http://localhost:7474
- **Bolt Connection**: bolt://localhost:7687
- **Credentials**: neo4j / ucosecure123

### Project Structure

```
claude-uco-test/
├── docker/                 # Docker configuration
│   ├── docker-compose.yml  # Neo4j container setup
│   ├── neo4j/             # Neo4j configuration
│   └── .env               # Environment variables
├── ontology/              # UCO ontology files
│   ├── uco/              # UCO 1.4.0 ontology
│   └── extensions/       # Custom extensions
├── src/                  # Source code
│   ├── ingestion/        # Data ingestion pipelines
│   ├── graphiti/         # Graphiti integration
│   └── api/              # API endpoints
├── data/                 # Data files
│   ├── payloads/         # PayloadsAllTheThings data
│   └── processed/        # Processed UCO data
├── tests/                # Test suites
└── docs/                 # Documentation
```

## Development Workflow

1. **Start Infrastructure**: `docker-compose up -d`
2. **Load UCO Schema**: Run schema loading scripts
3. **Ingest PayloadsAllTheThings**: Process and load payload data
4. **Query and Analyze**: Use Neo4j Browser or APIs

## UCO Compliance

This project follows the Unified Cyber Ontology (UCO) 1.4.0 specification:
- All entities inherit from proper UCO classes
- Relationships use UCO properties
- Data validation against UCO SHACL shapes
- JSON-LD serialization with UCO contexts

## Next Steps

- [ ] Copy UCO ontology files
- [ ] Set up Python environment
- [ ] Load UCO schema into Neo4j
- [ ] Ingest PayloadsAllTheThings data
- [ ] Implement Graphiti integration
- [ ] Create API endpoints