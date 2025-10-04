from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import sqlite3
import json

app = FastAPI(title="Krakowskie Cyfrowe Centrum Wolontariatu API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database connection
def get_db():
    conn = sqlite3.connect('volunteer.db')
    conn.row_factory = sqlite3.Row
    return conn


# Enums
class UserType(str, Enum):
    volunteer = "volunteer"
    organization = "organization"
    coordinator = "coordinator"


class InitiativeStatus(str, Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class ParticipationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"


# Pydantic Models
class InitiativeCreate(BaseModel):
    title: str
    description: str
    category: str
    location: str
    start_date: str
    end_date: str
    hours_required: int
    spots_available: int
    requirements: Optional[str] = None
    organization_id: int


class ParticipationApply(BaseModel):
    volunteer_id: int
    initiative_id: int
    message: Optional[str] = None


class ParticipationApprove(BaseModel):
    status: ParticipationStatus
    hours_completed: Optional[int] = None


class CertificateCreate(BaseModel):
    participation_id: int
    organization_id: int


# === ENDPOINTS ===

@app.get("/")
def root():
    return {
        "message": "Krakowskie Cyfrowe Centrum Wolontariatu API",
        "version": "1.0",
        "endpoints": {
            "initiatives": "/initiatives",
            "users": "/users",
            "statistics": "/statistics"
        }
    }


# === INITIATIVES ENDPOINTS ===

@app.get("/initiatives")
def get_initiatives(
        category: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = "active",
        organization_id: Optional[int] = None
):
    """Pobierz listę inicjatyw z filtrowaniem"""
    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT i.*, u.name as organization_name, u.email as organization_email
        FROM initiatives i
        JOIN users u ON i.organization_id = u.id
        WHERE 1=1
    """
    params = []

    if category:
        query += " AND i.category = ?"
        params.append(category)
    if location:
        query += " AND i.location LIKE ?"
        params.append(f"%{location}%")
    if status:
        query += " AND i.status = ?"
        params.append(status)
    if organization_id:
        query += " AND i.organization_id = ?"
        params.append(organization_id)

    query += " ORDER BY i.start_date DESC"

    cursor.execute(query, params)
    initiatives = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"initiatives": initiatives, "count": len(initiatives)}


@app.get("/initiatives/{initiative_id}")
def get_initiative(initiative_id: int):
    """Pobierz szczegóły inicjatywy"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.*, u.name as organization_name, u.email as organization_email, u.phone
        FROM initiatives i
        JOIN users u ON i.organization_id = u.id
        WHERE i.id = ?
    """, (initiative_id,))

    initiative = cursor.fetchone()
    if not initiative:
        conn.close()
        raise HTTPException(status_code=404, detail="Inicjatywa nie znaleziona")

    # Pobierz liczbę zgłoszeń
    cursor.execute("""
        SELECT COUNT(*) as applications
        FROM participations
        WHERE initiative_id = ? AND status IN ('pending', 'approved')
    """, (initiative_id,))

    stats = cursor.fetchone()
    result = dict(initiative)
    result['applications_count'] = stats['applications']

    conn.close()
    return result


@app.post("/initiatives")
def create_initiative(initiative: InitiativeCreate):
    """Utwórz nową inicjatywę (dla organizacji)"""
    conn = get_db()
    cursor = conn.cursor()

    # Sprawdź czy organizacja istnieje
    cursor.execute("SELECT * FROM users WHERE id = ? AND user_type = 'organization'",
                   (initiative.organization_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Organizacja nie znaleziona")

    cursor.execute("""
        INSERT INTO initiatives 
        (title, description, category, location, start_date, end_date, 
         hours_required, spots_available, requirements, organization_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
    """, (
        initiative.title, initiative.description, initiative.category,
        initiative.location, initiative.start_date, initiative.end_date,
        initiative.hours_required, initiative.spots_available,
        initiative.requirements, initiative.organization_id
    ))

    conn.commit()
    initiative_id = cursor.lastrowid
    conn.close()

    return {"message": "Inicjatywa utworzona", "initiative_id": initiative_id}


@app.post("/initiatives/{initiative_id}/apply")
def apply_to_initiative(initiative_id: int, application: ParticipationApply):
    """Zgłoś się do inicjatywy (dla wolontariusza)"""
    conn = get_db()
    cursor = conn.cursor()

    # Sprawdź czy inicjatywa istnieje
    cursor.execute("SELECT * FROM initiatives WHERE id = ?", (initiative_id,))
    initiative = cursor.fetchone()
    if not initiative:
        conn.close()
        raise HTTPException(status_code=404, detail="Inicjatywa nie znaleziona")

    # Sprawdź czy wolontariusz już się zgłosił
    cursor.execute("""
        SELECT * FROM participations 
        WHERE volunteer_id = ? AND initiative_id = ?
    """, (application.volunteer_id, initiative_id))

    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Już zgłosiłeś się do tej inicjatywy")

    # Dodaj zgłoszenie
    cursor.execute("""
        INSERT INTO participations 
        (volunteer_id, initiative_id, status, applied_date, message)
        VALUES (?, ?, 'pending', ?, ?)
    """, (application.volunteer_id, initiative_id,
          datetime.now().isoformat(), application.message))

    conn.commit()
    participation_id = cursor.lastrowid
    conn.close()

    return {"message": "Zgłoszenie wysłane", "participation_id": participation_id}


# === VOLUNTEERS ENDPOINTS ===

@app.get("/volunteers/{volunteer_id}/participations")
def get_volunteer_participations(volunteer_id: int):
    """Pobierz uczestnictwa wolontariusza"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*, i.title as initiative_title, i.category, 
               i.location, i.start_date, i.end_date,
               u.name as organization_name
        FROM participations p
        JOIN initiatives i ON p.initiative_id = i.id
        JOIN users u ON i.organization_id = u.id
        WHERE p.volunteer_id = ?
        ORDER BY p.applied_date DESC
    """, (volunteer_id,))

    participations = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"participations": participations, "count": len(participations)}


# === ORGANIZATIONS ENDPOINTS ===

@app.get("/organizations/{org_id}/initiatives")
def get_organization_initiatives(org_id: int):
    """Pobierz inicjatywy organizacji"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.*,
               COUNT(DISTINCT CASE WHEN p.status = 'pending' THEN p.id END) as pending_applications,
               COUNT(DISTINCT CASE WHEN p.status = 'approved' THEN p.id END) as approved_volunteers
        FROM initiatives i
        LEFT JOIN participations p ON i.id = p.initiative_id
        WHERE i.organization_id = ?
        GROUP BY i.id
        ORDER BY i.start_date DESC
    """, (org_id,))

    initiatives = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"initiatives": initiatives, "count": len(initiatives)}


@app.get("/organizations/{org_id}/applications")
def get_organization_applications(org_id: int, status: Optional[str] = None):
    """Pobierz zgłoszenia do inicjatyw organizacji"""
    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT p.*, i.title as initiative_title,
               v.name as volunteer_name, v.email as volunteer_email,
               v.phone as volunteer_phone, v.age_category
        FROM participations p
        JOIN initiatives i ON p.initiative_id = i.id
        JOIN users v ON p.volunteer_id = v.id
        WHERE i.organization_id = ?
    """
    params = [org_id]

    if status:
        query += " AND p.status = ?"
        params.append(status)

    query += " ORDER BY p.applied_date DESC"

    cursor.execute(query, params)
    applications = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"applications": applications, "count": len(applications)}


@app.put("/participations/{participation_id}/approve")
def approve_participation(participation_id: int, approval: ParticipationApprove):
    """Zatwierdź lub odrzuć zgłoszenie wolontariusza"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM participations WHERE id = ?", (participation_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Zgłoszenie nie znalezione")

    update_fields = ["status = ?"]
    params = [approval.status]

    if approval.hours_completed is not None:
        update_fields.append("hours_completed = ?")
        params.append(approval.hours_completed)

    if approval.status == "approved":
        update_fields.append("approved_date = ?")
        params.append(datetime.now().isoformat())

    params.append(participation_id)

    cursor.execute(f"""
        UPDATE participations 
        SET {', '.join(update_fields)}
        WHERE id = ?
    """, params)

    conn.commit()
    conn.close()

    return {"message": "Status zaktualizowany"}


# === CERTIFICATES ENDPOINTS ===

@app.post("/certificates")
def create_certificate(cert: CertificateCreate):
    """Wygeneruj zaświadczenie dla wolontariusza"""
    conn = get_db()
    cursor = conn.cursor()

    # Pobierz szczegóły uczestnictwa
    cursor.execute("""
        SELECT p.*, i.title as initiative_title, i.description,
               i.start_date, i.end_date, i.category,
               v.name as volunteer_name, o.name as organization_name
        FROM participations p
        JOIN initiatives i ON p.initiative_id = i.id
        JOIN users v ON p.volunteer_id = v.id
        JOIN users o ON i.organization_id = o.id
        WHERE p.id = ? AND p.status = 'completed'
    """, (cert.participation_id,))

    participation = cursor.fetchone()
    if not participation:
        conn.close()
        raise HTTPException(status_code=404,
                            detail="Uczestnictwo nie znalezione lub nieukończone")

    # Utwórz zaświadczenie
    cursor.execute("""
        INSERT INTO certificates 
        (participation_id, volunteer_id, organization_id, issued_date, 
         hours_completed, certificate_data)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        cert.participation_id,
        participation['volunteer_id'],
        cert.organization_id,
        datetime.now().isoformat(),
        participation['hours_completed'],
        json.dumps(dict(participation))
    ))

    conn.commit()
    certificate_id = cursor.lastrowid
    conn.close()

    return {
        "message": "Zaświadczenie wygenerowane",
        "certificate_id": certificate_id,
        "volunteer_name": participation['volunteer_name'],
        "initiative_title": participation['initiative_title'],
        "hours": participation['hours_completed']
    }


