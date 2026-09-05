"""
Bluescreen Trigger v4 - Enterprise BSOD Generator
Advanced version with database persistence, REST API, scheduling, and plugin architecture.
"""

import asyncio
import sys
import logging
import time
import json
import sqlite3
import threading
import hashlib
import secrets
from ctypes import windll, c_int, c_uint, c_ulong, POINTER, byref
from enum import Enum
from typing import Optional, Tuple, Dict, List, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
import psutil
import yaml
from pathlib import Path
import importlib.util
from abc import ABC, abstractmethod
from functools import wraps
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import base64


class PrivilegeLevel(Enum):
    """Enumeration for privilege levels."""
    PROCESS = 0
    THREAD = 1


class ErrorCode(Enum):
    """Common Windows NTSTATUS error codes."""
    INVALID_IMAGE_FORMAT = 0xC000007B
    FATAL_USER_CALLBACK_EXCEPTION = 0xC000013B
    PRIVILEGED_INSTRUCTION = 0xC0000096
    PAGE_FAULT_IN_NONPAGED_AREA = 0x00000050


class TriggerMethod(Enum):
    """Available trigger methods."""
    NTRAISE_HARDERROR = "ntraise"
    DRIVER_EXPLOIT = "driver"
    KERNEL_CALLBACK = "callback"
    PLUGIN_CUSTOM = "plugin"


class TriggerStatus(Enum):
    """Status of trigger execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ABORTED = "aborted"
    SCHEDULED = "scheduled"


@dataclass
class TriggerRecord:
    """Database record for trigger execution."""
    id: int = field(default_factory=lambda: secrets.randbelow(10000000))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    method: str = "ntraise"
    error_code: int = 0xC000007B
    status: str = TriggerStatus.PENDING.value
    duration_ms: float = 0.0
    memory_before_mb: float = 0.0
    memory_after_mb: float = 0.0
    cpu_percent: float = 0.0
    process_count: int = 0
    error_message: Optional[str] = None
    hostname: str = ""
    user: str = ""
    dry_run: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ScheduleConfig:
    """Configuration for scheduled execution."""
    enabled: bool = False
    interval_seconds: int = 3600
    method: str = "ntraise"
    error_code: str = "INVALID_IMAGE_FORMAT"
    dry_run: bool = False
    max_executions: int = -1  # -1 for unlimited
    execution_count: int = 0


@dataclass
class APIConfig:
    """REST API configuration."""
    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 8888
    auth_enabled: bool = False
    auth_token: str = ""
    ssl_enabled: bool = False


@dataclass
class TelemetryConfig:
    """Telemetry collection configuration."""
    enabled: bool = False
    endpoint: str = ""
    include_snapshots: bool = False
    batch_size: int = 10
    flush_interval_seconds: int = 60


class StringEncryption:
    """Simple XOR-based string encryption for obfuscation."""
    
    @staticmethod
    def encrypt(text: str, key: str = "bsod") -> str:
        """Encrypt text using XOR."""
        encrypted = bytearray()
        for i, char in enumerate(text):
            encrypted.append(ord(char) ^ ord(key[i % len(key)]))
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt(encrypted_text: str, key: str = "bsod") -> str:
        """Decrypt XOR-encrypted text."""
        encrypted = base64.b64decode(encrypted_text)
        decrypted = bytearray()
        for i, byte in enumerate(encrypted):
            decrypted.append(byte ^ ord(key[i % len(key)]))
        return decrypted.decode()


class Database:
    """SQLite database for trigger history and metrics."""
    
    def __init__(self, db_path: str = "bluescreen_v4.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Trigger history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS triggers (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    method TEXT NOT NULL,
                    error_code INTEGER,
                    status TEXT NOT NULL,
                    duration_ms REAL,
                    memory_before_mb REAL,
                    memory_after_mb REAL,
                    cpu_percent REAL,
                    process_count INTEGER,
                    error_message TEXT,
                    hostname TEXT,
                    user TEXT,
                    dry_run BOOLEAN
                )
            """)
            
            # Scheduled tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    id INTEGER PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    method TEXT NOT NULL,
                    error_code TEXT,
                    interval_seconds INTEGER,
                    max_executions INTEGER,
                    execution_count INTEGER,
                    enabled BOOLEAN
                )
            """)
            
            # Telemetry events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    data TEXT,
                    sent BOOLEAN DEFAULT 0
                )
            """)
            
            conn.commit()
    
    def insert_trigger(self, record: TriggerRecord) -> int:
        """Insert trigger record into database."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO triggers (timestamp, method, error_code, status, 
                    duration_ms, memory_before_mb, memory_after_mb, cpu_percent, 
                    process_count, error_message, hostname, user, dry_run)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.timestamp, record.method, record.error_code, record.status,
                    record.duration_ms, record.memory_before_mb, record.memory_after_mb,
                    record.cpu_percent, record.process_count, record.error_message,
                    record.hostname, record.user, record.dry_run
                ))
                conn.commit()
                return cursor.lastrowid
    
    def get_trigger_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve trigger history."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM triggers ORDER BY timestamp DESC LIMIT ?
                """, (limit,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total triggers
                cursor.execute("SELECT COUNT(*) FROM triggers")
                total = cursor.fetchone()[0]
                
                # By status
                cursor.execute("""
                    SELECT status, COUNT(*) FROM triggers GROUP BY status
                """)
                by_status = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Average metrics
                cursor.execute("""
                    SELECT AVG(duration_ms), AVG(cpu_percent), AVG(memory_before_mb)
                    FROM triggers WHERE status = 'success'
                """)
                avg_metrics = cursor.fetchone()
                
                return {
                    'total': total,
                    'by_status': by_status,
                    'avg_duration_ms': avg_metrics[0],
                    'avg_cpu_percent': avg_metrics[1],
                    'avg_memory_mb': avg_metrics[2]
                }


class TriggerPlugin(ABC):
    """Base class for trigger plugins."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.name = self.__class__.__name__
    
    @abstractmethod
    def execute(self, error_code: int) -> bool:
        """Execute trigger plugin. Return True if successful."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate plugin requirements."""
        pass
    
    def get_info(self) -> Dict[str, str]:
        """Get plugin information."""
        return {
            'name': self.name,
            'description': self.__class__.__doc__ or "No description"
        }


class PluginManager:
    """Manage trigger plugins."""
    
    def __init__(self, plugin_dir: str = "plugins", logger: Optional[logging.Logger] = None):
        self.plugin_dir = Path(plugin_dir)
        self.logger = logger or logging.getLogger("PluginManager")
        self.plugins: Dict[str, TriggerPlugin] = {}
        self._load_plugins()
    
    def _load_plugins(self):
        """Load plugins from plugin directory."""
        if not self.plugin_dir.exists():
            self.plugin_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for plugin_file in self.plugin_dir.glob("*.py"):
            try:
                self._load_plugin_file(plugin_file)
            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_file}: {e}")
    
    def _load_plugin_file(self, file_path: Path):
        """Load a single plugin file."""
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find TriggerPlugin subclasses
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, TriggerPlugin) and obj != TriggerPlugin:
                    plugin = obj(self.logger)
                    if plugin.validate():
                        self.plugins[plugin.name] = plugin
                        self.logger.info(f"Loaded plugin: {plugin.name}")
    
    def get_plugin(self, name: str) -> Optional[TriggerPlugin]:
        """Get plugin by name."""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[Dict[str, str]]:
        """List all available plugins."""
        return [plugin.get_info() for plugin in self.plugins.values()]


