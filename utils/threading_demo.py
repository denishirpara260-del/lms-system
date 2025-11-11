import threading
from library import Library

lock = threding.Lock()
lib = Library()

def borrow_simulation(member_id, book_id):
    with lock:
        try:
            print(f"Member {member_id} borrowing book {book_id}")
        except Exception as e:
            print("Error:", e)

threads = [threading.Thread(target=borrow_simulation, args=("m1", "b1")) for _ in range(3)]

for t in threads:
    t.start()
for t in threads:
    t.join()
