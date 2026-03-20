def __getattr__(name):
    if name == "Trainer":
        from src.training.trainer import Trainer
        return Trainer
    if name == "get_lora_config":
        from src.training.lora_config import get_lora_config
        return get_lora_config
    if name in ("EarlyStopping", "CheckpointCallback"):
        from src.training.callbacks import EarlyStopping, CheckpointCallback
        if name == "EarlyStopping":
            return EarlyStopping
        return CheckpointCallback
    raise AttributeError(f"module 'src.training' has no attribute {name!r}")
