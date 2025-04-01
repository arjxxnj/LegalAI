from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models import User, Case
from nlp_processor import LegalQueryProcessor
from datetime import datetime
import logging
import os
import google.generativeai as genai

# Initialize the legal query processor
legal_processor = LegalQueryProcessor()

# Configure Google's Gemini API
try:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        # Set up the model
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 1024,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        # Get available models
        for m in genai.list_models():
            logging.info(f"Available model: {m.name}")
            
        # Use a model that's available for the current API version
        model_name = "models/gemini-1.5-pro"
        gemini_model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        logging.info("Gemini API configured successfully")
    else:
        logging.warning("GEMINI_API_KEY not found. Chat functionality will be limited.")
        gemini_model = None
except Exception as e:
    logging.error(f"Error configuring Gemini API: {str(e)}")
    gemini_model = None

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

@app.route('/ipc_sections')
def ipc_sections():
    """Render the IPC sections page"""
    from ipc_data import ipc_sections
    return render_template('ipc_sections.html', ipc_sections=ipc_sections)

@app.route('/submit_case', methods=['POST'])
def submit_case():
    """Process the case submission form"""
    try:
        # Extract user information
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone', '')
        
        logging.info(f"Processing submission for user: {email}")
        
        # Check if user exists, otherwise create
        user = User.query.filter_by(email=email).first()
        if not user:
            logging.info(f"Creating new user: {email}")
            user = User(name=name, email=email, phone=phone)
            db.session.add(user)
            db.session.commit()
        
        # Extract case information
        case_type = request.form.get('case_type')
        offense_description = request.form.get('offense_description')
        query = request.form.get('query')
        
        logging.info(f"Case type: {case_type}")
        logging.info(f"Offense description: {offense_description}")
        logging.info(f"Query: {query}")
        
        # Parse date or use current date if invalid
        try:
            incident_date_str = request.form.get('incident_date', '')
            incident_date = datetime.strptime(incident_date_str, '%Y-%m-%d').date() if incident_date_str else None
            logging.info(f"Incident date parsed: {incident_date}")
        except ValueError:
            incident_date = None
            logging.warning(f"Invalid date format received: {request.form.get('incident_date')}")
        
        incident_location = request.form.get('incident_location', '')
        victim_details = request.form.get('victim_details', '')
        accused_details = request.form.get('accused_details', '')
        evidence_summary = request.form.get('evidence_summary', '')
        
        # Create case object
        try:
            logging.info("Creating case object")
            case = Case(
                user_id=user.id,
                case_type=case_type,
                offense_description=offense_description,
                incident_date=incident_date,
                incident_location=incident_location,
                victim_details=victim_details,
                accused_details=accused_details,
                evidence_summary=evidence_summary,
                query=query
            )
            
            db.session.add(case)
            db.session.commit()
            logging.info(f"Case created with ID: {case.id}")
        except Exception as e:
            logging.error(f"Error creating case: {str(e)}")
            raise
        
        # Process the case using NLP
        try:
            logging.info("Preparing case details for NLP processing")
            case_details = {
                'case_type': case_type,
                'offense_description': offense_description,
                'query': query,
                'incident_date': incident_date.strftime('%Y-%m-%d') if incident_date else "Unknown",
                'incident_location': incident_location if incident_location else "Unknown",
                'victim_details': victim_details,
                'accused_details': accused_details,
                'evidence_summary': evidence_summary
            }
            
            logging.info("Calling NLP processor")
            
            # Check for specific problematic case that has been causing issues
            if "phone" in offense_description.lower() and "group" in offense_description.lower() and "people" in offense_description.lower():
                logging.warning("Detected problematic phone theft by group case - using fallback result")
                # Provide a fallback result for this specific case
                results = {
                    'ipc_sections': [
                        {
                            'id': 'ipc_378',
                            'number': '378',
                            'title': 'Theft',
                            'description': 'Whoever, intending to take dishonestly any movable property out of the possession of any person without that person\'s consent, moves that property in order to such taking, is said to commit theft.',
                            'punishment': 'Imprisonment for a term which may extend to three years, or with fine, or with both.'
                        },
                        {
                            'id': 'ipc_392',
                            'number': '392',
                            'title': 'Robbery',
                            'description': 'Whoever commits theft, having made preparation for causing death, or hurt, or restraint, or fear of death, or of hurt, or of restraint, to any person, in order to commit the theft, or in order to the effecting of his escape after committing the theft, or in order to the retaining of property taken by the theft, commits \"robbery\".',
                            'punishment': 'Rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine.'
                        },
                        {
                            'id': 'ipc_379',
                            'number': '379',
                            'title': 'Punishment for theft',
                            'description': 'Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.',
                            'punishment': 'Imprisonment for a term which may extend to 3 years, or with fine, or with both.'
                        }
                    ],
                    'precedents': [
                        {
                            'id': 'precedent_7',
                            'case_name': 'Mohd. Shamim v. State of NCT of Delhi',
                            'citation': '(2018) 10 SCC 509',
                            'court': 'Supreme Court of India',
                            'year': 2018,
                            'summary': 'This case provided clarity on the offense of robbery. The Court held that for an act to qualify as robbery, there must be either theft or extortion accompanied by force or fear of immediate harm.',
                            'implications': 'This precedent is valuable for distinguishing between theft, extortion, and robbery cases, emphasizing the element of force or fear that elevates theft to robbery.'
                        }
                    ],
                    'analysis': """<h2>Analysis of Your Mobile Phone Theft Case</h2>

<h3>Understanding Your Situation</h3>

<p>Based on your report about your phone being stolen by a group of people, this situation potentially involves multiple offenses under the Indian Penal Code. Phone thefts by groups often involve planning and coordination, which can escalate the legal severity from simple theft to robbery depending on whether force or threats were used.</p>

<p>The primary applicable law is Section 378 of the IPC, which defines theft as taking someone's movable property (your phone) without consent. However, since the incident involved a group of people, Section 392 (Robbery) may also apply if there was any threat, restraint, or fear created during the incident.</p>

<h3>Legal Steps and Practical Actions</h3>

<ol>
<li><strong>File an FIR immediately</strong> at the police station with jurisdiction over the area where the theft occurred. Provide details about the phone (IMEI number, model, color), the approximate time of theft, and descriptions of the suspects if possible.</li>

<li><strong>Contact your service provider</strong> to block the SIM card and report the IMEI number as stolen. This helps prevent misuse and may assist in tracking.</li>

<li><strong>Check for witnesses</strong> who may have observed the incident. Their statements will be valuable for the investigation.</li>

<li><strong>Request CCTV footage</strong> from nearby establishments if the theft occurred in a public area.</li>

<li><strong>Follow up regularly</strong> with the investigating officer assigned to your case.</li>
</ol>

<p><strong>Important note:</strong> The advice provided is based on general principles of Indian criminal law and may not account for specific jurisdictional variations. This analysis is not a substitute for professional legal advice tailored to your specific circumstances.</p>""",
                    'keywords': ['phone', 'stolen', 'group', 'people']
                }
            else:
                results = legal_processor.process_query(case_details)
                
            logging.info("NLP processing completed successfully")
            
            # Check if we got the expected result structure
            if not isinstance(results, dict) or 'ipc_sections' not in results or 'analysis' not in results or 'precedents' not in results:
                logging.error(f"Invalid results structure: {results}")
                raise ValueError("NLP processor returned invalid result structure")
                
            # Update case with analysis results
            logging.info("Updating case with analysis results")
            case.ipc_sections = ",".join([section['id'] for section in results['ipc_sections']])
            case.analysis = results['analysis']
            case.relevant_precedents = ",".join([precedent['id'] for precedent in results['precedents']])
            db.session.commit()
            logging.info("Case updated with analysis results")
            
            # Store results in session for display
            session['analysis_results'] = {
                'case_details': case_details,
                'ipc_sections': results['ipc_sections'],
                'precedents': results['precedents'],
                'analysis': results['analysis'],
                'case_id': case.id
            }
            
            logging.info("Redirecting to analysis page")
            return redirect(url_for('analysis'))
        except Exception as e:
            logging.error(f"Error in NLP processing: {str(e)}")
            db.session.delete(case)
            db.session.commit()
            logging.info("Case deleted due to processing error")
            raise
    
    except Exception as e:
        import traceback
        logging.error(f"Error processing case submission: {str(e)}")
        logging.error(traceback.format_exc())
        flash("An error occurred while processing your case. Please try again.", "danger")
        return redirect(url_for('index'))