@app.get("/volunteers/{volunteer_id}/certificates")
def get_volunteer_certificates(volunteer_id: int):
    """Pobierz zaświadczenia wolontariusza"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.*, i.title as initiative_title, o.name as organization_name
        FROM certificates c
        JOIN participations p ON c.participation_id = p.id
        JOIN initiatives i ON p.initiative_id = i.id
        JOIN users o ON c.organization_id = o.id
        WHERE c.volunteer_id = ?
        ORDER BY c.issued_date DESC
    """, (volunteer_id,))

    certificates = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"certificates": certificates, "count": len(certificates)}


# === COORDINATORS ENDPOINTS ===

@app.get("/coordinators/{coordinator_id}/students")
def get_coordinator_students(coordinator_id: int):
    """Pobierz uczniów przypisanych do koordynatora"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.*,
               COUNT(DISTINCT p.id) as total_participations,
               SUM(CASE WHEN p.status = 'completed' THEN p.hours_completed ELSE 0 END) as total_hours
        FROM users u
        LEFT JOIN participations p ON u.id = p.volunteer_id
        WHERE u.user_type = 'volunteer' AND u.school_id = 
              (SELECT school_id FROM users WHERE id = ?)
        GROUP BY u.id
    """, (coordinator_id,))

    students = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"students": students, "count": len(students)}


