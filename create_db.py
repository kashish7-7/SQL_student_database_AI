from sqlalchemy import text
from database import engine

SAMPLE_STUDENTS = [
    ("Ananya", "Sharma", "ananya.sharma@example.com", "RA23456785"),
    ("Arjun", "Mehta", "arjun.mehta@example.com", "RA23456786"),
    ("Priya", "Nair", "priya.nair@example.com", "RA23456787"),
    ("Rahul", "Verma", "rahul.verma@example.com", "RA23456788"),
    ("Sneha", "Patil", "sneha.patil@example.com", "RA23456790"),
    ("Aditya", "Reddy", "aditya.reddy@example.com", "RA23456791"),
    ("Ishita", "Gupta", "ishita.gupta@example.com", "RA23456792"),
    ("Vikram", "Rao", "vikram.rao@example.com", "RA23456793"),
    ("Meera", "Iyer", "meera.iyer@example.com", "RA23456794"),
    ("Kashish", "Sah", "kashish@example.com", "RA23456789"),
    ("Karan", "Malhotra", "karan.malhotra@example.com", "RA23456795"),
    ("Divya", "Krishnan", "divya.krishnan@example.com", "RA23456796"),
    ("Nikhil", "Joshi", "nikhil.joshi@example.com", "RA23456797"),
    ("Aarav", "Kapoor", "aarav.kapoor@example.com", "RA23456798"),
    ("Pooja", "Menon", "pooja.menon@example.com", "RA23456799"),
    ("Varun", "Chopra", "varun.chopra@example.com", "RA23456800"),
    ("Riya", "Desai", "riya.desai@example.com", "RA23456801"),
    ("Siddharth", "Mishra", "siddharth.mishra@example.com", "RA23456802"),
    ("Neha", "Kulkarni", "neha.kulkarni@example.com", "RA23456803"),
    ("Yash", "Agarwal", "yash.agarwal@example.com", "RA23456804"),
    ("Aishwarya", "Pillai", "aishwarya.pillai@example.com", "RA23456805"),
    ("Manish", "Yadav", "manish.yadav@example.com", "RA23456806"),
    ("Tanvi", "Bhat", "tanvi.bhat@example.com", "RA23456807"),
    ("Dev", "Chatterjee", "dev.chatterjee@example.com", "RA23456808"),
    ("Simran", "Kaur", "simran.kaur@example.com", "RA23456809"),
    ("Abhishek", "Sinha", "abhishek.sinha@example.com", "RA23456810"),
]


def create_database():
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS students (
                student_id SERIAL PRIMARY KEY,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                email VARCHAR(100),
                register_number VARCHAR(20),
                age INTEGER,
                religion VARCHAR(50),
                cgpa DECIMAL(3,2)
            )
        """))

        existing_regs = {
            row[0]
            for row in connection.execute(
                text("SELECT register_number FROM students WHERE register_number IS NOT NULL")
            ).fetchall()
        }

        missing_students = [
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "register_number": register_number,
            }
            for first_name, last_name, email, register_number in SAMPLE_STUDENTS
            if register_number not in existing_regs
        ]

        if missing_students:
            connection.execute(
                text("""
                    INSERT INTO students (first_name, last_name, email, register_number)
                    VALUES (:first_name, :last_name, :email, :register_number)
                """),
                missing_students,
            )

    print("Database and student records are ready!")


if __name__ == "__main__":
    create_database()
