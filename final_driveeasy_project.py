import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import Label, Button, LEFT
import mysql.connector
import tkinter.simpledialog as simpledialog
from tkinter import Frame, CENTER
from tkinter import Toplevel, Button, Label
import re
from datetime import datetime as dt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime as dt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from tkcalendar import DateEntry
from tkinter import PhotoImage
from PIL import Image, ImageTk

# Connect to the database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Achyuth6812@",
    database="carrental"
)
cursor = db.cursor()

# Global variables
current_user_email = None
car_selection_frame = None  # Define car_selection_frame as a global variable
booking_frame = None
booking_frame_displayed = False
current_user_email = None
current_user_fullname = None
profile_frame_displayed = False

def create_tables():
    """
    Connect to the database and create necessary tables if they don't exist
    """
    global cursor
    # Creates 'users' table to store user information if not exists
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INT AUTO_INCREMENT PRIMARY KEY, "
                    "first_name VARCHAR(50), "
                    "last_name VARCHAR(50), "
                    "email VARCHAR(50), "
                    "phone_number VARCHAR(10), "
                    "age INT, "
                    "address1 VARCHAR(100), "
                    "address2 VARCHAR(100), "
                    "city VARCHAR(30), "
                    "state VARCHAR(30), "
                    "country VARCHAR(30), "
                    "zipcode VARCHAR(5), "
                    "password VARCHAR(100))")

    # Creates 'cars' table to store car information if not exists
    cursor.execute("CREATE TABLE IF NOT EXISTS cars (car_id INT AUTO_INCREMENT PRIMARY KEY, "
                    "car_name VARCHAR(50), "
                    "car_model VARCHAR(50), "
                    "car_view BLOB, "
                    "car_type VARCHAR(50), "
                    "car_features TEXT, "
                    "price DECIMAL(10,2), "
                    "availability BOOLEAN)")

    # Creates 'new_car_bookings' table to store car booking information
    cursor.execute("CREATE TABLE IF NOT EXISTS new_car_bookings (booking_id INT AUTO_INCREMENT PRIMARY KEY, "
                    "car_id INT NOT NULL, "
                    "user_id INT NOT NULL, "
                    "car_name VARCHAR(30) NOT NULL, "
                    "car_type VARCHAR(30) NOT NULL, "
                    "start_time DATE NOT NULL, "
                    "end_time DATE NOT NULL, "
                    "total_price FLOAT NOT NULL, "
                    "review VARCHAR(100), "
                    "rating INT, "
                    "status BOOLEAN NOT NULL)"
                   )

def is_valid_email(email):
    """
    Check if the provided email is in a valid format.
    """
    # Regular expression pattern for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

def is_valid_password(password):
    """
    Check if the provided password is in a valid format.
    """
    # Regular expression pattern for password validation
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[@$%0-9])[A-Za-z\d@$%]{8,}$"
    return bool(re.match(pattern, password))

def validate_phone_number(phone_number):
    # Check if the phone number contains only digits and has 10 characters
    if phone_number.isdigit() and len(phone_number) == 10:
        return True
    else:
        return False

def validate_age(age):
    try:
        age = int(age)
        if age >= 16 and age <= 100:
            return True
        else:
            return False
    except ValueError:
        return False

def validate_city(city):
    # Check if the city contains only letters
    if not city.isalpha():
        return False

    return True

def validate_state(state):
    # Check if the state contains only letters
    if not state.isalpha():
        return False

    return True

def validate_country(country):
    # Check if the country contains only letters
    if not country.isalpha():
        return False

    return True

def validate_zipcode(zipcode):
    # Check if the ZIP code contains only digits
    if not zipcode.isdigit():
        return False

    # Check if the ZIP code has the correct length (for example, 5 digits in the US)
    if len(zipcode) != 5:
        return False

    return True

def signup():
    """
    This method handles the user signup process, validates user input, checks for existing emails,
    inserts user data into the database, and displays success/error messages accordingly.
    """
    first_name = signup_entries['First name'].get()
    last_name = signup_entries['Last name'].get()
    email = signup_entries['Email'].get()
    phone_number = signup_entries['Phone number'].get()
    age = signup_entries['Age'].get()
    address1 = signup_entries['Address 1'].get()
    address2 = signup_entries['Address 2'].get()
    city = signup_entries['City'].get()
    state = signup_entries['State'].get()
    country = signup_entries['Country'].get()
    zipcode = signup_entries['Zipcode'].get()
    password = signup_password_entry.get()
    confirm_password = signup_confirm_password_entry.get()

    # Validation checks for all required fields
    if not (first_name and last_name and email and phone_number and age and address1 and city and state and country and zipcode and password and confirm_password):
        messagebox.showerror("Error", "Please fill in all required fields.")
        return

    # Validate email format
    if not is_valid_email(email):
        messagebox.showerror("Error", "Please enter a valid email address.")
        return

    # Validate phone number
    if not validate_phone_number(phone_number):
        messagebox.showerror("Error", "Please enter a valid 10-digit phone number.")

    # Validate age
    if not validate_age(age):
        messagebox.showerror("Error", "Please enter a valid age.")
        return

    # Validate city
    if not validate_city(city):
        messagebox.showerror("Error", "Please enter a valid city name.")
        return

    # Validate state
    if not validate_state(state):
        messagebox.showerror("Error", "Please enter a valid state name.")
        return

    # Validate country
    if not validate_country(country):
        messagebox.showerror("Error", "Please enter a valid country name.")
        return

    # Validate ZIP code
    if not validate_zipcode(zipcode):
        messagebox.showerror("Error", "Please enter a valid ZIP code.")
        return

    # Validation checks for password
    if not is_valid_password(password):
        messagebox.showerror("Error", "Password must contain at least one lowercase letter, one uppercase letter, one special character (@, $, %), one digit, and be at least 8 characters long.")
        return

    if password != confirm_password:
        messagebox.showerror("Error", "Password and Confirm Password must match")
        return



    # Checking if email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        messagebox.showerror("Error", "Email already exists. Please choose another one.")
        return

    # Insert user data into the database
    cursor.execute("INSERT INTO users (first_name, last_name, email, phone_number, age, address1, address2, "
                    "city, state, country, zipcode, password) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (first_name, last_name, email, phone_number, age,
                     address1, address2, city, state,
                     country, zipcode, password))
    db.commit()
    messagebox.showinfo("Success", "Sign up successful. You can now log in.")
    show_login_screen()

