"""
Flask API server for Fraud Detection Dashboard
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

from data_processor import FraudDetectionProcessor
from database import DatabaseManager
from config import API_HOST, API_PORT, API_DEBUG, CORS_ORIGINS, VALID_STATUSES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

# Initialize processor and database
processor = FraudDetectionProcessor()
db = DatabaseManager()

# Global storage for processed data
data_cache = {}


def initialize_data():
    """Initialize data on startup"""
    global data_cache
    
    logger.info("Initializing fraud detection data...")
    
    try:
        # Run full analysis
        results = processor.run_full_analysis()
        data_cache = results
        
        # Initialize entity statuses in database
        entity_names = results['entity_dashboard']['entity_name'].tolist()
        db.initialize_entity_statuses(entity_names)
        
        logger.info("Data initialization complete")
        return True
    except Exception as e:
        logger.error(f"Error initializing data: {e}")
        return False


@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is running',
        'data_loaded': len(data_cache) > 0
    })


@app.route('/api/entities', methods=['GET'])
def get_entities():
    """
    Get entity rankings list with optional filtering and sorting
    
    Query parameters:
    - sort_by: ensemble_score (default), total_exposure, connected_claims_count
    - filter_status: Investigation status filter
    - min_risk_score: Minimum ensemble score threshold
    - entity_type: Filter by entity type
    """
    try:
        if 'entity_dashboard' not in data_cache:
            return jsonify({
                'success': False,
                'error': 'Data not initialized'
            }), 500
        
        df = data_cache['entity_dashboard'].copy()
        
        # Get latest statuses from database
        statuses = db.get_all_latest_statuses()
        df['investigation_status'] = df['entity_name'].map(
            lambda x: statuses.get(x, 'Not Reviewed')
        )
        
        # Apply filters
        filter_status = request.args.get('filter_status')
        if filter_status and filter_status != 'all':
            df = df[df['investigation_status'] == filter_status]
        
        min_risk = request.args.get('min_risk_score', type=float)
        if min_risk is not None:
            df = df[df['ensemble_score'] >= min_risk]
        
        entity_type = request.args.get('entity_type')
        if entity_type and entity_type != 'All Types':
            df = df[df['entity_type'] == entity_type]
        
        # Apply sorting
        sort_by = request.args.get('sort_by', 'ensemble_score')
        if sort_by in ['ensemble_score', 'total_exposure', 'connected_claims_count']:
            df = df.sort_values(sort_by, ascending=False)
            # Recalculate priority rank after sorting
            df['priority_rank'] = range(1, len(df) + 1)
        
        # Convert to JSON-friendly format
        result = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        })
    
    except Exception as e:
        logger.error(f"Error in get_entities: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/entity/<entity_name>', methods=['GET'])
def get_entity_details(entity_name):
    """Get complete details for a specific entity"""
    try:
        # Get latest status from database
        latest_status = db.get_latest_status(entity_name)
        
        # Get entity details from processor
        details = processor.get_entity_details(entity_name)
        
        if not details:
            return jsonify({
                'success': False,
                'error': 'Entity not found'
            }), 404
        
        # Add investigation status
        details['entity']['investigation_status'] = latest_status or 'Not Reviewed'
        
        # Get community members for this entity's communities
        community_ids = [c['community_id'] for c in details['communities']]
        
        if len(community_ids) > 0:
            community_members = data_cache['community_members'][
                data_cache['community_members']['community_id'].isin(community_ids)
            ]
            details['community_members'] = community_members.to_dict('records')
        else:
            details['community_members'] = []
        
        return jsonify({
            'success': True,
            'data': details
        })
    
    except Exception as e:
        logger.error(f"Error in get_entity_details: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/entity/<entity_name>/status', methods=['PUT'])
def update_entity_status(entity_name):
    """Update investigation status for an entity"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Status field required'
            }), 400
        
        new_status = data['status']
        
        if new_status not in VALID_STATUSES:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {VALID_STATUSES}'
            }), 400
        
        # Update in database
        success = db.add_status(entity_name, new_status)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Status updated to {new_status}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update status'
            }), 500
    
    except Exception as e:
        logger.error(f"Error in update_entity_status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/entity/<entity_name>/status-history', methods=['GET'])
def get_entity_status_history(entity_name):
    """Get status change history for an entity"""
    try:
        history = db.get_status_history(entity_name)
        
        return jsonify({
            'success': True,
            'data': history,
            'count': len(history)
        })
    
    except Exception as e:
        logger.error(f"Error in get_entity_status_history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/communities', methods=['GET'])
def get_communities():
    """Get all communities with fraud statistics"""
    try:
        if 'community_members' not in data_cache:
            return jsonify({
                'success': False,
                'error': 'Data not initialized'
            }), 500
        
        df = data_cache['community_members'].copy()
        
        # Calculate community stats
        community_stats = df.groupby('community_id').agg({
            'entity_name': 'count',
            'is_fraud': ['sum', 'mean']
        }).reset_index()
        
        community_stats.columns = ['community_id', 'total_members', 'fraud_count', 'fraud_ratio']
        
        # Determine risk level
        def get_risk_level(ratio):
            if ratio > 0.4:
                return 'HIGH'
            elif ratio > 0.2:
                return 'MEDIUM'
            else:
                return 'LOW'
        
        community_stats['risk_level'] = community_stats['fraud_ratio'].apply(get_risk_level)
        
        result = community_stats.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        })
    
    except Exception as e:
        logger.error(f"Error in get_communities: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/reload', methods=['POST'])
def reload_data():
    """Reload all data (useful for development/testing)"""
    try:
        success = initialize_data()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Data reloaded successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to reload data'
            }), 500
    
    except Exception as e:
        logger.error(f"Error in reload_data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Initialize data on startup
    if initialize_data():
        logger.info(f"Starting Flask API server on {API_HOST}:{API_PORT}")
        app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)
    else:
        logger.error("Failed to initialize data. Server not started.")