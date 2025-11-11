import requests

BASE_URL = "http://127.0.0.1:5000"

MENU = """
===========================
      LIBRARY SYSTEM
===========================
1. Add Book
2. Remove Book
3. Register Member
4. Borrow Book
5. Return Book
6. List All Books
7. List Available Books
8. Search Books
9. List Members
10. List Borrowed Books
11. Exit
===========================
"""

def main():
    while True:
        print(MENU)
        choice = input("Enter your choice: ").strip()

        try:
            if choice == "1":
                bid = input("Enter Book ID: ").strip()
                title = input("Enter Title: ").strip()
                author = input("Enter Author: ").strip()
                res = requests.post(f"{BASE_URL}/books", json={"book_id": bid, "title": title, "author": author})
                print(res.json())

            elif choice == "2":
                bid = input("Enter Book ID to remove: ").strip()
                res = requests.delete(f"{BASE_URL}/books/{bid}")
                print(res.json())

            elif choice == "3":
                name = input("Enter Member Name: ").strip()
                mid = input("Enter Member ID: ").strip()
                res = requests.post(f"{BASE_URL}/members", json={"name": name, "member_id": mid})
                print(res.json())

            elif choice == "4":
                mid = input("Enter Member ID: ").strip()
                bid = input("Enter Book ID: ").strip()
                res = requests.post(f"{BASE_URL}/borrow", json={"member_id": mid, "book_id": bid})
                print(res.json())

            elif choice == "5":
                mid = input("Enter Member ID: ").strip()
                bid = input("Enter Book ID: ").strip()
                res = requests.post(f"{BASE_URL}/return", json={"member_id": mid, "book_id": bid})
                print(res.json())

            elif choice == "6":
                res = requests.get(f"{BASE_URL}/books")
                books = res.json()
                print("\n--- All Books ---")
                for b in books:
                    print(f"{b['book_id']} | {b['title']} | {b['author']} | Available: {b['available']}")
                print("----------------\n")

            elif choice == "7":
                res = requests.get(f"{BASE_URL}/books/available")
                books = res.json()
                print("\n--- Available Books ---")
                for b in books:
                    print(f"{b['book_id']} | {b['title']} | {b['author']}")
                print("-----------------------\n")

            elif choice == "8":
                query = input("Enter title or author keyword: ").strip()
                res = requests.get(f"{BASE_URL}/books/search", params={"q": query})
                print(res.json())

            elif choice == "9":
                res = requests.get(f"{BASE_URL}/members")
                print(res.json())

            elif choice == "10":
                res = requests.get(f"{BASE_URL}/borrowed")
                print(res.json())

            elif choice == "11":
                print("Exiting CLI. Goodbye!")
                break

            else:
                print("Invalid choice. Enter 1–11.")

        except requests.exceptions.ConnectionError:
            print("Cannot connect to API. Make sure Flask server is running at", BASE_URL)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
