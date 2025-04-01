
from app import app, db
from models import User, Case
from datetime import datetime

def test_murder_case():
    with app.app_context():
        # Create test user
        test_user = User(
            name="Test User",
            email="test@example.com",
            phone="9876543210"
        )
        db.session.add(test_user)
        db.session.commit()

        # Create murder case
        test_case = Case(
            user_id=test_user.id,
            case_type="Murder",
            offense_description="On April 1st, 2024, at approximately 10:30 PM, the accused allegedly shot the victim with a firearm after a heated argument at their residence. The victim was pronounced dead at the scene. The incident was witnessed by two neighbors who heard the argument and gunshot.",
            incident_date=datetime.strptime("2024-04-01", "%Y-%m-%d").date(),
            incident_location="123 Test Street, Test City",
            victim_details="Male, age 35, local businessman",
            accused_details="Male, age 40, former business partner of the victim",
            evidence_summary="1. Recovered firearm from the scene\n2. Two eyewitness statements\n3. CCTV footage from nearby building\n4. Forensic evidence including gunshot residue\n5. Audio recording of argument from neighbor's phone",
            query="What are the applicable sections and potential legal consequences for this murder case?"
        )
        db.session.add(test_case)
        db.session.commit()
        
        return test_case.id

if __name__ == "__main__":
    case_id = test_murder_case()
    print(f"Test murder case created with ID: {case_id}")
