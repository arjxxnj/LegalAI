
from app import app, db
from models import User, Case
from nlp_processor import LegalQueryProcessor
from datetime import datetime
import json

def create_test_cases():
    """Create a set of test cases with known expected outcomes"""
    test_cases = [
        {
            "case_type": "Murder",
            "offense_description": "Intentional shooting resulting in death",
            "expected_sections": ["ipc_302", "ipc_304", "ipc_307"],
        },
        {
            "case_type": "Theft",
            "offense_description": "Stole mobile phone from shop counter",
            "expected_sections": ["ipc_378", "ipc_379"],
        },
        {
            "case_type": "Assault",
            "offense_description": "Physical attack causing serious injuries",
            "expected_sections": ["ipc_323", "ipc_324", "ipc_325"],
        },
        {
            "case_type": "Robbery",
            "offense_description": "Armed theft with violence at a jewelry store",
            "expected_sections": ["ipc_392", "ipc_397", "ipc_398"],
        },
        {
            "case_type": "Kidnapping",
            "offense_description": "Forcibly took minor from school premises",
            "expected_sections": ["ipc_359", "ipc_363", "ipc_365"],
        },
        {
            "case_type": "Criminal Intimidation",
            "offense_description": "Threatening messages sent to victim's phone",
            "expected_sections": ["ipc_503", "ipc_506", "ipc_507"],
        },
        {
            "case_type": "House Breaking",
            "offense_description": "Broke into residence at night and stole valuables",
            "expected_sections": ["ipc_445", "ipc_446", "ipc_380"],
        },
        {
            "case_type": "Forgery",
            "offense_description": "Created fake documents for property transfer",
            "expected_sections": ["ipc_463", "ipc_464", "ipc_468"],
        },
        {
            "case_type": "Criminal Conspiracy",
            "offense_description": "Planned and coordinated bank robbery with accomplices",
            "expected_sections": ["ipc_120A", "ipc_120B", "ipc_392"],
        },
        {
            "case_type": "Culpable Homicide",
            "offense_description": "Death caused by reckless driving",
            "expected_sections": ["ipc_299", "ipc_304A", "ipc_279"],
        },
        {
            "case_type": "Grievous Hurt",
            "offense_description": "Attacked victim with acid causing permanent disfigurement",
            "expected_sections": ["ipc_320", "ipc_326", "ipc_326A"],
        },
        {
            "case_type": "Cybercrime",
            "offense_description": "Hacked victim's bank account and transferred money",
            "expected_sections": ["ipc_420", "ipc_465", "ipc_468"],
        },
        {
            "case_type": "Gang Violence",
            "offense_description": "Group of people attacked shop with weapons",
            "expected_sections": ["ipc_147", "ipc_148", "ipc_149"],
        },
        {
            "case_type": "Extortion",
            "offense_description": "Demanded money with threats of violence",
            "expected_sections": ["ipc_383", "ipc_384", "ipc_385"],
        },
        {
            "case_type": "Criminal Trespass",
            "offense_description": "Entered private property at night with intent to commit offense",
            "expected_sections": ["ipc_441", "ipc_447", "ipc_448"],
        },
        {
            "case_type": "Domestic Violence",
            "offense_description": "Physical and mental abuse of spouse in shared household",
            "expected_sections": ["ipc_498A", "ipc_323", "ipc_506"],
        },
        {
            "case_type": "Cheating",
            "offense_description": "Fraudulent investment scheme causing financial loss",
            "expected_sections": ["ipc_415", "ipc_420", "ipc_421"],
        },
        {
            "case_type": "Public Nuisance",
            "offense_description": "Organizing illegal gathering causing disturbance",
            "expected_sections": ["ipc_268", "ipc_290", "ipc_291"],
        },
        {
            "case_type": "Defamation",
            "offense_description": "Published false statements damaging reputation",
            "expected_sections": ["ipc_499", "ipc_500", "ipc_501"],
        },
        {
            "case_type": "Attempt to Murder",
            "offense_description": "Stabbed victim with intent to kill but victim survived",
            "expected_sections": ["ipc_307", "ipc_324", "ipc_326"],
        }
    ]
    return test_cases

def evaluate_accuracy():
    """Test the model accuracy against known cases"""
    processor = LegalQueryProcessor()
    test_cases = create_test_cases()
    
    total_cases = len(test_cases)
    correct_predictions = 0
    section_accuracy = []
    
    print("\nTesting Model Accuracy...")
    print("-" * 50)
    
    for idx, test_case in enumerate(test_cases, 1):
        # Process the test case
        case_details = {
            "case_type": test_case["case_type"],
            "offense_description": test_case["offense_description"],
            "incident_date": datetime.now().date(),
            "incident_location": "Test Location",
            "query": test_case["offense_description"]
        }
        
        # Get model predictions
        results = processor.process_query(case_details)
        predicted_sections = [section['id'] for section in results['ipc_sections']]
        
        # Calculate weighted accuracy for this case
        correct_sections = set(predicted_sections) & set(test_case["expected_sections"])
        false_positives = set(predicted_sections) - set(test_case["expected_sections"])
        false_negatives = set(test_case["expected_sections"]) - set(predicted_sections)
        
        # Weights for different types of matches/mismatches
        correct_weight = 1.0
        false_positive_penalty = 0.3
        false_negative_penalty = 0.3
        
        # Calculate weighted score
        weighted_score = (
            len(correct_sections) * correct_weight -
            len(false_positives) * false_positive_penalty -
            len(false_negatives) * false_negative_penalty
        )
        
        max_possible_score = len(test_case["expected_sections"]) * correct_weight
        case_accuracy = max(0, weighted_score / max_possible_score) if max_possible_score > 0 else 0
        section_accuracy.append(case_accuracy)
        
        # Use a more nuanced threshold for correct predictions
        if case_accuracy >= 0.7:  # Increased threshold for higher quality
            correct_predictions += 1
            
        # Print detailed analysis for each case
        print(f"\nDetailed Analysis for Case {idx}:")
        print(f"Correct Matches: {len(correct_sections)}")
        print(f"False Positives: {len(false_positives)}")
        print(f"False Negatives: {len(false_negatives)}")
        print(f"Weighted Score: {weighted_score:.2f}")
        print(f"Max Possible Score: {max_possible_score:.2f}")
            
        print(f"\nTest Case {idx}:")
        print(f"Type: {test_case['case_type']}")
        print(f"Expected Sections: {test_case['expected_sections']}")
        print(f"Predicted Sections: {predicted_sections}")
        print(f"Case Accuracy: {case_accuracy:.2%}")
    
    # Calculate overall accuracy
    overall_accuracy = correct_predictions / total_cases
    avg_section_accuracy = sum(section_accuracy) / len(section_accuracy)
    
    print("\nOverall Results:")
    print("-" * 50)
    print(f"Total Test Cases: {total_cases}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Overall Accuracy: {overall_accuracy:.2%}")
    print(f"Average Section Accuracy: {avg_section_accuracy:.2%}")
    
    return {
        "overall_accuracy": overall_accuracy,
        "avg_section_accuracy": avg_section_accuracy,
        "total_cases": total_cases,
        "correct_predictions": correct_predictions
    }

if __name__ == "__main__":
    with app.app_context():
        results = evaluate_accuracy()
        print("\nTest completed.")
