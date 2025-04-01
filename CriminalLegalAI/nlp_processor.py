from utils import preprocess_text, extract_keywords, find_relevant_ipc_sections, find_relevant_precedents, generate_legal_analysis
from ipc_data import ipc_sections
from precedents_data import legal_precedents
import logging

class LegalQueryProcessor:
    """
    Process legal queries and generate relevant legal analysis
    """
    
    def __init__(self):
        """Initialize the NLP processor"""
        self.ipc_data = ipc_sections
        self.precedents = legal_precedents
        logging.info("LegalQueryProcessor initialized with %d IPC sections and %d precedents", 
                     len(self.ipc_data), len(self.precedents))
    
    def process_query(self, case_details):
        """
        Process a legal query and return analysis
        
        Args:
            case_details (dict): Dictionary containing case details
            
        Returns:
            dict: Results including relevant IPC sections, precedents, and analysis
        """
        logging.info("LegalQueryProcessor: Starting to process query")
        try:
            # Extract query text
            query_text = case_details.get('query', '')
            offense_description = case_details.get('offense_description', '')
            
            logging.info("Processing query: '%s'", query_text[:100])
            logging.info("Offense description: '%s'", offense_description[:100])
            
            # Combine query and offense description for keyword extraction
            combined_text = query_text + " " + offense_description
            
            # Extract keywords from the query
            logging.info("Extracting keywords")
            try:
                keywords = extract_keywords(combined_text)
                logging.info("Extracted %d keywords: %s", len(keywords), str(keywords[:10]))
            except Exception as e:
                logging.error("Error extracting keywords: %s", str(e))
                keywords = []
                raise
            
            # Find relevant IPC sections
            logging.info("Finding relevant IPC sections")
            try:
                relevant_ipc_ids = find_relevant_ipc_sections(keywords, case_details)
                logging.info("Found %d relevant IPC sections: %s", len(relevant_ipc_ids), str(relevant_ipc_ids))
            except Exception as e:
                logging.error("Error finding relevant IPC sections: %s", str(e))
                relevant_ipc_ids = []
                raise
            
            # Get the detailed section data
            logging.info("Getting detailed IPC section data")
            try:
                relevant_ipc_sections = [
                    {
                        'id': section_id,
                        'number': self.ipc_data[section_id]['number'],
                        'title': self.ipc_data[section_id]['title'],
                        'description': self.ipc_data[section_id]['description'],
                        'punishment': self.ipc_data[section_id]['punishment']
                    }
                    for section_id in relevant_ipc_ids if section_id in self.ipc_data
                ]
                logging.info("Processed %d detailed IPC sections", len(relevant_ipc_sections))
            except Exception as e:
                logging.error("Error getting detailed section data: %s", str(e))
                relevant_ipc_sections = []
                raise
            
            # Find relevant legal precedents
            logging.info("Finding relevant precedents")
            try:
                relevant_precedent_ids = find_relevant_precedents(relevant_ipc_ids, keywords)
                logging.info("Found %d relevant precedents: %s", len(relevant_precedent_ids), str(relevant_precedent_ids))
            except Exception as e:
                logging.error("Error finding relevant precedents: %s", str(e))
                relevant_precedent_ids = []
                raise
            
            # Get the detailed precedent data
            logging.info("Getting detailed precedent data")
            try:
                relevant_precedents = [
                    {
                        'id': precedent_id,
                        'case_name': self.precedents[precedent_id]['case_name'],
                        'citation': self.precedents[precedent_id]['citation'],
                        'court': self.precedents[precedent_id]['court'],
                        'year': self.precedents[precedent_id]['year'],
                        'summary': self.precedents[precedent_id]['summary'],
                        'implications': self.precedents[precedent_id]['implications']
                    }
                    for precedent_id in relevant_precedent_ids if precedent_id in self.precedents
                ]
                logging.info("Processed %d detailed precedents", len(relevant_precedents))
            except Exception as e:
                logging.error("Error getting detailed precedent data: %s", str(e))
                relevant_precedents = []
                raise
            
            # Generate legal analysis
            logging.info("Generating legal analysis")
            try:
                analysis = generate_legal_analysis(case_details, relevant_ipc_ids, relevant_precedent_ids)
                logging.info("Legal analysis generated successfully (%d characters)", len(analysis) if analysis else 0)
            except Exception as e:
                logging.error("Error generating legal analysis: %s", str(e))
                analysis = "We apologize, but we are unable to generate a detailed analysis at this time. Please try again later."
                raise
            
            # If we don't have any IPC sections or precedents, provide some feedback
            if not relevant_ipc_sections:
                logging.warning("No relevant IPC sections found for this case")
                if relevant_precedents:
                    logging.info("However, %d relevant precedents were found", len(relevant_precedents))
            
            if not relevant_precedents:
                logging.warning("No relevant precedents found for this case")
                if relevant_ipc_sections:
                    logging.info("However, %d relevant IPC sections were found", len(relevant_ipc_sections))
            
            # If we don't have any analysis, provide a fallback
            if not analysis:
                logging.warning("No analysis was generated")
                analysis = "We apologize, but we could not generate a detailed analysis for your case at this time. Please try with more specific details."
            
            # Compile and return results
            results = {
                'ipc_sections': relevant_ipc_sections,
                'precedents': relevant_precedents,
                'analysis': analysis,
                'keywords': keywords
            }
            
            logging.info("LegalQueryProcessor: Query processing completed successfully")
            return results
            
        except Exception as e:
            import traceback
            logging.error("Error in process_query: %s", str(e))
            logging.error(traceback.format_exc())
            # Provide a fallback result with error information
            return {
                'ipc_sections': [],
                'precedents': [],
                'analysis': f"We apologize, but an error occurred while processing your case: {str(e)}. Please try again later or with different information.",
                'keywords': [],
                'error': str(e)
            }
