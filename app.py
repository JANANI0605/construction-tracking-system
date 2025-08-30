from flask import Flask, render_template, request, redirect, url_for, session, flash
import oracledb
import os

oracledb.init_oracle_client(lib_dir=r"C:\Program Files\Oracle\instantclient_19_26")

app = Flask(__name__)
app.secret_key = 'your_secret_key'

connection = oracledb.connect(
    user="YOUR_USERNAME",
    password="YOUR_PASSWORD",
    dsn="localhost/XE"
)
cursor = connection.cursor()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        user_id = request.form['user_id']
        session['role'] = role
        session['user_id'] = user_id

        if role == 'contractor':
            return redirect(url_for('contractor_dashboard'))
        elif role == 'customer':
            return redirect(url_for('customer_dashboard'))
    return render_template('login.html')  # or your login logic

@app.route('/update_customer_details', methods=['POST'])
def update_customer_details():
    cust_id = session['user_id']
    name = request.form['name']
    phone = request.form['phone_no'] 
    address = request.form['address']

    cursor.execute("""
        UPDATE customer
        SET cname = :1, phone_no = :2, address = :3
        WHERE cust_id = :4
    """, (name, phone, address, cust_id))
    connection.commit()
    flash('Details updated successfully.')
    return redirect(url_for('customer_dashboard'))

@app.route('/contractor')
def contractor_dashboard():
    return render_template("contractor_dashboard.html")

