from enum import Enum


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    
    def is_final(self) -> bool:
        """Check if status is final (no further processing)"""
        return self in [self.COMPLETED, self.FAILED, self.CANCELLED]
    
    def is_processing(self) -> bool:
        """Check if currently processing"""
        return self in [self.PENDING, self.PROCESSING]
    