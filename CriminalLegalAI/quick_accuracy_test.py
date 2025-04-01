#!/usr/bin/env python3
"""
Quick accuracy test script for the Legal Assistant application.
Tests the system with 5 representative cases and measures accuracy against expected outputs.
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
    """Create a set of 5 representative test cases with known expected outcomes"""
    
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
        
        # Case 3: Assault with weapon
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
        
        # Case 4: Domestic violence
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
        
        # Case 5: Online fraud
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
    Test the model accuracy against the 5 test cases
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
    
    # Print summary table for console output
    print("\n===== ACCURACY TEST RESULTS =====")
    print(f"Overall Accuracy: {accuracy:.2f} ({accurate_count}/{len(test_cases)} cases)")
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
    
    return accuracy, results

if __name__ == "__main__":
    logger.info("Starting quick accuracy testing")
    accuracy, results = evaluate_accuracy()
    logger.info(f"Testing completed with accuracy: {accuracy:.2f}")