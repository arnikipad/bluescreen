"""
Bluescreen Trigger v2 - Windows BSOD Generator
Enhanced version with async support, detailed logging, and recovery options.
"""

import asyncio
import sys
import logging
from ctypes import windll, c_int, c_uint, c_ulong, POINTER, byref
from enum import Enum
from typing import Optional, Tuple
from datetime import datetime


class PrivilegeLevel(Enum):
    """Enumeration for privilege levels."""
    PROCESS = 0
    THREAD = 1


class ErrorCode(Enum):
    """Common Windows NTSTATUS error codes."""
    INVALID_IMAGE_FORMAT = 0xC000007B
    FATAL_USER_CALLBACK_EXCEPTION = 0xC000013B
    PRIVILEGED_INSTRUCTION = 0xC0000096


class ResponseOption(Enum):
    """Response options for error dialog."""
    ABORT_RETRY_IGNORE = 6
    OK = 0
    OK_CANCEL = 1


class BlueScreenLogger:
    """Custom logger for BSOD trigger operations."""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or "bluescreen.log"
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging with file and console handlers."""
        logger = logging.getLogger("BlueScreenTrigger")
        logger.setLevel(logging.DEBUG)
        
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


class BlueScreenTrigger:
    """Main class to handle BSOD triggering with safety checks."""
    
    def __init__(self, log_file: Optional[str] = None, dry_run: bool = False):
        self.logger = BlueScreenLogger(log_file)
        self.dry_run = dry_run
        self.privilege_adjusted = False
        self.error_code = ErrorCode.INVALID_IMAGE_FORMAT
    
    def is_windows(self) -> bool:
        """Verify the current platform is Windows."""
        return sys.platform.startswith('win')
    
    def check_environment(self) -> bool:
        """Perform environment checks before proceeding."""
        self.logger.info("Performing environment checks...")
        
        if not self.is_windows():
            self.logger.error(f"Unsupported platform: {sys.platform}. Windows required.")
            return False
        
        self.logger.debug("Platform check passed: Windows detected")
        return True
    
    def adjust_privilege(self, privilege: PrivilegeLevel = PrivilegeLevel.PROCESS) -> bool:
        """
        Adjust system privilege for shutdown operations.
        
        Args:
            privilege: Process or Thread level privilege adjustment
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info("Attempting to adjust SeShutdownPrivilege...")
            
            if self.dry_run:
                self.logger.warning("[DRY RUN] Skipping actual privilege adjustment")
                self.privilege_adjusted = True
                return True
            
            windll.ntdll.RtlAdjustPrivilege(
                c_uint(19),                    # SeShutdownPrivilege
                c_uint(1),                     # Enable
                c_uint(privilege.value),       # Process or Thread
                byref(c_int())                 # Previous state
            )
            
            self.privilege_adjusted = True
            self.logger.info("Successfully adjusted SeShutdownPrivilege")
            return True
            
        except Exception as e:
            self.logger.error(f"Privilege adjustment failed: {e}")
            return False
    
    def trigger_hard_error(self, error_code: Optional[ErrorCode] = None) -> bool:
        """
        Trigger a hard error causing Windows BSOD.
        
        Args:
            error_code: Specific NTSTATUS error code to raise
            
        Returns:
            bool: True if function called successfully (execution won't reach here)
        """
        try:
            code = error_code or self.error_code
            self.logger.warning(f"Triggering hard error with code: 0x{code.value:X}")
            
            if self.dry_run:
                self.logger.warning("[DRY RUN] Skipping actual hard error trigger")
                return True
            
            nullptr = POINTER(c_int)()
            
            windll.ntdll.NtRaiseHardError(
                c_ulong(code.value),           # Error code
                c_ulong(0),                    # Number of parameters
                nullptr,                       # Parameter array
                nullptr,                       # String parameter
                c_uint(ResponseOption.ABORT_RETRY_IGNORE.value),
                byref(c_uint())                # Selected option
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Hard error trigger failed: {e}")
            return False
    
    def get_system_info(self) -> Tuple[str, str, str]:
        """Gather system information for logging."""
        import platform
        return (
            platform.system(),
            platform.release(),
            platform.version()
        )
    
    async def execute_async(self, delay: float = 0) -> None:
        """
        Execute BSOD trigger asynchronously with optional delay.
        
        Args:
            delay: Seconds to wait before triggering
        """
        if delay > 0:
            self.logger.info(f"Waiting {delay} seconds before trigger...")
            await asyncio.sleep(delay)
        
        self.execute()
    
    def execute(self) -> None:
        """Execute the BSOD trigger sequence."""
        mode = "[DRY RUN MODE]" if self.dry_run else ""
        self.logger.info(f"BlueScreen Trigger v2.0 {mode}")
        
        # Get system info
        system, release, version = self.get_system_info()
        self.logger.debug(f"System: {system} {release} ({version})")
        self.logger.debug(f"Timestamp: {datetime.now().isoformat()}")
        
        # Environment check
        if not self.check_environment():
            self.logger.error("Environment check failed. Aborting.")
            sys.exit(1)
        
        # Critical warning
        if not self.dry_run:
            self.logger.warning("=" * 60)
            self.logger.warning("CRITICAL: System will crash without saving data!")
            self.logger.warning("=" * 60)
        
        # Adjust privilege
        if not self.adjust_privilege():
            self.logger.error("Failed to adjust privileges. Aborting.")
            sys.exit(1)
        
        # Trigger hard error
        if not self.trigger_hard_error():
            self.logger.error("Failed to trigger hard error.")
            sys.exit(1)
        
        # Should not reach here
        self.logger.error("Execution continued unexpectedly")
        sys.exit(1)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Windows BSOD Trigger Utility")
    parser.add_argument("--dry-run", action="store_true", help="Run without actual system effects")
    parser.add_argument("--log-file", help="Custom log file path")
    parser.add_argument("--delay", type=float, default=0, help="Delay in seconds before trigger")
    parser.add_argument("--error-code", type=str, default="INVALID_IMAGE_FORMAT",
                       choices=["INVALID_IMAGE_FORMAT", "FATAL_USER_CALLBACK_EXCEPTION", "PRIVILEGED_INSTRUCTION"],
                       help="NTSTATUS error code to raise")
    
    args = parser.parse_args()
    
    trigger = BlueScreenTrigger(log_file=args.log_file, dry_run=args.dry_run)
    trigger.error_code = ErrorCode[args.error_code]
    
    if args.delay > 0:
        asyncio.run(trigger.execute_async(args.delay))
    else:
        trigger.execute()


if __name__ == "__main__":
    main()