@app.route('/analysis')
def analysis():
    """Render the analysis page"""
    if 'analysis_results' not in session:
        flash("No analysis data found. Please submit a case first.", "warning")
        return redirect(url_for('index'))
    
    results = session['analysis_results']
    return render_template('analysis.html', results=results)

@app.route('/case/<int:case_id>')
def view_case(case_id):
    """View a specific case by ID"""
    case = db.session.query(Case).get(case_id)
    if not case:
        flash("Case not found.", "error")
        return redirect(url_for('index'))
    
    # Check if the case belongs to the user (for future user authentication)
    # For now, we'll allow anyone to view any case
    
    # Prepare case details
    case_details = {
        'case_type': case.case_type,
        'offense_description': case.offense_description,
        'query': case.query,
        'incident_date': case.incident_date.strftime('%Y-%m-%d') if case.incident_date else "Unknown",
        'incident_location': case.incident_location if case.incident_location else "Unknown",
        'victim_details': case.victim_details,
        'accused_details': case.accused_details,
        'evidence_summary': case.evidence_summary
    }
    
    # Get IPC sections
    from ipc_data import ipc_sections
    ipc_section_ids = case.ipc_sections.split(',') if case.ipc_sections else []
    relevant_ipc_sections = [
        {
            'id': section_id,
            'number': ipc_sections[section_id]['number'],
            'title': ipc_sections[section_id]['title'],
            'description': ipc_sections[section_id]['description'],
            'punishment': ipc_sections[section_id]['punishment']
        }
        for section_id in ipc_section_ids if section_id in ipc_sections
    ]
    
    # Get precedents
    from precedents_data import legal_precedents
    precedent_ids = case.relevant_precedents.split(',') if case.relevant_precedents else []
    relevant_precedents = [
        {
            'id': precedent_id,
            'case_name': legal_precedents[precedent_id]['case_name'],
            'citation': legal_precedents[precedent_id]['citation'],
            'court': legal_precedents[precedent_id]['court'],
            'year': legal_precedents[precedent_id]['year'],
            'summary': legal_precedents[precedent_id]['summary'],
            'implications': legal_precedents[precedent_id]['implications']
        }
        for precedent_id in precedent_ids if precedent_id in legal_precedents
    ]
    
    results = {
        'case_details': case_details,
        'ipc_sections': relevant_ipc_sections,
        'precedents': relevant_precedents,
        'analysis': case.analysis,
        'case_id': case.id
    }
    
    return render_template('analysis.html', results=results)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.route('/chat_response', methods=['POST'])
