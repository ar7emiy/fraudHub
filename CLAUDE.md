# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fraud Hub is a network analysis-based system for detecting potential fraud conspiracies in workers compensation claims. The system uses social network analysis (overlapping community detection with k-clique algorithm) and external fraud indicators to identify entities (doctors, lawyers, businesses, claimants) who may be engaged in coordinated fraud activities.

**Architecture**: Full-stack application with Python Flask backend + React frontend

## Development Commands

### Backend (Python Flask API)

```bash
# Initial setup (from project root)
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Start the API server
python app.py
# Server runs at http://localhost:5000

# Test the API
curl http://localhost:5000/api/health

# Run data processor standalone (for testing)
python data_processor.py

# Run database operations standalone (for testing)
python database.py
```

### Frontend (React + Vite)

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Dev server runs at http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview
```

## High-Level Architecture

### Backend Data Flow

The fraud detection engine follows this pipeline in `data_processor.py`:

1. **Dataset Creation** → Creates synthetic workers comp claims with entities
2. **NER Extraction** → Extracts entity mentions from claim notes using pattern matching
3. **Network Building** → Builds graph where nodes are entities, edges represent co-occurrence in claims
4. **Community Detection** → Uses k-clique overlapping community detection (k=3) to identify fraud rings
5. **Centrality Calculation** → Calculates social network scores using weighted combination of degree, betweenness, and eigenvector centrality
6. **External Data Integration** → Loads external fraud scores and fraud rules from CSV files (or simulates if missing)
7. **Ensemble Scoring** → Combines social network score (60%) with external fraud score (40%) to create final risk ranking
8. **Dashboard Data Generation** → Creates 6 key DataFrames for API consumption

### Key Backend Modules

- **`app.py`**: Flask API server with REST endpoints for entity rankings, details, status updates
- **`data_processor.py`**: Core fraud detection engine (`FraudDetectionProcessor` class) with full analysis pipeline
- **`database.py`**: SQLite operations for investigation status tracking with full history
- **`config.py`**: Centralized configuration for file paths, API settings, scoring weights, and algorithm parameters

### Frontend Architecture

React single-page application with component hierarchy:

- **`App.jsx`**: Main container managing state, filters, API calls
- **`FilterBar`**: Controls for sorting, filtering by status/risk/type, and search
- **`EntityList`**: Left panel showing ranked entity list
- **`EntityDetail`**: Right panel with detailed entity view (risk scores, communities, connections, claims, fraud rules)
- **`services/api.js`**: Axios-based API client for backend communication

### Database Schema

SQLite database stores investigation workflow:

```sql
investigation_status_history
  - id (PK)
  - entity_name
  - status (Not Reviewed | Under Investigation | Bad Actor | Cleared)
  - timestamp

Indexes: entity_name, timestamp
```

Status changes are immutable and tracked with full history.

### API Structure

All endpoints return JSON with format: `{ success: bool, data: any, message?: string }`

Key endpoints:
- `GET /api/entities` - Get ranked entities (supports filters: sort_by, filter_status, min_risk_score, entity_type)
- `GET /api/entity/<name>` - Get full entity details including connections, claims, fraud rules
- `PUT /api/entity/<name>/status` - Update investigation status
- `GET /api/entity/<name>/status-history` - Get status change history
- `GET /api/communities` - Get community statistics with fraud ratios
- `POST /api/reload` - Reload all data (dev/testing)

## Important Implementation Details

### Network Connections Bug Fix

The codebase has a known issue with duplicate network connections in the `NetworkConnectionsTable`. The fix is implemented in `data_processor.py:508-559` which ensures:
- No self-connections (entity connected to itself)
- No duplicate pairs (A→B and B→A represented once)
- Uses `processed_pairs` set to track sorted tuples

When working with network connections, always verify connections are bidirectional but stored once, and ensure `source_entity != target_entity`.

### Fraud Detection Algorithm

The ensemble risk score is calculated as:
```
ensemble_score = (0.6 * social_network_score) + (0.4 * external_fraud_score * 100)

social_network_score = 0.4 * degree_centrality + 0.3 * betweenness_centrality + 0.3 * eigenvector_centrality
external_fraud_score = avg_score * log(1 + claim_count)
```

These weights are configurable in `config.py`.

### External Data Files

The system expects two CSV files in `data/input/`:
- `external_fraud_scores.csv` (columns: claim_number, external_fraud_score)
- `claim_fraud_rules.csv` (columns: claim_number, rule_no, rule_desc, priority, value)

If files don't exist, the system generates simulated data automatically. When adding real data integration, update the load methods in `data_processor.py:290-313`.

### Community Detection

Uses NetworkX's k-clique community detection algorithm (overlapping communities). Key parameters:
- **k=3**: Entities sharing 3+ connections form a community
- Entities can belong to multiple communities (overlapping)
- Community fraud ratio = (fraud members / total members)

The one-to-many entity-community relationship is stored in `entity_communities` defaultdict and requires special handling in DataFrames.

## Configuration

Key settings in `backend/config.py`:
- API host/port (default: 0.0.0.0:5000)
- Database path (data/output/fraud_detection.db)
- K-clique size (default: 3)
- Scoring weights for ensemble model
- Valid investigation statuses
- CORS origins for frontend

## Data Privacy

This system processes sensitive claim and entity data. The codebase includes notes about HIPAA compliance, data encryption, and audit logging requirements. When deploying, ensure proper security measures are implemented.

## Known Issues

1. **Network Connections Duplicates**: Fixed in data_processor.py but may require additional verification in UI
2. **External Data**: Currently uses simulated data; real data integration needs implementation
3. **spaCy Dependency**: Requires manual download of en_core_web_sm model after pip install
4. **Windows Path Handling**: Uses pathlib.Path for cross-platform compatibility

## Testing

To verify the system is working:
1. Start backend: `python backend/app.py`
2. Check health: `curl http://localhost:5000/api/health` (should return `data_loaded: true`)
3. Start frontend: `cd frontend && npm run dev`
4. Open browser to http://localhost:5173
5. Verify entity list loads and detail panel shows data when clicking entities

## Future Enhancements

The README mentions planned features:
- Interactive network visualization
- Time-series fraud pattern analysis
- Machine learning fraud prediction models
- Integration with claim management systems
- Advanced reporting and export capabilities
