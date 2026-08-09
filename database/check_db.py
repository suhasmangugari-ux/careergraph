# database/check_db.py
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USER = os.getenv("COGNODB_USERNAME", "cognodb")
PASSWORD = os.getenv("COGNODB_PASSWORD")

def verify_data():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    with driver.session() as session:
        print("\n===DATABASE NODE COUNTS ===")
        # Count total nodes by label
        result = session.run("""
            MATCH (n)
            RETURN labels(n)[0] AS Label, count(n) AS Count
            ORDER BY Count DESC
        """)
        for record in result:
            print(f"• {record['Label']}: {record['Count']} nodes")

        print("\n=== ADDED STUDENTS ===")
        students = session.run("MATCH (s:Student) RETURN s.id AS id, s.name AS name ORDER BY s.id")
        for record in students:
            print(f"[{record['id']}] {record['name']}")

        print("\n===ADDED COMPANIES & JOBS ===")
        companies = session.run("""
            MATCH (c:Company)-[:OFFERS]->(j:Job)
            RETURN c.name AS company, j.title AS job
        """)
        for record in companies:
            print(f"• {record['company']} -> Offering: {record['job']}")

    driver.close()

if __name__ == "__main__":
    verify_data()