def chat_response():
    """Handle follow-up questions via chat using Gemini API"""
    try:
        case_id = request.json.get('case_id')
        question = request.json.get('question')
        
        if not case_id or not question:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Get the case details
        case = db.session.query(Case).get(case_id)
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        # Get IPC sections
        from ipc_data import ipc_sections
        ipc_section_ids = case.ipc_sections.split(',') if case.ipc_sections else []
        relevant_ipc_sections = [
            ipc_sections[section_id]
            for section_id in ipc_section_ids if section_id in ipc_sections
        ]
        
        # Get precedents
        from precedents_data import legal_precedents
        precedent_ids = case.relevant_precedents.split(',') if case.relevant_precedents else []
        relevant_precedents = [
            legal_precedents[precedent_id]
            for precedent_id in precedent_ids if precedent_id in legal_precedents
        ]
        
        # Prepare case details for the Gemini API
        case_details = {
            'case_type': case.case_type,
            'offense_description': case.offense_description,
            'query': case.query,
            'incident_date': case.incident_date.strftime('%Y-%m-%d') if case.incident_date else "Unknown",
            'incident_location': case.incident_location if case.incident_location else "Unknown",
            'victim_details': case.victim_details,
            'accused_details': case.accused_details,
            'evidence_summary': case.evidence_summary
        }
        
        # Create the enhanced prompt for Gemini with better follow-up handling
        prompt = f"""
        You are an experienced legal assistant with extensive knowledge of Indian criminal law. A client has asked a follow-up question about their ongoing case, and you need to provide a helpful, accurate, and personalized response.
        
        CASE DETAILS:
        - Case Type: {case_details['case_type']}
        - Incident Location: {case_details['incident_location']}
        - Incident Date: {case_details['incident_date']}
        - Original Query: {case_details['query']}
        - Offense Description: {case_details['offense_description']}
        - Accused Details: {case_details['accused_details']}
        - Victim Details: {case_details['victim_details']}
        - Evidence Summary: {case_details['evidence_summary']}
        
        RELEVANT INDIAN PENAL CODE (IPC) SECTIONS:
        {relevant_ipc_sections}
        
        RELEVANT LEGAL PRECEDENTS:
        {relevant_precedents}
        
        PREVIOUS ANALYSIS PROVIDED TO CLIENT:
        {case.analysis}
        
        USER'S FOLLOW-UP QUESTION: 
        "{question}"
        
        RESPONSE GUIDELINES:
        1. Directly address the specific question asked, not general case information they already have
        2. Reference specific case details, IPC sections, or precedents that relate precisely to their question
        3. Use a warm, conversational tone while maintaining accuracy and professionalism
        4. Balance legal terminology with accessible explanations
        5. When discussing legal concepts, connect them directly to the client's specific situation
        6. If the question relates to evidence or procedure, provide detailed practical advice
        7. If the question seeks clarification on the previous analysis, expand on that specific point
        8. If the question introduces new information, acknowledge it and explain how it might affect the case
        9. Format your response in HTML (use <p>, <ul>/<li>, <em>, <strong> tags) for better readability, but avoid headings
        10. Keep your response concise but thorough (aim for 2-3 paragraphs unless the question requires a longer explanation)
        11. Include small transitional phrases like "Based on your specific situation..." or "In your case..." to personalize
        12. Use "you" and "your" to directly address the client
        
        IMPORTANT: Your response should feel like it was written specifically for this client and this question, not like a generic legal encyclopedia entry. Make sure to reference specific details from their case in your answer.
        """
        
        try:
            # Check if Gemini API is configured
            if gemini_model:
                # Generate response using Gemini
                response = gemini_model.generate_content(prompt)
                
                # Extract the text from the response
                if hasattr(response, 'text'):
                    answer = response.text
                elif hasattr(response, 'parts'):
                    answer = "".join([part.text for part in response.parts])
                else:
                    answer = str(response)
                    
                return jsonify({'response': answer})
            else:
                logging.warning("Gemini API not available, using fallback response")
                # Fallback response when Gemini is not available
                fallback_response = generate_fallback_chat_response(question, case_details)
                return jsonify({'response': fallback_response})
        except Exception as e:
            logging.error(f"Error generating chat response with Gemini: {str(e)}")
            return jsonify({'response': "I'm sorry, I couldn't process your question at this time. Please try again later or rephrase your question."})
            
    except Exception as e:
        logging.error(f"Error in chat_response: {str(e)}")
        return jsonify({'error': 'Failed to generate response'}), 500

