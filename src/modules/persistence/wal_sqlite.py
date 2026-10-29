"""
FreeNode SQLite WAL Persister
Stores FreeNode state with Write-Ahead Logging for atomic, crash-safe persistence
Based on lxcbot pattern from hopingboyz/lxcbot
"""
import sqlite3
import json
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("freenode.persistence.wal")


class SQLitePersister:
    """Atomic state persistence with SQLite WAL mode"""
    
    def __init__(self, db_path: str = "/opt/freenode/state/freenode.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self._init_db()
    
    def _init_db(self):
        """Initialize database with WAL mode and proper schema"""
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                # Enable WAL mode for crash safety
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=FULL")
                cursor.execute("PRAGMA foreign_keys=ON")
                
                # Create state table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS freenode_state (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create checkpoint table for recovery tracking
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS checkpoint (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        state_hash TEXT,
                        status TEXT DEFAULT 'success'
                    )
                """)
                
                conn.commit()
                conn.close()
                logger.info("✅ SQLite WAL database initialized")
        except Exception as e:
            logger.error(f"Database init failed: {e}")
    
    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection with proper settings"""
        conn = sqlite3.connect(str(self.db_path), timeout=30, check_same_thread=False)
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("PRAGMA synchronous=FULL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """Atomically save state with WAL guarantees"""
        try:
            with self.lock:
                conn = self._get_conn()
                
                # Start immediate transaction for atomicity
                conn.execute("BEGIN IMMEDIATE")
                
                try:
                    state_json = json.dumps(state)
                    state_hash = str(hash(state_json))
                    
                    cursor = conn.cursor()
                    
                    # Save state
                    cursor.execute(
                        "INSERT OR REPLACE INTO freenode_state (key, value) VALUES (?, ?)",
                        ("state", state_json)
                    )
                    
                    # Record checkpoint
                    cursor.execute(
                        "INSERT INTO checkpoint (state_hash, status) VALUES (?, ?)",
                        (state_hash, "success")
                    )
                    
                    conn.commit()
                    logger.info(f"✅ State saved (hash: {state_hash})")
                    return True
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Transaction failed: {e}")
                    return False
                finally:
                    conn.close()
        except Exception as e:
            logger.error(f"SQLite save failed: {e}")
            return False
    
    def load_state(self) -> Dict[str, Any]:
        """Load state with automatic recovery on corruption"""
        try:
            with self.lock:
                conn = self._get_conn()
                cursor = conn.cursor()
                
                # Try to load current state
                cursor.execute("SELECT value FROM freenode_state WHERE key='state'")
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    state = json.loads(row[0])
                    logger.info("✅ State loaded successfully")
                    return state
                
                logger.warning("No previous state found, returning empty")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"State JSON corrupt: {e}")
            return {}
        except Exception as e:
            logger.error(f"SQLite load failed: {e}")
            return {}
    
    def backup(self, backup_path: str = None) -> bool:
        """Create a backup of the database"""
        if backup_path is None:
            backup_path = str(self.db_path) + ".backup"
        
        try:
            with self.lock:
                conn = self._get_conn()
                backup_conn = sqlite3.connect(backup_path)
                
                conn.backup(backup_conn)
                backup_conn.close()
                conn.close()
                
                logger.info(f"✅ Backup created: {backup_path}")
                return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def checkpoint(self) -> bool:
        """Force WAL checkpoint (optional maintenance)"""
        try:
            with self.lock:
                conn = self._get_conn()
                conn.execute("PRAGMA wal_checkpoint(RESTART)")
                conn.close()
                logger.info("✅ WAL checkpoint completed")
                return True
        except Exception as e:
            logger.error(f"Checkpoint failed: {e}")
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    persister = SQLitePersister()
    
    # Test save and load
    test_state = {"platform": "chainide", "uptime": 3600, "version": "0.6.0"}
    persister.save_state(test_state)
    
    loaded = persister.load_state()
    print(f"Saved state: {test_state}")
    print(f"Loaded state: {loaded}")