def logout():
    """
    This method handles user logout by clearing the current session's user credentials and returning to the login screen.
    """
    global current_user_email
    current_user_email = None
     # Clear the content in the entry boxes in the login frame
    login_email_entry.delete(0, 'end')
    login_password_entry.delete(0, 'end')
    login_frame.pack(expand=1)
    car_selection_frame.pack_forget()

def login():
    """
    This method handles user login, validates credentials against the database, and displays success/error messages.
    """
    global current_user_email
    global current_user_name
    email = login_email_entry.get()
    password = login_password_entry.get()

    if not email or not password:
        messagebox.showerror("Error", "Please enter both email and password.")
        return

    # Checking if the provided email and password match any user in the database
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user_data = cursor.fetchone()
    if user_data:
        current_user_email = email  # Store current user's email
    else:
        messagebox.showerror("Error", "Invalid username or password.")
        return

    # Fetch the user's name and email from the database
    first_name, last_name, current_user_email = user_data[1], user_data[2], user_data[3]
    current_user_name = f"{first_name} {last_name}"

    create_car_selection_screen()  # Proceed to car selection screen after successful login


def show_booking_screen(car_id, car_name):
    """
    This method creates a screen to select booking dates and calculate total price.
    """
    def calculate_price(event=None):
        start_date = start_date_entry.get_date()
        end_date = end_date_entry.get_date()
        if start_date and end_date:
            try:
                # Validate start date and end date to ensure they are not in the past
                today = dt.today().date()

                if start_date < today:
                    messagebox.showerror("Error", "Start date cannot be in the past.")
                    return
                if end_date < today:
                    messagebox.showerror("Error", "End date cannot be in the past.")
                    return
                if end_date < start_date:
                    messagebox.showerror("Error", "End date should be after start date.")
                    return

                num_days = (end_date - start_date).days
                if num_days <= 0:
                    messagebox.showerror("Error", "End date should be after start date.")
                    return
                cursor.execute("SELECT price FROM cars WHERE car_id = %s", (car_id,))
                car_price = cursor.fetchone()[0]
                total_price = car_price * num_days
                total_price_label.config(text=f"Total Price: ${total_price:.2f}")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid dates.")
        else:
            messagebox.showerror("Error", "Please select both start and end dates.")

    global booking_frame_displayed
    # Hide car selection frame
    car_selection_frame.pack_forget()

    # Create booking frame
    global booking_frame
    booking_frame = tk.Frame(root, padx=20, pady=15)
    booking_frame.pack(expand=1)


    tk.Label(booking_frame, text=f"Book '{car_name}'", font=("Calibri", 16)).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

    tk.Label(booking_frame, text="Start Date:", font=("Calibri", 11)).grid(row=1, column=0, sticky="w", pady=(0, 5))
    start_date_entry = DateEntry(booking_frame, date_pattern='mm-dd-yyyy', font=("Calibri", 11), width=12, background='darkblue', foreground='white', borderwidth=2)
    start_date_entry.grid(row=1, column=1, pady=(0, 5))
    start_date_entry.bind("<<DateEntrySelected>>", calculate_price)

    tk.Label(booking_frame, text="End Date:", font=("Calibri", 11)).grid(row=2, column=0, sticky="w", pady=(0, 5))
    end_date_entry = DateEntry(booking_frame, date_pattern='mm-dd-yyyy', font=("Calibri", 11), width=12, background='darkblue', foreground='white', borderwidth=2)
    end_date_entry.grid(row=2, column=1, pady=(0, 5))
    end_date_entry.bind("<<DateEntrySelected>>", calculate_price)

    total_price_label = tk.Label(booking_frame, text="Total Price: $0.00", font=("Calibri", 11))
    total_price_label.grid(row=3, column=0, columnspan=2, pady=(10, 5))

    def display_booking_details(car_id, current_user_id,current_user_fullname, car_name, car_type, start_date, end_date, total_price):
        booking_frame.pack_forget()

        # Create a new frame to display booking details
        global booking_details_frame
        booking_details_frame = Frame(root)
        booking_details_frame.pack(expand=True, fill='both', pady=(50, 0))

        # Heading for booking details
        Label(booking_details_frame, text="Booking Details", font=("Calibri", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Labels and values to display booking details
        labels = [("User Name", current_user_fullname), ("Car Name", car_name), ("Car Type", car_type), ("Start Date", start_date), ("End Date", end_date), ("Total Price", f"${total_price:.2f}")]
        for i, (label, value) in enumerate(labels, start=1):
            label_widget = Label(booking_details_frame, text=label, font=("Calibri", 12, "bold"), width=12, anchor="w")
            label_widget.grid(row=i, column=0, pady=(5, 0), padx=(10, 5), sticky="w")
            value_widget = Label(booking_details_frame, text=value, font=("Calibri", 12), anchor="w")
            value_widget.grid(row=i, column=1, pady=(5, 0), padx=(0, 10), sticky="w")

        # Confirm and cancel booking buttons
        button_frame = Frame(booking_details_frame)
        button_frame.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)
        confirm_button = Button(button_frame, text="Confirm Booking", bg="#B3DFF7", font=("Calibri", 11),command=lambda: confirm_booking(car_id,current_user_id,current_user_fullname, car_name, car_type, start_date, end_date, total_price))
        confirm_button.pack(side='left', padx=5)
        cancel_button = Button(button_frame, text="Cancel", bg="#B3DFF7", font=("Calibri", 11), command=cancel_booking)
        cancel_button.pack(side='left', padx=5)

        # Center the frame within the root window
        booking_details_frame.place(relx=0.5, rely=0.5, anchor=CENTER)



    def confirm_booking(car_id, current_user_id, current_user_fullname, car_name, car_type, start_date_formatted, end_date_formatted, total_price):
        booking_frame.pack_forget()
        # Update the database
        cursor.execute("INSERT INTO new_car_bookings (car_id, user_id, car_name, car_type, start_time, end_time, total_price, status) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (car_id, current_user_id, car_name, car_type, start_date_formatted, end_date_formatted, total_price, '1'))
        db.commit()

        # Send email confirmation
        message = f"Dear {current_user_fullname},\n\nYour booking for {car_name} ({car_type}) has been confirmed.\n\nBooking Details:\n\nStart Date: {start_date_formatted}\nEnd Date: {end_date_formatted}\nTotal Price: ${total_price}\n\nThank you for choosing our service.\nHere is the attached receipt for your reference.\n\nBest Regards,\nDriveEasy Team"
        send_confirmation_email(current_user_fullname, current_user_email, car_name, car_type, start_date_formatted, end_date_formatted, total_price, message)

        # Update the availability of the booked car in the database
        cursor.execute("UPDATE cars SET availability = FALSE WHERE car_id = %s", (car_id,))
        db.commit()

        # Display success message
        messagebox.showinfo("Confirm","Successfully Booked! A confirmation email has been sent")

        # Close the booking details window
        booking_details_frame.destroy()
        create_car_selection_screen()

    def cancel_booking():
        # Close the booking details window
        booking_details_frame.destroy()
        show_booking_screen(car_id, car_name)

    def proceed_to_book():
        calculate_price()  # Ensure total price is calculated before proceeding
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        start_date = dt.strptime(start_date, "%m-%d-%Y")
        end_date = dt.strptime(end_date, "%m-%d-%Y")
        start_date_formatted = start_date.strftime('%Y-%m-%d')
        end_date_formatted = end_date.strftime('%Y-%m-%d')

        # Insert booking data into the database
        cursor.execute("SELECT * FROM users WHERE email = %s", (current_user_email,))
        user_data = cursor.fetchone()
        if user_data:
            current_user_id = user_data[0]
            current_user_firstname = user_data[1]
            current_user_lastname = user_data[2]
            current_user_fullname = current_user_firstname+' '+current_user_lastname
        cursor.execute("SELECT car_type FROM cars WHERE car_id = %s", (car_id,))
        car_type = cursor.fetchone()[0]
        # Extract the numeric part of the total price string and remove the dollar sign
        total_price_str = total_price_label.cget("text")
        numeric_part = total_price_str.split("$")[-1]  # Extract the part after the dollar sign
        total_price = float(numeric_part)
        #Display booking details in another screen
        display_booking_details(car_id, current_user_id,current_user_fullname,car_name, car_type, start_date_formatted, end_date_formatted, total_price)

    proceed_button = tk.Button(booking_frame, text="Proceed to Book", command=proceed_to_book, bg="#B3DFF7", font=("Calibri", 11))
    proceed_button.grid(row=5, column=0, pady=10, padx=(0, 5))

    # Button to go back to car selection
    back_button = tk.Button(booking_frame, text="Back to Car Selection", command=create_car_selection_screen, bg="#B3DFF7", font=("Calibri", 11))
    back_button.grid(row=5, column=1, pady=10, padx=(5, 0))

    # Set the column weight so that buttons will stay aligned
    booking_frame.columnconfigure(0, weight=1)
    booking_frame.columnconfigure(1, weight=1)

    # Set booking frame displayed status to True
    booking_frame_displayed = True

def generate_booking_pdf(car_name, car_type, start_date, end_date, total_price, user_email):
    # Fetch user details from the database
    cursor.execute("SELECT first_name, last_name, address1, address2, city, state, country, zipcode FROM users WHERE email = %s", (user_email,))
    user_data = cursor.fetchone()
    if user_data:
        first_name, last_name, address1, address2, city, state, country, zipcode = user_data
        user_details = [
            f"User Name: {first_name},",
            f"Last Name: {last_name}",
            f"Address: {address1}, {address2}",
            f"City: {city}",
            f"State: {state}",
            f"Country: {country}",
            f"Zipcode: {zipcode}",
        ]
    else:
        # If user details are not found, set user_details to an empty list
        user_details = []

    # Define booking details
    booking_details = [
        ["Car Name", car_name],
        ["Car Type", car_type],
        ["Start Date", start_date],
        ["End Date", end_date],
        ["Total Price", f"${total_price:.2f}"],
    ]
    # Get predefined styles
    styles = getSampleStyleSheet()

    # Create a PDF document
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

    # Add main heading
    main_heading = Paragraph("DriveEasy Booking Confirmation", styles['Heading1'])

    # Create a table for booking details
    booking_table = Table(booking_details)
    booking_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                                       ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                       ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                       ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                       ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                       ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                       ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    # Add main heading and user details to content
    content = [main_heading]
    for detail in user_details:
        content.append(Paragraph(detail, styles['Normal']))
    content.append(Spacer(1, 12))  # Add 12 points of space
    content.append(booking_table)

    # Build PDF document
    doc.build(content)

    # Reset the buffer position to start
    pdf_buffer.seek(0)
    return pdf_buffer

def send_confirmation_email(user_fullname, user_email, car_name, car_type, start_date, end_date, total_price,message):
    # Email content
    subject = "Booking Confirmation"
    # Setup the email
    msg = MIMEMultipart()
    msg.attach(MIMEText(message))
    pdf_buffer= generate_booking_pdf(car_name, car_type, start_date, end_date, total_price, current_user_email)
    part = MIMEApplication(pdf_buffer.read(), Name=f"{user_email}_booking.pdf")
    part['Content-Disposition'] = f'attachment; filename="{user_email}_booking.pdf"'
    msg.attach(part)

    msg['From'] = "driveeasy702@gmail.com"
    msg['To'] = user_email
    msg['Subject'] = subject

    # Connect to m server and send email
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login("driveeasy702@gmail.com", "fgdw namz ymvc rqxs")
    smtp_server.send_message(msg)
    smtp_server.quit()


def create_car_selection_screen():
    """
    This method creates a screen to display available cars for selection, fetches
    car data from the database, populates a treeview widget with car information,
    and provides a button to book the selected car.
    """
    global current_user_name
    global booking_frame_displayed
    global profile_frame_displayed
    global booking_frame
    global profile_frame
    # Hide the booking frame if it's currently displayed
    if booking_frame_displayed:
        booking_frame.pack_forget()

    if profile_frame_displayed:
       profile_frame.pack_forget()

    global current_user_name

    login_frame.pack_forget()
    global car_selection_frame
    car_selection_frame = tk.Frame(root, padx=20, pady=15)
    car_selection_frame.pack(expand=1)

    tk.Label(car_selection_frame, text=f"Welcome, {current_user_name}!", font=("Calibri", 16, "bold")).grid(row=0, column=0, columnspan=9,
                                                                                     sticky="ew")
    tk.Button(car_selection_frame, text="Profile", command=show_profile, bg="#B3DFF7", font=("Calibri", 11)).grid(row=0, column=8, padx=(0,15))
    tk.Button(car_selection_frame, text="Logout", command=logout, bg="#B3DFF7", font=("Calibri", 11)).grid(row=0, column=8, sticky="e")

    tk.Label(car_selection_frame, text="Available Cars", font=("Helvetica", 16)).grid(row=1, column=0, columnspan=9,
                                                                                     sticky="ew")

    tree = ttk.Treeview(car_selection_frame, columns=("Car ID", "Car Name", "Car Model", "Car Type", "Car Features", "Price"),
                         show="headings")
    tree.grid(row=2, column=0, columnspan=9, sticky="nsew")

    tree.heading("Car ID", text="Car ID")
    tree.heading("Car Name", text="Car Name")
    tree.heading("Car Model", text="Car Model")
    tree.heading("Car Type", text="Car Type")
    tree.heading("Car Features", text="Car Features")
    tree.heading("Price", text="Price")

    # Set column widths based on content length
    tree.column("Car ID", width=50)
    tree.column("Car Name", width=150)
    tree.column("Car Model", width=100)
    tree.column("Car Type", width=100)
    tree.column("Car Features", width=400)
    tree.column("Price", width=80)

    cursor.execute("SELECT * FROM cars WHERE availability IS TRUE")
    cars = cursor.fetchall()

    for car in cars:
        tree.insert("", "end", values=(car[0], car[1], car[2], car[4],car[5], car[6]))

    book_button = tk.Button(car_selection_frame, text="Book Car", command=lambda: book_car(tree), bg="#B3DFF7", font=("Calibri", 11))
    book_button.grid(row=3, column=0, columnspan=9, pady=10)

def logout():
    """
    This method handles user logout by clearing the current session's user credentials and returning to the login screen.
    """
    global current_user_email
    current_user_email = None
    # Clear the content in the entry boxes in the login frame
    login_email_entry.delete(0, 'end')
    login_password_entry.delete(0, 'end')
    login_frame.pack(expand=1)
    car_selection_frame.pack_forget()

def book_car(tree):
    """
    This method handles the booking of a selected car, updates its availability status
    in the database, and displays a success message.
    """
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a car to book.")
    else:
        car_id = tree.item(selected_item, "values")[0]
        car_name = tree.item(selected_item, "values")[1]
        # Redirect to the booking screen passing car_id and car_name
        show_booking_screen(car_id, car_name)

def create_forget_password_screen():

    # Define forget password screen
    tk.Label(forget_password_frame, text="Reset Password", font=("Calibri", 16)).grid(row=0, column=0, columnspan=2, sticky="ew")
    # Empty row for spacing
    tk.Label(forget_password_frame).grid(row=1, column=0, columnspan=2)

    tk.Label(forget_password_frame, text="Enter your email:", font=("Calibri", 11)).grid(row=2, column=0, sticky="w",padx=(10,0) )
    forget_email_entry.grid(row=2, column=1)

    # Empty row for spacing
    tk.Label(forget_password_frame).grid(row=3, column=0, columnspan=2)
    tk.Button(forget_password_frame, text="Reset Password", command=reset_password,bg="#B3DFF7", font=("Calibri", 11)).grid(row=4, column=0,sticky='e', padx=(20,0))

    # Place Cancel button next to Reset Password button
    tk.Button(forget_password_frame, text="Cancel", command=hide_forget_password,bg="#B3DFF7", font=("Calibri", 11)).grid(row=4, column=1)

def sort_treeview(tree, column, reverse):

    """Sort the treeview by given column."""
    data = [(tree.set(child, column), child) for child in tree.get_children("")]
    data.sort(reverse=reverse)

    for index, (val, child) in enumerate(data):
        tree.move(child, "", index)

    # Switch the sorting direction
    tree.heading(column, command=lambda: sort_treeview(tree, column, not reverse))

def show_profile():

    car_selection_frame.pack_forget()
    global current_user_email
    global profile_frame
    global profile_frame_displayed
    # Fetch user details from the database
    cursor.execute("SELECT * FROM users WHERE email = %s", (current_user_email,))
    user_data = cursor.fetchone()
    global user_id

    if user_data:
        current_user_fullname = user_data[1]+" "+user_data[2]
        # Create a new frame for displaying the profile
        profile_frame = tk.Frame(root, padx=20, pady=15)
        profile_frame.pack(expand=1)

        # Display user details heading
        tk.Label(profile_frame, text="User Details", font=("Calibri", 16)).grid(row=0, column=0, columnspan=3, sticky="ew",pady=10)

        # Display user details
        first_name_var = tk.StringVar(value=user_data[1])
        tk.Label(profile_frame, text="First Name:").grid(row=1, column=0, sticky="w")
        first_name_entry = tk.Entry(profile_frame, textvariable=first_name_var, state='readonly', width=45)
        first_name_entry.grid(row=1, column=1, sticky="w")
        first_name_entry.insert(0, user_data[1])
        last_name_var = tk.StringVar(value=user_data[2])
        tk.Label(profile_frame, text="Last Name:").grid(row=2, column=0, sticky="w")
        last_name_entry = tk.Entry(profile_frame,textvariable=last_name_var, state='readonly', width=45)
        last_name_entry.grid(row=2, column=1, sticky="w")
        last_name_entry.insert(0, user_data[2])
        email_var = tk.StringVar(value=user_data[3])
        tk.Label(profile_frame, text="Email:").grid(row=3, column=0, sticky="w")
        email_entry = tk.Entry(profile_frame, textvariable=email_var, state='readonly', width=45)
        email_entry.grid(row=3, column=1, sticky="w")
        phone_var = tk.StringVar(value=user_data[4])
        tk.Label(profile_frame, text="Phone Number:").grid(row=4, column=0, sticky="w")
        phone_entry = tk.Entry(profile_frame, textvariable=phone_var, state='readonly', width=45)
        phone_entry.grid(row=4, column=1, sticky="w")
        age_var = tk.StringVar(value=user_data[5])
        tk.Label(profile_frame, text="Age:").grid(row=5, column=0, sticky="w")
        age_entry = tk.Entry(profile_frame, textvariable=age_var, state='readonly', width=45)
        age_entry.grid(row=5, column=1, sticky="w")
        address_var = tk.StringVar(value=f"{user_data[6]}, {user_data[7]}, {user_data[8]}, {user_data[9]}, {user_data[10]}, {user_data[11]}")
        tk.Label(profile_frame, text="Address:").grid(row=6, column=0, sticky="w")
        address_entry = tk.Entry(profile_frame, textvariable=address_var, state='readonly', width=45)
        address_entry.grid(row=6, column=1, columnspan=2, sticky="w")

        # Draw line to segregate user details and booking details
        ttk.Separator(profile_frame, orient='horizontal').grid(row=7, columnspan=3, sticky='ew', pady=10)

        # Fetch booking details for the current user
        cursor.execute("SELECT * FROM new_car_bookings WHERE user_id = (SELECT user_id FROM users WHERE email = %s)", (current_user_email,))
        booking_data = cursor.fetchall()

        if booking_data:
            tk.Label(profile_frame, text="Booking History", font=("Calibri", 16)).grid(row=8, column=0, columnspan=3, sticky="ew", pady=10)

            tree = ttk.Treeview(profile_frame, columns=("Booking ID", "Car Name", "Car Type", "Start Date", "End Date", "Total Price"),
                                show="headings")
            tree.grid(row=9, column=0, columnspan=3, sticky="nsew")
            tree.heading("Booking ID", text="Booking ID")
            tree.heading("Car Name", text="Car Name")
            tree.heading("Car Type", text="Car Type")
            tree.heading("Start Date", text="Start Date")
            tree.heading("End Date", text="End Date")
            tree.heading("Total Price", text="Total Price")

            for booking in booking_data:
                tree.insert("", "end", values=(booking[0], booking[3], booking[4], booking[5], booking[6], booking[7]), tags=(booking[0],))

            for column in ["Booking ID", "Car Name", "Car Type", "Start Date", "End Date", "Total Price"]:
                tree.heading(column, text=column, command=lambda c=column: sort_treeview(tree, c, False))
                tree.column(column, width=120, anchor='center')

            def edit_booking_dates():
                selected_item = tree.selection()
                if selected_item:
                    booking_id = tree.item(selected_item)['values'][0]
                    cursor.execute("SELECT status, start_time, end_time FROM new_car_bookings WHERE booking_id = %s", (booking_id,))
                    booking_info = cursor.fetchone()
                    if booking_info and booking_info[0] == 1:
                        status, start_date, end_date = booking_info[0], booking_info[1], booking_info[2]

                        # Open a new window for editing dates
                        edit_dates_window = tk.Toplevel(root)
                        edit_dates_window.title("Edit Booking Dates")

                        # Heading "Edit Booking"
                        tk.Label(edit_dates_window, text="Edit Booking", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, padx=(10,0), pady=(10, 20))

                        tk.Label(edit_dates_window, text="New Start Date:").grid(row=1, column=0, padx=10, pady=5)
                        new_start_date_entry = DateEntry(edit_dates_window, date_pattern = "mm-dd-yyyy", width=12, background='darkblue',
                                                        foreground='white', borderwidth=2)
                        new_start_date_entry.grid(row=1, column=1, padx=10, pady=5)
                        new_start_date_entry.set_date(start_date)  # Set the default date to the current start date

                        # DateEntry widget for selecting new end date
                        tk.Label(edit_dates_window, text="New End Date:").grid(row=2, column=0, padx=10, pady=5)
                        new_end_date_entry = DateEntry(edit_dates_window, date_pattern = "mm-dd-yyyy", width=12, background='darkblue',
                                                    foreground='white', borderwidth=2)
                        new_end_date_entry.grid(row=2, column=1, padx=10, pady=5)
                        new_end_date_entry.set_date(end_date)  # Set the default date to the current end date


                        def save_changes():
                            new_start_date = new_start_date_entry.get()
                            new_end_date = new_end_date_entry.get()
                            #print("Dates:", new_start_date,new_end_date)
                            new_start_date = dt.strptime(new_start_date, "%m-%d-%Y")
                            new_end_date = dt.strptime(new_end_date, "%m-%d-%Y")
                            start_date_formatted = new_start_date.strftime('%Y-%m-%d')
                            end_date_formatted = new_end_date.strftime('%Y-%m-%d')

                            def refresh_booking_details():
                                # Clear existing booking details in the treeview
                                for child in tree.get_children():
                                    tree.delete(child)

                                # Fetch and display updated booking details
                                cursor.execute("SELECT * FROM new_car_bookings WHERE user_id = (SELECT user_id FROM users WHERE email = %s)", (current_user_email,))
                                booking_data = cursor.fetchall()
                                for booking in booking_data:
                                    tree.insert("", "end", values=(booking[0], booking[3], booking[4], booking[5], booking[6], booking[7]), tags=(booking[0],))

                            
                            if new_start_date < datetime.now():
                                messagebox.showerror("Error", "Start date cannot be in the past.")
                                return edit_booking_dates()

                            if new_end_date < datetime.now():
                                messagebox.showerror("Error", "End date cannot be in the past.")
                                return edit_booking_dates()

                            if new_end_date < new_start_date:
                                messagebox.showerror("Error", "End date cannot be before start date.")
                                return edit_booking_dates()

                            cursor.execute("UPDATE new_car_bookings SET start_time = %s, end_time = %s WHERE booking_id = %s", (start_date_formatted, end_date_formatted, booking_id))
                            db.commit()

                            # Fetch booking information including the daily rate
                            cursor.execute("SELECT car_id FROM new_car_bookings WHERE booking_id = %s", (booking_id,))
                            car_id = cursor.fetchone()
                            cursor.execute("SELECT price,car_name,car_type FROM cars WHERE car_id = %s", (car_id[0],))
                            booking_info = cursor.fetchone()
                            if booking_info:
                                daily_rate = booking_info[0]

                                # Calculate the number of days between the new start and end dates
                                num_days = (new_end_date - new_start_date).days
                                # Calculate the new total price based on the daily rate and number of days
                                new_price = num_days * daily_rate
                                # Update the price in the database
                                cursor.execute("UPDATE new_car_bookings SET total_price = %s WHERE car_id = %s", (new_price, car_id[0]))
                                db.commit()

                                # Close edit_dates_window
                                edit_dates_window.destroy()

                                # Refresh the booking details section in the profile frame
                                refresh_booking_details()
                            else:
                                messagebox.showerror("Error", "Failed to fetch booking details.")

                            start_date_formatted = new_start_date.strftime('%m-%d-%Y')
                            end_date_formatted = new_end_date.strftime('%m-%d-%Y')
                            message= f"Dear {current_user_fullname},\n\nYour booking for {booking_info[1]} ({booking_info[2]}) has been modified.\n\nBooking Details:\n\nUpdated Start Date: {start_date_formatted}\nUpdated End Date: {end_date_formatted}\nUpdated Total Price: ${new_price}\n\nThank you for choosing our service.\nHere is the attached receipt for your reference.\n\nBest Regards,\nThe Car Rental Team"
                            # Send confirmation email to the user
                            send_confirmation_email(current_user_name, current_user_email, booking_info[1], booking_info[2], start_date_formatted, end_date_formatted, new_price,message)

                            messagebox.showinfo("Success", f"Booking dates updated successfully.\nUpdated Start Date: {start_date_formatted}\nUpdated End Date: {end_date_formatted}\nUpdated Price: {new_price}\n\nConfirmation Mail sent to {current_user_email}")
                            # Close edit_dates_window
                            edit_dates_window.destroy()

                            # Refresh the booking details section in the profile frame
                            refresh_booking_details()


                        def cancel_changes():
                            edit_dates_window.destroy()

                        save_button = tk.Button(edit_dates_window, text="Save", command=save_changes, bg="#B3DFF7", font=("Calibri", 11))
                        save_button.grid(row=3, column=0, padx=(10, 5), pady=10)

                        # Button to cancel changes
                        cancel_button = tk.Button(edit_dates_window, text="Cancel", command=cancel_changes, bg="#B3DFF7", font=("Calibri", 11))
                        cancel_button.grid(row=3, column=1, padx=(5, 10), pady=10)

                    else:
                        messagebox.showinfo("Information", "This car has been returned. Dates cannot be edited.")
                else:
                    messagebox.showinfo("Information", "Please select a booking to edit dates.")

            edit_button = tk.Button(profile_frame, text="Edit Booking Dates", command=edit_booking_dates, bg="#B3DFF7", font=("Calibri", 11))
            edit_button.grid(row=10, column=1, pady=10)

        else:
            tk.Label(profile_frame, text="No Booking History", font=("Helvetica", 12)).grid(row=8, column=0, columnspan=3, sticky="ew")


        def edit_profile():
            # Enable editing of user details
            first_name_entry.config(state='normal')
            last_name_entry.config(state='normal')
            email_entry.config(state='normal')
            phone_entry.config(state='normal')
            age_entry.config(state='normal')
            address_entry.config(state='normal')

            # Change the text of the button to "Save"
            edit_button.config(text="Save", command=save_profile)



        def save_profile():
            # Get updated user details
            updated_first_name = first_name_entry.get()
            updated_last_name = last_name_entry.get()
            updated_email = email_entry.get()
            updated_phone = phone_entry.get()
            updated_age = age_entry.get()
            updated_address = address_entry.get()

            # Update user details in the database
            cursor.execute("UPDATE users SET first_name = %s, last_name = %s, email = %s, phone_number = %s, age = %s, address1 = %s WHERE email = %s",
                           (updated_first_name, updated_last_name, updated_email, updated_phone, updated_age, updated_address.split(",")[0], current_user_email))
            db.commit()

            # Display success message
            messagebox.showinfo("Success", "Profile updated successfully.")

            # Disable editing of user details
            first_name_entry.config(state='readonly')
            last_name_entry.config(state='readonly')
            email_entry.config(state='readonly')
            phone_entry.config(state='readonly')
            age_entry.config(state='readonly')
            address_entry.config(state='readonly')

            # Change the text of the button back to "Edit Profile"
            edit_button.config(text="Edit Profile", command=edit_profile)

        def leave_feedback():
            selected_item = tree.selection()
            if selected_item:
                booking_id = tree.item(selected_item)['values'][0]

                # Open a new window for feedback
                feedback_window = tk.Toplevel(root)
                feedback_window.title("Leave Feedback")

                # Heading "Leave Feedback"
                tk.Label(feedback_window, text="Leave Feedback", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, padx=(10,0), pady=(10, 20))

                # Label and text box for review
                tk.Label(feedback_window, text="Review:").grid(row=1, column=0, padx=10, pady=5)
                review_text = tk.Text(feedback_window, height=5, width=40)
                review_text.grid(row=1, column=1, padx=10, pady=5)

                tk.Label(feedback_window, text="Rating:").grid(row=2, column=0, padx=10, pady=5)
                rating_var = tk.StringVar(value="")  # Default rating is empty
                rating_combobox = ttk.Combobox(feedback_window, textvariable=rating_var, values=["1", "2", "3", "4", "5"])
                rating_combobox.grid(row=2, column=1, padx=10, pady=5)

                # Set the background color of the Combobox
                rating_combobox['style'] = 'W.TCombobox'  # This line ensures that the Combobox has a white background
                feedback_window.style = ttk.Style()
                feedback_window.style.theme_use('clam')
                feedback_window.style.configure('W.TCombobox', background="white")

                def submit_feedback():
                    review = review_text.get("1.0", tk.END).strip()  # Get the content of the text box and strip any leading/trailing whitespace
                    rating = rating_var.get().strip()  # Get the selected rating and strip any leading/trailing whitespace

                    # Check if either review or rating is provided
                    if review or rating:
                        # Convert rating to integer if it's provided
                        if rating:
                            rating = int(rating)

                        # Update the review column in the database if review is provided
                        if review:
                            cursor.execute("UPDATE new_car_bookings SET review = %s WHERE booking_id = %s", (review, booking_id))
                            db.commit()

                        # Update the rating column in the database if rating is provided
                        if rating:
                            cursor.execute("UPDATE new_car_bookings SET rating = %s WHERE booking_id = %s", (rating, booking_id))
                            db.commit()

                        # Close the feedback window
                        feedback_window.destroy()
                        messagebox.showinfo("Success", "Feedback submitted successfully.")
                    else:
                        # If neither review nor rating is provided, allow submission
                        messagebox.showwarning("Warning", "You haven't provided a review or a rating. Are you sure you want to proceed?")
                        # Close the feedback window
                        feedback_window.destroy()


                # Button to submit feedback
                submit_button = tk.Button(feedback_window, text="Submit", command=submit_feedback, bg="#B3DFF7", font=("Calibri", 11))
                submit_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

            else:
                messagebox.showinfo("Information", "Please select a booking to leave feedback.")

        # Create buttons for editing and saving profile
        edit_button = tk.Button(profile_frame, text="Edit Profile", command=edit_profile, bg="#B3DFF7", font=("Calibri", 11))
        edit_button.grid(row=10, column=1, pady=15, sticky='w')

        # Add a button for leaving feedback
        feedback_button = tk.Button(profile_frame, text="Feedback", command=leave_feedback, bg="#B3DFF7", font=("Calibri", 11))
        feedback_button.grid(row=10, column=1, pady=10,sticky='e')
        # Create a button to close the profile frame
        close_button = tk.Button(profile_frame, text="Back", command=create_car_selection_screen, bg="#B3DFF7", font=("Calibri", 11))
        close_button.grid(row=0, column=2, padx=10, pady=10, sticky='ne')
    else:
        messagebox.showerror("Error", "Failed to fetch user details.")
    profile_frame_displayed = True

def reset_password():
    email = forget_email_entry.get()
    if not email:
        messagebox.showerror("Error", "Please enter your email.")
        return

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        # Prompt the user to enter a new password
        new_password = prompt_for_new_password()

        cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
        password = cursor.fetchone()[0]

        if password==new_password:
            messagebox.showerror("Error", "Your new password cannot be the same as your old password.")
            return

        # Validation checks for password
        if not is_valid_password(new_password):
            messagebox.showerror("Error", "Password must contain at least one lowercase letter, one uppercase letter, one special character (@, $, %), one digit, and be at least 8 characters long.")
            return

        # Update the password in the database
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
        db.commit()
        messagebox.showinfo("Success", "Your password has been successfully reset.")
        forget_password_frame.pack_forget()
        show_login_screen()

    else:
        messagebox.showerror("Error", "Invalid username")

def show_signup_screen():
    # Shows the signup screen by hiding the login screen
    login_frame.pack_forget()
    signup_frame.pack(expand=1)

def show_login_screen():
    # Shows the login screen by hiding the signup screen
    signup_frame.pack_forget()
    login_frame.pack(expand=1)

def show_forget_password():
    # Hide login frame
    login_frame.pack_forget()
    forget_password_frame.pack(expand=1)
    # Create forget password screen if not already created
    if not 'forget_password_screen_created' in globals() or not forget_password_screen_created:
        create_forget_password_screen()
        forget_password_screen_created = True

    #Clear the email entry
    forget_email_entry.delete(0, tk.END)

def hide_forget_password():
    forget_password_frame.pack_forget()
    login_frame.pack(expand=1)

def prompt_for_new_password():
    new_password = simpledialog.askstring("New Password", "Enter your new password:", show='*')
    return new_password

def toggle_password_visibility():
    if show_hide_password_var.get():
        login_password_entry.config(show="")
    else:
        login_password_entry.config(show="*")

# Initialize the root window
root = tk.Tk()
root.title("DriveEasy - CarRentalSystem")
root.geometry("1100x600")
root.configure(bg="#DFFFFF")
create_tables()

background_image = tk.PhotoImage(file=r"C:\Users\preet\OneDrive\Desktop\698\banner-2.png")

# Create a label with the background image
background_label = tk.Label(root, image=background_image)
background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

signup_frame = tk.Frame(root, padx=20, pady=15)
signup_frame.pack(expand=1)

tk.Label(signup_frame, text="Sign Up", font=("Helvetica", 20, "bold")).grid(row=0, column=0, columnspan=2, sticky="ew")

signup_attributes = ['First name', 'Last name', 'Email', 'Phone number', 'Age', 'Address 1', 'Address 2',
                      'City', 'State', 'Country', 'Zipcode']
signup_entries = {}
for idx, attribute in enumerate(signup_attributes, start=1):
    tk.Label(signup_frame, text=f"{attribute}:", anchor="w", font=("Calibri", 11)).grid(row=idx, column=0, sticky="w", pady=(5, 0))
    signup_entries[attribute] = tk.Entry(signup_frame, width=35)
    signup_entries[attribute].grid(row=idx, column=1, padx=(0, 10), pady=(5, 0))

# Password fields for signup
idx += 1
tk.Label(signup_frame, text="Password:", anchor="w", font=("Calibri", 11)).grid(row=idx, column=0, sticky="w", pady=(5, 0))
signup_password_entry = tk.Entry(signup_frame, show="*", width=35)
signup_password_entry.grid(row=idx, column=1, padx=(0, 10), pady=(5, 0))

idx += 1
tk.Label(signup_frame, text="Confirm Password:", font=("Calibri", 11), anchor="w").grid(row=idx, column=0, sticky="w", pady=(5, 0))
signup_confirm_password_entry = tk.Entry(signup_frame, show="*", width=35)
signup_confirm_password_entry.grid(row=idx, column=1, padx=(0, 10), pady=(5, 0))

# Signup button and login redirection
idx += 1
tk.Button(signup_frame, text="Sign Up", command=signup, bg="#B3DFF7", font=("Calibri", 11)).grid(row=idx, column=0, columnspan=2, pady=(10, 5))
tk.Button(signup_frame, text="Already have an account? Login", command=show_login_screen, bg="#B3DFF7", font=("Calibri", 11)).grid(
    row=idx + 1, column=0, columnspan=2, pady=(5, 0))

# Creates a frame for the login section
login_frame = tk.Frame(root, padx=15, pady=15)
login_frame.pack(expand=1)

# Labels and entry fields for user login
tk.Label(login_frame, text="DriveEasyLogin", font=("Helvetica", 20, "bold")).grid(row=0, column=0, columnspan=2, sticky="ew")

# Add space after the login heading by inserting an empty row
tk.Label(login_frame).grid(row=1)  # Empty row

tk.Label(login_frame, text="Email:", font=("Calibri", 14)).grid(row=2, column=0, sticky="w")
login_email_entry = tk.Entry(login_frame, width=30)
login_email_entry.grid(row=2, column=1)

# Add space after the login heading by inserting an empty row
tk.Label(login_frame).grid(row=3)  # Empty row

tk.Label(login_frame, text="Password:", font=("Calibri", 14)).grid(row=4, column=0, sticky="w")
login_password_entry = tk.Entry(login_frame, show="*", width=30)
login_password_entry.grid(row=4, column=1)

# Create a checkbox below the password entry box
show_hide_password_var = tk.BooleanVar()
show_hide_password_checkbutton = tk.Checkbutton(login_frame, text="Show Password", font=("Calibri", 12),variable=show_hide_password_var, command=toggle_password_visibility)
show_hide_password_checkbutton.grid(row=5, column=1, columnspan=2, sticky="w",padx=(0, 10))

# Login button and signup redirection
login_button = tk.Button(login_frame, text="Login", command=login, bg="#B3DFF7", font=("Calibri", 11))
login_button.grid(row=6, column=0, columnspan=2, pady=(20, 5))  # Add padding on the top and bottom

# Create an account button
create_account_button = tk.Button(login_frame, text="Create an account", command=show_signup_screen, bg="#B3DFF7", font=("Calibri", 11))
create_account_button.grid(row=7, column=0, pady=(5, 20), sticky="w",  padx=(40, 0))  # Align to the right side

# Forgot Password button
forgot_password_button = tk.Button(login_frame, text="Forgot Password?", command=show_forget_password, bg="#B3DFF7", font=("Calibri", 11))
forgot_password_button.grid(row=7, column=1, pady=(5, 20), sticky="e",  padx=(0, 40))  # Align to the left side

# Displaying the login screen initially
show_login_screen()
forget_password_frame = tk.Frame(root, padx=15, pady=15)
forget_email_entry = tk.Entry(forget_password_frame, width=30)


# Creates the main application window and start the application
root.mainloop()