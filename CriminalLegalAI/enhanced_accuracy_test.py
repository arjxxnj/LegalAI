#!/usr/bin/env python3
"""
Enhanced accuracy test script for the Legal Assistant application.
Tests the system with 20 cases and measures accuracy against expected outputs.
"""

import os
import sys
import logging
import json
from datetime import datetime, date
from nlp_processor import LegalQueryProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_cases():
    """Create a comprehensive set of 20 test cases with known expected outcomes"""
    
    test_cases = [
        # Case 1: Basic mobile phone theft
        {
            "case_type": "Theft",
            "offense_description": "My mobile phone was stolen from my pocket while I was walking in a market.",
            "query": "My phone was stolen, what can I do?",
            "incident_date": date(2025, 3, 15),
            "incident_location": "Local Market, Delhi",
            "victim_details": "Self",
            "accused_details": "Unknown",
            "evidence_summary": "None",
            "expected_sections": ["ipc_378", "ipc_379"],
            "case_name": "Basic Mobile Theft"
        },
        
        # Case 2: House break-in theft
        {
            "case_type": "Theft",
            "offense_description": "Someone broke into my house at night and stole jewelry, cash, and a laptop.",
            "query": "My house was broken into and valuables were stolen.",
            "incident_date": date(2025, 3, 10),
            "incident_location": "Residential Colony, Mumbai",
            "victim_details": "Self and family",
            "accused_details": "Unknown",
            "evidence_summary": "Broken window, CCTV footage from neighbor's house",
            "expected_sections": ["ipc_378", "ipc_380", "ipc_457"],
            "case_name": "House Break-in Theft"
        },
        
        # Case 3: Robbery with weapon
        {
            "case_type": "Robbery",
            "offense_description": "Two men threatened me with a knife and took my wallet and watch.",
            "query": "I was robbed at knife-point. What sections apply?",
            "incident_date": date(2025, 3, 20),
            "incident_location": "Park, Bangalore",
            "victim_details": "Self",
            "accused_details": "Two unknown men, around 25-30 years old",
            "evidence_summary": "Medical report showing minor injuries, description of attackers",
            "expected_sections": ["ipc_390", "ipc_392", "ipc_397"],
            "case_name": "Armed Robbery"
        },
        
        # Case 4: Simple assault
        {
            "case_type": "Assault",
            "offense_description": "I was hit in the face during an argument with a neighbor.",
            "query": "My neighbor hit me during an argument.",
            "incident_date": date(2025, 3, 18),
            "incident_location": "Apartment Building, Chennai",
            "victim_details": "Self",
            "accused_details": "Neighbor, Mr. Sharma",
            "evidence_summary": "Medical report showing bruising, witness statements",
            "expected_sections": ["ipc_319", "ipc_323"],
            "case_name": "Simple Assault"
        },
        
        # Case 5: Grievous assault with weapon
        {
            "case_type": "Grievous Hurt",
            "offense_description": "A person attacked me with an iron rod, causing a fracture in my arm.",
            "query": "I was attacked with an iron rod and my arm is fractured.",
            "incident_date": date(2025, 3, 5),
            "incident_location": "Street, Hyderabad",
            "victim_details": "Self",
            "accused_details": "Mr. Patel, a local shopkeeper",
            "evidence_summary": "Hospital records, X-rays showing fracture, witness statements",
            "expected_sections": ["ipc_320", "ipc_325", "ipc_326"],
            "case_name": "Grievous Assault with Weapon"
        },
        
        # Case 6: Online fraud
        {
            "case_type": "Fraud",
            "offense_description": "I paid 50,000 rupees online for a product that was never delivered, and the seller has disappeared.",
            "query": "I was cheated in an online purchase and lost money.",
            "incident_date": date(2025, 2, 28),
            "incident_location": "Online transaction from home in Pune",
            "victim_details": "Self",
            "accused_details": "Online seller with username 'TechDeals'",
            "evidence_summary": "Payment receipts, chat history, fake website screenshots",
            "expected_sections": ["ipc_415", "ipc_420"],
            "case_name": "Online Shopping Fraud"
        },
        
        # Case 7: Criminal breach of trust by employee
        {
            "case_type": "Criminal Breach of Trust",
            "offense_description": "My company's accountant embezzled funds by transferring money to personal accounts.",
            "query": "My employee stole company funds.",
            "incident_date": date(2025, 3, 1),
            "incident_location": "Office premises, Gurgaon",
            "victim_details": "XYZ Company",
            "accused_details": "Rajesh Kumar, Company Accountant",
            "evidence_summary": "Bank statements, transaction history, accounting discrepancies",
            "expected_sections": ["ipc_405", "ipc_409"],
            "case_name": "Employee Embezzlement"
        },
        
        # Case 8: Sexual harassment
        {
            "case_type": "Sexual Harassment",
            "offense_description": "A colleague repeatedly made unwelcome advances and inappropriate comments.",
            "query": "My colleague is sexually harassing me at work.",
            "incident_date": date(2025, 3, 8),
            "incident_location": "Office, Kolkata",
            "victim_details": "Female employee",
            "accused_details": "Senior colleague, Mr. Verma",
            "evidence_summary": "Email exchanges, witness statements, complaint to HR",
            "expected_sections": ["ipc_354", "ipc_354A", "ipc_509"],
            "case_name": "Workplace Sexual Harassment"
        },
        
        # Case 9: Domestic violence and dowry harassment
        {
            "case_type": "Domestic Violence",
            "offense_description": "My husband and his family have been physically abusing me and demanding additional dowry.",
            "query": "I am facing domestic violence and dowry demands.",
            "incident_date": date(2025, 3, 15),
            "incident_location": "Matrimonial home, Jaipur",
            "victim_details": "Mrs. Sharma, married for 2 years",
            "accused_details": "Husband and in-laws",
            "evidence_summary": "Medical reports, photographs of injuries, previous police complaints",
            "expected_sections": ["ipc_498A", "ipc_323", "ipc_506"],
            "case_name": "Domestic Violence and Dowry Harassment"
        },
        
        # Case 10: Kidnapping
        {
            "case_type": "Kidnapping",
            "offense_description": "My 10-year-old son was taken from his school by unknown persons demanding ransom.",
            "query": "My child has been kidnapped for ransom.",
            "incident_date": date(2025, 3, 12),
            "incident_location": "School, Lucknow",
            "victim_details": "Minor child, age 10",
            "accused_details": "Unknown kidnappers, ransom call received",
            "evidence_summary": "Ransom call recordings, CCTV footage from school",
            "expected_sections": ["ipc_359", "ipc_363", "ipc_364A"],
            "case_name": "Child Kidnapping for Ransom"
        },
        
        # Case 11: Group theft (dacoity)
        {
            "case_type": "Theft",
            "offense_description": "A group of 6-7 people broke into our home at night and stole valuables while threatening us.",
            "query": "A group of people robbed our house.",
            "incident_date": date(2025, 3, 2),
            "incident_location": "Residential house, Ahmedabad",
            "victim_details": "Family of four",
            "accused_details": "Group of 6-7 unknown persons",
            "evidence_summary": "CCTV footage, broken door, list of stolen items",
            "expected_sections": ["ipc_391", "ipc_395", "ipc_452"],
            "case_name": "Dacoity/Group Robbery"
        },
        
        # Case 12: Defamation
        {
            "case_type": "Defamation",
            "offense_description": "A person posted false accusations about me on social media damaging my reputation.",
            "query": "Someone is spreading false information about me online.",
            "incident_date": date(2025, 2, 25),
            "incident_location": "Online/Social Media",
            "victim_details": "Self, a business owner",
            "accused_details": "Mr. Khanna, a competitor",
            "evidence_summary": "Screenshots of posts, witness statements, business losses",
            "expected_sections": ["ipc_499", "ipc_500"],
            "case_name": "Online Defamation"
        },
        
        # Case 13: Public nuisance/obscenity
        {
            "case_type": "Public Nuisance",
            "offense_description": "A group of people are regularly drinking and creating disturbance in our residential area.",
            "query": "People creating nuisance in residential area.",
            "incident_date": date(2025, 3, 14),
            "incident_location": "Residential Colony, Bhopal",
            "victim_details": "Residents of the colony",
            "accused_details": "Group of young men from nearby area",
            "evidence_summary": "Video recordings, complaint signed by multiple residents",
            "expected_sections": ["ipc_268", "ipc_290", "ipc_294"],
            "case_name": "Public Nuisance and Obscenity"
        },
        
        # Case 14: Forgery
        {
            "case_type": "Forgery",
            "offense_description": "Someone forged my signature on documents to transfer my property.",
            "query": "My signature was forged on property documents.",
            "incident_date": date(2025, 2, 15),
            "incident_location": "Property registration office, Indore",
            "victim_details": "Self, property owner",
            "accused_details": "Distant relative Mr. Mishra",
            "evidence_summary": "Original documents, forensic handwriting analysis",
            "expected_sections": ["ipc_463", "ipc_464", "ipc_468"],
            "case_name": "Forgery of Documents"
        },
        
        # Case 15: Extortion
        {
            "case_type": "Extortion",
            "offense_description": "I am receiving threatening calls demanding money, threatening to harm my family.",
            "query": "Someone is threatening me for money.",
            "incident_date": date(2025, 3, 17),
            "incident_location": "Phone calls received at home in Patna",
            "victim_details": "Self, a businessman",
            "accused_details": "Unknown caller using different phone numbers",
            "evidence_summary": "Call recordings, phone numbers, threat messages",
            "expected_sections": ["ipc_383", "ipc_384", "ipc_506"],
            "case_name": "Extortion through Threats"
        },
        
        # Case 16: Vehicle theft
        {
            "case_type": "Theft",
            "offense_description": "My car was stolen from outside my office building.",
            "query": "My car has been stolen.",
            "incident_date": date(2025, 3, 11),
            "incident_location": "Office parking, Noida",
            "victim_details": "Self",
            "accused_details": "Unknown",
            "evidence_summary": "CCTV footage from nearby buildings, car documents",
            "expected_sections": ["ipc_378", "ipc_379"],
            "case_name": "Vehicle Theft"
        },
        
        # Case 17: Identity theft
        {
            "case_type": "Identity Theft",
            "offense_description": "Someone used my personal information to apply for a loan and credit cards.",
            "query": "Someone has stolen my identity for financial fraud.",
            "incident_date": date(2025, 2, 20),
            "incident_location": "Online/Multiple locations",
            "victim_details": "Self",
            "accused_details": "Unknown",
            "evidence_summary": "Bank statements, loan applications, credit reports",
            "expected_sections": ["ipc_419", "ipc_420", "ipc_468"],
            "case_name": "Identity Theft and Financial Fraud"
        },
        
        # Case 18: Trespassing
        {
            "case_type": "Trespassing",
            "offense_description": "A person repeatedly enters my property despite warnings not to do so.",
            "query": "Someone keeps trespassing on my property.",
            "incident_date": date(2025, 3, 16),
            "incident_location": "Private property, Chandigarh",
            "victim_details": "Self, property owner",
            "accused_details": "Neighbor, Mr. Singh",
            "evidence_summary": "CCTV footage, witness statements, previous warnings",
            "expected_sections": ["ipc_441", "ipc_447"],
            "case_name": "Criminal Trespassing"
        },
        
        # Case 19: Wrongful restraint
        {
            "case_type": "Wrongful Restraint",
            "offense_description": "Security guards prevented me from leaving a building for several hours.",
            "query": "I was wrongfully detained by security guards.",
            "incident_date": date(2025, 3, 9),
            "incident_location": "Shopping Mall, Surat",
            "victim_details": "Self",
            "accused_details": "Security personnel of ABC Mall",
            "evidence_summary": "CCTV footage, witness statements",
            "expected_sections": ["ipc_339", "ipc_341"],
            "case_name": "Wrongful Restraint by Security"
        },
        
        # Case 20: Cheating in business deal
        {
            "case_type": "Cheating",
            "offense_description": "A business partner took investment money but never started the promised business.",
            "query": "My business partner cheated me out of my investment.",
            "incident_date": date(2025, 2, 10),
            "incident_location": "Business meeting in Delhi",
            "victim_details": "Self, investor",
            "accused_details": "Mr. Kapoor, business partner",
            "evidence_summary": "Investment agreement, bank transfers, email communications",
            "expected_sections": ["ipc_415", "ipc_420", "ipc_406"],
            "case_name": "Business Investment Fraud"
        }
    ]
    
    return test_cases

