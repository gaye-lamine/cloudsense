from backend.models.database import SessionLocal, AnomalyRecord, ProposedFixRecord

def delete_i81m32f5():
    db = SessionLocal()
    try:
        anoms = db.query(AnomalyRecord).filter(AnomalyRecord.instance_id == "i-81m32f5").all()
        anom_ids = [a.id for a in anoms]
        num_fixes = db.query(ProposedFixRecord).filter(ProposedFixRecord.anomaly_id.in_(anom_ids)).delete(synchronize_session=False)
        num_anoms = db.query(AnomalyRecord).filter(AnomalyRecord.instance_id == "i-81m32f5").delete(synchronize_session=False)
        db.commit()
        print(f"Success! Deleted {num_anoms} anomalies and {num_fixes} proposed fixes for i-81m32f5.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    delete_i81m32f5()