@app.route('/contractor/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        pid = request.form['pid']
        name = request.form['name']
        status = request.form['status']
        cost_per_sq = request.form['cost']
        area_covered = request.form['area']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        cust_id = request.form['cust_id']
        cid = session['user_id']

        # Insert into project table
        cursor.execute("""
            INSERT INTO project (pid, name, status, cost_per_sq, area_covered, start_date, end_date)
            VALUES (:1, :2, :3, :4, :5, TO_DATE(:6, 'YYYY-MM-DD'), TO_DATE(:7, 'YYYY-MM-DD'))
        """, (pid, name, status, cost_per_sq, area_covered, start_date, end_date))

        # Link contractor to project
        cursor.execute("""
            UPDATE contractor SET pid = :1 WHERE cid = :2
        """, (pid, cid))

        # Link customer to project
        cursor.execute("""
            UPDATE customer SET pid = :1 WHERE cust_id = :2
        """, (pid, cust_id))

        connection.commit()
        return redirect(url_for('view_projects'))

    return render_template("add_project.html")



@app.route('/contractor/project/delete/<pid>', methods=['GET'])
def delete_project(pid):
    cursor.execute("DELETE FROM material WHERE pid = :1", (pid,))
    cursor.execute("DELETE FROM contractor WHERE pid = :1", (pid,))
    cursor.execute("DELETE FROM customer WHERE pid = :1", (pid,))
    cursor.execute("DELETE FROM payment WHERE pid = :1", (pid,))
    cursor.execute("DELETE FROM project WHERE pid = :1", (pid,))
    connection.commit()
    return redirect(url_for('view_contractor_projects'))

@app.route('/contractor/projects')
def view_projects():
    cid = session['user_id']

    # Get all projects assigned to this contractor
    cursor.execute("""
        SELECT * FROM project 
        WHERE pid IN (SELECT pid FROM contractor WHERE cid = :1)
    """, (cid,))
    projects = cursor.fetchall()

    # Get materials per project
    materials_by_project = {}
    customer_by_project = {}

    for project in projects:
        pid = project[0]
        
        cursor.execute("SELECT * FROM material WHERE pid = :1", (pid,))
        materials_by_project[pid] = cursor.fetchall()

        cursor.execute("SELECT * FROM customer WHERE pid = :1", (pid,))
        customer = cursor.fetchone()
        customer_by_project[pid] = customer

    return render_template("view_projects.html", projects=projects, materials_by_project=materials_by_project, customer_by_project=customer_by_project)

@app.route('/contractor/materials/<pid>', methods=['GET', 'POST'])
def view_project_materials(pid):
    if request.method == 'POST':
        mid = request.form['mid']
        name = request.form['material_name']
        qty = request.form['quantity']
        cost = request.form['cost']
        cursor.execute("""
            INSERT INTO material (mid, pid, material_name, quantity, cost)
            VALUES (:1, :2, :3, :4, :5)
        """, (mid, pid, name, qty, cost))
        connection.commit()

    # Fetch materials for this project
    cursor.execute("SELECT * FROM material WHERE pid = :1", (pid,))
    materials = cursor.fetchall()

    # Fetch project details
    cursor.execute("SELECT * FROM project WHERE pid = :1", (pid,))
    project = cursor.fetchone()

    return render_template("view_projects.html", materials=materials, project=project)
@app.route('/contractor/add_customer/<pid>', methods=['POST'])
def add_customer_to_project(pid):
    cname = request.form['cname']
    phone_no = request.form['phone_no']
    address = request.form['address']
    email = request.form['email']
    budget = request.form['budget']

    # Generate a new customer ID (simplified)
    cursor.execute("SELECT MAX(cust_id) FROM customer")
    max_id = cursor.fetchone()[0]
    new_id = (max_id + 1) if max_id else 1

    cursor.execute("""
        INSERT INTO customer (cust_id, cname, phone_no, address, email, budget, pid)
        VALUES (:1, :2, :3, :4, :5, :6, :7)
    """, (new_id, cname, phone_no, address, email, budget, pid))
    connection.commit()

    return redirect(url_for('view_contractor_projects'))


@app.route('/contractor/materials/edit/<mid>', methods=['GET', 'POST'])
def edit_material(mid):
    if request.method == 'POST':
        material_name = request.form['material_name']
        quantity = request.form['quantity']
        cost = request.form['cost']
        cursor.execute("""
            UPDATE material
            SET material_name = :1, quantity = :2, cost = :3
            WHERE mid = :4
        """, (material_name, quantity, cost, mid))
        connection.commit()
        return redirect(url_for('view_contractor_projects'))  # safer than using form pid
    cursor.execute("SELECT * FROM material WHERE mid = :1", (mid,))
    material = cursor.fetchone()
    return render_template("edit_material.html", material=material)

@app.route('/contractor/materials/delete/<mid>/<pid>', methods=['GET'])
def delete_material(mid, pid):
    cursor.execute("DELETE FROM material WHERE mid = :1", (mid,))
    connection.commit()
    return redirect(url_for('view_project_materials', pid=pid))

@app.route('/contractor/materials/add/<pid>', methods=['GET', 'POST'])
def add_material(pid):
    if request.method == 'POST':
        mid = request.form['mid']
        material_name = request.form['material_name']
        quantity = request.form['quantity']
        cost = request.form['cost']
        cursor.execute("""
            INSERT INTO material (mid, pid, material_name, quantity, cost)
            VALUES (:1, :2, :3, :4, :5)
        """, (mid, pid, material_name, quantity, cost))
        connection.commit()
        return redirect(url_for('view_projects', pid=pid))  # <-- use function name, not HTML file
    return render_template("add_material.html", pid=pid)


@app.route('/contractor/payments')
def track_payments():
    cid = session['user_id']

    cursor.execute("""
        SELECT pay.pay_id AS payment_id,
               pay.paid_date,
               pay.amount,
               p.name AS project_name
        FROM payment pay
        JOIN project p ON pay.pid = p.pid
        JOIN contractor c ON p.pid = c.pid  -- Ensure contractor is linked to project through pid
        WHERE c.cid = :1
    """, (cid,))

    rows = cursor.fetchall()

    # Convert to list of dictionaries to support dot-notation in template
    payments = [
        {
            'payment_id': row[0],
            'paid_date': row[1],
            'amount': row[2],
            'project_name': row[3]
        } for row in rows
    ]

    return render_template("track_payments.html", payments=payments)

@app.route('/edit_project/<int:pid>', methods=['GET', 'POST'])
def edit_project(pid):
    # Step 1: Fetch existing project details
    cursor.execute("SELECT * FROM project WHERE pid = :pid", {'pid': pid})
    project = cursor.fetchone()
    
    if project is None:
        flash("Project not found", "danger")
        return redirect(url_for('contractor_dashboard'))

    if request.method == 'POST':
        # Step 2: Get form data and update project
        name = request.form['name']
        status = request.form['status']
        cost_per_sq = request.form['cost_per_sq']
        area_covered = request.form['area_covered']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        try:
            # Step 3: Update project in the database
            cursor.execute("""
                UPDATE project 
                SET name = :name, status = :status, cost_per_sq = :cost_per_sq, 
                    area_covered = :area_covered, start_date = :start_date, end_date = :end_date 
                WHERE pid = :pid
            """, {
                'name': name, 'status': status, 'cost_per_sq': cost_per_sq,
                'area_covered': area_covered, 'start_date': start_date,
                'end_date': end_date, 'pid': pid
            })
            connection.commit()

            flash("Project updated successfully", "success")
            return redirect(url_for('contractor_dashboard'))

        except Exception as e:
            connection.rollback()
            flash(f"Error updating project: {e}", "danger")

    # Step 4: Pre-fill the form with existing project data for GET request
    return render_template('edit_project.html', project=project)


@app.route('/contractor/add_payment', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        try:
            # Get form data
            payment_id = request.form['payment_id']
            paid_date = request.form['paid_date']
            amount = request.form['amount']
            pid = request.form['pid']  # project ID associated with the payment

            # Insert payment into the database
            cursor.execute("""
                INSERT INTO payment (pay_id, paid_date, amount, pid)
                VALUES (:1, :2, :3, :4)
            """, (payment_id, paid_date, amount, pid))
            connection.commit()  # Commit the transaction

            flash("Payment added successfully", "success")
            return redirect(url_for('track_payments'))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('add_payment'))

    return render_template('add_payment.html')

@app.route('/customer')
def customer_dashboard():
    cust_id = session['user_id']
    
    # Fetch editable customer details
    cursor.execute("SELECT cname, phone_no, address FROM customer WHERE cust_id = :1", (cust_id,))
    customer_row = cursor.fetchone()
    customer = {
        'name': customer_row[0],
        'phone_no': customer_row[1],
        'address': customer_row[2]
    } if customer_row else {}

    # Fetch project, contractor, and payment info (read-only)
    cursor.execute("""
        SELECT p.name AS project_name, p.status AS project_status, 
               p.start_date, p.end_date,
               c.name AS contractor_name, c.speciality, c.contact,
               pay.amount, pay.paid_date
        FROM customer cust
        JOIN project p ON cust.pid = p.pid
        JOIN contractor c ON c.pid = p.pid
        LEFT JOIN payment pay ON pay.pid = p.pid
        WHERE cust.cust_id = :1
    """, (cust_id,))
    rows = cursor.fetchall()

    details = [
        {
            'name': row[0],
            'status': row[1],
            'start_date': row[2],
            'end_date': row[3],
            'contractor_name': row[4],
            'speciality': row[5],
            'contact': row[6],
            'amount': row[7],
            'paid_date': row[8]
        } for row in rows
    ]

    return render_template('customer_dashboard.html', customer=customer, details=details, payments=details)


@app.route('/register_customer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        # Extract the form data using get to avoid KeyError
        cname = request.form.get('cname')
        phone_no = request.form.get('phone_no')
        address = request.form.get('address')
        email = request.form.get('email')
        budget = request.form.get('budget')
        cust_id = request.form.get('cust_id')  # Add this if you want to pass cust_id manually

        # Debugging: print form data to check what's being sent
        print(f"Form data: cust_id={cust_id}, cname={cname}, phone_no={phone_no}, address={address}, email={email}, budget={budget}")

        # Check if any required field is missing
        if not cust_id or not cname or not phone_no or not address or not email or not budget:
            return "All fields are required", 400  # Return an error message if any field is missing

        # Insert new customer into the database
        cursor.execute("""
            INSERT INTO customer (cust_id, cname, phone_no, address, email, budget)
            VALUES (:1, :2, :3, :4, :5, :6)
        """, (cust_id, cname, phone_no, address, email, budget))  # Pass cust_id here if it's needed

        connection.commit()

        return redirect(url_for('login'))

    return render_template("register_customer.html")



@app.route('/register_contractor', methods=['GET', 'POST'])
def register_contractor():
    if request.method == 'POST':
        # Extract the form data
        cid=request.form['id']
        name = request.form['name']
        speciality = request.form['speciality']
        contact = request.form['contact']

        # Insert new contractor into the database
        cursor.execute("""
            INSERT INTO contractor (cid,name, speciality, contact)
            VALUES (:1, :2, :3,:4)
        """, (cid,name, speciality, contact))
        connection.commit()

        return redirect(url_for('login'))

    return render_template("register_contractor.html")


if __name__ == '__main__':
    app.run(debug=True)