class BlueScreenLogger:
    """Enhanced logger with multiple outputs."""
    
    def __init__(self, log_file: Optional[str] = None, use_event_log: bool = False):
        self.log_file = log_file or "bluescreen_v4.log"
        self.use_event_log = use_event_log
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging."""
        logger = logging.getLogger("BlueScreenV4")
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s: %(message)s')
        file_handler.setFormatter(file_format)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)


class ConfigManager:
    """Manage configuration from YAML/JSON files."""
    
    def __init__(self, config_file: str = "bluescreen_config.yaml"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            return self._create_default_config()
        
        try:
            if self.config_file.suffix == '.yaml' or self.config_file.suffix == '.yml':
                with open(self.config_file) as f:
                    return yaml.safe_load(f) or {}
            else:
                with open(self.config_file) as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
            return {}
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        default = {
            'general': {
                'dry_run': True,
                'obfuscate': False,
                'log_file': 'bluescreen_v4.log'
            },
            'database': {
                'enabled': True,
                'path': 'bluescreen_v4.db'
            },
            'api': {
                'enabled': False,
                'host': '127.0.0.1',
                'port': 8888,
                'auth_enabled': False
            },
            'schedule': {
                'enabled': False,
                'interval_seconds': 3600
            },
            'telemetry': {
                'enabled': False,
                'endpoint': ''
            },
            'trigger': {
                'method': 'ntraise',
                'error_code': 'INVALID_IMAGE_FORMAT',
                'timeout_seconds': 10
            }
        }
        
        self.save_config(default)
        return default
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            if self.config_file.suffix == '.yaml' or self.config_file.suffix == '.yml':
                with open(self.config_file, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
            else:
                with open(self.config_file, 'w') as f:
                    json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value or default


class TelemetryCollector:
    """Collect and send telemetry data."""
    
    def __init__(self, config: TelemetryConfig, database: Database, logger: BlueScreenLogger):
        self.config = config
        self.database = database
        self.logger = logger
        self.queue: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def collect_event(self, event_type: str, data: Dict[str, Any]):
        """Collect a telemetry event."""
        if not self.config.enabled:
            return
        
        with self.lock:
            event = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'data': data,
                'sent': False
            }
            self.queue.append(event)
            
            if len(self.queue) >= self.config.batch_size:
                self._flush()
    
    def _flush(self):
        """Send queued events to telemetry endpoint."""
        if not self.queue or not self.config.enabled:
            return
        
        try:
            payload = json.dumps(self.queue)
            response = requests.post(
                self.config.endpoint,
                data=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                self.queue.clear()
                self.logger.debug("Telemetry flushed successfully")
            else:
                self.logger.warning(f"Telemetry flush failed: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Telemetry collection error: {e}")


class TriggerScheduler:
    """Schedule automatic trigger execution."""
    
    def __init__(self, config: ScheduleConfig, trigger_fn: Callable, logger: BlueScreenLogger):
        self.config = config
        self.trigger_fn = trigger_fn
        self.logger = logger
        self.running = False
        self.thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start scheduler."""
        if not self.config.enabled or self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.logger.info("Scheduler started")
    
    def stop(self):
        """Stop scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info("Scheduler stopped")
    
    def _run(self):
        """Scheduler main loop."""
        while self.running:
            try:
                if self._should_execute():
                    self.logger.info("Executing scheduled trigger")
                    self.trigger_fn()
                    self.config.execution_count += 1
                
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
    
    def _should_execute(self) -> bool:
        """Check if trigger should execute."""
        if not self.config.enabled:
            return False
        
        if self.config.max_executions > 0 and self.config.execution_count >= self.config.max_executions:
            self.config.enabled = False
            return False
        
        return True


class BlueScreenAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for REST API."""
    
    trigger_v4: Optional['BlueScreenTriggerV4'] = None
    
    def do_GET(self):
        """Handle GET requests."""
        path = urllib.parse.urlparse(self.path).path
        
        if path == '/api/health':
            self._send_response({'status': 'ok'})
        elif path == '/api/history':
            history = self.trigger_v4.database.get_trigger_history()
            self._send_response({'history': history})
        elif path == '/api/stats':
            stats = self.trigger_v4.database.get_statistics()
            self._send_response(stats)
        elif path == '/api/plugins':
            plugins = self.trigger_v4.plugin_manager.list_plugins()
            self._send_response({'plugins': plugins})
        else:
            self._send_error(404, "Not found")
    
    def do_POST(self):
        """Handle POST requests."""
        if not self._verify_auth():
            self._send_error(401, "Unauthorized")
            return
        
        path = urllib.parse.urlparse(self.path).path
        
        if path == '/api/trigger':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body)
                
                self.trigger_v4.execute()
                self._send_response({'status': 'triggered'})
            except Exception as e:
                self._send_error(400, str(e))
        else:
            self._send_error(404, "Not found")
    
    def _verify_auth(self) -> bool:
        """Verify API authentication."""
        if not self.trigger_v4.api_config.auth_enabled:
            return True
        
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            return token == self.trigger_v4.api_config.auth_token
        
        return False
    
    def _send_response(self, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, code: int, message: str):
        """Send error response."""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class BlueScreenTriggerV4:
    """Main BSOD trigger controller with all v4 features."""
    
    def __init__(self, config_file: str = "bluescreen_config.yaml"):
        self.config_manager = ConfigManager(config_file)
        self.logger = BlueScreenLogger(
            self.config_manager.get('general.log_file'),
            self.config_manager.get('general.use_event_log', False)
        )
        
        # Initialize components
        self.database = Database(self.config_manager.get('database.path', 'bluescreen_v4.db'))
        self.api_config = APIConfig(**self.config_manager.get('api', {}))
        self.schedule_config = ScheduleConfig(**self.config_manager.get('schedule', {}))
        self.telemetry_config = TelemetryConfig(**self.config_manager.get('telemetry', {}))
        
        self.plugin_manager = PluginManager(logger=self.logger)
        self.telemetry = TelemetryCollector(self.telemetry_config, self.database, self.logger)
        self.scheduler = TriggerScheduler(self.schedule_config, self.execute, self.logger)
        
        self.error_code = ErrorCode.INVALID_IMAGE_FORMAT
        self.method = TriggerMethod.NTRAISE_HARDERROR
        self.dry_run = self.config_manager.get('general.dry_run', True)
        
        self.api_server: Optional[HTTPServer] = None
        self.api_thread: Optional[threading.Thread] = None
    
    def is_windows(self) -> bool:
        """Verify Windows platform."""
        return sys.platform.startswith('win')
    
    def execute(self) -> bool:
        """Execute trigger with all features."""
        start_time = time.time()
        record = TriggerRecord()
        
        try:
            self.logger.info("BlueScreen Trigger v4.0")
            
            if not self.is_windows():
                raise Exception(f"Windows required, got {sys.platform}")
            
            # Record system state
            record.memory_before_mb = psutil.virtual_memory().used / (1024 * 1024)
            record.cpu_percent = psutil.cpu_percent(interval=0.5)
            record.process_count = len(psutil.pids())
            record.hostname = __import__('socket').gethostname()
            record.user = __import__('getpass').getuser()
            record.dry_run = self.dry_run
            
            if self.dry_run:
                self.logger.warning("[DRY RUN] Skipping actual trigger")
                record.status = TriggerStatus.SUCCESS.value
            else:
                # Execute trigger
                if self.method == TriggerMethod.NTRAISE_HARDERROR:
                    nullptr = POINTER(c_int)()
                    windll.ntdll.NtRaiseHardError(
                        c_ulong(self.error_code.value),
                        c_ulong(0),
                        nullptr,
                        nullptr,
                        c_uint(6),
                        byref(c_uint())
                    )
                record.status = TriggerStatus.SUCCESS.value
            
            # Record metrics
            record.duration_ms = (time.time() - start_time) * 1000
            record.memory_after_mb = psutil.virtual_memory().used / (1024 * 1024)
            record.method = self.method.value
            record.error_code = self.error_code.value
            
            # Store in database
            record_id = self.database.insert_trigger(record)
            self.logger.info(f"Trigger recorded with ID: {record_id}")
            
            # Collect telemetry
            self.telemetry.collect_event('trigger_executed', record.to_dict())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Trigger failed: {e}")
            record.status = TriggerStatus.FAILED.value
            record.error_message = str(e)
            record.duration_ms = (time.time() - start_time) * 1000
            self.database.insert_trigger(record)
            return False
    
    def start_api_server(self):
        """Start REST API server."""
        if not self.api_config.enabled:
            return
        
        BlueScreenAPIHandler.trigger_v4 = self
        
        self.api_server = HTTPServer(
            (self.api_config.host, self.api_config.port),
            BlueScreenAPIHandler
        )
        
        self.api_thread = threading.Thread(
            target=self.api_server.serve_forever,
            daemon=True
        )
        self.api_thread.start()
        
        self.logger.info(f"API server started on {self.api_config.host}:{self.api_config.port}")
    
    def stop_api_server(self):
        """Stop REST API server."""
        if self.api_server:
            self.api_server.shutdown()
            if self.api_thread:
                self.api_thread.join(timeout=5)
            self.logger.info("API server stopped")
    
    def start_scheduler(self):
        """Start trigger scheduler."""
        self.scheduler.start()
    
    def stop_scheduler(self):
        """Stop trigger scheduler."""
        self.scheduler.stop()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            'version': 'v4.0',
            'timestamp': datetime.now().isoformat(),
            'database_stats': self.database.get_statistics(),
            'scheduler_enabled': self.schedule_config.enabled,
            'api_enabled': self.api_config.enabled,
            'plugins_loaded': len(self.plugin_manager.plugins)
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="BlueScreen Trigger v4.0 - Enterprise BSOD Generator"
    )
    
    parser.add_argument("--config", default="bluescreen_config.yaml", help="Config file")
    parser.add_argument("--trigger", action="store_true", help="Execute trigger")
    parser.add_argument("--api", action="store_true", help="Start API server")
    parser.add_argument("--scheduler", action="store_true", help="Start scheduler")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--history", type=int, default=0, help="Show trigger history")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    args = parser.parse_args()
    
    trigger = BlueScreenTriggerV4(args.config)
    
    if args.dry_run:
        trigger.dry_run = True
    
    if args.status:
        print(json.dumps(trigger.get_status(), indent=2))
    elif args.history > 0:
        history = trigger.database.get_trigger_history(args.history)
        print(json.dumps(history, indent=2))
    elif args.trigger:
        trigger.execute()
    elif args.api:
        trigger.start_api_server()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            trigger.stop_api_server()
    elif args.scheduler:
        trigger.start_scheduler()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            trigger.stop_scheduler()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
