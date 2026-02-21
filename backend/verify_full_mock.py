import requests
import json

def verify_full_mock():
    url = "http://localhost:8000/api/questions"
    params = {
        "subject": "Full NEET",
        "duration": 12000 # 3h 20m
    }
    
    try:
        response = requests.get(url, params=params)
        questions = response.json()
        
        print(f"Total Questions: {len(questions)}")
        
        distribution = {
            "Physics": {"A": 0, "B": 0},
            "Chemistry": {"A": 0, "B": 0},
            "Botany": {"A": 0, "B": 0},
            "Zoology": {"A": 0, "B": 0},
            "Other": 0
        }
        
        for q in questions:
            sub = q.get("subsection") or q.get("subject")
            sec = q.get("section", "A")
            
            if sub in distribution:
                distribution[sub][sec] += 1
            else:
                distribution["Other"] += 1
                print(f"Unknown Sub: {sub}")
                
        print(json.dumps(distribution, indent=2))
        
        # Assertions
        assert len(questions) == 200, "Total questions should be 200"
        assert distribution["Physics"]["A"] == 35
        assert distribution["Physics"]["B"] == 15
        assert distribution["Chemistry"]["A"] == 35
        assert distribution["Chemistry"]["B"] == 15
        assert distribution["Botany"]["A"] == 35
        assert distribution["Botany"]["B"] == 15
        assert distribution["Zoology"]["A"] == 35
        assert distribution["Zoology"]["B"] == 15
        
        print("VERIFICATION SUCCESSFUL: Full NEET Pattern confirmed.")
        
    except Exception as e:
        print(f"VERIFICATION FAILED: {e}")

if __name__ == "__main__":
    verify_full_mock()