def evaluate_case(processor, case):
    """
    Test a single case and return accuracy information
    """
    try:
        # Prepare case details for processing
        case_details = {
            "case_type": case["case_type"],
            "offense_description": case["offense_description"],
            "query": case["query"],
            "incident_date": case["incident_date"],
            "incident_location": case["incident_location"],
            "victim_details": case["victim_details"],
            "accused_details": case["accused_details"],
            "evidence_summary": case["evidence_summary"]
        }
        
        # Process the case
        logger.info(f"Processing test case: {case['case_name']}")
        results = processor.process_query(case_details)
        
        # Get the identified IPC sections
        identified_sections = [section['id'] for section in results['ipc_sections']]
        
        # Calculate section match statistics
        correct_sections = set(identified_sections).intersection(set(case["expected_sections"]))
        missed_sections = set(case["expected_sections"]) - set(identified_sections)
        extra_sections = set(identified_sections) - set(case["expected_sections"])
        
        precision = len(correct_sections) / len(identified_sections) if identified_sections else 0
        recall = len(correct_sections) / len(case["expected_sections"]) if case["expected_sections"] else 1
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # Detailed logging
        logger.info(f"Case: {case['case_name']}")
        logger.info(f"Expected sections: {case['expected_sections']}")
        logger.info(f"Identified sections: {identified_sections}")
        logger.info(f"Correct: {list(correct_sections)}, Missed: {list(missed_sections)}, Extra: {list(extra_sections)}")
        logger.info(f"Precision: {precision:.2f}, Recall: {recall:.2f}, F1: {f1_score:.2f}")
        
        # Consider case accurate if at least 70% of expected sections were found
        # and at least 70% of identified sections were expected
        accurate = precision >= 0.7 and recall >= 0.7
        
        return {
            "case_name": case["case_name"],
            "expected_sections": case["expected_sections"],
            "identified_sections": identified_sections,
            "correct_sections": list(correct_sections),
            "missed_sections": list(missed_sections),
            "extra_sections": list(extra_sections),
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "accurate": accurate
        }
    except Exception as e:
        logger.error(f"Error evaluating case {case['case_name']}: {str(e)}")
        return {
            "case_name": case["case_name"],
            "error": str(e),
            "accurate": False
        }

