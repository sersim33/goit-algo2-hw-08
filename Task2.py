import time
from typing import Dict
import random

class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval
        # Dictionary to store the timestamp of the last request for each user
        self.last_request_time: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        current_time = time.time()
        # Check if the user has sent a message before and if the minimum interval has passed
        if user_id not in self.last_request_time:
            return True  # No previous requests, so allowed
        return current_time - self.last_request_time[user_id] >= self.min_interval

    def record_message(self, user_id: str) -> bool:
        current_time = time.time()
        if self.can_send_message(user_id):
            # Record the current timestamp as the last request time
            self.last_request_time[user_id] = current_time
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        if user_id not in self.last_request_time:
            return 0.0  # Allowed to send immediately

        # Calculate the time until the minimum interval has passed since the last request
        time_since_last_request = current_time - self.last_request_time[user_id]
        wait_time = max(0.0, self.min_interval - time_since_last_request)
        return wait_time

def test_throttling_limiter():
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\\n=== Симуляція потоку повідомлень (Throttling) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Випадкова затримка між повідомленнями
        time.sleep(random.uniform(0.1, 1.0))

    print("\\nОчікуємо 10 секунд...")
    time.sleep(10)

    print("\\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_throttling_limiter()
