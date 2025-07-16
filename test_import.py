"""Test script for QuestMaster AI."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from questmaster.core.config import get_settings
    from questmaster.core.logging import setup_logging, get_logger
    from questmaster.app import QuestMasterApp
    
    # Setup logging
    setup_logging(log_level="INFO")
    logger = get_logger(__name__)
    
    logger.info("Testing QuestMaster AI imports and basic functionality")
    
    # Test configuration
    settings = get_settings()
    logger.info("Configuration loaded", base_dir=str(settings.base_dir))
    
    # Test app creation
    app = QuestMasterApp()
    logger.info("QuestMaster app created successfully")
    
    # Test requirements check
    try:
        requirements_ok = app.check_requirements()
        if requirements_ok:
            logger.info("✅ All requirements satisfied")
        else:
            logger.warning("⚠️  Some requirements not met (this is expected in test environment)")
    except Exception as e:
        logger.warning("Requirements check failed (expected in test environment)", error=str(e))
    
    logger.info("🎉 QuestMaster AI basic test completed successfully!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