def evaluate_accuracy():
    """
    Test the model accuracy against the 20 test cases
    """
    test_cases = create_test_cases()
    processor = LegalQueryProcessor()
    
    logger.info(f"Starting accuracy evaluation with {len(test_cases)} test cases")
    
    results = []
    accurate_count = 0
    error_count = 0
    
    # Process each test case
    for i, case in enumerate(test_cases, 1):
        logger.info(f"Processing case {i}/{len(test_cases)}: {case['case_name']}")
        try:
            result = evaluate_case(processor, case)
            results.append(result)
            
            if result.get("accurate", False):
                accurate_count += 1
            if "error" in result:
                error_count += 1
                
        except Exception as e:
            logger.error(f"Fatal error processing case {case['case_name']}: {str(e)}")
            results.append({
                "case_name": case["case_name"],
                "error": str(e),
                "accurate": False
            })
            error_count += 1
    
    # Calculate overall accuracy
    accuracy = accurate_count / len(test_cases)
    logger.info(f"Overall accuracy: {accuracy:.2f} ({accurate_count}/{len(test_cases)} cases)")
    logger.info(f"Errors encountered: {error_count}")
    
    # Calculate average metrics
    avg_precision = sum(r.get("precision", 0) for r in results if "precision" in r) / len(results)
    avg_recall = sum(r.get("recall", 0) for r in results if "recall" in r) / len(results)
    avg_f1 = sum(r.get("f1_score", 0) for r in results if "f1_score" in r) / len(results)
    
    logger.info(f"Average Precision: {avg_precision:.2f}")
    logger.info(f"Average Recall: {avg_recall:.2f}")
    logger.info(f"Average F1 Score: {avg_f1:.2f}")
    
    # Save the evaluation results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"accuracy_results_{timestamp}.json"
    
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "total_cases": len(test_cases),
            "accurate_cases": accurate_count,
            "accuracy": accuracy,
            "avg_precision": avg_precision,
            "avg_recall": avg_recall,
            "avg_f1": avg_f1,
            "case_results": results
        }, f, indent=2, default=str)
    
    logger.info(f"Results saved to {results_file}")
    
    return accuracy, results

if __name__ == "__main__":
    logger.info("Starting enhanced accuracy testing")
    accuracy, results = evaluate_accuracy()
    logger.info(f"Testing completed with accuracy: {accuracy:.2f}")
    
    # Print summary table for console output
    print("\n===== ACCURACY TEST RESULTS =====")
    print(f"Overall Accuracy: {accuracy:.2f} ({results.count(True)}/{len(results)} cases)")
    print("\nCase-by-case summary:")
    print(f"{'CASE NAME':<30} | {'RESULT':<10} | {'PRECISION':<10} | {'RECALL':<10} | {'F1 SCORE':<10}")
    print("-" * 80)
    
    for result in results:
        case_name = result.get("case_name", "Unknown")
        status = "ACCURATE" if result.get("accurate", False) else "FAILED"
        precision = f"{result.get('precision', 0):.2f}" if "precision" in result else "N/A"
        recall = f"{result.get('recall', 0):.2f}" if "recall" in result else "N/A"
        f1 = f"{result.get('f1_score', 0):.2f}" if "f1_score" in result else "N/A"
        
        print(f"{case_name:<30} | {status:<10} | {precision:<10} | {recall:<10} | {f1:<10}")
    
    print("\n===============================")