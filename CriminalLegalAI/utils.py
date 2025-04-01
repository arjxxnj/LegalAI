import re
import random
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from ipc_data import ipc_sections
from precedents_data import legal_precedents
import os
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# Download necessary NLTK packages
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Download punkt_tab if needed
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Additional legal stop words
legal_stop_words = {
    'section', 'act', 'law', 'legal', 'court', 'criminal', 'case',
    'judge', 'prosecution', 'defense', 'plaintiff', 'defendant',
    'evidence', 'witness', 'testimony', 'jury', 'verdict', 'sentence',
    'appeal', 'hearing', 'trial', 'order', 'petition', 'ipc'
}

stop_words = stop_words.union(legal_stop_words)

def preprocess_text(text):
    """
    Preprocess text for NLP analysis:
    - Convert to lowercase
    - Remove special characters
    - Tokenize using simple split (avoiding NLTK issues)
    - Remove stopwords
    - Lemmatize
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Simple tokenization by splitting on whitespace
    tokens = text.split()
    
    # Remove stopwords and lemmatize
    processed_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    
    return processed_tokens

def extract_keywords(text, threshold=0.4):
    """
    Extract keywords from text for identifying relevant IPC sections
    and precedents
    """
    tokens = preprocess_text(text)
    # Return unique tokens
    return list(set(tokens))

def find_relevant_ipc_sections(keywords, case_details):
    """
    Find relevant IPC sections based on keywords and case details
    with improved contextual filtering and semantic understanding
    """
    import logging
    import re
    
    logging.info("Finding relevant IPC sections for case")
    relevant_sections = []
    
    # Extract detailed case information
    offense_description = case_details.get('offense_description', '').lower()
    query = case_details.get('query', '').lower()
    case_type = case_details.get('case_type', '').lower()
    victim_details = case_details.get('victim_details', '').lower()
    accused_details = case_details.get('accused_details', '').lower()
    evidence_summary = case_details.get('evidence_summary', '').lower()
    
    # Create a combined text for comprehensive context analysis
    combined_text = f"{case_type} {offense_description} {query} {victim_details} {accused_details} {evidence_summary}"
    logging.info(f"Case type: {case_type}")
    
    # Preprocess and tokenize text
    case_type_tokens = preprocess_text(case_type)
    offense_tokens = preprocess_text(offense_description)
    query_tokens = preprocess_text(query)
    
    # Combine all keywords for matching
    all_keywords = set(keywords + offense_tokens + case_type_tokens + query_tokens)
    logging.info(f"Total unique keywords for matching: {len(all_keywords)}")
    
    # ENHANCED CASE CATEGORIZATION - More detailed classification
    # Define crime categories with expanded keywords
    crime_categories = {
        'theft': ['theft', 'steal', 'stolen', 'took', 'take', 'taking', 'rob', 'robbed', 
                 'burglary', 'shoplifting', 'pickpocket', 'loot', 'misappropriation', 
                 'dishonest', 'removed', 'burglar', 'break-in', 'missing', 'lost', 'disappeared'],
        
        'robbery': ['robbery', 'armed', 'force', 'weapon', 'threat', 'gun', 'knife', 'intimidate',
                   'forceful', 'forcibly', 'snatched', 'mugging', 'mugged', 'dacoity'],
        
        'assault': ['assault', 'hurt', 'injure', 'attack', 'beat', 'hit', 'punch', 'slap', 
                   'wound', 'harm', 'injury', 'bodily', 'physical', 'violence', 'beaten', 
                   'bruise', 'fracture', 'bleeding', 'pain', 'fighting'],
        
        'sexual_offense': ['rape', 'sexual', 'molest', 'touch', 'modesty', 'obscene', 'expose', 
                          'indecent', 'harassment', 'outrage', 'eve teasing', 'non-consensual'],
        
        'fraud': ['fraud', 'cheat', 'deceive', 'dupe', 'swindle', 'misrepresentation', 
                 'dishonest', 'false', 'fake', 'pretend', 'impersonate', 'forge', 'scam', 
                 'trick', 'mislead', 'con', 'ponzi', 'scheme', 'duped', 'cheated'],
        
        'criminal_breach_of_trust': ['trust', 'misappropriate', 'breach', 'entrusted', 'fiduciary', 
                                   'betrayal', 'embezzle', 'misuse', 'company', 'employer'],
        
        'kidnapping': ['kidnap', 'abduct', 'forcibly', 'detain', 'confine', 'illegal', 'captive', 
                      'hostage', 'ransom', 'missing person', 'child abduction'],
        
        'murder': ['murder', 'kill', 'death', 'homicide', 'slay', 'fatal', 'deadly', 'lethal',
                  'died', 'deceased', 'body', 'corpse', 'blood', 'weapon'],
        
        'domestic_violence': ['domestic', 'spouse', 'wife', 'husband', 'marriage', 'dowry', 'cruelty', 
                             'matrimonial', 'in-laws', 'family', 'household', 'married', 'divorce'],
        
        'cybercrime': ['cyber', 'online', 'internet', 'computer', 'hacking', 'password', 'account', 
                       'data', 'social media', 'email', 'identity', 'phishing', 'website', 'profile'],
        
        'extortion': ['extortion', 'blackmail', 'ransom', 'demand', 'threaten', 'coerce', 'pay',
                     'intimidate', 'fear', 'consequences'],
        
        'defamation': ['defame', 'slander', 'libel', 'reputation', 'character', 'honor', 'dignity',
                      'false accusation', 'rumor', 'social media', 'post', 'image']
    }
    
    # Identify which crime categories apply to this case
    case_categories = []
    for category, category_keywords in crime_categories.items():
        if any(keyword in combined_text for keyword in category_keywords):
            case_categories.append(category)
    
    logging.info(f"Identified case categories: {case_categories}")
    
    # CONTEXTUAL SCENARIO DETECTION - Identify specific scenarios in the case
    # This significantly improves the accuracy of section matching
    scenarios = {
        'group_crime': re.search(r'\b(group|gang|multiple|several|many|crowd|together)\s+(people|persons|men|women|thieves|individuals|accused)\b', combined_text) is not None,
        
        'weapon_used': re.search(r'\b(gun|pistol|knife|blade|sword|stick|rod|bat|weapon|firearm|revolver|sharp|weapon)\b', combined_text) is not None,
        
        'violence_involved': any(term in combined_text for term in ['hurt', 'injured', 'beat', 'hit', 'attack', 'harm', 'wound', 'force', 'violent']),
        
        'night_time': re.search(r'\b(night|dark|midnight|evening|after sunset|late hours)\b', combined_text) is not None,
        
        'dwelling_house': re.search(r'\b(house|home|apartment|residence|flat|dwelling)\b', combined_text) is not None,
        
        'public_place': re.search(r'\b(public|street|road|market|mall|station|bus|train|shop|store|restaurant)\b', combined_text) is not None,
        
        'electronic_device': re.search(r'\b(phone|mobile|smartphone|laptop|computer|tablet|device|electronic)\b', combined_text) is not None,
        
        'valuable_property': re.search(r'\b(jewellery|gold|cash|money|valuable|watch|wallet|expensive|worth)\b', combined_text) is not None,
        
        'vehicle_involved': re.search(r'\b(car|bike|bicycle|motorcycle|scooter|auto|vehicle|transport)\b', combined_text) is not None,
        
        'intoxication': re.search(r'\b(drunk|alcohol|intoxicated|drink|liquor|beer|wine|drug)\b', combined_text) is not None,
        
        'repeat_offense': re.search(r'\b(previous|before|history|repeatedly|again|once more|already)\b', combined_text) is not None,
        
        'minor_involved': re.search(r'\b(child|minor|kid|young|underage|juvenile|below 18|teenager)\b', combined_text) is not None,
        
        'online_component': re.search(r'\b(online|internet|website|email|cyber|digital|electronic|virtual|web)\b', combined_text) is not None,
        
        'professional_relationship': re.search(r'\b(employee|employer|company|office|business|work|job|professional|workplace)\b', combined_text) is not None
    }
    
    # Log detected scenarios
    detected_scenarios = [scenario for scenario, is_present in scenarios.items() if is_present]
    logging.info(f"Detected scenarios: {detected_scenarios}")
    
    # ENHANCED KEYWORD IMPORTANCE - Assign weights to important terms
    important_keywords = {
        'theft': 3, 'robbery': 3, 'assault': 3, 'murder': 3, 'rape': 3, 'fraud': 3, 'kidnap': 3, 'abduct': 3,
        'hurt': 2, 'injury': 2, 'weapon': 2, 'force': 2, 'threat': 2, 'violence': 2, 'stolen': 2, 'attacked': 2,
        'property': 1, 'money': 1, 'valuable': 1, 'victim': 1, 'accused': 1, 'police': 1, 'report': 1, 'file': 1
    }
    
    # INTELLIGENCE MAPPING - Map certain case combinations to specific IPC sections
    priority_section_mapping = {
        'theft': ['ipc_378', 'ipc_379'],  # Basic theft
        'theft+dwelling_house': ['ipc_380'],  # Theft in dwelling house
        'theft+night_time': ['ipc_380'],  # Theft at night time
        'theft+violence_involved': ['ipc_392'],  # Robbery
        'theft+weapon_used': ['ipc_392', 'ipc_397'],  # Robbery with deadly weapon
        'theft+group_crime': ['ipc_391', 'ipc_395'],  # Dacoity
        'theft+electronic_device': ['ipc_378', 'ipc_379'],  # Mobile theft
        'theft+valuable_property': ['ipc_379'],  # Theft of property
        'theft+vehicle_involved': ['ipc_379'],  # Vehicle theft
        
        'assault': ['ipc_323'],  # Simple hurt
        'assault+weapon_used': ['ipc_324', 'ipc_326'],  # Hurt by dangerous weapon
        'assault+violence_involved': ['ipc_325'],  # Grievous hurt
        'assault+group_crime': ['ipc_147', 'ipc_148'],  # Rioting
        
        'fraud': ['ipc_415', 'ipc_420'],  # Cheating
        'fraud+professional_relationship': ['ipc_406', 'ipc_409'],  # Criminal breach of trust
        'fraud+online_component': ['ipc_468', 'ipc_471'],  # Forgery for cheating
        
        'sexual_offense': ['ipc_354', 'ipc_354A'],  # Outraging modesty
        'sexual_offense+minor_involved': ['ipc_376'],  # Rape of minor
        
        'domestic_violence': ['ipc_498A'],  # Cruelty by husband or relatives
        'kidnapping': ['ipc_363', 'ipc_365'],  # Kidnapping
        'murder': ['ipc_302', 'ipc_304'],  # Murder
        'extortion': ['ipc_383', 'ipc_384'],  # Extortion
        'defamation': ['ipc_499', 'ipc_500']  # Defamation
    }
    
    # PRIORITY SECTIONS IDENTIFICATION - Determine directly applicable sections
    priority_sections = []
    
    # Check for specific case+scenario combinations that directly map to certain sections
    for categories_combo, sections in priority_section_mapping.items():
        categories_split = categories_combo.split('+')
        
        # Check if main category matches
        if categories_split[0] in case_categories:
            # If there's a scenario component, check it too
            if len(categories_split) == 1:
                priority_sections.extend(sections)
                logging.info(f"Adding priority sections {sections} for category {categories_split[0]}")
            elif len(categories_split) == 2 and categories_split[1] in detected_scenarios:
                priority_sections.extend(sections)
                logging.info(f"Adding priority sections {sections} for {categories_combo}")
    
    # SCORING ALGORITHM - Enhanced relevance scoring
    # Evaluate each IPC section for relevance
    for section_id, section_data in ipc_sections.items():
        section_title = section_data['title'].lower()
        section_desc = section_data['description'].lower()
        section_combined = f"{section_title} {section_desc}"
        total_score = 0
        
        # Check if this is a priority section identified through direct mapping
        if section_id in priority_sections:
            total_score += 12  # Give high base score to mapped sections
            logging.info(f"Section {section_id} is a priority section, base score: 12")
        
        # Skip sections that clearly don't match the case categorization
        # If it's a pure theft case, skip sexual offense sections
        if 'theft' in case_categories and not 'sexual_offense' in case_categories:
            if any(term in section_title for term in ['rape', 'modesty', 'sexual']):
                continue
                
        # If it's a pure assault case, skip specific theft sections
        if 'assault' in case_categories and not 'theft' in case_categories:
            if any(term in section_title for term in ['theft', 'robbery']) and not 'hurt' in section_title:
                continue
        
        # Calculate keyword matching score with weighting
        section_keywords = preprocess_text(section_combined)
        
        # Regular keyword matching
        basic_matches = sum(1 for keyword in all_keywords if keyword in section_keywords)
        
        # Weighted matching for important keywords
        weighted_matches = sum(important_keywords.get(keyword, 1) 
                              for keyword in all_keywords 
                              if keyword in section_keywords and keyword in important_keywords)
        
        # Title matching - higher weight for matches in the section title
        title_keywords = preprocess_text(section_title)
        title_matches = sum(3 for keyword in case_type_tokens if keyword in title_keywords)
        
        # Number matching - important for scenarios where section numbers are mentioned
        section_number = section_data.get('number', '')
        if section_number and section_number in combined_text:
            total_score += 10
            logging.info(f"Section number {section_number} explicitly mentioned, adding 10 points")
        
        # Add weighted scores
        total_score += basic_matches + weighted_matches + title_matches
        
        # CONTEXT-SPECIFIC BOOSTING - Add scores based on specific conditions
        
        # Exact case type match (strong indicator)
        if case_type in section_title:
            total_score += 8
            logging.info(f"Exact case type match for section {section_id}, adding 8 points")
        
        # Scenario-based section boosting
        if 'group_crime' in detected_scenarios and ('unlawful assembly' in section_combined or 
                                                   'common intention' in section_combined or 
                                                   'conspiracy' in section_combined or
                                                   'more than five persons' in section_combined):
            total_score += 5
            logging.info(f"Group crime match for section {section_id}, adding 5 points")
            
        if 'weapon_used' in detected_scenarios and ('weapon' in section_combined or 
                                                   'armed' in section_combined or 
                                                   'dangerous' in section_combined):
            total_score += 5
            logging.info(f"Weapon involved match for section {section_id}, adding 5 points")
        
        if 'violence_involved' in detected_scenarios and ('hurt' in section_combined or 
                                                         'injury' in section_combined or 
                                                         'assault' in section_combined):
            total_score += 4
            logging.info(f"Violence match for section {section_id}, adding 4 points")
        
        if 'night_time' in detected_scenarios and 'night' in section_combined:
            total_score += 3
            logging.info(f"Night time match for section {section_id}, adding 3 points")
        
        if 'dwelling_house' in detected_scenarios and ('house' in section_combined or 
                                                     'dwelling' in section_combined or 
                                                     'building' in section_combined):
            total_score += 3
            logging.info(f"Dwelling house match for section {section_id}, adding 3 points")
        
        # SPECIAL CASE HANDLING - Category-specific optimizations
        if 'theft' in case_categories:
            # For basic theft cases, prioritize foundational theft sections
            if section_id in ['ipc_378', 'ipc_379']:
                total_score += 4
                logging.info(f"Basic theft section {section_id}, adding 4 points")
            
            # For thefts with force, boost robbery sections
            if scenarios['violence_involved'] and section_id in ['ipc_390', 'ipc_392']:
                total_score += 5
                logging.info(f"Theft with violence match for section {section_id}, adding 5 points")
                
            # For house break-ins, boost house trespass sections
            if scenarios['dwelling_house'] and section_id in ['ipc_380', 'ipc_454', 'ipc_457']:
                total_score += 5
                logging.info(f"House theft match for section {section_id}, adding 5 points")
        
        if 'assault' in case_categories:
            # Distinguish between simple and grievous hurt
            if 'simple hurt' in section_title and not scenarios['weapon_used']:
                total_score += 3
                logging.info(f"Simple hurt match for section {section_id}, adding 3 points")
                
            if 'grievous hurt' in section_title and (scenarios['weapon_used'] or scenarios['violence_involved']):
                total_score += 5
                logging.info(f"Grievous hurt match for section {section_id}, adding 5 points")
        
        # Filter sections with sufficient relevance
        if total_score >= 3:
            relevant_sections.append({
                'id': section_id,
                'score': total_score
            })
            logging.info(f"Added section {section_id} with score {total_score}")
    
    # Sort by relevance score
    relevant_sections.sort(key=lambda x: x['score'], reverse=True)
    
    # Log the top sections found
    top_sections = [section['id'] for section in relevant_sections[:5]]
    logging.info(f"Top 5 selected sections: {top_sections}")
    
    # Return top 5 most relevant section IDs
    return top_sections

def find_relevant_precedents(ipc_section_ids, keywords):
    """
    Find relevant legal precedents based on IPC sections and keywords
    with enhanced matching for better accuracy
    """
    import logging
    relevant_precedents = []
    
    logging.info(f"Finding relevant precedents based on {len(ipc_section_ids)} IPC sections and {len(keywords)} keywords")
    
    # Define important legal terms that should be weighted more heavily
    important_legal_terms = {
        'murder': 3, 'theft': 3, 'criminal': 3, 'robbery': 3, 'assault': 3, 
        'hurt': 2, 'sexual': 3, 'rape': 3, 'fraud': 3, 'cheating': 2,
        'breach': 2, 'trust': 2, 'dishonest': 2, 'intention': 2, 'consent': 2,
        'defamation': 3, 'criminal force': 3, 'kidnapping': 3, 'abduction': 3,
        'forgery': 3, 'extortion': 3, 'blackmail': 3
    }
    
    # Extract case-specific terms from keywords for better matching
    case_specific_terms = [kw for kw in keywords if len(kw) > 3]  # Filter out very short terms
    
    # Track precedents by section importance
    section_matched_precedents = {}
    
    # First, find precedents directly related to the IPC sections
    for precedent_id, precedent_data in legal_precedents.items():
        # Section matching score - more weight for exact matches
        section_match_score = 0
        related_sections = precedent_data.get('related_sections', [])
        
        # Check for direct section matches
        for section_id in ipc_section_ids:
            if section_id in related_sections:
                section_match_score += 5  # Base score for direct section match
                logging.info(f"Precedent {precedent_id} matches section {section_id}")
                
                # Group precedents by section for later retrieval
                if section_id not in section_matched_precedents:
                    section_matched_precedents[section_id] = []
                section_matched_precedents[section_id].append(precedent_id)
        
        # Skip precedents with no section matches (unlike previous implementation)
        if section_match_score == 0:
            continue
        
        # Calculate relevance based on improved keyword matching
        precedent_text = precedent_data.get('summary', '') + ' ' + precedent_data.get('implications', '')
        precedent_keywords = preprocess_text(precedent_text)
        
        # Basic keyword matching
        basic_matches = sum(1 for keyword in keywords if keyword in precedent_keywords)
        
        # Weighted matching for important legal terms
        weighted_matches = sum(important_legal_terms.get(keyword, 1) 
                              for keyword in keywords 
                              if keyword in precedent_keywords and keyword in important_legal_terms)
        
        # Case-specific term matching (more weight)
        case_specific_matches = sum(2 for term in case_specific_terms if term in precedent_keywords)
        
        # Calculate year recency factor (more recent cases get slightly higher scores)
        year = precedent_data.get('year', 2000)
        recency_factor = min(1.5, max(1.0, (year - 1950) / 50))  # 1.0 to 1.5 based on year
        
        # Supreme Court decisions get higher weight
        court_weight = 1.5 if 'supreme' in precedent_data.get('court', '').lower() else 1.0
        
        # Calculate final relevance score
        relevance = (section_match_score + basic_matches + weighted_matches + case_specific_matches) * recency_factor * court_weight
        
        if relevance > 0:
            logging.info(f"Precedent {precedent_id} relevance score: {relevance}")
            relevant_precedents.append({
                'id': precedent_id,
                'relevance': relevance,
                'data': precedent_data
            })
    
    # If we have too few precedents, try to add more based on keywords
    if len(relevant_precedents) < 2:
        logging.info("Found fewer than 2 precedents with section matches, adding keyword-based matches")
        for precedent_id, precedent_data in legal_precedents.items():
            # Skip precedents we've already added
            if any(p['id'] == precedent_id for p in relevant_precedents):
                continue
            
            # Match purely on keywords for backup precedents
            precedent_text = precedent_data.get('summary', '') + ' ' + precedent_data.get('implications', '')
            precedent_keywords = preprocess_text(precedent_text)
            
            # More aggressive keyword matching
            basic_matches = sum(1 for keyword in keywords if keyword in precedent_keywords)
            weighted_matches = sum(important_legal_terms.get(keyword, 1) 
                                  for keyword in keywords 
                                  if keyword in precedent_keywords and keyword in important_legal_terms)
            
            relevance = basic_matches + weighted_matches
            
            if relevance >= 3:  # Higher threshold for keyword-only matches
                logging.info(f"Added keyword-only precedent {precedent_id} with score {relevance}")
                relevant_precedents.append({
                    'id': precedent_id,
                    'relevance': relevance * 0.7,  # Lower weight than section matches
                    'data': precedent_data
                })
    
    # Ensure diversity of precedents - try to include at least one precedent from each matched section
    if len(relevant_precedents) < 3 and section_matched_precedents:
        logging.info("Ensuring precedent diversity by section")
        
        # Get current precedent IDs
        current_ids = [p['id'] for p in relevant_precedents]
        
        # Try to add one precedent from each section not already represented
        for section_id, precedent_ids in section_matched_precedents.items():
            if len(relevant_precedents) >= 3:
                break
                
            # Find a precedent from this section that isn't already included
            for pid in precedent_ids:
                if pid not in current_ids:
                    precedent_data = legal_precedents.get(pid)
                    if precedent_data:
                        logging.info(f"Adding diverse precedent {pid} from section {section_id}")
                        relevant_precedents.append({
                            'id': pid,
                            'relevance': 1.0,  # Baseline relevance
                            'data': precedent_data
                        })
                        current_ids.append(pid)
                        break
    
    # Sort by relevance
    relevant_precedents.sort(key=lambda x: x['relevance'], reverse=True)
    
    # Get top precedents, ensuring we include at least one Supreme Court case if available
    top_precedents = []
    added_supreme = False
    
    # First, check if there's a Supreme Court case in the top 3
    for p in relevant_precedents[:3]:
        if 'supreme' in p['data'].get('court', '').lower():
            added_supreme = True
            break
    
    # If no Supreme Court case in top 3, try to include one
    if not added_supreme and len(relevant_precedents) > 3:
        for p in relevant_precedents[3:]:
            if 'supreme' in p['data'].get('court', '').lower():
                # Replace the third precedent with this Supreme Court case
                top_precedents = [p['id'] for p in relevant_precedents[:2]]
                top_precedents.append(p['id'])
                logging.info(f"Added Supreme Court precedent {p['id']} for diversity")
                break
    
    # If we didn't do the Supreme Court replacement, use the standard top 3
    if not top_precedents:
        top_precedents = [p['id'] for p in relevant_precedents[:3]]
    
    logging.info(f"Selected precedents: {top_precedents}")
    return top_precedents

def generate_legal_analysis(case_details, ipc_section_ids, precedent_ids):
    """
    Generate a legal analysis based on case details, relevant IPC sections,
    and legal precedents with balanced terminology that's understandable.
    Uses Gemini API if available, otherwise falls back to template-based generation.
    """
    # Check if Gemini API is available and configured
    if GEMINI_API_KEY and 'gemini_model' in globals():
        return generate_gemini_analysis(case_details, ipc_section_ids, precedent_ids)
    
    # Fall back to template-based generation if Gemini is not available
    return generate_template_analysis(case_details, ipc_section_ids, precedent_ids)

def generate_gemini_analysis(case_details, ipc_section_ids, precedent_ids):
    """
    Generate a legal analysis using Google's Gemini AI based on case details, 
    relevant IPC sections, and legal precedents.
    """
    # Get case type and details for personalization
    case_type = case_details['case_type'].lower()
    location = case_details['incident_location']
    date = case_details['incident_date']
    query = case_details.get('query', '').lower()
    offense_description = case_details.get('offense_description', '')
    accused_details = case_details.get('accused_details', '')
    victim_details = case_details.get('victim_details', '')
    evidence_summary = case_details.get('evidence_summary', '')
    
    # Format IPC sections data
    ipc_sections_data = []
    for section_id in ipc_section_ids:
        section = ipc_sections.get(section_id)
        if section:
            ipc_sections_data.append({
                'number': section['number'],
                'title': section['title'],
                'description': section['description'],
                'punishment': section['punishment']
            })
    
    # Format precedents data
    precedents_data = []
    for precedent_id in precedent_ids:
        precedent = legal_precedents.get(precedent_id)
        if precedent:
            precedents_data.append({
                'case_name': precedent['case_name'],
                'citation': precedent['citation'],
                'court': precedent['court'],
                'year': precedent['year'],
                'summary': precedent['summary'],
                'implications': precedent['implications']
            })
    
    # Format the prompt for Gemini with significantly enhanced instructions
    prompt = f"""
    You are an expert legal assistant specializing in Indian criminal law with over 20 years of experience. You need to create a detailed legal analysis for a client based on their specific case details and relevant legal information.
    
    Please provide an extremely personalized, conversational analysis that balances legal terminology with accessible explanations. Your response should feel custom-written for this specific situation, not generic legal advice. Make precise connections between the case details and the relevant laws.
    
    Format your response in clean HTML with headers, paragraphs, and lists for readability.
    
    CASE DETAILS:
    - Case Type: {case_type}
    - Incident Location: {location}
    - Incident Date: {date}
    - Client's Query: {query}
    - Offense Description: {offense_description}
    - Accused Details: {accused_details}
    - Victim Details: {victim_details}
    - Evidence Summary: {evidence_summary}
    
    RELEVANT INDIAN PENAL CODE (IPC) SECTIONS:
    {ipc_sections_data}
    
    RELEVANT LEGAL PRECEDENTS:
    {precedents_data}
    
    ANALYSIS STRUCTURE:
    1. TITLE: Create a specific, personalized title directly relevant to this exact case (e.g., "Analysis of Your Mobile Phone Theft at MG Road Metro Station" rather than "Mobile Theft Case Analysis").
    
    2. INTRODUCTION: Write a warm, empathetic introduction that:
       - References specific case details and circumstances
       - Acknowledges the client's concerns 
       - Establishes a connection by showing you understand their unique situation
       - Briefly outlines what your analysis will cover
    
    3. APPLICABLE LAW: Explain the relevant IPC sections with:
       - Clear explanations of how each section directly relates to this specific case
       - Analysis of how the case details satisfy or don't satisfy specific elements of each offense
       - A breakdown of potential charges based on the specific circumstances
       - Discussion of potential defenses if relevant
    
    4. PRECEDENT ANALYSIS: Discuss the legal precedents by:
       - Explaining how each precedent relates specifically to the client's situation
       - Highlighting similarities and differences between the precedent cases and the current case
       - Drawing concrete implications for how courts might view this specific case
       - Using these precedents to support your legal reasoning
    
    5. PRACTICAL GUIDANCE: Provide detailed next steps including:
       - Specific documentation needed for this particular case
       - Where and how to file reports or complaints
       - Expected timeline for this type of case in the specific jurisdiction
       - Preparation needed for potential legal proceedings
       - Any evidence gathering steps specific to this case type
    
    6. BRIEF DISCLAIMER: Include a concise disclaimer about the nature of this advice.
    
    IMPORTANT STYLE GUIDELINES:
    - Use natural, conversational language that reads like a human expert wrote it
    - Refer to specific details from the case throughout your analysis
    - Avoid generic language that could apply to any similar case
    - Use varied sentence structures and diverse vocabulary
    - Balance formal legal terminology with clear explanations
    - Use "you" and "your" to directly address the client
    - Include specific examples and scenarios relevant to the case details
    - Make connections between legal concepts and the client's specific situation
    - Maintain a supportive, informative tone throughout
    
    This analysis should feel like it was prepared by an experienced legal professional who has thoroughly reviewed the specific case and is providing thoughtful, customized guidance.
    """
    
    try:
        # Generate analysis using Gemini
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating analysis with Gemini: {str(e)}")
        # Fall back to template-based generation if Gemini fails
        return generate_template_analysis(case_details, ipc_section_ids, precedent_ids)

def generate_template_analysis(case_details, ipc_section_ids, precedent_ids):
    """
    Generate a legal analysis based on case details, relevant IPC sections,
    and legal precedents using templates when Gemini is not available.
    """
    analysis = []
    import random
    
    # Get case type and details for personalization 
    case_type = case_details['case_type'].lower()
    location = case_details['incident_location']
    date = case_details['incident_date']
    query = case_details.get('query', '').lower()
    offense_description = case_details.get('offense_description', '').lower()
    accused_details = case_details.get('accused_details', '')
    victim_details = case_details.get('victim_details', '')
    evidence_summary = case_details.get('evidence_summary', '')
    
    # Extract specific items, locations, or circumstances from the descriptions for personalization
    specific_details = {}
    
    # Look for smartphone/phone details
    phone_match = re.search(r'(smartphone|phone|mobile|cell phone|iphone|samsung|galaxy|pixel|oneplus|mi|redmi|vivo|oppo)(\s+\w+)?\s+(s\d+|note\s*\d+|\d+|pro|max|ultra)', offense_description, re.I)
    if phone_match:
        specific_details['phone_model'] = phone_match.group(0)
    elif 'phone' in offense_description or 'mobile' in offense_description:
        specific_details['phone_model'] = 'phone'
    
    # Look for other electronic devices
    device_match = re.search(r'(laptop|computer|tablet|ipad|macbook|camera|smartwatch|watch|airpods|headphones|tv|console)', offense_description, re.I)
    if device_match:
        specific_details['device'] = device_match.group(0)
    
    # Look for vehicle details
    vehicle_match = re.search(r'(car|bike|motorcycle|scooter|bicycle|auto|truck|van)(\s+\w+)?', offense_description, re.I)
    if vehicle_match:
        specific_details['vehicle'] = vehicle_match.group(0)
    
    # Look for jewelry/valuables
    valuables_match = re.search(r'(jewelry|gold|silver|diamond|necklace|ring|bracelet|chain|watch|purse|wallet|cash|money|bag|handbag|backpack)', offense_description, re.I)
    if valuables_match:
        specific_details['valuables'] = valuables_match.group(0)
    
    # Look for specific locations
    location_match = re.search(r'(mall|shop|store|market|restaurant|hotel|house|apartment|office|building|street|road|park|station|bus|train|metro|theater|cinema|hospital|bank|atm|school|college)', offense_description, re.I)
    if location_match:
        specific_details['specific_location'] = location_match.group(0)
    
    # Look for time references
    time_match = re.search(r'(morning|afternoon|evening|night|midnight|dawn|dusk|(\d{1,2}\s*(am|pm|o\'clock)))', offense_description, re.I)
    if time_match:
        specific_details['time_of_day'] = time_match.group(0)
    
    # Extract IMEI or identification numbers if mentioned
    id_match = re.search(r'(imei|serial number|identification number|id number)', offense_description, re.I)
    if id_match:
        specific_details['has_id_number'] = True
    
    # Extract when they noticed the theft/incident
    notice_match = re.search(r'noticed|realized|found out|discovered.{1,30}(after|later|missing)', offense_description, re.I)
    if notice_match:
        specific_details['delayed_discovery'] = True
    
    # Analysis of injuries for assault cases
    injury_match = re.search(r'(injur(y|ies|ed)|hurt|wound|bruise|cut|bleeding|pain|hospital|doctor|medical)', offense_description, re.I)
    if injury_match:
        specific_details['has_injuries'] = True
    
    # Determine distinctive case patterns for personalized responses
    is_violent_case = any(word in query for word in ["hit", "beat", "attack", "hurt", "injure", "wound", "punch", "assault", "slap", "fight", "violence"])
    is_theft_case = any(word in query for word in ["steal", "theft", "stole", "took", "robbed", "shoplifting", "missing", "burglar", "snatch", "pickpocket"])
    is_fraud_case = any(word in query for word in ["fraud", "cheat", "deceive", "scam", "fake", "false", "misled", "lied", "trick", "ponzi", "scheme"])
    is_harassment_case = any(word in query for word in ["harass", "stalk", "follow", "threat", "intimidate", "scare", "fear", "message", "call", "verbal"])
    is_sexual_case = any(word in query for word in ["rape", "molest", "touch", "sexual", "modesty", "consent", "force", "inappropriate", "harass", "eve teasing"])
    is_dowry_case = any(word in query for word in ["dowry", "bride", "marriage", "husband", "wife", "in-law", "gift", "demand", "harassment", "matrimonial"])
    
    # Dynamic title based on case type
    title_variations = {
        "theft": ["Analysis of Your Theft Case", "Understanding Your Property Theft Situation", "Legal Perspective on Your Stolen Property Case"],
        "robbery": ["Breaking Down Your Robbery Case", "Analysis of Your Armed Theft Situation", "Understanding the Legal Aspects of Your Robbery"],
        "assault": ["Examining Your Assault Case", "Legal Analysis of Your Physical Altercation", "Understanding Your Assault Incident"],
        "rape": ["Legal Assessment of Your Sexual Violence Case", "Understanding Your Sexual Assault Report", "Analysis of Your Reported Sexual Violence"],
        "fraud": ["Evaluating Your Fraud Complaint", "Analysis of Your Financial Deception Case", "Breaking Down Your Cheating/Fraud Report"],
        "harassment": ["Understanding Your Harassment Situation", "Legal Analysis of Reported Harassment", "Examining Your Intimidation Case"],
        "domestic violence": ["Assessment of Your Domestic Violence Report", "Analysis of Your Family Violence Situation", "Understanding Your Household Dispute"],
        "cheating": ["Examining Your Fraud/Cheating Case", "Legal Analysis of Your Deception Complaint", "Understanding Your Financial Fraud Case"]
    }
    
    # Choose appropriate title
    if any(key in case_type for key in title_variations.keys()):
        for key in title_variations.keys():
            if key in case_type:
                title = random.choice(title_variations[key])
                break
    else:
        title = f"Legal Analysis: {case_details['case_type'].title()} Case"
    
    # Add the title
    analysis.append(f"<h2>{title}</h2>")
    
    # Create personalized case summary section based on case type
    
    # Different heading styles based on case type
    summary_headings = {
        "theft": ["Your Case at a Glance", "Property Theft Overview", "Understanding What Happened"],
        "assault": ["Incident Assessment", "Understanding the Confrontation", "Violence Incident Overview"],
        "fraud": ["Fraud Case Overview", "Understanding the Deception", "Examining the Financial Fraud"],
        "sexual": ["Analyzing the Reported Incident", "Case Assessment", "Understanding the Situation"],
        "default": ["Case Summary", "Understanding Your Situation", "Overview of the Incident"]
    }
    
    # Choose appropriate heading
    if is_theft_case:
        heading = random.choice(summary_headings["theft"])
    elif is_violent_case:
        heading = random.choice(summary_headings["assault"])
    elif is_fraud_case:
        heading = random.choice(summary_headings["fraud"])
    elif is_sexual_case:
        heading = random.choice(summary_headings["sexual"])
    else:
        heading = random.choice(summary_headings["default"])
    
    analysis.append(f"\n<h3>{heading}</h3>")
    
    # Personalized case intro based on case type
    if is_theft_case:
        # Create highly specific theft intro based on extracted details
        stolen_item = ""
        location_detail = ""
        time_detail = ""
        discovery_detail = ""
        evidence_detail = ""
        
        # Determine what was stolen
        if 'phone_model' in specific_details:
            stolen_item = f"your {specific_details['phone_model']}"
        elif 'device' in specific_details:
            stolen_item = f"your {specific_details['device']}"
        elif 'vehicle' in specific_details:
            stolen_item = f"your {specific_details['vehicle']}"
        elif 'valuables' in specific_details:
            stolen_item = f"your {specific_details['valuables']}"
        else:
            stolen_item = "your property"
        
        # Specific location within the main location
        if 'specific_location' in specific_details:
            location_detail = f" specifically in the {specific_details['specific_location']} area,"
        
        # Time of day detail
        if 'time_of_day' in specific_details:
            time_detail = f" during the {specific_details['time_of_day']},"
        
        # How they discovered the theft
        discovery_phrase = ""
        if 'delayed_discovery' in specific_details:
            discovery_options = [
                "only realizing it was missing later",
                "not immediately noticing it was gone",
                "discovering it was missing after some time had passed",
                "noticing it was missing when you tried to use it later"
            ]
            discovery_phrase = random.choice(discovery_options)
            discovery_detail = f" and {discovery_phrase}"
        
        # Evidence they mentioned
        if 'has_id_number' in specific_details:
            evidence_options = [
                "Having the IMEI or identification number will be helpful for reporting and potentially tracking the device.",
                "The IMEI/identification number you mentioned will be important for the police report and possible recovery.",
                "Your foresight in having the identification number ready is valuable for the investigation process."
            ]
            evidence_detail = f" {random.choice(evidence_options)}"
        elif evidence_summary and 'cctv' in evidence_summary.lower():
            evidence_options = [
                "The potential CCTV footage you mentioned could be crucial evidence in identifying the perpetrator.",
                "Securing the CCTV footage from the location should be a priority, as it may capture the incident.",
                "The surveillance footage you referenced could provide valuable evidence for your case."
            ]
            evidence_detail = f" {random.choice(evidence_options)}"
        
        # Construct personalized theft intros
        theft_intros = [
            f"<p>I've examined your report about the theft of {stolen_item} that occurred at {location}{location_detail} on {date}{time_detail}{discovery_detail}. This appears to be a case of property being taken without your consent, which is defined as theft under Indian law.{evidence_detail}</p>",
            
            f"<p>I understand that {stolen_item} was stolen while you were at {location}{location_detail} on {date}{discovery_detail}. This is understandably distressing, and I want to help you understand your legal options and the potential for recovery.{evidence_detail}</p>",
            
            f"<p>Thank you for sharing the details about {stolen_item} being stolen from {location} on {date}{time_detail}{discovery_detail}. I've analyzed your case carefully and can offer guidance on how Indian law addresses this type of theft situation and what steps you can take next.{evidence_detail}</p>"
        ]
        analysis.append(random.choice(theft_intros))
        
    elif is_violent_case:
        violent_intros = [
            f"<p>I've carefully reviewed the details of the physical altercation that occurred at {location} on {date}. Violence cases like this are taken seriously under Indian law, and there are specific provisions that may apply to your situation.</p>",
            
            f"<p>I understand you were involved in a physical confrontation at {location} on {date}. This must have been traumatic, and I want to help you understand how the law views this incident and what protections are available to you.</p>",
            
            f"<p>Thank you for providing information about the assault incident at {location}. Based on what you've shared, I can see several legal aspects that need to be addressed to ensure justice in your case.</p>"
        ]
        analysis.append(random.choice(violent_intros))
        
    elif is_fraud_case:
        fraud_intros = [
            f"<p>I've analyzed your report regarding the financial deception that occurred in relation to {location}. Fraud cases can be complex, but I'll help you understand how Indian law addresses situations where someone has been dishonestly misled.</p>",
            
            f"<p>I understand you've been the victim of financial deception or fraud related to {location}. This can be both financially and emotionally distressing. Let me help you understand the legal framework that protects people from such deceptive practices.</p>",
            
            f"<p>Thank you for sharing the details about being cheated or defrauded. Based on your description, there appear to be several legal violations that may provide you with recourse under Indian criminal law.</p>"
        ]
        analysis.append(random.choice(fraud_intros))
        
    elif is_sexual_case:
        sexual_intros = [
            f"<p>I've carefully reviewed your report about the incident at {location}. Sexual violence and harassment cases are treated with utmost seriousness under Indian law, and there are specific protections in place for survivors.</p>",
            
            f"<p>I understand you've experienced a traumatic incident related to sexual misconduct. First, I want to acknowledge your courage in seeking information about your legal options. The Indian legal system has several provisions specifically designed to address these situations.</p>",
            
            f"<p>Thank you for sharing details about this sensitive matter. Based on what you've described, there are several legal provisions that may apply to your case, and I want to help you understand your rights and options.</p>"
        ]
        analysis.append(random.choice(sexual_intros))
        
    elif is_harassment_case:
        harassment_intros = [
            f"<p>I've analyzed your report about the harassment situation that's been occurring. Harassment and intimidation are recognized offenses under Indian law, and there are legal remedies available to address this conduct.</p>",
            
            f"<p>I understand you've been experiencing harassment or intimidation. This can be extremely distressing, and it's important you know that Indian law provides protections against such behavior. Let me explain the relevant legal framework.</p>",
            
            f"<p>Thank you for sharing details about the harassment you've faced. Based on your description, there appear to be several legal provisions that could help address this situation and provide you with protection.</p>"
        ]
        analysis.append(random.choice(harassment_intros))
        
    elif is_dowry_case:
        dowry_intros = [
            f"<p>I've carefully reviewed your report regarding matrimonial issues and possible dowry-related harassment. The Indian legal system has strong provisions against dowry demands and related cruelty within marriages.</p>",
            
            f"<p>I understand you're facing challenges related to marriage and possible dowry demands or harassment. These situations are specifically addressed in Indian law with serious consequences for offenders. Let me explain the relevant protections.</p>",
            
            f"<p>Thank you for sharing details about the matrimonial difficulties you're experiencing. Based on what you've described, there are specific legal provisions designed to protect individuals from dowry-related harassment and cruelty.</p>"
        ]
        analysis.append(random.choice(dowry_intros))
        
    else:
        general_intros = [
            f"<p>I've examined the details of the {case_details['case_type']} incident that happened at {location} on {date}. Based on your description, I can provide some insights on how Indian law applies to this situation.</p>",
            
            f"<p>Thank you for sharing information about what happened at {location}. I've analyzed your {case_details['case_type']} case and can help you understand the legal framework that applies to this type of situation.</p>",
            
            f"<p>Based on the {case_details['case_type']} incident you've described at {location}, I can offer some guidance on the legal aspects and potential next steps in your case.</p>"
        ]
        analysis.append(random.choice(general_intros))
    
    # Add a personalized bridge to the laws section
    bridge_to_laws = [
        f"<p>Let's look at the specific laws that apply to your situation:</p>",
        f"<p>Based on your description, here are the relevant sections of Indian law that address this type of case:</p>",
        f"<p>The Indian Penal Code includes several provisions that are directly relevant to what you've described:</p>",
        f"<p>To understand your legal position better, let's examine the specific laws that apply:</p>",
        f"<p>Your case likely falls under the following legal provisions in the Indian Penal Code:</p>"
    ]
    analysis.append(random.choice(bridge_to_laws))
    
    # Relevant IPC Sections with more conversational explanations
    analysis.append("\n<h3>Relevant Laws (Indian Penal Code)</h3>")
    
    if not ipc_section_ids:
        no_laws_found = [
            "<p>Based on the information provided, I can't pinpoint specific IPC sections that directly apply to your situation. To give you more accurate guidance, I would need additional details about what exactly happened, who was involved, and the nature of the incident.</p>",
            
            "<p>I don't have enough information yet to identify which specific laws apply to your case. If you could share more details about the incident—such as what exactly happened, how it occurred, who was involved, and what harm was caused—I could provide more precise legal guidance.</p>",
            
            "<p>The details you've provided don't clearly match specific IPC sections in a way that allows me to give definitive legal guidance. To better assist you, consider sharing more specific information about the incident, including actions taken, intentions, and outcomes.</p>"
        ]
        analysis.append(random.choice(no_laws_found))
    else:
        for i, section_id in enumerate(ipc_section_ids):
            section = ipc_sections.get(section_id)
            if section:
                # First section gets a header format
                if i == 0:
                    primary_section_intros = [
                        f"<h4>Section {section['number']}: {section['title']} (Primary Applicable Law)</h4>",
                        f"<h4>Section {section['number']} - {section['title']} (Most Relevant to Your Case)</h4>",
                        f"<h4>IPC Section {section['number']}: {section['title']} (Key Legal Provision)</h4>"
                    ]
                    analysis.append(random.choice(primary_section_intros))
                # Additional sections get transition phrases
                else:
                    # More varied connectors based on the section type
                    if "theft" in section['title'].lower():
                        theft_connectors = [
                            f"<p><strong>Additionally, Section {section['number']} ({section['title']})</strong> might also apply since it deals specifically with how property crimes are handled under the law.</p>",
                            f"<p><strong>Your case may also involve Section {section['number']}</strong> which addresses {section['title'].lower()} - this is relevant because it covers another aspect of unauthorized taking of property.</p>",
                            f"<p><strong>We should also consider Section {section['number']}</strong> since it specifically addresses {section['title'].lower()} and could be applicable to your situation.</p>"
                        ]
                        analysis.append(random.choice(theft_connectors))
                    
                    elif any(term in section['title'].lower() for term in ["hurt", "injury", "assault", "grievous"]):
                        violence_connectors = [
                            f"<p><strong>Section {section['number']} ({section['title']})</strong> is also relevant since it specifically addresses the physical harm aspect of your case.</p>",
                            f"<p><strong>The physical aspect of your case falls under Section {section['number']}</strong> which deals with {section['title'].lower()} - this is important because it addresses the injuries described.</p>",
                            f"<p><strong>Given the nature of the physical confrontation, Section {section['number']}</strong> on {section['title'].lower()} would also be applicable here.</p>"
                        ]
                        analysis.append(random.choice(violence_connectors))
                        
                    elif any(term in section['title'].lower() for term in ["rape", "sexual", "modesty"]):
                        sexual_connectors = [
                            f"<p><strong>Your case also involves considerations under Section {section['number']},</strong> which specifically addresses {section['title'].lower()} - a crucial protection in the law.</p>",
                            f"<p><strong>Additionally, Section {section['number']}</strong> on {section['title'].lower()} provides further legal framework relevant to your situation.</p>",
                            f"<p><strong>It's important to note that Section {section['number']}</strong> specifically addresses {section['title'].lower()} and provides additional protections in cases like yours.</p>"
                        ]
                        analysis.append(random.choice(sexual_connectors))
                        
                    elif any(term in section['title'].lower() for term in ["cheat", "fraud", "dishonest"]):
                        fraud_connectors = [
                            f"<p><strong>The deceptive aspects of your case are covered by Section {section['number']},</strong> which specifically addresses {section['title'].lower()}.</p>",
                            f"<p><strong>Your situation also falls under Section {section['number']}</strong> since it deals with {section['title'].lower()} - addressing how deception is treated under Indian law.</p>",
                            f"<p><strong>We should examine Section {section['number']}</strong> as well, which covers {section['title'].lower()} and is directly relevant to the misrepresentations you described.</p>"
                        ]
                        analysis.append(random.choice(fraud_connectors))
                        
                    else:
                        general_connectors = [
                            f"<p><strong>Another relevant law is Section {section['number']}</strong> which addresses {section['title'].lower()}.</p>",
                            f"<p><strong>Your case also touches on Section {section['number']}</strong> - {section['title']} - which is applicable here because of the specific circumstances you described.</p>",
                            f"<p><strong>Section {section['number']} ({section['title']})</strong> should also be considered given the nature of your situation.</p>"
                        ]
                        analysis.append(random.choice(general_connectors))
                
                # Include the legal text but with better plain language explanations
                analysis.append(f"<p class='legal-citation'><small>\"{section['description']}\"</small></p>")
                
                # Dynamic explanations based on section type
                if "theft" in section['title'].lower():
                    theft_explanations = [
                        f"<p><strong>What this means in simple terms:</strong> This law makes it a crime to take someone else's property without their permission, with the intention of keeping it. The key elements are that the taking must be dishonest and without the owner's consent.</p>",
                        
                        f"<p><strong>In everyday language:</strong> If someone takes your belongings without asking and intends to keep them for themselves, that's theft under this law. It doesn't matter how small or large the item is - taking what doesn't belong to you is against the law.</p>",
                        
                        f"<p><strong>Breaking it down:</strong> This section applies when someone deliberately takes something that belongs to someone else without permission. The law recognizes your right to your property and makes it an offense for others to take it without your consent.</p>"
                    ]
                    analysis.append(random.choice(theft_explanations))
                    
                elif "rape" in section['title'].lower():
                    rape_explanations = [
                        f"<p><strong>What this means in simple terms:</strong> This law defines sexual assault very clearly as sexual acts performed without consent. It emphasizes that consent must be freely given, and recognizes many situations where genuine consent is impossible.</p>",
                        
                        f"<p><strong>In everyday language:</strong> This section protects individuals from non-consensual sexual acts. It clearly states that consent is essential, and that consent obtained through fear, intoxication, deception, or when a person cannot understand what they're agreeing to, is not valid consent at all.</p>",
                        
                        f"<p><strong>Breaking it down:</strong> This law recognizes sexual autonomy as a fundamental right and makes it a serious crime to violate that autonomy through force, coercion, deception, or by taking advantage of someone's inability to consent.</p>"
                    ]
                    analysis.append(random.choice(rape_explanations))
                    
                elif any(term in section['title'].lower() for term in ["assault", "hurt", "grievous"]):
                    violence_explanations = [
                        f"<p><strong>What this means in simple terms:</strong> This law makes it illegal to physically harm someone else. The severity of punishment increases with the seriousness of the injuries caused, especially if weapons were used or if the injuries are permanent.</p>",
                        
                        f"<p><strong>In everyday language:</strong> If someone physically attacks you and causes injury, this law provides protection and consequences for the attacker. It recognizes your right to physical safety and bodily integrity.</p>",
                        
                        f"<p><strong>Breaking it down:</strong> This section addresses situations where someone intentionally causes physical harm to another person. The law takes this seriously and provides penalties that match the severity of the harm caused.</p>"
                    ]
                    analysis.append(random.choice(violence_explanations))
                    
                elif any(term in section['title'].lower() for term in ["cheat", "fraud"]):
                    fraud_explanations = [
                        f"<p><strong>What this means in simple terms:</strong> This law makes it a crime to deceive someone to get their money or property. The deception must be deliberate, and the victim must have handed over something of value because they believed the false information.</p>",
                        
                        f"<p><strong>In everyday language:</strong> If someone lies to you to get you to give them money or property, that's fraud under this law. It protects people from scams, false promises, and dishonest schemes designed to trick you out of your possessions.</p>",
                        
                        f"<p><strong>Breaking it down:</strong> This section addresses situations where someone deliberately misleads you with the intention of getting something from you. The law recognizes that deception for financial gain is a serious offense.</p>"
                    ]
                    analysis.append(random.choice(fraud_explanations))
                    
                else:
                    general_explanations = [
                        f"<p><strong>What this means in simple terms:</strong> This law applies when someone {section['title'].lower()} and provides specific legal protections and consequences in such situations.</p>",
                        
                        f"<p><strong>In everyday language:</strong> The behavior described in your case falls under this section because it involves {section['title'].lower()}, which is specifically addressed by this provision of the law.</p>",
                        
                        f"<p><strong>Breaking it down:</strong> This section is relevant to your situation because it deals with {section['title'].lower()}, providing a legal framework for addressing this type of conduct.</p>"
                    ]
                    analysis.append(random.choice(general_explanations))
                
                # More conversational punishment discussions
                case_type_word = section['title'].lower()
                punishment = section['punishment'].lower()
                
                punishment_comments = [
                    f"<p><strong>Potential consequences:</strong> If someone is convicted under this section, they may face {punishment}. This reflects how seriously the law takes {case_type_word} cases.</p>",
                    
                    f"<p><strong>Legal penalties:</strong> The punishment for this offense can include {punishment}. The courts consider various factors including the specific circumstances, the severity of the offense, and previous criminal history.</p>",
                    
                    f"<p><strong>What the law prescribes:</strong> For this type of offense, the law provides for {punishment}. The actual sentence in any specific case would depend on the circumstances and is at the discretion of the court.</p>"
                ]
                analysis.append(random.choice(punishment_comments))
    
    # Precedent Analysis with more personalized commentary
    if precedent_ids:
        precedent_intros = [
            "\n<h3>Similar Court Cases That May Help Your Situation</h3>",
            "\n<h3>How the Courts Have Ruled in Similar Cases</h3>",
            "\n<h3>Legal Precedents Relevant to Your Case</h3>",
            "\n<h3>Past Court Decisions That Offer Guidance</h3>"
        ]
        analysis.append(random.choice(precedent_intros))
        
        precedent_bridges = [
            "<p>Looking at past court decisions can help us understand how your case might be treated. Here are some relevant examples:</p>",
            
            "<p>The following court cases share similarities with your situation and provide insight into how the legal system approaches these matters:</p>",
            
            "<p>To better understand how the courts might view your case, let's look at some previous decisions in similar situations:</p>",
            
            "<p>These previous court rulings can help illuminate how the legal principles apply in real-world situations similar to yours:</p>"
        ]
        analysis.append(random.choice(precedent_bridges))
        
        for precedent_id in precedent_ids:
            precedent = legal_precedents.get(precedent_id)
            if precedent:
                # More engaging case headers
                case_headers = [
                    f"<h4>{precedent['case_name']} ({precedent['year']}) - {precedent['court']}</h4>",
                    f"<h4>The Case of {precedent['case_name']} ({precedent['year']})</h4>",
                    f"<h4>{precedent['case_name']} - Decided by {precedent['court']} in {precedent['year']}</h4>"
                ]
                analysis.append(random.choice(case_headers))
                
                # Make the summary more engaging and relevant
                case_summary_intros = [
                    f"<p><strong>What happened:</strong> {precedent['summary']}</p>",
                    f"<p><strong>Case background:</strong> {precedent['summary']}</p>",
                    f"<p><strong>The court considered:</strong> {precedent['summary']}</p>"
                ]
                analysis.append(random.choice(case_summary_intros))
                
                # Make the relevance explanation more personalized
                relevance_explanations = [
                    f"<p><strong>Relevance to your situation:</strong> {precedent['implications']} This precedent may help establish how the court might approach the specific circumstances of your case.</p>",
                    
                    f"<p><strong>How this might apply to you:</strong> {precedent['implications']} Understanding this precedent could be valuable in developing your legal strategy.</p>",
                    
                    f"<p><strong>Why this matters for your case:</strong> {precedent['implications']} This case demonstrates how the courts have interpreted the law in situations with similarities to yours.</p>"
                ]
                analysis.append(random.choice(relevance_explanations))
    
    # More tailored legal guidance based on case type
    guidance_headers = [
        "\n<h3>Practical Steps You Can Take</h3>",
        "\n<h3>Recommended Actions</h3>",
        "\n<h3>What You Can Do Next</h3>",
        "\n<h3>Moving Forward with Your Case</h3>"
    ]
    analysis.append(random.choice(guidance_headers))
    
    guidance_intros = [
        "<p>Based on my analysis of your situation, here are some specific steps that could help strengthen your position:</p>",
        
        "<p>Now that we've examined the legal aspects, here are some practical actions you might consider taking:</p>",
        
        "<p>To help address this situation effectively, I would recommend the following steps:</p>,",
        
        "<p>Here are some concrete actions that could help you move forward with your case:</p>"
    ]
    analysis.append(random.choice(guidance_intros))
    
    analysis.append("<ul>")
    
    # Theft-specific guidance
    if is_theft_case:
        theft_guidance = [
            "<li><strong>Create a detailed inventory:</strong> Make a comprehensive list of all stolen items with descriptions, approximate values, purchase dates, and any identifying features or serial numbers.</li>",
            
            "<li><strong>Gather proof of ownership:</strong> Collect receipts, warranty cards, photographs, insurance documents, or any other evidence that proves the items belonged to you.</li>",
            
            "<li><strong>Check for surveillance footage:</strong> If the theft occurred in a location with CCTV (like a shop, apartment building, or public space), request access to the footage as soon as possible before it gets deleted.</li>",
            
            "<li><strong>Identify witnesses:</strong> Make a list of anyone who saw the theft occur, noticed suspicious activity, or can confirm you owned the stolen items.</li>",
            
            "<li><strong>File a detailed FIR:</strong> Ensure your police report (First Information Report) includes all relevant information, including when and where the theft occurred, what was taken, and any suspects you might have.</li>",
            
            "<li><strong>Check online marketplaces:</strong> Sometimes stolen items appear for sale online. Regularly check platforms like OLX, Facebook Marketplace, and other secondhand sales platforms.</li>",
            
            "<li><strong>Contact your insurance company:</strong> If the stolen items were insured, notify your insurance provider about the theft and follow their claim process.</li>"
        ]
        
        # Add 4-5 randomly selected theft-specific guidance items
        for item in random.sample(theft_guidance, min(5, len(theft_guidance))):
            analysis.append(item)
            
    # Assault/violence specific guidance
    elif is_violent_case:
        violence_guidance = [
            "<li><strong>Seek medical attention:</strong> Even if injuries seem minor, get a proper medical examination that documents all injuries. Medical records serve as important evidence.</li>",
            
            "<li><strong>Photograph injuries:</strong> Take clear, well-lit photographs of all visible injuries immediately and as they evolve over the coming days (bruises often become more visible after 24-48 hours).</li>",
            
            "<li><strong>Preserve damaged belongings:</strong> If any clothing was torn or belongings damaged during the assault, keep these items as evidence.</li>",
            
            "<li><strong>Document emotional effects:</strong> Keep a journal noting any psychological impacts such as difficulty sleeping, anxiety, fear, or other emotional distress resulting from the incident.</li>",
            
            "<li><strong>Collect witness information:</strong> Make a list of anyone who saw the assault or its immediate aftermath, along with their contact information.</li>",
            
            "<li><strong>Note the location details:</strong> Document exactly where the incident occurred, including any features that might have contributed to the situation (poor lighting, isolated area, etc.).</li>",
            
            "<li><strong>Identify any surveillance:</strong> Note whether the location has security cameras that might have captured the incident.</li>",
            
            "<li><strong>Record previous incidents:</strong> If there's a history of conflicts with the same person, document dates, times, and descriptions of previous incidents.</li>"
        ]
        
        # Add 4-5 randomly selected violence-specific guidance items
        for item in random.sample(violence_guidance, min(5, len(violence_guidance))):
            analysis.append(item)
            
    # Fraud-specific guidance
    elif is_fraud_case:
        fraud_guidance = [
            "<li><strong>Gather all communications:</strong> Collect all emails, text messages, letters, and records of phone calls between you and the person/company that defrauded you.</li>",
            
            "<li><strong>Save financial records:</strong> Compile bank statements, receipts, invoices, contracts, and any other financial documents related to the fraud.</li>",
            
            "<li><strong>Document the timeline:</strong> Create a chronological record of all interactions, promises made, money transferred, and when you discovered the deception.</li>",
            
            "<li><strong>Screenshot online evidence:</strong> If the fraud involved websites, online profiles, or social media, take screenshots before this content can be deleted.</li>",
            
            "<li><strong>Identify witnesses:</strong> Note anyone who witnessed transactions, heard promises made, or was present during relevant interactions.</li>",
            
            "<li><strong>Contact your bank:</strong> If you made payments through a bank, contact them immediately as they may be able to help recover funds in some cases.</li>",
            
            "<li><strong>Report to regulatory bodies:</strong> Depending on the type of fraud, consider reporting to relevant authorities like SEBI (for investment fraud), RBI (for banking fraud), or consumer protection agencies.</li>",
            
            "<li><strong>Check for other victims:</strong> If possible, identify whether others have been similarly defrauded, as multiple complaints can strengthen a case.</li>"
        ]
        
        # Add 4-5 randomly selected fraud-specific guidance items
        for item in random.sample(fraud_guidance, min(5, len(fraud_guidance))):
            analysis.append(item)
    
    # Sexual assault specific guidance
    elif is_sexual_case:
        sexual_guidance = [
            "<li><strong>Seek medical attention:</strong> Consider getting a medical examination as soon as possible, ideally at a hospital with a specialized sexual assault response team if available.</li>",
            
            "<li><strong>Preserve evidence:</strong> If possible, avoid washing, changing clothes, or cleaning up before the medical examination to preserve potential evidence.</li>",
            
            "<li><strong>Consider counseling support:</strong> Connect with a counselor or therapist experienced in trauma, as they can both support your wellbeing and potentially provide testimony about the psychological impact.</li>",
            
            "<li><strong>Document communication:</strong> Save any messages, emails, or other communications from before or after the incident that might be relevant to establishing what happened.</li>",
            
            "<li><strong>Record your recollections:</strong> Write down everything you can remember about the incident while it's fresh in your memory, including specific details about what happened, when, where, and any witnesses.</li>",
            
            "<li><strong>Identify safe contacts:</strong> Make a list of people you trust who can provide emotional support, accompany you to appointments, or potentially serve as character witnesses.</li>",
            
            "<li><strong>Consider a protection order:</strong> If you feel at risk of further harm, you might qualify for a protection order that legally requires the other person to stay away from you.</li>"
        ]
        
        # Add 4-5 randomly selected sexual assault-specific guidance items
        for item in random.sample(sexual_guidance, min(4, len(sexual_guidance))):
            analysis.append(item)
    
    # Add a couple of general recommendations for all cases
    general_guidance = [
        "<li><strong>Consult a specialized attorney:</strong> Speak with a lawyer who has experience specifically with this type of case. They can provide advice tailored to your exact situation and local legal practices.</li>",
        
        "<li><strong>Keep a case journal:</strong> Start a dedicated notebook or document where you record all developments in your case, including dates of interviews, names of officials you speak with, and copies of documents filed.</li>",
        
        "<li><strong>Preserve all evidence:</strong> Store any evidence in a safe place where it won't be damaged, lost, or accessed by unauthorized people.</li>",
        
        "<li><strong>Be careful about social media:</strong> Avoid posting details about your case on social media, as these posts could potentially be used against you later.</li>",
        
        "<li><strong>Consider emotional support:</strong> Legal proceedings can be stressful. Consider seeking support from trusted friends, family members, or professional counselors.</li>"
    ]
    
    # Add 2-3 general guidance items
    for item in random.sample(general_guidance, min(3, len(general_guidance))):
        analysis.append(item)
        
    analysis.append("</ul>")
    
    # Next steps - more personalized and varied
    next_step_headers = [
        "\n<h3>Your Path Forward</h3>",
        "\n<h3>Immediate Next Steps</h3>",
        "\n<h3>Moving Your Case Forward</h3>",
        "\n<h3>Key Actions to Consider</h3>"
    ]
    analysis.append(random.choice(next_step_headers))
    
    next_steps_intros = [
        "<p>Here's a suggested sequence of actions to help you navigate the next phase of this process:</p>",
        
        "<p>As you move forward with this matter, here are the key steps to consider taking, in order of priority:</p>",
        
        "<p>To effectively address this situation, I would recommend the following sequence of actions:</p>",
        
        "<p>Based on my analysis, here's a roadmap for the immediate steps you should consider:</p>"
    ]
    analysis.append(random.choice(next_steps_intros))
    
    analysis.append("<ol>")
    
    # Create a pool of potential next steps based on case type
    next_steps_pool = [
        "<li><strong>File a police report (if not done):</strong> Ensure you have an official First Information Report (FIR) filed at the nearest police station. This creates an official record and is often necessary for further legal action.</li>",
        
        "<li><strong>Consult with a specialist attorney:</strong> Seek advice from a lawyer who specializes in this specific area of law. Look for someone with a track record of handling similar cases.</li>",
        
        "<li><strong>Organize your evidence:</strong> Create a well-organized file with all documents, photographs, communications, and other evidence related to your case. Make copies of everything.</li>",
        
        "<li><strong>Prepare a detailed written statement:</strong> Write down everything that happened in chronological order with as much detail as possible while events are still fresh in your memory.</li>",
        
        "<li><strong>Follow up with investigating officers:</strong> Stay in regular contact with the police officers handling your case to ensure it's progressing and to provide any additional information they might need.</li>",
        
        "<li><strong>Consider interim protection:</strong> Depending on your case, you might be eligible for protective orders or other interim measures while your case proceeds.</li>",
        
        "<li><strong>Prepare for potential mediation:</strong> In some cases, courts encourage mediation before proceeding to trial. Consider whether this might be appropriate for your situation.</li>",
        
        "<li><strong>Understand the timeline:</strong> Discuss with your lawyer how long the legal process might take and what milestones to expect along the way.</li>",
        
        "<li><strong>Explore compensation options:</strong> Discuss with your lawyer whether you should pursue compensation for damages, injuries, or losses resulting from the incident.</li>",
        
        "<li><strong>Create a support system:</strong> Identify friends, family members, or support groups who can provide emotional support throughout what might be a lengthy legal process.</li>"
    ]
    
    # Select 4-5 next steps randomly from the pool
    selected_next_steps = random.sample(next_steps_pool, min(5, len(next_steps_pool)))
    for step in selected_next_steps:
        analysis.append(step)
        
    analysis.append("</ol>")
    
    # More varied and personalized disclaimer
    analysis.append("\n<h3>Important Information</h3>")
    
    disclaimer_variations = [
        "<p>Please note that this analysis is based on the information you've provided and is meant to give you general guidance rather than formal legal advice. Every case has unique aspects that can significantly affect legal outcomes. For personalized advice tailored to all the specifics of your situation, I strongly recommend consulting with a practicing lawyer who specializes in this area of law.</p>",
        
        "<p>While I've provided an analysis based on Indian law and similar cases, it's important to understand that legal outcomes can vary widely depending on the specific details, evidence available, local court practices, and many other factors. This information should be used as a starting point for understanding your legal situation, but shouldn't replace the guidance of a qualified legal professional who can evaluate all aspects of your specific case.</p>",
        
        "<p>The information provided here is meant to help you understand the legal framework around your situation, but shouldn't be considered a substitute for personalized legal counsel. Legal cases involve many nuances and strategic considerations that can only be properly addressed by a practicing attorney who has full access to all the details of your case and knowledge of local court practices. I recommend using this analysis as background information when you consult with a legal professional.</p>",
        
        "<p>This analysis offers a general overview of how Indian law applies to situations like the one you've described. However, effective legal representation requires consideration of many factors including jurisdiction-specific practices, precedents, and the specific evidence in your case. I encourage you to share this information with a qualified attorney who can provide advice specifically tailored to your unique circumstances.</p>"
    ]
    
    analysis.append(random.choice(disclaimer_variations))
    
    return "\n".join(analysis)
