import streamlit as st
from pymongo import MongoClient
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["library"]
books_collection = db["books"]
readers_collection = db["readers"]
borrowed_books_collection = db["borrowed_books"]

# Streamlit UI
st.title("Library Management System")
st.image("library.jpg")
menu = ["Books", "Readers", "Borrow", "Fines"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Books":
    st.subheader("Books")

    book_menu = ["Add Book", "View Books", "Search Book", "Delete Book"]
    book_choice = st.sidebar.selectbox("Book Menu", book_menu)

    if book_choice == "Add Book":
        st.subheader("Add New Book")
        title = st.text_input("Title")
        author = st.text_input("Author")
        genre = st.text_input("Genre")
        if st.button("Add Book"):
            book = {"title": title, "author": author, "genre": genre}
            books_collection.insert_one(book)
            st.success("Book added successfully!")

    elif book_choice == "View Books":
        st.subheader("View All Books")
        books = books_collection.find()
        for book in books:
            st.write(f"Title: {book['title']}, Author: {book['author']}, Genre: {book['genre']}")

    elif book_choice == "Search Book":
        st.subheader("Search Books")
        search_term = st.text_input("Enter Book Name / Author / Genre")
        search_results = books_collection.find({"$or": [{"title": {"$regex": search_term, "$options": "i"}},
                                                        {"author": {"$regex": search_term, "$options": "i"}},
                                                        {"genre": {"$regex": search_term, "$options": "i"}}]})
        for result in search_results:
            st.write(f"Title: {result['title']}, Author: {result['author']}, Genre: {result['genre']}")

    elif book_choice == "Delete Book":
        st.subheader("Delete Book")
        book_id = st.text_input("Enter Book Title")
        if st.button("Delete Book"):
            result = books_collection.delete_one({"title": book_id})
            if result.deleted_count > 0:
                st.success("Book deleted successfully!")
            else:
                st.error("Book not found!")

elif choice == "Readers":
    st.subheader("Readers")

    reader_menu = ["Add Reader", "View Readers", "Delete Reader"]
    reader_choice = st.sidebar.selectbox("Reader Menu", reader_menu)

    if reader_choice == "Add Reader":
        st.subheader("Add New Reader")
        name = st.text_input("Name")
        email = st.text_input("Email")
        if st.button("Add Reader"):
            reader = {"name": name, "email": email}
            readers_collection.insert_one(reader)
            st.success("Reader added successfully!")

    elif reader_choice == "View Readers":
        st.subheader("View All Readers")
        readers = readers_collection.find()
        for reader in readers:
            st.write(f"Name: {reader['name']}, Email: {reader['email']}")

    elif reader_choice == "Delete Reader":
        st.subheader("Delete Reader")
        reader_id = st.text_input("Enter Reader Name")
        if st.button("Delete Reader"):
            result = readers_collection.delete_one({"name": reader_id})
            if result.deleted_count > 0:
                st.success("Reader deleted successfully!")
            else:
                st.error("Reader not found!")

elif choice == "Borrow":
    st.subheader("Borrow Books")
    book_id = st.text_input("Enter Book Name")
    reader_id = st.text_input("Enter Reader Name")
    due_date = st.date_input("Due Date", datetime.now() + timedelta(days=14))

    if st.button("Borrow"):
        book = books_collection.find_one({"title": book_id})
        reader = readers_collection.find_one({"name": reader_id})

        if book is None:
            st.error("Book not found!")
        elif reader is None:
            st.error("Reader not found!")
        else:
            borrowed_book = {"book_id": book_id, "reader_id": reader_id, "due_date": due_date.strftime('%Y-%m-%d')}
            borrowed_books_collection.insert_one(borrowed_book)
            st.success("Book borrowed successfully!")

            # Check if due date exceeds current date
            if due_date < datetime.now().date():
                # Calculate fine (for example, $1 per day)
                fine_days = (datetime.now().date() - due_date).days
                fine_amount = fine_days * 1
                st.warning(f"Book is {fine_days} days overdue. Fine amount: ${fine_amount}")



elif choice == "Fines":
    st.subheader("Fines")

    # Find readers with overdue books
    current_date = datetime.now().date()
    overdue_books = borrowed_books_collection.find({"due_date": {"$lt": current_date.strftime('%Y-%m-%d')}})
    overdue_readers = set()
    for book in overdue_books:
        reader_id = book["reader_id"]
        overdue_readers.add(reader_id)

    if overdue_readers:
        st.write("Readers with overdue books:")
        for reader_id in overdue_readers:
            reader = readers_collection.find_one({"name": reader_id})
            st.write(f"Name: {reader['name']} , Due Date: {current_date.strftime('%Y-%m-%d')}")

    else:
        st.write("No readers have overdue books.")
