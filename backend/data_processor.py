"""
Core data processing for fraud detection analysis
Extends original notebook with dashboard-specific functionality
"""

import pandas as pd
import networkx as nx
import numpy as np
import logging
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available")

from config import (
    EXTERNAL_FRAUD_SCORES_FILE,
    CLAIM_FRAUD_RULES_FILE,
    K_CLIQUE_SIZE,
    SOCIAL_NETWORK_WEIGHT,
    EXTERNAL_FRAUD_WEIGHT,
    DEGREE_CENTRALITY_WEIGHT,
    BETWEENNESS_CENTRALITY_WEIGHT,
    EIGENVECTOR_CENTRALITY_WEIGHT,
    NER_METHOD
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import network complexity configuration
try:
    from network_config import (
        NUM_DOCTORS, NUM_LAWYERS, NUM_BUSINESSES, NUM_CLAIMANTS,
        NUM_CLAIMS, MIN_ENTITIES_PER_CLAIM, MAX_ENTITIES_PER_CLAIM,
        FRAUD_RATIO, CLAIM_NOTE_TEMPLATES, INJURY_TYPES,
        FRAUD_CLAIM_INCURRED_MIN, FRAUD_CLAIM_INCURRED_MAX,
        FRAUD_CLAIM_RESERVE_MIN, FRAUD_CLAIM_RESERVE_MAX,
        NORMAL_CLAIM_INCURRED_MIN, NORMAL_CLAIM_INCURRED_MAX,
        NORMAL_CLAIM_RESERVE_MIN, NORMAL_CLAIM_RESERVE_MAX,
        ACTIVE_PRESET, get_preset
    )
    NETWORK_CONFIG_AVAILABLE = True
    logger.info(f"Network configuration loaded: {ACTIVE_PRESET if ACTIVE_PRESET else 'custom'}")
    if ACTIVE_PRESET:
        preset_info = get_preset(ACTIVE_PRESET)
        logger.info(f"  → {preset_info['description']}")
except ImportError:
    NETWORK_CONFIG_AVAILABLE = False
    logger.warning("Network config not available, using default hardcoded dataset")


class FraudDetectionProcessor:
    """Main data processor for fraud detection dashboard"""
    
    def __init__(self):
        self.entities_df = None
        self.notes_df = None
        self.extracted_entities = None
        self.network = nx.Graph()
        self.communities = {}
        self.entity_communities = defaultdict(list)  # One-to-many mapping
        self.fraud_entities = set()
        self.node_sizes = {}
        
        # External data
        self.external_fraud_scores = None
        self.claim_fraud_rules = None
        self.claim_financials = None
        
        # Dashboard DataFrames
        self.df_entity_dashboard = None
        self.df_entity_communities = None
        self.df_community_members = None
        self.df_entity_connections = None
        self.df_entity_claims = None
        self.df_entity_fraud_rules = None
        
        # Initialize NER if available
        if SPACY_AVAILABLE:
            self.ner_model = nlp
        else:
            self.ner_model = None
            logger.warning("NER model not available")
    
    def create_dataset(self):
        """Create the workers compensation dataset - scalable version"""

        if NETWORK_CONFIG_AVAILABLE:
            logger.info("Using scalable dataset generation from network_config.py")
            self._create_scalable_dataset()
        else:
            logger.info("Using default hardcoded dataset (40 entities, 20 claims)")
            self._create_hardcoded_dataset()

        self.fraud_entities = set(self.entities_df[self.entities_df['FraudList'] == 1]['Name_Business'].values)
        logger.info(f"Dataset created: {len(self.entities_df)} entities, {len(self.notes_df)} notes")
        logger.info(f"Fraud entities identified: {len(self.fraud_entities)}")

    def _create_scalable_dataset(self):
        """Generate large-scale dataset using templates (token-efficient)"""

        # Name generation pools
        doctor_first = ['Michael', 'Jennifer', 'Amanda', 'Steven', 'Carlos', 'Lisa', 'Thomas', 'Nicole',
                        'David', 'Sarah', 'Robert', 'Patricia', 'James', 'Maria', 'Kevin', 'Daniel',
                        'Angela', 'Christopher', 'Elizabeth', 'Matthew', 'Jessica', 'Andrew', 'Michelle',
                        'Joshua', 'Rachel', 'Ryan', 'Rebecca', 'Brian', 'Laura', 'William']
        doctor_last = ['Rodriguez', 'Walsh', 'Foster', 'Kim', 'Mendez', 'Patel', 'Burke', 'Zhang',
                       'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                       'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas']

        person_first = ['Sarah', 'David', 'Lisa', 'Robert', 'Maria', 'Kevin', 'Patricia', 'Frank',
                        'Janet', 'Brandon', 'Emma', 'Angela', 'Mark', 'Chris', 'Samantha', 'Daniel',
                        'Michelle', 'Steven', 'Rachel', 'Tony', 'Jessica', 'Andrew', 'Nicole', 'Brian']
        person_last = ['Thompson', 'Park', 'Chen', 'Davis', 'Gonzalez', 'O\'Brien', 'Williams', 'Harrison',
                       'Murphy', 'Taylor', 'Watson', 'Scott', 'Johnson', 'Adams', 'Lee', 'Cooper',
                       'Mitchell', 'Green', 'Ricci', 'Martinez', 'Brown', 'Moore', 'Jackson', 'White']

        business_prefixes = ['Atlantic', 'Quick Heal', 'Summit', 'Elite', 'Northside', 'Thompson',
                            'Miller', 'City', 'Valley', 'Metro', 'Precision', 'Global', 'Progressive',
                            'Premier', 'United', 'National', 'Regional', 'Central', 'Coastal', 'Mountain']
        business_suffixes = ['Medical Group', 'Physical Therapy', 'Construction LLC', 'Diagnostics Center',
                            'Medical Plaza', 'Associates', 'Defense Attorneys', 'Medical Associates',
                            'Orthopedic Clinic', 'Legal Group', 'Logistics Inc', 'Shipping Services',
                            'Wellness Center', 'Care Center', 'Health Services', 'Solutions LLC']

        lawyer_firms = ['Thompson & Associates Law', 'Miller Defense Attorneys', 'Metro Legal Group',
                        'Coastal Law Partners', 'Premier Legal Services', 'United Defense Group',
                        'National Claims Attorneys', 'Regional Legal Associates']

        # Generate entities
        entities = []
        entity_types = []
        fraud_flags = []

        # Doctors
        for i in range(NUM_DOCTORS):
            first = doctor_first[i % len(doctor_first)]
            last = doctor_last[i % len(doctor_last)]
            name = f"Dr. {first} {last}" if i < len(doctor_first) else f"Dr. {first} {last}{i}"
            entities.append(name)
            entity_types.append('Doctor')
            fraud_flags.append(1 if np.random.random() < FRAUD_RATIO else 0)

        # Lawyers
        for i in range(NUM_LAWYERS):
            first = person_first[i % len(person_first)]
            last = person_last[i % len(person_last)]
            name = f"{first} {last}" if i < len(person_first) else f"{first} {last}{i}"
            entities.append(name)
            entity_types.append('Lawyer')
            fraud_flags.append(1 if np.random.random() < FRAUD_RATIO else 0)

        # Businesses
        for i in range(NUM_BUSINESSES):
            prefix = business_prefixes[i % len(business_prefixes)]
            suffix = business_suffixes[i % len(business_suffixes)]
            name = f"{prefix} {suffix}" if i < len(business_prefixes) else f"{prefix} {suffix} {i}"
            entities.append(name)
            entity_types.append('Business')
            fraud_flags.append(1 if np.random.random() < FRAUD_RATIO else 0)

        # Claimants (Regular Person / Driver)
        for i in range(NUM_CLAIMANTS):
            first = person_first[i % len(person_first)]
            last = person_last[i % len(person_last)]
            name = f"{first} {last}" if i < len(person_first) else f"{first} {last}{i}"
            entities.append(name)
            entity_types.append('Driver' if i % 3 == 0 else 'Regular Person')
            fraud_flags.append(1 if np.random.random() < FRAUD_RATIO else 0)

        self.entities_df = pd.DataFrame({
            'Name_Business': entities,
            'Type': entity_types,
            'FraudList': fraud_flags
        })

        # Generate claims using templates
        claim_numbers = []
        note_ids = []
        notes = []

        # Get entity lists by type for sampling
        doctors = self.entities_df[self.entities_df['Type'] == 'Doctor']['Name_Business'].tolist()
        lawyers = self.entities_df[self.entities_df['Type'] == 'Lawyer']['Name_Business'].tolist()
        businesses = self.entities_df[self.entities_df['Type'] == 'Business']['Name_Business'].tolist()
        claimants = self.entities_df[self.entities_df['Type'].isin(['Regular Person', 'Driver'])]['Name_Business'].tolist()

        note_counter = 1
        for claim_idx in range(NUM_CLAIMS):
            claim_num = f'WC-2024-{claim_idx+1:04d}'

            # How many notes for this claim (1-3)
            num_notes = np.random.randint(1, 4)

            for note_num in range(num_notes):
                # Pick entities for this claim note
                claimant = np.random.choice(claimants)
                doctor = np.random.choice(doctors) if len(doctors) > 0 else "Dr. Unknown"
                lawyer = np.random.choice(lawyers) if len(lawyers) > 0 else "Attorney Unknown"
                business = np.random.choice(businesses) if len(businesses) > 0 else "Unknown Business"
                injury = np.random.choice(INJURY_TYPES)

                # Use template
                template = np.random.choice(CLAIM_NOTE_TEMPLATES)
                note_text = template.format(
                    claimant=claimant,
                    doctor=doctor,
                    lawyer=lawyer,
                    business=business,
                    injury_type=injury
                )

                claim_numbers.append(claim_num)
                note_ids.append(f'N{note_counter:05d}')
                notes.append(note_text)
                note_counter += 1

        self.notes_df = pd.DataFrame({
            'ClaimNumber': claim_numbers,
            'NoteID': note_ids,
            'Note': notes
        })

        logger.info(f"Generated {len(entities)} entities: {NUM_DOCTORS} doctors, {NUM_LAWYERS} lawyers, {NUM_BUSINESSES} businesses, {NUM_CLAIMANTS} claimants")
        logger.info(f"Generated {NUM_CLAIMS} claims with {len(notes)} total notes")

    def _create_hardcoded_dataset(self):
        """Fallback: original hardcoded 40-entity dataset"""

        entities_data = {
            'Name_Business': [
                'Dr. Michael Rodriguez', 'Sarah Thompson', 'Atlantic Medical Group', 'James Mitchell',
                'Lisa Chen', 'Robert Davis', 'Quick Heal Physical Therapy', 'Dr. Jennifer Walsh',
                'Maria Gonzalez', 'David Park', 'Thompson & Associates Law', 'Dr. Amanda Foster',
                'Kevin O\'Brien', 'Summit Construction LLC', 'Patricia Williams', 'Dr. Steven Kim',
                'Elite Diagnostics Center', 'Mark Johnson', 'Rachel Green', 'Tony Ricci',
                'Northside Medical Plaza', 'Dr. Carlos Mendez', 'Janet Murphy', 'Global Shipping Services',
                'Frank Harrison', 'Miller Defense Attorneys', 'Dr. Lisa Patel', 'Brandon Taylor',
                'Emma Watson', 'City Medical Associates', 'Dr. Thomas Burke', 'Angela Scott',
                'Precision Logistics Inc', 'Chris Adams', 'Valley Orthopedic Clinic', 'Dr. Nicole Zhang',
                'Metro Legal Group', 'Daniel Cooper', 'Samantha Lee', 'Progressive Wellness Center'
            ],
            'Type': [
                'Doctor', 'Regular Person', 'Business', 'Lawyer', 'Regular Person', 'Driver', 'Business',
                'Doctor', 'Regular Person', 'Driver', 'Business', 'Doctor', 'Regular Person', 'Business',
                'Regular Person', 'Doctor', 'Business', 'Driver', 'Lawyer', 'Regular Person', 'Business',
                'Doctor', 'Regular Person', 'Business', 'Driver', 'Business', 'Doctor', 'Regular Person',
                'Lawyer', 'Business', 'Doctor', 'Regular Person', 'Business', 'Driver', 'Business',
                'Doctor', 'Business', 'Regular Person', 'Lawyer', 'Business'
            ],
            'FraudList': [
                1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1,
                0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1
            ]
        }

        notes_data = {
            'ClaimNumber': [
                'WC-2024-001', 'WC-2024-001', 'WC-2024-001', 'WC-2024-002', 'WC-2024-002',
                'WC-2024-003', 'WC-2024-003', 'WC-2024-004', 'WC-2024-005', 'WC-2024-005',
                'WC-2024-006', 'WC-2024-007', 'WC-2024-007', 'WC-2024-008', 'WC-2024-009',
                'WC-2024-010', 'WC-2024-010', 'WC-2024-011', 'WC-2024-012', 'WC-2024-012'
            ],
            'NoteID': [f'N{i:03d}' for i in range(1, 21)],
            'Note': [
                "Initial claim received for workplace injury at Summit Construction LLC. Claimant Sarah Thompson reports back strain while lifting materials on 3/15/24. Witness Mark Johnson confirmed incident occurred during normal work duties. Medical attention sought at Northside Medical Plaza same day.",
                "Follow-up with treating physician Dr. Jennifer Walsh regarding Sarah Thompson's back injury. Medical records show consistent findings with reported mechanism of injury.",
                "Sarah Thompson returned to full duty on 4/20/24 as cleared by Dr. Jennifer Walsh. Summit Construction LLC confirmed employee performance remains satisfactory.",
                "New claim filed by David Park, driver for Global Shipping Services, alleging shoulder injury from vehicle rollover on 4/2/24. Claimant sought treatment at Atlantic Medical Group with Dr. Michael Rodriguez.",
                "Surveillance conducted on David Park shows activities inconsistent with reported shoulder limitations. Treatment records from Dr. Michael Rodriguez show minimal objective findings despite extensive symptom complaints.",
                "Lisa Chen, warehouse worker, sustained ankle fracture after fall from ladder at Precision Logistics Inc on 4/10/24. Incident witnessed by Patricia Williams and Frank Harrison. Immediate medical attention provided by Dr. Amanda Foster at City Medical Associates.",
                "Lisa Chen underwent successful ankle surgery performed by Dr. Thomas Burke at Valley Orthopedic Clinic. Estimated time loss 12-16 weeks.",
                "Robert Davis, delivery driver, reports repetitive stress injury to wrists and forearms. Initial evaluation by Dr. Lisa Patel shows early signs of carpal tunnel syndrome. Work conditioning program recommended through Quick Heal Physical Therapy.",
                "Complex claim involving Maria Gonzalez who sustained multiple injuries in workplace machinery accident. Legal representation by Emma Watson from Miller Defense Attorneys raising questions about safety violations. Dr. Carlos Mendez at Elite Diagnostics Center conducting extensive diagnostic testing.",
                "Settlement discussions initiated for Maria Gonzalez claim through attorney Emma Watson. Independent medical examination scheduled with Dr. Nicole Zhang to assess permanent disability rating.",
                "Kevin O'Brien sustained chemical burn injury during routine maintenance at Atlantic Medical Group facility. Immediate treatment provided by Dr. Steven Kim showing second-degree burns requiring specialized care.",
                "Suspicious claim filed by Tony Ricci alleging back injury with no witnesses present. Treatment sought exclusively at Quick Heal Physical Therapy with excessive therapy utilization. Legal representation by James Mitchell from Thompson & Associates Law raising red flags.",
                "Investigation results for Tony Ricci claim reveal social media posts showing activities inconsistent with disability claims. Treatment provider Quick Heal Physical Therapy has history of questionable billing practices. Attorney James Mitchell represents multiple suspicious claims.",
                "Janet Murphy, office administrator, developed gradual onset back pain over several months. Ergonomic assessment conducted by Brandon Taylor identified workstation deficiencies. Conservative treatment with Dr. Jennifer Walsh showing good progress.",
                "Chris Adams sustained laceration injury requiring emergency surgery at Northside Medical Plaza. Dr. Amanda Foster performed successful repair with good healing progress noted. Employer Summit Construction LLC reviewing safety procedures.",
                "Daniel Cooper reports hearing loss allegedly from prolonged noise exposure at Metro Legal Group office location. Audiological testing by Dr. Nicole Zhang shows results inconsistent with claimed exposure levels.",
                "Hearing loss claim for Daniel Cooper requires additional medical evaluation by specialist Dr. Thomas Burke. Independent assessment confirms pre-existing condition significantly contributing to current hearing status.",
                "Angela Scott sustained serious injury in forklift accident witnessed by multiple employees including Samantha Lee. Emergency treatment at Valley Orthopedic Clinic with Dr. Carlos Mendez revealed multiple fractures requiring extensive rehabilitation.",
                "Routine claim closure for Mark Johnson's minor laceration injury treated at City Medical Associates. Dr. Lisa Patel provided appropriate care with complete healing achieved within standard timeframe.",
                "Final settlement reached for Mark Johnson claim with total costs of $1,450 including medical expenses and wage replacement. Dr. Lisa Patel released claimant to full duty status."
            ]
        }

        self.entities_df = pd.DataFrame(entities_data)
        self.notes_df = pd.DataFrame(notes_data)
    
    def extract_entities_ner(self):
        """Extract entities from notes using NER"""
        
        logger.info("Performing Named Entity Recognition...")
        
        # Create entity patterns for better matching
        entity_patterns = {}
        for entity in self.entities_df['Name_Business']:
            patterns = [entity]
            if 'Dr. ' in entity:
                patterns.append(entity.replace('Dr. ', ''))
            if ' LLC' in entity:
                patterns.append(entity.replace(' LLC', ''))
            entity_patterns[entity] = patterns
        
        note_entities = []
        
        for idx, row in self.notes_df.iterrows():
            note_text = row['Note']
            claim_num = row['ClaimNumber']
            note_id = row['NoteID']
            
            found_entities = []
            
            # Custom entity matching - use longest match to avoid duplicates
            matched_entities = set()
            for entity, patterns in entity_patterns.items():
                for pattern in patterns:
                    if pattern in note_text and entity not in matched_entities:
                        found_entities.append(entity)
                        matched_entities.add(entity)
                        break
            
            # Store results
            for entity in found_entities:
                note_entities.append({
                    'ClaimNumber': claim_num,
                    'NoteID': note_id,
                    'Entity': entity,
                    'IsFraud': 1 if entity in self.fraud_entities else 0
                })
        
        self.extracted_entities = pd.DataFrame(note_entities)
        
        # Remove any duplicate entity mentions in the same note
        self.extracted_entities = self.extracted_entities.drop_duplicates(subset=['NoteID', 'Entity'])
        
        logger.info(f"Extracted {len(self.extracted_entities)} entity mentions")
    
    def build_network(self):
        """Build network graph from entity co-occurrences"""
        
        logger.info("Building network graph...")
        
        # Group entities by note to find co-occurrences
        note_groups = self.extracted_entities.groupby('NoteID')['Entity'].apply(list).reset_index()
        
        edge_weights = defaultdict(int)
        
        # Create edges for entities that appear together
        for _, row in note_groups.iterrows():
            entities = row['Entity']
            if len(entities) > 1:
                for entity1, entity2 in combinations(entities, 2):
                    edge = tuple(sorted([entity1, entity2]))
                    edge_weights[edge] += 1
        
        # Build NetworkX graph
        self.network = nx.Graph()
        
        # Add nodes with attributes
        for _, entity_row in self.entities_df.iterrows():
            entity = entity_row['Name_Business']
            self.network.add_node(entity,
                                type=entity_row['Type'],
                                fraud=entity_row['FraudList'])
        
        # Add edges with weights - ensure no self-loops
        for (entity1, entity2), weight in edge_weights.items():
            if entity1 != entity2:  # Prevent self-loops
                self.network.add_edge(entity1, entity2, weight=weight)
        
        logger.info(f"Network created: {self.network.number_of_nodes()} nodes, {self.network.number_of_edges()} edges")
    
    def detect_overlapping_communities(self):
        """Detect overlapping communities using k-clique algorithm"""
        
        logger.info(f"Detecting overlapping communities (k={K_CLIQUE_SIZE})...")
        
        # Use k-clique communities (built-in NetworkX)
        k_clique_communities = list(nx.algorithms.community.k_clique_communities(self.network, K_CLIQUE_SIZE))
        
        # Store communities and entity-to-community mappings
        self.communities = {}
        self.entity_communities = defaultdict(list)
        
        for comm_id, community in enumerate(k_clique_communities):
            community_list = list(community)
            self.communities[comm_id] = community_list
            
            # Map each entity to this community
            for entity in community_list:
                self.entity_communities[entity].append(comm_id)
        
        logger.info(f"Found {len(self.communities)} overlapping communities")
        
        # Log community sizes and fraud ratios
        for comm_id, members in self.communities.items():
            fraud_count = sum(1 for m in members if m in self.fraud_entities)
            fraud_ratio = fraud_count / len(members) if len(members) > 0 else 0
            logger.info(f"Community {comm_id}: {len(members)} members, {fraud_ratio:.1%} fraud rate")
    
    def calculate_node_importance(self):
        """Calculate node importance using centrality measures"""
        
        logger.info("Calculating node importance...")
        
        # Calculate various centrality measures
        degree_centrality = nx.degree_centrality(self.network)
        betweenness_centrality = nx.betweenness_centrality(self.network, weight='weight')
        eigenvector_centrality = nx.eigenvector_centrality(self.network, weight='weight')
        
        # Combine centralities (weighted average)
        importance_scores = {}
        
        for node in self.network.nodes():
            importance = (DEGREE_CENTRALITY_WEIGHT * degree_centrality[node] +
                         BETWEENNESS_CENTRALITY_WEIGHT * betweenness_centrality[node] +
                         EIGENVECTOR_CENTRALITY_WEIGHT * eigenvector_centrality[node])
            importance_scores[node] = importance
        
        # Normalize to 0-100 scale for social network score
        max_importance = max(importance_scores.values())
        min_importance = min(importance_scores.values())
        
        self.social_network_scores = {}
        for node, importance in importance_scores.items():
            if max_importance > min_importance:
                normalized = (importance - min_importance) / (max_importance - min_importance)
            else:
                normalized = 0.5
            self.social_network_scores[node] = normalized * 100
        
        logger.info("Node importance calculated")
        return self.social_network_scores
    
    def load_external_data(self):
        """Load external fraud scores and fraud rules"""
        
        logger.info("Loading external data...")
        
        # Load external fraud scores
        if EXTERNAL_FRAUD_SCORES_FILE.exists():
            self.external_fraud_scores = pd.read_csv(EXTERNAL_FRAUD_SCORES_FILE)
            logger.info(f"Loaded {len(self.external_fraud_scores)} external fraud scores")
        else:
            logger.warning("External fraud scores file not found, using simulated data")
            self.external_fraud_scores = self._simulate_external_fraud_scores()
        
        # Load fraud rules
        if CLAIM_FRAUD_RULES_FILE.exists():
            self.claim_fraud_rules = pd.read_csv(CLAIM_FRAUD_RULES_FILE)
            logger.info(f"Loaded {len(self.claim_fraud_rules)} fraud rule mappings")
        else:
            logger.warning("Fraud rules file not found, using simulated data")
            self.claim_fraud_rules = self._simulate_fraud_rules()
        
        # Simulate claim financials
        self.claim_financials = self._simulate_claim_financials()
    
    def _simulate_external_fraud_scores(self):
        """Simulate external fraud scores for demo"""
        claim_numbers = self.notes_df['ClaimNumber'].unique()
        
        scores = []
        for claim in claim_numbers:
            # Higher scores for claims with fraud entities
            entities_in_claim = self.extracted_entities[
                self.extracted_entities['ClaimNumber'] == claim
            ]['Entity'].tolist()
            
            has_fraud = any(e in self.fraud_entities for e in entities_in_claim)
            
            if has_fraud:
                score = np.random.uniform(0.7, 0.95)
            else:
                score = np.random.uniform(0.1, 0.5)
            
            scores.append({'claim_number': claim, 'external_fraud_score': score})
        
        return pd.DataFrame(scores)
    
    def _simulate_fraud_rules(self):
        """Simulate fraud rules for demo"""
        
        rules = [
            {'rule_no': 5, 'rule_desc': 'Any law enforcement inquiry regarding the validity of any part of the claim', 'priority': 'High', 'value': 9},
            {'rule_no': 7, 'rule_desc': 'A surveillance or tip reveals the totally disabled worker is currently employed elsewhere', 'priority': 'High', 'value': 10},
            {'rule_no': 10, 'rule_desc': 'Any false statement, willfully made with the intent to deceive', 'priority': 'High', 'value': 8},
            {'rule_no': 26, 'rule_desc': 'Multiple providers billing for same service on same date', 'priority': 'Medium', 'value': 6},
            {'rule_no': 37, 'rule_desc': 'Claimant history shows pattern of similar claims across multiple employers', 'priority': 'Medium', 'value': 7},
            {'rule_no': 75, 'rule_desc': 'Medical treatment inconsistent with documented injury severity', 'priority': 'Low', 'value': 4}
        ]
        
        claim_rules = []
        claim_numbers = self.notes_df['ClaimNumber'].unique()
        
        for claim in claim_numbers:
            # Assign random rules to claims with fraud entities
            entities_in_claim = self.extracted_entities[
                self.extracted_entities['ClaimNumber'] == claim
            ]['Entity'].tolist()
            
            has_fraud = any(e in self.fraud_entities for e in entities_in_claim)
            
            if has_fraud:
                num_rules = np.random.randint(2, 5)
            else:
                num_rules = np.random.randint(0, 2)
            
            selected_rules = np.random.choice(len(rules), size=min(num_rules, len(rules)), replace=False)
            
            for rule_idx in selected_rules:
                rule = rules[rule_idx]
                claim_rules.append({
                    'claim_number': claim,
                    'rule_no': rule['rule_no'],
                    'rule_desc': rule['rule_desc'],
                    'priority': rule['priority'],
                    'value': rule['value']
                })
        
        return pd.DataFrame(claim_rules)
    
    def _simulate_claim_financials(self):
        """Simulate claim financial data"""
        claim_numbers = self.notes_df['ClaimNumber'].unique()

        # Use network config financial parameters if available
        if NETWORK_CONFIG_AVAILABLE:
            fraud_inc_min, fraud_inc_max = FRAUD_CLAIM_INCURRED_MIN, FRAUD_CLAIM_INCURRED_MAX
            fraud_res_min, fraud_res_max = FRAUD_CLAIM_RESERVE_MIN, FRAUD_CLAIM_RESERVE_MAX
            norm_inc_min, norm_inc_max = NORMAL_CLAIM_INCURRED_MIN, NORMAL_CLAIM_INCURRED_MAX
            norm_res_min, norm_res_max = NORMAL_CLAIM_RESERVE_MIN, NORMAL_CLAIM_RESERVE_MAX
        else:
            fraud_inc_min, fraud_inc_max = 15000, 50000
            fraud_res_min, fraud_res_max = 10000, 30000
            norm_inc_min, norm_inc_max = 1000, 15000
            norm_res_min, norm_res_max = 500, 10000

        financials = []
        for claim in claim_numbers:
            # Higher costs for claims with fraud entities
            entities_in_claim = self.extracted_entities[
                self.extracted_entities['ClaimNumber'] == claim
            ]['Entity'].tolist()

            has_fraud = any(e in self.fraud_entities for e in entities_in_claim)

            if has_fraud:
                incurred = np.random.randint(fraud_inc_min, fraud_inc_max)
                reserve = np.random.randint(fraud_res_min, fraud_res_max)
            else:
                incurred = np.random.randint(norm_inc_min, norm_inc_max)
                reserve = np.random.randint(norm_res_min, norm_res_max)

            financials.append({
                'claim_number': claim,
                'total_incurred': incurred,
                'reserve_amount': reserve
            })

        return pd.DataFrame(financials)
    
    def aggregate_entity_metrics(self):
        """Aggregate all metrics at entity level"""
        
        logger.info("Aggregating entity-level metrics...")
        
        entity_metrics = []
        
        for entity in self.entities_df['Name_Business']:
            # Get entity type and fraud flag
            entity_info = self.entities_df[self.entities_df['Name_Business'] == entity].iloc[0]
            
            # Get claims associated with this entity
            entity_claims = self.extracted_entities[
                self.extracted_entities['Entity'] == entity
            ]['ClaimNumber'].unique()
            
            # Calculate external fraud score metrics
            if len(entity_claims) > 0 and self.external_fraud_scores is not None:
                entity_fraud_scores = self.external_fraud_scores[
                    self.external_fraud_scores['claim_number'].isin(entity_claims)
                ]['external_fraud_score']
                
                max_ext_score = entity_fraud_scores.max() if len(entity_fraud_scores) > 0 else 0
                avg_ext_score = entity_fraud_scores.mean() if len(entity_fraud_scores) > 0 else 0
                composite_ext_score = avg_ext_score * np.log(1 + len(entity_claims))
            else:
                max_ext_score = 0
                avg_ext_score = 0
                composite_ext_score = 0
            
            # Get social network score
            social_score = self.social_network_scores.get(entity, 0)
            
            # Calculate ensemble score
            ensemble_score = (SOCIAL_NETWORK_WEIGHT * social_score + 
                            EXTERNAL_FRAUD_WEIGHT * (composite_ext_score * 100))
            
            # Calculate total exposure
            if len(entity_claims) > 0 and self.claim_financials is not None:
                entity_financials = self.claim_financials[
                    self.claim_financials['claim_number'].isin(entity_claims)
                ]
                total_exposure = entity_financials['total_incurred'].sum() + entity_financials['reserve_amount'].sum()
            else:
                total_exposure = 0
            
            entity_metrics.append({
                'entity_name': entity,
                'entity_type': entity_info['Type'],
                'social_network_score': social_score,
                'max_external_fraud_score': max_ext_score,
                'avg_external_fraud_score': avg_ext_score,
                'composite_external_score': composite_ext_score,
                'ensemble_score': ensemble_score,
                'connected_claims_count': len(entity_claims),
                'total_exposure': total_exposure,
                'is_fraud': entity_info['FraudList']
            })
        
        # Create DataFrame and add priority ranking
        df = pd.DataFrame(entity_metrics)
        df = df.sort_values('ensemble_score', ascending=False)
        df['priority_rank'] = range(1, len(df) + 1)
        
        self.df_entity_dashboard = df
        logger.info(f"Aggregated metrics for {len(df)} entities")
    
    def generate_dashboard_dataframes(self):
        """Generate all DataFrames needed for dashboard"""
        
        logger.info("Generating dashboard DataFrames...")
        
        # 1. Entity-Community mapping
        entity_comm_data = []
        for entity, communities in self.entity_communities.items():
            entity_info = self.entities_df[self.entities_df['Name_Business'] == entity]
            is_fraud = entity_info['FraudList'].iloc[0] if len(entity_info) > 0 else 0
            
            for comm_id in communities:
                entity_comm_data.append({
                    'entity_name': entity,
                    'community_id': comm_id,
                    'is_fraud': is_fraud
                })
        
        self.df_entity_communities = pd.DataFrame(entity_comm_data)
        
        # 2. Community members table
        comm_members_data = []
        for comm_id, members in self.communities.items():
            for member in members:
                entity_info = self.entities_df[self.entities_df['Name_Business'] == member]
                is_fraud = entity_info['FraudList'].iloc[0] if len(entity_info) > 0 else 0
                
                comm_members_data.append({
                    'community_id': comm_id,
                    'entity_name': member,
                    'is_fraud': is_fraud
                })
        
        self.df_community_members = pd.DataFrame(comm_members_data)
        
        # 3. Entity connections (FIXED: no duplicates or self-connections)
        connection_data = []
        processed_pairs = set()
        
        for entity in self.entities_df['Name_Business']:
            if entity not in self.network:
                continue
                
            neighbors = list(self.network.neighbors(entity))
            
            for neighbor in neighbors:
                # Skip self-connections - double check
                if entity == neighbor or entity.strip() == neighbor.strip():
                    continue
                
                # Create ordered pair to avoid duplicates
                pair = tuple(sorted([entity, neighbor]))
                if pair in processed_pairs:
                    continue
                processed_pairs.add(pair)
                
                # Get shared claims
                entity_claims = set(self.extracted_entities[
                    self.extracted_entities['Entity'] == entity
                ]['ClaimNumber'])
                
                neighbor_claims = set(self.extracted_entities[
                    self.extracted_entities['Entity'] == neighbor
                ]['ClaimNumber'])
                
                shared_claims = entity_claims.intersection(neighbor_claims)
                
                # Get max fraud score from shared claims
                if len(shared_claims) > 0:
                    max_fraud_score = self.external_fraud_scores[
                        self.external_fraud_scores['claim_number'].isin(shared_claims)
                    ]['external_fraud_score'].max()
                else:
                    max_fraud_score = 0
                
                # Double-check to ensure no self-connections
                if entity != neighbor:
                    connection_data.append({
                        'source_entity': entity,
                        'target_entity': neighbor,
                        'connection_strength': self.network[entity][neighbor]['weight'],
                        'shared_claim_numbers': ', '.join(sorted(shared_claims)),
                        'target_is_confirmed_fraud': neighbor in self.fraud_entities,
                        'max_shared_claim_fraud_score': max_fraud_score
                    })
        
        self.df_entity_connections = pd.DataFrame(connection_data)
        
        # 4. Entity claims
        entity_claims_data = []
        for entity in self.entities_df['Name_Business']:
            entity_claim_numbers = self.extracted_entities[
                self.extracted_entities['Entity'] == entity
            ]['ClaimNumber'].unique()
            
            for claim_num in entity_claim_numbers:
                # Get external fraud score
                ext_score_row = self.external_fraud_scores[
                    self.external_fraud_scores['claim_number'] == claim_num
                ]
                ext_score = ext_score_row['external_fraud_score'].iloc[0] if len(ext_score_row) > 0 else 0
                
                # Get financial info
                financial_row = self.claim_financials[
                    self.claim_financials['claim_number'] == claim_num
                ]
                total_incurred = financial_row['total_incurred'].iloc[0] if len(financial_row) > 0 else 0
                
                # Get other entities on claim
                other_entities = self.extracted_entities[
                    (self.extracted_entities['ClaimNumber'] == claim_num) &
                    (self.extracted_entities['Entity'] != entity)
                ]['Entity'].unique()
                
                entity_claims_data.append({
                    'entity_name': entity,
                    'claim_number': claim_num,
                    'external_fraud_score': ext_score,
                    'total_incurred': total_incurred,
                    'other_entities_on_claim': ', '.join(other_entities)
                })
        
        self.df_entity_claims = pd.DataFrame(entity_claims_data)
        
        # 5. Entity fraud rules
        entity_rules_data = []
        for entity in self.entities_df['Name_Business']:
            entity_claim_numbers = self.extracted_entities[
                self.extracted_entities['Entity'] == entity
            ]['ClaimNumber'].unique()
            
            # Get all rules for this entity's claims
            entity_rules = self.claim_fraud_rules[
                self.claim_fraud_rules['claim_number'].isin(entity_claim_numbers)
            ]
            
            # Group by rule to combine claim numbers
            for rule_no in entity_rules['rule_no'].unique():
                rule_rows = entity_rules[entity_rules['rule_no'] == rule_no]
                
                entity_rules_data.append({
                    'entity_name': entity,
                    'rule_no': rule_no,
                    'rule_desc': rule_rows['rule_desc'].iloc[0],
                    'priority': rule_rows['priority'].iloc[0],
                    'value': rule_rows['value'].iloc[0],
                    'claim_numbers': ', '.join(rule_rows['claim_number'].unique())
                })
        
        self.df_entity_fraud_rules = pd.DataFrame(entity_rules_data)
        
        logger.info("All dashboard DataFrames generated")
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        
        logger.info("Starting full fraud detection analysis...")
        
        # Step 1: Create dataset
        self.create_dataset()
        
        # Step 2: Extract entities
        self.extract_entities_ner()
        
        # Step 3: Build network
        self.build_network()
        
        # Step 4: Detect overlapping communities
        self.detect_overlapping_communities()
        
        # Step 5: Calculate node importance
        self.calculate_node_importance()
        
        # Step 6: Load external data
        self.load_external_data()
        
        # Step 7: Aggregate entity metrics
        self.aggregate_entity_metrics()
        
        # Step 8: Generate dashboard DataFrames
        self.generate_dashboard_dataframes()
        
        logger.info("Analysis complete!")
        
        return {
            'entity_dashboard': self.df_entity_dashboard,
            'entity_communities': self.df_entity_communities,
            'community_members': self.df_community_members,
            'entity_connections': self.df_entity_connections,
            'entity_claims': self.df_entity_claims,
            'entity_fraud_rules': self.df_entity_fraud_rules
        }
    
    def get_entity_details(self, entity_name):
        """Get all details for a specific entity"""
        
        if self.df_entity_dashboard is None:
            raise ValueError("Analysis not run yet. Call run_full_analysis() first.")
        
        entity_data = self.df_entity_dashboard[
            self.df_entity_dashboard['entity_name'] == entity_name
        ]
        
        if len(entity_data) == 0:
            return None
        
        communities = self.df_entity_communities[
            self.df_entity_communities['entity_name'] == entity_name
        ]
        
        connections = self.df_entity_connections[
            (self.df_entity_connections['source_entity'] == entity_name) |
            (self.df_entity_connections['target_entity'] == entity_name)
        ]
        
        # Filter out any self-connections that might have slipped through
        connections = connections[
            connections['source_entity'] != connections['target_entity']
        ]
        
        claims = self.df_entity_claims[
            self.df_entity_claims['entity_name'] == entity_name
        ]
        
        rules = self.df_entity_fraud_rules[
            self.df_entity_fraud_rules['entity_name'] == entity_name
        ]
        
        return {
            'entity': entity_data.to_dict('records')[0],
            'communities': communities.to_dict('records'),
            'connections': connections.to_dict('records'),
            'claims': claims.to_dict('records'),
            'fraud_rules': rules.to_dict('records')
        }


if __name__ == "__main__":
    # Test the processor
    processor = FraudDetectionProcessor()
    results = processor.run_full_analysis()
    
    print("\nEntity Dashboard Sample:")
    print(results['entity_dashboard'].head())
    
    print("\nEntity Communities Sample:")
    print(results['entity_communities'].head())
    
    print("\nTest entity details:")
    details = processor.get_entity_details('Dr. Michael Rodriguez')
    if details:
        print(f"Entity: {details['entity']['entity_name']}")
        print(f"Ensemble Score: {details['entity']['ensemble_score']:.2f}")
        print(f"Communities: {len(details['communities'])}")
        print(f"Connections: {len(details['connections'])}")