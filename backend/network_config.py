"""
Network Complexity Configuration
Adjust these parameters to control the size and density of the fraud network
"""

# ===== NETWORK SIZE PARAMETERS =====
# Increase these for more impressive/complex networks without token cost

# Entity counts by type
NUM_DOCTORS = 15  # Default: 10 (increase to 20-30 for wow factor)
NUM_LAWYERS = 10  # Default: 6 (increase to 15-20)
NUM_BUSINESSES = 15  # Default: 12 (increase to 25-40)
NUM_CLAIMANTS = 40  # Default: 12 (increase to 60-100)

# Total entities = NUM_DOCTORS + NUM_LAWYERS + NUM_BUSINESSES + NUM_CLAIMANTS
# Recommended for client demos: 100-150 total entities

# Claim generation
NUM_CLAIMS = 150  # Default: 20 (increase to 150-300 for dense network)
MIN_ENTITIES_PER_CLAIM = 2  # Minimum entities mentioned in each claim
MAX_ENTITIES_PER_CLAIM = 5  # Maximum entities mentioned in each claim

# Fraud ratio (what % of entities are fraudulent)
FRAUD_RATIO = 0.35  # 35% of entities are confirmed fraud (creates red borders)


# ===== NETWORK DENSITY PARAMETERS =====
# Control how connected the network is

# Community detection
K_CLIQUE_SIZE_OVERRIDE = 3  # k-clique parameter (3 = tight communities, 2 = looser)

# Connection probability
# Higher = more edges, denser network (0.0 to 1.0)
RANDOM_CONNECTION_PROBABILITY = 0.15  # Add random connections beyond claim-based ones


# ===== CLAIM NOTE TEMPLATES =====
# These are lightweight templates that don't consume tokens

CLAIM_NOTE_TEMPLATES = [
    "{claimant} filed claim for {injury_type} at {business}. Treated by {doctor}. Legal rep: {lawyer}.",
    "Workplace incident involving {claimant} at {business}. Medical evaluation by {doctor}. Attorney {lawyer} reviewing case.",
    "{doctor} provided treatment to {claimant} for {injury_type} sustained at {business}. {lawyer} handling legal matters.",
    "Claim filed: {claimant} injured at {business}. {doctor} ordered diagnostic testing. {lawyer} representing claimant.",
    "{claimant} sustained {injury_type}. Initial treatment at {business} facility by {doctor}. {lawyer} initiated proceedings.",
    "Workers comp case: {claimant} at {business}. Treatment provider: {doctor}. Legal counsel: {lawyer}.",
    "{doctor} evaluated {claimant} for {injury_type} from {business} incident. Legal representation by {lawyer}.",
    "Ongoing treatment for {claimant} by {doctor}. Incident occurred at {business}. {lawyer} managing claim.",
]

INJURY_TYPES = [
    "back strain", "shoulder injury", "knee injury", "repetitive stress injury",
    "slip and fall", "lifting injury", "carpal tunnel syndrome", "neck strain",
    "ankle sprain", "wrist fracture", "chemical exposure", "hearing loss",
    "rotator cuff tear", "herniated disc", "soft tissue damage", "laceration"
]


# ===== FINANCIAL PARAMETERS =====
# Control claim financial exposure

# For fraud entities (higher amounts)
FRAUD_CLAIM_INCURRED_MIN = 25000
FRAUD_CLAIM_INCURRED_MAX = 75000
FRAUD_CLAIM_RESERVE_MIN = 15000
FRAUD_CLAIM_RESERVE_MAX = 45000

# For non-fraud entities (lower amounts)
NORMAL_CLAIM_INCURRED_MIN = 2000
NORMAL_CLAIM_INCURRED_MAX = 18000
NORMAL_CLAIM_RESERVE_MIN = 1000
NORMAL_CLAIM_RESERVE_MAX = 12000


# ===== VISUALIZATION PARAMETERS =====
# These affect how the network looks in the UI

# Node sizing
MIN_NODE_SIZE = 3
MAX_NODE_SIZE = 12

# Force graph physics
FORCE_LINK_DISTANCE = 100  # Distance between connected nodes
FORCE_CHARGE_STRENGTH = -300  # Repulsion between all nodes (negative = repel)
FORCE_COLLISION_RADIUS = 30  # Prevent node overlap


# ===== PRESET CONFIGURATIONS =====

def get_preset(preset_name):
    """Get preconfigured network sizes for different scenarios"""

    presets = {
        'demo': {
            'NUM_DOCTORS': 10,
            'NUM_LAWYERS': 6,
            'NUM_BUSINESSES': 12,
            'NUM_CLAIMANTS': 12,
            'NUM_CLAIMS': 25,
            'description': 'Small demo network (40 entities, 25 claims)'
        },
        'client_presentation': {
            'NUM_DOCTORS': 25,
            'NUM_LAWYERS': 18,
            'NUM_BUSINESSES': 35,
            'NUM_CLAIMANTS': 70,
            'NUM_CLAIMS': 200,
            'description': 'Impressive client demo (148 entities, 200 claims)'
        },
        'production': {
            'NUM_DOCTORS': 50,
            'NUM_LAWYERS': 40,
            'NUM_BUSINESSES': 80,
            'NUM_CLAIMANTS': 200,
            'NUM_CLAIMS': 500,
            'description': 'Production-scale network (370 entities, 500 claims)'
        },
        'stress_test': {
            'NUM_DOCTORS': 100,
            'NUM_LAWYERS': 80,
            'NUM_BUSINESSES': 150,
            'NUM_CLAIMANTS': 400,
            'NUM_CLAIMS': 1000,
            'description': 'Stress test (730 entities, 1000 claims)'
        }
    }

    return presets.get(preset_name, presets['demo'])


# ===== ACTIVE PRESET =====
# Change this to switch between presets quickly
ACTIVE_PRESET = 'client_presentation'  # Options: 'demo', 'client_presentation', 'production', 'stress_test'

# Apply preset (will override the manual settings above)
if ACTIVE_PRESET:
    preset = get_preset(ACTIVE_PRESET)
    NUM_DOCTORS = preset['NUM_DOCTORS']
    NUM_LAWYERS = preset['NUM_LAWYERS']
    NUM_BUSINESSES = preset['NUM_BUSINESSES']
    NUM_CLAIMANTS = preset['NUM_CLAIMANTS']
    NUM_CLAIMS = preset['NUM_CLAIMS']
