import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

from infrastructure.database.db_engine import AsyncSessionLocal, engine, Base
from infrastructure.database.orm import (
    StudentTable,
    SchoolTable,
    SchoolStudentsTable,
    InvoiceTable,
    PaymentTable,
)
from domain.models.invoice import InvoiceStatus
from domain.models.student import StudentStatus


async def populate_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        schools = [
            SchoolTable(
                ref="SCH001",
                name="Lincoln High School",
                created_at=datetime.now() - timedelta(days=1095),
            ),
            SchoolTable(
                ref="SCH002",
                name="Washington Academy",
                created_at=datetime.now() - timedelta(days=730),
            ),
            SchoolTable(
                ref="SCH003",
                name="Jefferson Elementary",
                created_at=datetime.now() - timedelta(days=365),
            ),
            SchoolTable(
                ref="SCH004",
                name="Roosevelt Middle School",
                created_at=datetime.now() - timedelta(days=180),
            ),
        ]
        session.add_all(schools)
        await session.flush()
        
        students = [
            StudentTable(first_name="Alice", last_name="Johnson", email="alice.johnson@email.com", age=16, created_at=datetime.now() - timedelta(days=900)),
            StudentTable(first_name="Bob", last_name="Smith", email="bob.smith@email.com", age=15, created_at=datetime.now() - timedelta(days=850)),
            StudentTable(first_name="Charlie", last_name="Brown", email="charlie.brown@email.com", age=17, created_at=datetime.now() - timedelta(days=800)),
            StudentTable(first_name="Diana", last_name="Martinez", email="diana.martinez@email.com", age=14, created_at=datetime.now() - timedelta(days=750)),
            StudentTable(first_name="Ethan", last_name="Davis", email="ethan.davis@email.com", age=16, created_at=datetime.now() - timedelta(days=700)),
            StudentTable(first_name="Fiona", last_name="Wilson", email="fiona.wilson@email.com", age=15, created_at=datetime.now() - timedelta(days=650)),
            StudentTable(first_name="George", last_name="Garcia", email="george.garcia@email.com", age=13, created_at=datetime.now() - timedelta(days=600)),
            StudentTable(first_name="Hannah", last_name="Rodriguez", email="hannah.rodriguez@email.com", age=14, created_at=datetime.now() - timedelta(days=550)),
            StudentTable(first_name="Isaac", last_name="Lee", email="isaac.lee@email.com", age=17, created_at=datetime.now() - timedelta(days=500)),
            StudentTable(first_name="Julia", last_name="Anderson", email="julia.anderson@email.com", age=16, created_at=datetime.now() - timedelta(days=450)),
            StudentTable(first_name="Kevin", last_name="Taylor", email="kevin.taylor@email.com", age=15, created_at=datetime.now() - timedelta(days=400)),
            StudentTable(first_name="Laura", last_name="Thomas", email="laura.thomas@email.com", age=14, created_at=datetime.now() - timedelta(days=350)),
            StudentTable(first_name="Michael", last_name="Moore", email="michael.moore@email.com", age=13, created_at=datetime.now() - timedelta(days=300)),
            StudentTable(first_name="Nina", last_name="Jackson", email="nina.jackson@email.com", age=16, created_at=datetime.now() - timedelta(days=250)),
            StudentTable(first_name="Oliver", last_name="White", email="oliver.white@email.com", age=15, created_at=datetime.now() - timedelta(days=200)),
        ]
        session.add_all(students)
        await session.flush()
        
        # Create School-Student relationships with history
        # Simulate students transferring between schools
        school_students = [
            # Alice: Started at Lincoln, transferred to Washington, currently active
            SchoolStudentsTable(school_id=schools[0].id, student_id=students[0].id, date_joined=datetime.now() - timedelta(days=900), status=StudentStatus.DEACTIVATED.value),
            SchoolStudentsTable(school_id=schools[1].id, student_id=students[0].id, date_joined=datetime.now() - timedelta(days=400), status=StudentStatus.ACTIVE.value),
            
            # Bob: Only at Lincoln, active
            SchoolStudentsTable(school_id=schools[0].id, student_id=students[1].id, date_joined=datetime.now() - timedelta(days=850), status=StudentStatus.ACTIVE.value),
            
            # Charlie: Started at Jefferson, transferred to Lincoln, currently active
            SchoolStudentsTable(school_id=schools[2].id, student_id=students[2].id, date_joined=datetime.now() - timedelta(days=800), status=StudentStatus.DEACTIVATED.value),
            SchoolStudentsTable(school_id=schools[0].id, student_id=students[2].id, date_joined=datetime.now() - timedelta(days=300), status=StudentStatus.ACTIVE.value),
            
            # Diana: Only at Washington, active
            SchoolStudentsTable(school_id=schools[1].id, student_id=students[3].id, date_joined=datetime.now() - timedelta(days=750), status=StudentStatus.ACTIVE.value),
            
            # Ethan: At Roosevelt, deactivated (graduated/left)
            SchoolStudentsTable(school_id=schools[3].id, student_id=students[4].id, date_joined=datetime.now() - timedelta(days=700), status=StudentStatus.DEACTIVATED.value),
            
            # Fiona: At Jefferson, active
            SchoolStudentsTable(school_id=schools[2].id, student_id=students[5].id, date_joined=datetime.now() - timedelta(days=650), status=StudentStatus.ACTIVE.value),
            
            # George: At Lincoln, active
            SchoolStudentsTable(school_id=schools[0].id, student_id=students[6].id, date_joined=datetime.now() - timedelta(days=600), status=StudentStatus.ACTIVE.value),
            
            # Hannah: At Washington, active
            SchoolStudentsTable(school_id=schools[1].id, student_id=students[7].id, date_joined=datetime.now() - timedelta(days=550), status=StudentStatus.ACTIVE.value),
            
            # Isaac: Started at Roosevelt, transferred to Washington
            SchoolStudentsTable(school_id=schools[3].id, student_id=students[8].id, date_joined=datetime.now() - timedelta(days=500), status=StudentStatus.DEACTIVATED.value),
            SchoolStudentsTable(school_id=schools[1].id, student_id=students[8].id, date_joined=datetime.now() - timedelta(days=200), status=StudentStatus.ACTIVE.value),
            
            # Julia: At Jefferson, active
            SchoolStudentsTable(school_id=schools[2].id, student_id=students[9].id, date_joined=datetime.now() - timedelta(days=450), status=StudentStatus.ACTIVE.value),
            
            # Kevin: At Lincoln, active
            SchoolStudentsTable(school_id=schools[0].id, student_id=students[10].id, date_joined=datetime.now() - timedelta(days=400), status=StudentStatus.ACTIVE.value),
            
            # Laura: At Roosevelt, active
            SchoolStudentsTable(school_id=schools[3].id, student_id=students[11].id, date_joined=datetime.now() - timedelta(days=350), status=StudentStatus.ACTIVE.value),
            
            # Michael: At Jefferson, deactivated
            SchoolStudentsTable(school_id=schools[2].id, student_id=students[12].id, date_joined=datetime.now() - timedelta(days=300), status=StudentStatus.DEACTIVATED.value),
            
            # Nina: At Washington, active
            SchoolStudentsTable(school_id=schools[1].id, student_id=students[13].id, date_joined=datetime.now() - timedelta(days=250), status=StudentStatus.ACTIVE.value),
            
            # Oliver: At Roosevelt, active
            SchoolStudentsTable(school_id=schools[3].id, student_id=students[14].id, date_joined=datetime.now() - timedelta(days=200), status=StudentStatus.ACTIVE.value),
        ]
        session.add_all(school_students)
        await session.flush()
        
        invoices = []
        invoice_counter = 1
    
        def create_invoice(student_id, school_id, value, days_ago, status):
            nonlocal invoice_counter
            inv = InvoiceTable(
                ref=f"INV{invoice_counter:05d}",
                value=Decimal(str(value)),
                date=datetime.now() - timedelta(days=days_ago),
                status=status,
                student_id=student_id,
                school_id=school_id,
                created_at=datetime.now() - timedelta(days=days_ago),
            )
            invoice_counter += 1
            return inv
        
        # Alice at Lincoln (old school) - all paid
        invoices.extend([
            create_invoice(students[0].id, schools[0].id, 500.00, 850, InvoiceStatus.PAID),
            create_invoice(students[0].id, schools[0].id, 500.00, 750, InvoiceStatus.PAID),
            create_invoice(students[0].id, schools[0].id, 500.00, 650, InvoiceStatus.PAID),
        ])
        
        # Alice at Washington (current school) - mix of paid and pending
        invoices.extend([
            create_invoice(students[0].id, schools[1].id, 600.00, 350, InvoiceStatus.PAID),
            create_invoice(students[0].id, schools[1].id, 600.00, 250, InvoiceStatus.PAID),
            create_invoice(students[0].id, schools[1].id, 600.00, 150, InvoiceStatus.PENDING),
            create_invoice(students[0].id, schools[1].id, 600.00, 50, InvoiceStatus.PENDING),
        ])
        
        # Bob at Lincoln - some pending
        invoices.extend([
            create_invoice(students[1].id, schools[0].id, 500.00, 800, InvoiceStatus.PAID),
            create_invoice(students[1].id, schools[0].id, 500.00, 700, InvoiceStatus.PAID),
            create_invoice(students[1].id, schools[0].id, 500.00, 600, InvoiceStatus.PAID),
            create_invoice(students[1].id, schools[0].id, 500.00, 500, InvoiceStatus.PENDING),
            create_invoice(students[1].id, schools[0].id, 500.00, 400, InvoiceStatus.PENDING),
        ])
        
        # Charlie at Jefferson (old) and Lincoln (current)
        invoices.extend([
            create_invoice(students[2].id, schools[2].id, 450.00, 750, InvoiceStatus.PAID),
            create_invoice(students[2].id, schools[2].id, 450.00, 650, InvoiceStatus.PAID),
            create_invoice(students[2].id, schools[0].id, 500.00, 250, InvoiceStatus.PAID),
            create_invoice(students[2].id, schools[0].id, 500.00, 150, InvoiceStatus.PENDING),
        ])
        
        # Diana at Washington - all paid
        invoices.extend([
            create_invoice(students[3].id, schools[1].id, 600.00, 700, InvoiceStatus.PAID),
            create_invoice(students[3].id, schools[1].id, 600.00, 600, InvoiceStatus.PAID),
            create_invoice(students[3].id, schools[1].id, 600.00, 500, InvoiceStatus.PAID),
        ])
        
        # Ethan at Roosevelt - has pending debt even though deactivated
        invoices.extend([
            create_invoice(students[4].id, schools[3].id, 550.00, 650, InvoiceStatus.PAID),
            create_invoice(students[4].id, schools[3].id, 550.00, 550, InvoiceStatus.PENDING),
            create_invoice(students[4].id, schools[3].id, 550.00, 450, InvoiceStatus.PENDING),
        ])
        
        # Fiona at Jefferson
        invoices.extend([
            create_invoice(students[5].id, schools[2].id, 450.00, 600, InvoiceStatus.PAID),
            create_invoice(students[5].id, schools[2].id, 450.00, 500, InvoiceStatus.PAID),
            create_invoice(students[5].id, schools[2].id, 450.00, 400, InvoiceStatus.PENDING),
        ])
        
        # George at Lincoln
        invoices.extend([
            create_invoice(students[6].id, schools[0].id, 500.00, 550, InvoiceStatus.PAID),
            create_invoice(students[6].id, schools[0].id, 500.00, 450, InvoiceStatus.PENDING),
        ])
        
        # Hannah at Washington
        invoices.extend([
            create_invoice(students[7].id, schools[1].id, 600.00, 500, InvoiceStatus.PAID),
            create_invoice(students[7].id, schools[1].id, 600.00, 400, InvoiceStatus.PAID),
            create_invoice(students[7].id, schools[1].id, 600.00, 300, InvoiceStatus.PENDING),
        ])
        
        # Isaac at Roosevelt (old) and Washington (current)
        invoices.extend([
            create_invoice(students[8].id, schools[3].id, 550.00, 450, InvoiceStatus.PAID),
            create_invoice(students[8].id, schools[1].id, 600.00, 150, InvoiceStatus.PAID),
            create_invoice(students[8].id, schools[1].id, 600.00, 50, InvoiceStatus.PENDING),
        ])
        
        # Julia at Jefferson
        invoices.extend([
            create_invoice(students[9].id, schools[2].id, 450.00, 400, InvoiceStatus.PAID),
            create_invoice(students[9].id, schools[2].id, 450.00, 300, InvoiceStatus.PENDING),
        ])
        
        # Kevin at Lincoln
        invoices.extend([
            create_invoice(students[10].id, schools[0].id, 500.00, 350, InvoiceStatus.PAID),
            create_invoice(students[10].id, schools[0].id, 500.00, 250, InvoiceStatus.PENDING),
        ])
        
        # Laura at Roosevelt
        invoices.extend([
            create_invoice(students[11].id, schools[3].id, 550.00, 300, InvoiceStatus.PAID),
            create_invoice(students[11].id, schools[3].id, 550.00, 200, InvoiceStatus.PENDING),
        ])
        
        # Nina at Washington
        invoices.extend([
            create_invoice(students[13].id, schools[1].id, 600.00, 200, InvoiceStatus.PAID),
            create_invoice(students[13].id, schools[1].id, 600.00, 100, InvoiceStatus.PENDING),
        ])
        
        # Oliver at Roosevelt
        invoices.extend([
            create_invoice(students[14].id, schools[3].id, 550.00, 150, InvoiceStatus.PAID),
            create_invoice(students[14].id, schools[3].id, 550.00, 50, InvoiceStatus.PENDING),
        ])
        
        session.add_all(invoices)
        await session.flush()
        
        payments = []
        payment_counter = 1
        
        for invoice in invoices:
            if invoice.status == InvoiceStatus.PAID:
                if payment_counter % 3 == 0:
                    # Partial payments
                    partial_amount = invoice.value / 2
                    payments.append(PaymentTable(
                        ref=f"PAY{payment_counter:05d}",
                        value=partial_amount,
                        date=invoice.date + timedelta(days=10),
                        invoice_id=invoice.id,
                        created_at=invoice.date + timedelta(days=10),
                    ))
                    payment_counter += 1
                    payments.append(PaymentTable(
                        ref=f"PAY{payment_counter:05d}",
                        value=invoice.value - partial_amount,
                        date=invoice.date + timedelta(days=20),
                        invoice_id=invoice.id,
                        created_at=invoice.date + timedelta(days=20),
                    ))
                    payment_counter += 1
                else:
                    payments.append(PaymentTable(
                        ref=f"PAY{payment_counter:05d}",
                        value=invoice.value,
                        date=invoice.date + timedelta(days=15),
                        invoice_id=invoice.id,
                        created_at=invoice.date + timedelta(days=15),
                    ))
                    payment_counter += 1
        
        session.add_all(payments)
        await session.commit()
        
        print("✅ Database populated successfully!")
        print(f"   - {len(schools)} schools")
        print(f"   - {len(students)} students")
        print(f"   - {len(school_students)} school-student relationships")
        print(f"   - {len(invoices)} invoices")
        print(f"   - {len(payments)} payments")


if __name__ == "__main__":
    asyncio.run(populate_database())
