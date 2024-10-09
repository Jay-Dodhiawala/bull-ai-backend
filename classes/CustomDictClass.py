from threading import Thread, Lock
import time

class ActiveUserDictionary:
    def __init__(self, timeout=180):  # 180 seconds = 3 minutes
        self.users = {}
        self.timeout = timeout
        self.lock = Lock()
        self.cleanup_thread = Thread(target=self._cleanup_inactive_users, daemon=True)
        self.cleanup_thread.start()

    def __setitem__(self, key, value):
        with self.lock:
            if key not in self.users:
                self.users[key] = {"data": {}, "last_active": time.time()}
            self.users[key]["data"].update(value)
            self.users[key]["last_active"] = time.time()

    def __getitem__(self, key):
        with self.lock:
            if key in self.users:
                self.users[key]["last_active"] = time.time()
                return self.users[key]["data"]
            raise KeyError(key)

    def __contains__(self, key):
        with self.lock:
            return key in self.users

    def __delitem__(self, key):
        with self.lock:
            del self.users[key]

    def _cleanup_inactive_users(self):
        while True:
            with self.lock:
                current_time = time.time()
                inactive_users = [
                    key for key, data in self.users.items()
                    if current_time - data["last_active"] > self.timeout
                ]
                for user in inactive_users:
                    del self.users[user]
            time.sleep(60)  # Check every minute