# Implementation Plan - Fraud Detection Dashboard

## Project Structure

```
fraud-detection-dashboard/
|
|-- backend/
|   |-- app.py                      # Flask API server
|   |-- data_processor.py           # Core fraud detection analysis
|   |-- database.py                 # SQLite operations
|   |-- config.py                   # Configuration settings
|   |-- requirements.txt            # Python dependencies
|   |-- README.md                   # Backend setup instructions
|
|-- data/
|   |-- input/
|   |   |-- external_fraud_scores.csv     # External fraud scores (placeholder)
|   |   |-- claim_fraud_rules.csv         # Fraud rules mapping (placeholder)
|   |
|   |-- output/
|   |   |-- fraud_detection.db            # SQLite database (auto-created)
|
|-- frontend/
|   |-- [Future Phase - React Dashboard]
|
|-- README.md                       # Main project documentation
```

## Implementation Phases

### PHASE 1: Backend Data Processing (CURRENT FOCUS)

**File: data_processor.py**
- Extend existing notebook WorkersCompFraudDetector class
- Add overlapping community detection (k-clique)
- Add external fraud score aggregation
- Add fraud rules integration
- Generate all dashboard DataFrames
- Export functions for API consumption

**File: database.py**
- SQLite connection management
- Investigation status CRUD operations
- Status history tracking
- Database initialization

**File: app.py**
- Flask API setup
- Endpoints for entity data
- Status update endpoints
- CORS configuration for frontend

**File: config.py**
- File paths
- Database configuration
- API settings

### PHASE 2: Frontend Dashboard (FUTURE)
- React app from wireframe
- API integration
- Power BI styling

## Backend API Endpoints

```
GET  /api/entities
     Query params: sort_by, filter_status, min_risk_score
     Returns: df_entity_dashboard as JSON

GET  /api/entity/<entity_name>
     Returns: Complete entity details including:
              - Risk scores
              - Community memberships
              - Connections
              - Claims
              - Fraud rules

PUT  /api/entity/<entity_name>/status
     Body: {"status": "Under Investigation"}
     Returns: Success/failure

GET  /api/entity/<entity_name>/status-history
     Returns: All status changes for entity

GET  /api/health
     Returns: API health check
```

## Data Processing Flow

```
1. Load base data (entities, notes)
   |
2. Run NER extraction
   |
3. Build network graph
   |
4. Detect overlapping communities (k-clique)
   |
5. Calculate centrality scores
   |
6. Import external fraud scores (CSV)
   |
7. Import fraud rules (CSV)
   |
8. Aggregate entity-level metrics
   |
9. Generate all dashboard DataFrames
   |
10. Store in memory for API serving
```

## Key Dependencies

**Python Packages:**
```
flask==3.0.0
flask-cors==4.0.0
pandas==2.1.0
networkx==3.2.0
numpy==1.24.0
spacy==3.7.0
scikit-learn==1.3.0
```

**Data Files (Placeholders):**
```
external_fraud_scores.csv:
    claim_number,external_fraud_score
    WC-2024-001,0.75
    WC-2024-002,0.89

claim_fraud_rules.csv:
    claim_number,rule_no,rule_desc,priority,value
    WC-2024-001,5,"Law enforcement inquiry",High,9
```

## Critical Implementation Notes

**1. Overlapping Communities**
- Use: `nx.algorithms.community.k_clique_communities(G, k)`
- Start with k=3 (entities sharing 3+ common connections form community)
- Entities can belong to multiple communities
- Need to handle community membership as one-to-many relationship

**2. External Data Import**
- Always check if CSV exists before loading
- Fall back to simulated data if file missing
- Log warnings when using simulated data

**3. SQLite Schema**
```sql
CREATE TABLE IF NOT EXISTS investigation_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_name TEXT NOT NULL,
    status TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_entity_name ON investigation_status_history(entity_name);
CREATE INDEX idx_timestamp ON investigation_status_history(timestamp);
```

**4. API Response Format**
All endpoints return JSON:
```json
{
    "success": true,
    "data": {...},
    "message": "Optional message"
}
```

Error responses:
```json
{
    "success": false,
    "error": "Error description"
}
```

## Development Workflow

**Step 1: Setup Environment**
```bash
cd fraud-detection-dashboard/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

**Step 2: Initialize Database**
```bash
python database.py  # Creates tables
```

**Step 3: Run Data Processing**
```bash
python data_processor.py  # Generates all DataFrames
```

**Step 4: Start API Server**
```bash
python app.py  # Starts Flask on http://localhost:5000
```

**Step 5: Test Endpoints**
```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/entities
```

## Testing Strategy

**Unit Tests:**
- data_processor.py: Test each DataFrame generation function
- database.py: Test CRUD operations

**Integration Tests:**
- API endpoints with sample data
- End-to-end data flow

**Manual Testing:**
- Use Postman/curl to test all endpoints
- Verify DataFrame structures match wireframe requirements

## Performance Considerations

**Data Processing:**
- Cache processed DataFrames in memory (reload only when data changes)
- Pre-calculate all metrics at startup
- Avoid re-running analysis on every API call

**Database:**
- Index on entity_name for fast status lookups
- Limit status history queries with pagination

**API:**
- Enable CORS for local development
- Add request validation
- Return appropriate HTTP status codes

## Next Steps After Backend Complete

1. Test all API endpoints thoroughly
2. Document API with example requests/responses
3. Begin frontend React implementation
4. Integrate frontend with backend API
5. Deploy locally for user testing

## File Creation Order

1. config.py
2. database.py
3. data_processor.py
4. app.py
5. requirements.txt
6. README.md (backend)
7. CSV templates (data/input/)
8. Main README.md

Each file will be provided as separate artifact with naming:
fraud-detection-dashboard/backend/[filename] -- v0