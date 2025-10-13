# Fraud Hub - Network-mapping-aglorith-enhanced fraud detection & analytics software

A network analysis-based system for detecting potential fraud conspiracies in workers compensation claims.

## Overview

This system uses social network analysis and external fraud indicators to identify entities (doctors, lawyers, businesses, claimants) who may be engaged in coordinated fraud activities. The dashboard provides claim operations teams with ranked lists of suspicious entities and detailed evidence for investigation prioritization.

## Features

- Network-based fraud detection using overlapping community detection
- Entity risk scoring combining social network patterns and external fraud signals
- Investigation status tracking with full history
- Entity relationship visualization and analysis
- Fraud rules tracking per claim
- Financial exposure calculation
- REST API for integration with other systems

## Project Structure

```
fraud-detection-dashboard/
|
|-- backend/                    # Python Flask API
|   |-- app.py                 # Main API server
|   |-- data_processor.py      # Fraud detection analysis engine
|   |-- database.py            # SQLite operations
|   |-- config.py              # Configuration settings
|   |-- requirements.txt       # Python dependencies
|   |-- README.md             # Backend documentation
|
|-- data/
|   |-- input/                # External data files
|   |   |-- external_fraud_scores.csv
|   |   |-- claim_fraud_rules.csv
|   |
|   |-- output/               # Generated data
|       |-- fraud_detection.db
|
|-- frontend/                 # React dashboard (future phase)
|
|-- README.md                 # This file
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 2GB RAM minimum
- 500MB disk space

### Installation

1. Clone or download this repository
2. Navigate to the backend directory:
```bash
cd fraud-detection-dashboard/backend
```

3. Create and activate virtual environment:

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

5. Start the API server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Verify Installation

Test the API:
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "success": true,
  "message": "API is running",
  "data_loaded": true
}
```

## Usage

### Get Entity Rankings

```bash
curl "http://localhost:5000/api/entities?sort_by=ensemble_score"
```

Returns ranked list of entities by fraud risk score.

### Get Entity Details

```bash
curl "http://localhost:5000/api/entity/Dr. Michael Rodriguez"
```

Returns complete fraud profile including:
- Risk score breakdown
- Community memberships
- Network connections
- Associated claims
- Triggered fraud rules

### Update Investigation Status

```bash
curl -X PUT "http://localhost:5000/api/entity/Dr. Michael Rodriguez/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "Under Investigation"}'
```

## How It Works

### 1. Data Processing

The system analyzes claim notes to extract entity relationships:
- Named Entity Recognition (NER) identifies entities in claim notes
- Co-occurrence patterns build a network graph
- Entities connected through shared claims form relationships

### 2. Community Detection

Overlapping k-clique community detection identifies fraud rings:
- Entities with 3+ shared connections form communities
- Entities can belong to multiple communities
- Communities with high fraud ratios are flagged

### 3. Risk Scoring

Ensemble risk score combines:
- Social Network Score (60%): Centrality in fraud network
- External Fraud Score (40%): Pre-calculated fraud indicators

Social Network Score formula:
```
0.4 * Degree Centrality + 
0.3 * Betweenness Centrality + 
0.3 * Eigenvector Centrality
```

External Fraud Score formula:
```
Average Score * log(1 + Claim Count)
```

### 4. Investigation Prioritization

Entities ranked by ensemble score provide investigation priority:
- High scores indicate strong fraud indicators
- Multiple community memberships suggest coordination
- Connections to confirmed fraud entities increase risk

## Configuration

Edit `backend/config.py` to customize:

- API settings (host, port, debug mode)
- Database location
- Scoring weights
- Community detection parameters (k-clique size)
- Investigation status options

## External Data Integration

### External Fraud Scores

Place your external fraud scoring data in:
```
data/input/external_fraud_scores.csv
```

Format:
```csv
claim_number,external_fraud_score
WC-2024-001,0.75
WC-2024-002,0.89
```

### Fraud Rules

Place fraud rules mapping in:
```
data/input/claim_fraud_rules.csv
```

Format:
```csv
claim_number,rule_no,rule_desc,priority,value
WC-2024-001,5,Law enforcement inquiry regarding claim,High,9
WC-2024-001,7,Surveillance reveals employed elsewhere,High,10
```

If these files are not provided, the system uses simulated data for demonstration.

## Investigation Workflow

1. View ranked entity list sorted by risk score
2. Select high-risk entity to view details
3. Review evidence:
   - Community fraud ratios
   - Network connections to known fraudsters
   - Triggered fraud rules
   - Financial exposure
4. Update investigation status:
   - Not Reviewed (default)
   - Under Investigation
   - Bad Actor (confirmed fraud)
   - Cleared (investigation closed, no fraud)
5. Status changes are tracked with timestamps in database

## API Documentation

Complete API documentation available in:
```
backend/README.md
```

Key endpoints:
- GET `/api/entities` - Entity rankings
- GET `/api/entity/<name>` - Entity details
- PUT `/api/entity/<name>/status` - Update status
- GET `/api/entity/<name>/status-history` - Status history
- GET `/api/communities` - Community statistics

## Troubleshooting

### Port 5000 Already in Use

Change port in `backend/config.py`:
```python
API_PORT = 5001
```

### Database Errors

Delete and recreate database:
```bash
rm data/output/fraud_detection.db
python backend/app.py
```

### Memory Issues

Reduce dataset size or increase available RAM.

### spaCy Model Missing

Download the required model:
```bash
python -m spacy download en_core_web_sm
```

## Data Privacy and Security

This system processes sensitive claim and entity data. Ensure:

- Run on secure, isolated networks
- Implement access controls
- Follow HIPAA and data privacy regulations
- Audit log all investigation status changes
- Encrypt data at rest and in transit
- Regularly backup the SQLite database

## Future Enhancements

- React frontend dashboard with Power BI styling
- Interactive network visualization
- Time-series fraud pattern analysis
- Machine learning fraud prediction models
- Integration with claim management systems
- Advanced reporting and export capabilities

## Support

For issues or questions:
1. Check the backend README for detailed API documentation
2. Review error logs in console output
3. Verify all dependencies are installed correctly

## License

Proprietary - For internal use only

## Version

v0 - Initial Release

Backend complete and ready for local deployment.