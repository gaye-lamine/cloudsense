from backend.models.database import SessionLocal, AnomalyRecord, ProposedFixRecord

def clean_db():
    db = SessionLocal()
    try:
        num_fixes = db.query(ProposedFixRecord).delete()
        num_anoms = db.query(AnomalyRecord).delete()
        db.commit()
        print(f"Success! Wiped {num_anoms} anomalies and {num_fixes} proposed fixes from the database.")
    except Exception as e:
        db.rollback()
        print(f"Error wiping database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clean_db()
