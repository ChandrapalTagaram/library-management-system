
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Chan@2026",
    database="library_management"
)

cursor = conn.cursor()


# 1. Add Book
def add_book():
    title = input("Enter book title: ").strip()
    author = input("Enter author name: ").strip()
    quantity = input("Enter number of copies: ")

    if not title or not author:
        print("Title and author cannot be empty.")
        return

    if not quantity.isdigit() or int(quantity) < 1:
        print("Enter a valid quantity (at least 1).")
        return

    cursor.execute(
        """INSERT INTO books (title, author, quantity)
        VALUES (%s, %s, %s)""",
        (title, author, int(quantity))
    )
    conn.commit()
    print("Book added successfully!")


# 2. View Books
def view_books():
    cursor.execute(
        "SELECT book_id, title, author, quantity FROM books"
    )
    books = cursor.fetchall()

    if not books:
        print("No books found.")
        return

    print("\n===== BOOK LIST =====")

    for book in books:
        print(
            f"ID: {book[0]} | Title: {book[1]} | "
            f"Author: {book[2]} | Available Copies: {book[3]}"
        )


# 3. Search Book
def search_book():
    title = input("Enter book title to search: ").strip()

    cursor.execute(
        """SELECT book_id, title, author, quantity
        FROM books WHERE title LIKE %s""",
        ("%" + title + "%",)
    )

    results = cursor.fetchall()

    if results:
        for book in results:
            print(
                f"ID: {book[0]} | Title: {book[1]} | "
                f"Author: {book[2]} | Available Copies: {book[3]}"
            )
    else:
        print("Book not found.")


# 4. Delete Book
def delete_book():
    book_id = input("Enter book ID to delete: ")

    if not book_id.isdigit() or int(book_id) <= 0:
        print("Enter a valid book ID.")
        return

    try:
        cursor.execute(
            "DELETE FROM books WHERE book_id = %s",
            (int(book_id),)
        )

        deleted = cursor.rowcount
        conn.commit()

        if deleted > 0:
            print("Book deleted successfully!")
        else:
            print("Book ID not found.")

    except mysql.connector.IntegrityError:
        conn.rollback()
        print(
            "Cannot delete this book because issue records exist."
        )
        print(
            "The book and its issue history have been preserved."
        )


# 5. Add Student
def add_student():
    name = input("Enter student name: ").strip()

    if not name:
        print("Student name cannot be empty.")
        return

    cursor.execute(
        "INSERT INTO students (name) VALUES (%s)",
        (name,)
    )
    conn.commit()

    print("Student added successfully!")
    print("Student ID:", cursor.lastrowid)


# 6. Issue Book
def issue_book():
    book_id = input("Enter book ID: ")
    student_id = input("Enter student ID: ")

    if (not book_id.isdigit() or int(book_id) <= 0
            or not student_id.isdigit()
            or int(student_id) <= 0):
        print("Enter valid book and student IDs.")
        return

    book_id = int(book_id)
    student_id = int(student_id)

    try:
        cursor.execute(
            """SELECT quantity FROM books
            WHERE book_id = %s FOR UPDATE""",
            (book_id,)
        )
        book = cursor.fetchone()

        if book is None:
            conn.rollback()
            print("Book ID not found.")
            return

        if book[0] <= 0:
            conn.rollback()
            print("No copies are available.")
            return

        cursor.execute(
            "SELECT student_id FROM students WHERE student_id = %s",
            (student_id,)
        )

        if cursor.fetchone() is None:
            conn.rollback()
            print("Student ID not found.")
            return

        cursor.execute(
            """INSERT INTO issued_books
            (book_id, student_id, issue_date)
            VALUES (%s, %s, CURDATE())""",
            (book_id, student_id)
        )

        cursor.execute(
            """UPDATE books
            SET quantity = quantity - 1
            WHERE book_id = %s""",
            (book_id,)
        )

        issue_id = cursor.lastrowid
        conn.commit()

        print("Book issued successfully!")
        print("Issue ID:", issue_id)

    except mysql.connector.Error as error:
        conn.rollback()
        print("Could not issue book:", error)


# 7. Return Book
def return_book():
    issue_id = input("Enter issue ID: ")

    if not issue_id.isdigit() or int(issue_id) <= 0:
        print("Enter a valid issue ID.")
        return

    try:
        cursor.execute(
            """SELECT book_id FROM issued_books
            WHERE issue_id = %s AND return_date IS NULL""",
            (int(issue_id),)
        )

        record = cursor.fetchone()

        if record is None:
            print("Issue ID not found or book already returned.")
            return

        book_id = record[0]

        cursor.execute(
            """UPDATE issued_books
            SET return_date = CURDATE()
            WHERE issue_id = %s AND return_date IS NULL""",
            (int(issue_id),)
        )

        if cursor.rowcount == 0:
            conn.rollback()
            print("Book could not be returned.")
            return

        cursor.execute(
            """UPDATE books
            SET quantity = quantity + 1
            WHERE book_id = %s""",
            (book_id,)
        )

        conn.commit()

        print("Book returned successfully!")
        print("Available copies increased by 1.")

    except mysql.connector.Error as error:
        conn.rollback()
        print("Could not return book:", error)


# 8. View Issued Books
def view_issued_books():
    cursor.execute("""
        SELECT ib.issue_id, b.title, s.name,
               ib.issue_date, ib.return_date
        FROM issued_books ib
        JOIN books b ON ib.book_id = b.book_id
        JOIN students s ON ib.student_id = s.student_id
        ORDER BY ib.issue_id
    """)

    records = cursor.fetchall()

    if not records:
        print("No issued books found.")
        return

    print("\n===== ISSUED BOOKS REPORT =====")

    for record in records:
        issue_id, title, student, issue_date, return_date = record

        status = "Returned" if return_date else "Currently Issued"

        print("-" * 40)
        print("Issue ID:", issue_id)
        print("Book Title:", title)
        print("Student Name:", student)
        print("Issue Date:", issue_date)
        print("Return Date:", return_date or "Not returned")
        print("Status:", status)


# 9. View Book Availability
def view_availability():
    cursor.execute(
        """SELECT book_id, title, author, quantity
        FROM books ORDER BY book_id"""
    )

    books = cursor.fetchall()

    if not books:
        print("No books found.")
        return

    print("\n===== BOOK AVAILABILITY =====")

    for book in books:
        status = "Available" if book[3] > 0 else "Out of Stock"

        print(
            f"ID: {book[0]} | Title: {book[1]} | "
            f"Author: {book[2]} | Available Copies: {book[3]} | "
            f"{status}"
        )


# Main Menu
while True:
    print("\n===== LIBRARY MANAGEMENT SYSTEM =====")
    print("1. Add Book")
    print("2. View Books")
    print("3. Search Book")
    print("4. Delete Book")
    print("5. Add Student")
    print("6. Issue Book")
    print("7. Return Book")
    print("8. View Issued Books")
    print("9. View Book Availability")
    print("10. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_book()
    elif choice == "2":
        view_books()
    elif choice == "3":
        search_book()
    elif choice == "4":
        delete_book()
    elif choice == "5":
        add_student()
    elif choice == "6":
        issue_book()
    elif choice == "7":
        return_book()
    elif choice == "8":
        view_issued_books()
    elif choice == "9":
        view_availability()
    elif choice == "10":
        cursor.close()
        conn.close()
        print("Program closed.")
        break
    else:
        print("Invalid choice. Try again.")
