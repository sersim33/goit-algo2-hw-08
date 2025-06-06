import random
from typing import Dict
import time
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, window_size: float, max_requests: int):
        # Initialize the attributes
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_requests: Dict[str, deque] = {}  # Dictionary to store user requests

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        # Remove timestamps outside the current window
        if user_id in self.user_requests:
            # Remove requests older than window_size
            while self.user_requests[user_id] and self.user_requests[user_id][0] <= current_time - self.window_size:
                self.user_requests[user_id].popleft()


    def can_send_message(self, user_id: str) -> bool:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        # Check if the number of requests in the window is within the limit
        if user_id not in self.user_requests:
            return True # No requests yet, so allowed

        return len(self.user_requests[user_id]) < self.max_requests


    def record_message(self, user_id: str) -> bool:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if self.can_send_message(user_id):
            # Record the current request timestamp
            if user_id not in self.user_requests:
                self.user_requests[user_id] = deque()
            self.user_requests[user_id].append(current_time)
            return True
        return False


    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.user_requests or len(self.user_requests[user_id]) < self.max_requests:
            return 0.0  # Allowed to send immediately

        # The earliest request in the window
        earliest_request_time = self.user_requests[user_id][0]
        # The time when the earliest request will fall out of the window
        window_end_time = earliest_request_time + self.window_size
        # Time until the window opens up again by removing the oldest request
        wait_time = max(0.0, window_end_time - current_time)
        return wait_time

# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
