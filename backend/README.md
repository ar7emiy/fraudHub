# Fraud Detection Dashboard - Backend

Python Flask API backend for the Workers Compensation Fraud Detection Dashboard.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd fraud-detection-dashboard/backend
python -m venv venv
```

### 2. Activate Virtual Environment

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 5. Create Data Directories

The application will auto-create directories, but you can create them manually:

```bash
mkdir -p ../data/input
mkdir -p ../data/output
```

### 6. (Optional) Add External Data Files

If you have real external fraud scores and fraud rules data, place them in the data/input directory:

- `../data/input/external_fraud_scores.csv`
- `../data/input/claim_fraud_rules.csv`

If these files are not present, the system will use simulated data.

### 7. Start the API Server

```bash
python app.py
```

The API will start on `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /api/health
```
Returns API status and whether data is loaded.

### Get All Entities
```
GET /api/entities
```
Query parameters:
- `sort_by`: ensemble_score (default), total_exposure, connected_claims_count
- `filter_status`: Not Reviewed, Under Investigation, Bad Actor, Cleared
- `min_risk_score`: Minimum ensemble score (0-100)
- `entity_type`: Doctor, Lawyer, Business, Regular Person, Driver

Example:
```bash
curl "http://localhost:5000/api/entities?sort_by=ensemble_score&min_risk_score=70"
```

### Get Entity Details
```
GET /api/entity/<entity_name>
```
Returns complete details for a specific entity including risk scores, communities, connections, claims, and fraud rules.

Example:
```bash
curl "http://localhost:5000/api/entity/Dr. Michael Rodriguez"
```

### Update Entity Status
```
PUT /api/entity/<entity_name>/status
```
Request body:
```json
{
  "status": "Under Investigation"
}
```

Valid status values:
- Not Reviewed
- Under Investigation
- Bad Actor
- Cleared

Example:
```bash
curl -X PUT "http://localhost:5000/api/entity/Dr. Michael Rodriguez/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "Under Investigation"}'
```

### Get Status History
```
GET /api/entity/<entity_name>/status-history
```
Returns all status changes for an entity with timestamps.

### Get Communities
```
GET /api/communities
```
Returns all communities with fraud statistics and risk levels.

### Reload Data
```
POST /api/reload
```
Reloads all data (useful during development).

## Configuration

Edit `config.py` to modify:

- API host and port
- Database location
- Data file paths
- Scoring weights
- Community detection parameters

## Database

The SQLite database is automatically created at:
```
../data/output/fraud_detection.db
```

It stores investigation status history with timestamps.

## Testing

### Run Data Processor Standalone
```bash
python data_processor.py
```

### Test Database Operations
```bash
python database.py
```

### Test API Endpoints

Start the server, then use curl or Postman:

```bash
# Health check
curl http://localhost:5000/api/health

# Get entities
curl http://localhost:5000/api/entities

# Get specific entity
curl http://localhost:5000/api/entity/Dr.%20Michael%20Rodriguez
```

## Data Processing Flow

1. Load base entities and claim notes data
2. Extract entities from notes using NER
3. Build network graph from entity co-occurrences
4. Detect overlapping communities using k-clique algorithm
5. Calculate centrality scores for social network risk
6. Load external fraud scores (or simulate if not provided)
7. Load fraud rules mappings (or simulate if not provided)
8. Aggregate all metrics at entity level
9. Generate dashboard DataFrames
10. Initialize investigation statuses in database
11. Serve data through API endpoints

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, change it in `config.py`:
```python
API_PORT = 5001
```

### spaCy Model Not Found
Download the spaCy model:
```bash
python -m spacy download en_core_web_sm
```

### Database Locked Error
Close any other processes accessing the database, or delete the database file to recreate it:
```bash
rm ../data/output/fraud_detection.db
```

### Out of Memory
If processing fails due to memory, reduce the dataset size or increase available memory.

## Development

### Adding New Endpoints

1. Add route handler in `app.py`
2. Follow the existing pattern for error handling and JSON responses
3. Update this README with the new endpoint

### Modifying Scoring Algorithm

Edit weights in `config.py`:
```python
SOCIAL_NETWORK_WEIGHT = 0.6
EXTERNAL_FRAUD_WEIGHT = 0.4
```

### Changing Community Detection

Modify the k-clique size in `config.py`:
```python
K_CLIQUE_SIZE = 3  # Increase for tighter communities
```

## Next Steps

After the backend is running:

1. Verify all endpoints return data correctly
2. Test status update functionality
3. Proceed with frontend React development
4. Connect frontend to these API endpoints