@app.get("/coordinators/{coordinator_id}/reports")
def get_coordinator_reports(coordinator_id: int):
    """Wygeneruj raport dla koordynatora"""
    conn = get_db()
    cursor = conn.cursor()

    # Pobierz szkołę koordynatora
    cursor.execute("SELECT school_id FROM users WHERE id = ?", (coordinator_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="Koordynator nie znaleziony")

    school_id = result['school_id']

    # Statystyki uczniów
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT u.id) as total_students,
            COUNT(DISTINCT p.id) as total_participations,
            SUM(CASE WHEN p.status = 'completed' THEN p.hours_completed ELSE 0 END) as total_hours,
            COUNT(DISTINCT c.id) as total_certificates
        FROM users u
        LEFT JOIN participations p ON u.id = p.volunteer_id
        LEFT JOIN certificates c ON u.id = c.volunteer_id
        WHERE u.school_id = ? AND u.user_type = 'volunteer'
    """, (school_id,))

    stats = dict(cursor.fetchone())

    # Najpopularniejsze kategorie
    cursor.execute("""
        SELECT i.category, COUNT(*) as count
        FROM participations p
        JOIN initiatives i ON p.initiative_id = i.id
        JOIN users u ON p.volunteer_id = u.id
        WHERE u.school_id = ?
        GROUP BY i.category
        ORDER BY count DESC
        LIMIT 5
    """, (school_id,))

    categories = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "school_id": school_id,
        "statistics": stats,
        "popular_categories": categories,
        "generated_at": datetime.now().isoformat()
    }


# === USERS ENDPOINTS ===

@app.get("/users")
def get_users(user_type: Optional[str] = None):
    """Pobierz listę użytkowników"""
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE 1=1"
    params = []

    if user_type:
        query += " AND user_type = ?"
        params.append(user_type)

    cursor.execute(query, params)
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"users": users, "count": len(users)}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Pobierz szczegóły użytkownika"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")

    conn.close()
    return dict(user)


# === STATISTICS ENDPOINTS ===

@app.get("/statistics")
def get_statistics():
    """Pobierz statystyki platformy"""
    conn = get_db()
    cursor = conn.cursor()

    # Podstawowe statystyki
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM users WHERE user_type = 'volunteer') as volunteers,
            (SELECT COUNT(*) FROM users WHERE user_type = 'organization') as organizations,
            (SELECT COUNT(*) FROM users WHERE user_type = 'coordinator') as coordinators,
            (SELECT COUNT(*) FROM initiatives WHERE status = 'active') as active_initiatives,
            (SELECT COUNT(*) FROM participations WHERE status = 'completed') as completed_participations,
            (SELECT SUM(hours_completed) FROM participations WHERE status = 'completed') as total_hours
    """)

    stats = dict(cursor.fetchone())

    # Inicjatywy według kategorii
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM initiatives
        GROUP BY category
        ORDER BY count DESC
    """)

    categories = [dict(row) for row in cursor.fetchall()]

    # Ostatnie inicjatywy
    cursor.execute("""
        SELECT i.title, i.category, i.start_date, u.name as organization
        FROM initiatives i
        JOIN users u ON i.organization_id = u.id
        ORDER BY i.created_at DESC
        LIMIT 5
    """)

    recent = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "overview": stats,
        "categories": categories,
        "recent_initiatives": recent
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)