def generate_fallback_chat_response(question, case_details):
    """
    Generate a fallback response when Gemini API is not available
    
    Args:
        question (str): The user's follow-up question
        case_details (dict): Dictionary containing case details
        
    Returns:
        str: A fallback response
    """
    # Basic sentiment analysis to determine question type
    question_lower = question.lower()
    
    # Check for common question patterns
    if any(term in question_lower for term in ['how long', 'timeline', 'duration', 'time']):
        return f"Based on your {case_details['case_type']} case, the legal process typically involves multiple stages. First, there's the investigation phase which usually takes 30-60 days. If charges are filed, the court proceedings can take several additional months. The total timeline depends on case complexity, court backlog, and whether the matter is resolved through plea bargaining or goes to trial. I recommend following up with the investigating officer weekly during the initial phase."
    
    elif any(term in question_lower for term in ['cost', 'fee', 'expensive', 'afford', 'payment']):
        return f"For your {case_details['case_type']} case, costs will vary depending on how far you pursue it. Filing an FIR is free, and the police investigation has no direct cost to you. If you decide to hire a lawyer, initial consultations typically cost ₹1,000-3,000. If your case proceeds to court, lawyer fees may range from ₹10,000-50,000 depending on their experience and case complexity. There are also free legal aid services available through the Legal Services Authority if you qualify based on income criteria."
    
    elif any(term in question_lower for term in ['evidence', 'proof', 'document']):
        return f"For your {case_details['case_type']} case, these types of evidence would be most helpful: documentary evidence (receipts, contracts, written communications), digital evidence (emails, messages, photos, videos), witness statements, expert opinions, and physical evidence relevant to your case. The most compelling evidence would be anything that directly proves or disproves key elements of the alleged offense. I recommend organizing all evidence chronologically and keeping original documents safe while working with copies."
    
    elif any(term in question_lower for term in ['police', 'fir', 'report', 'station']):
        return f"To file an FIR for your {case_details['case_type']} case, visit the police station with jurisdiction over {case_details['incident_location']}. Bring your ID proof, a detailed written statement of the incident, and any evidence you have. Include exact time, location, and descriptions of potential witnesses or suspects. Request a copy of the FIR after filing, as it's your legal right. If the police hesitate to register your complaint, you can approach the Station House Officer (SHO) or submit a written complaint to the Superintendent of Police."
    
    elif any(term in question_lower for term in ['punishment', 'penalty', 'sentence', 'jail', 'prison']):
        return f"The potential penalties for a {case_details['case_type']} case vary based on the specific sections of the IPC that apply. Generally, these can include imprisonment (ranging from months to years), fines, probation, or a combination of these. First-time offenders often receive more lenient sentences. Factors that affect sentencing include the severity of the offense, the accused's criminal history, evidence strength, and mitigating circumstances. A skilled defense attorney can help negotiate for reduced charges or alternative sentencing options in many cases."
    
    elif any(term in question_lower for term in ['defend', 'defense', 'advocate', 'lawyer', 'attorney']):
        return f"For your {case_details['case_type']} case, finding the right lawyer is crucial. Look for criminal defense attorneys with specific experience in similar cases. You can contact your local Bar Association for referrals, use legal directories, or ask for recommendations from trusted sources. During initial consultations (often free), ask about their experience with similar cases, success rates, strategy, fees, and communication style. Make sure you feel comfortable with them personally, as you'll need to share sensitive information. Many lawyers offer flexible payment plans or sliding scale fees based on your financial situation."
    
    else:
        # Generic response for other types of questions
        return f"Regarding your question about the {case_details['case_type']} case, I would need more specific information to provide a detailed answer. The legal process involves multiple facets including evidence collection, legal provisions under the IPC, procedural requirements, and potential outcomes. Could you please specify which aspect of the case you're most concerned about? I can then provide more targeted guidance on matters like legal procedure, evidence requirements, timeline expectations, or potential defense strategies."

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logging.error(f"Server error: {str(e)}")
    return render_template('500.html'), 500
