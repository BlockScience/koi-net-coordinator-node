import pytest
import os
import sys
from unittest.mock import Mock

_mpatch = None

def pytest_configure(config):
    """
    Called by pytest before test collection. This is the earliest point to
    apply patches before any modules are imported. We patch the config loader
    to prevent it from auto-generating keys on import, which is the true
    source of the crash.
    """
    global _mpatch
    _mpatch = pytest.MonkeyPatch()
    from koi_net_coordinator_node.config import CoordinatorConfig
    # Prevent the real load_from_yaml from running on import.
    # Return a default, inert config object just to allow the module to load.
    _mpatch.setattr(
        "koi_net.config.NodeConfig.load_from_yaml",
        lambda *args, **kwargs: CoordinatorConfig()
    )

def pytest_unconfigure(config):
    """
    Called by pytest after the entire test session finishes.
    """
    global _mpatch
    if _mpatch:
        _mpatch.undo()

from koi_net_coordinator_node.config import CoordinatorConfig
from koi_net.protocol.secure import PrivateKey
from rid_lib.types import KoiNetNode
from rid_lib.ext.utils import sha256_hash
from koi_net.processor.handler import HandlerType
from rid_lib.types import KoiNetNode as RID_KoiNetNode


@pytest.fixture
def coordinator_node(monkeypatch, tmp_path):
    """
    Pytest fixture that creates an isolated coordinator node instance for tests.
    This fixture will now run correctly because the import-time crash has been
    prevented by the pytest_configure hook.
    """
    # 1. Undo the global patch so we can use the REAL NodeConfig loader
    #    and NodeInterface for our test.
    _mpatch.undo()

    # 2. Ensure PRIV_KEY_PASSWORD is set for the test environment.
    priv_password = os.getenv("PRIV_KEY_PASSWORD")
    if priv_password is None:
        priv_password = "dev_password_123"
        monkeypatch.setenv("PRIV_KEY_PASSWORD", priv_password)
    print(f"PRIV_KEY_PASSWORD: {priv_password}")

    # 3. Create a temporary private key file for this test node.
    priv_path = tmp_path / "test_priv_key.pem"
    priv_key = PrivateKey.generate()
    pub_key = priv_key.public_key()

    with open(priv_path, "w") as f:
        f.write(priv_key.to_pem(priv_password))

    # 4. Create a fresh CoordinatorConfig and point it at our temporary key.
    config = CoordinatorConfig()
    config.koi_net.private_key_pem_path = str(priv_path)
    config.koi_net.node_profile.public_key = pub_key.to_der()
    config.koi_net.node_rid = KoiNetNode(
        config.koi_net.node_name,
        sha256_hash(pub_key.to_der())
    )

    # 5. Clear modules to ensure a fresh import using the real classes.
    if 'koi_net_coordinator_node.core' in sys.modules:
        del sys.modules['koi_net_coordinator_node.core']
    if 'koi_net_coordinator_node.handlers' in sys.modules:
        del sys.modules['koi_net_coordinator_node.handlers']

    # 6. Instantiate the *real* NodeInterface.
    from koi_net import NodeInterface
    node = NodeInterface(
        config=config,
        use_kobj_processor_thread=True
    )

    # 7. Import and manually register handlers onto the real node's pipeline.
    import koi_net_coordinator_node.handlers as handlers_mod
    try:
        node.processor.pipeline.add_handler(handlers_mod.handshake_handler)
    except Exception as e:
        print(f"Warning: Could not register handshake_handler on test node: {e}")
        pass

    yield node

    # 8. Re-apply the global patch after the test is done.
    _mpatch.setattr(
        "koi_net.config.NodeConfig.load_from_yaml",
        lambda *args, **kwargs: CoordinatorConfig()
    )


@pytest.fixture
def mock_coordinator_node():
    """
    Pytest fixture that provides a mocked coordinator node for tests that
    don't need the full node functionality.
    """
    from koi_net_coordinator_node.config import CoordinatorConfig
    
    mock_node = Mock()
    mock_node.config = CoordinatorConfig()
    mock_node.identity = Mock()
    mock_node.identity.rid = KoiNetNode("coordinator", "test_hash")
    
    return mock_node
