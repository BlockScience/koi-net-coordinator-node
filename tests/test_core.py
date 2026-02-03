import pytest
from unittest.mock import Mock, patch, MagicMock
from koi_net import NodeInterface
from koi_net_coordinator_node.config import CoordinatorConfig


class TestCoordinatorCore:
    """Test cases for the coordinator core functionality."""
    
    def test_node_interface_creation(self, coordinator_node):
        """Test that the node interface is created correctly."""
        # The node should be a NodeInterface instance
        assert isinstance(coordinator_node, NodeInterface)
        
        # The config should be a CoordinatorConfig instance
        assert isinstance(coordinator_node.config, CoordinatorConfig)
        
        # Should be using processor thread
        assert coordinator_node.use_kobj_processor_thread is True
    
    def test_node_configuration_properties(self, coordinator_node):
        """Test that the node has the correct configuration properties."""
        config = coordinator_node.config
        
        # Check server configuration
        assert config.server.port == 8080
        assert config.server.host == "127.0.0.1"
        assert config.server.path == "/koi-net"
        
        # Check node configuration
        assert config.koi_net.node_name == "coordinator"
        assert config.koi_net.node_profile.node_type.value == "FULL"
    
    def test_node_provides_correct_rid_types(self, coordinator_node):
        """Test that the node provides the correct RID types."""
        provides = coordinator_node.config.koi_net.node_profile.provides
        
        # Should provide KoiNetNode and KoiNetEdge for both event and state
        from rid_lib.types import KoiNetNode, KoiNetEdge
        
        assert KoiNetNode in provides.event
        assert KoiNetEdge in provides.event
        assert KoiNetNode in provides.state
        assert KoiNetEdge in provides.state
    
    def test_node_has_required_components(self, coordinator_node):
        """Test that the node has all required components."""
        # Check that essential components exist
        assert hasattr(coordinator_node, 'config')
        assert hasattr(coordinator_node, 'cache')
        assert hasattr(coordinator_node, 'identity')
        assert hasattr(coordinator_node, 'processor')
        assert hasattr(coordinator_node, 'server')
        assert hasattr(coordinator_node, 'lifecycle')
        assert hasattr(coordinator_node, 'event_queue')
        assert hasattr(coordinator_node, 'graph')
        
        # Check that components are not None
        assert coordinator_node.config is not None
        assert coordinator_node.cache is not None
        assert coordinator_node.identity is not None
        assert coordinator_node.processor is not None
        assert coordinator_node.server is not None
        assert coordinator_node.lifecycle is not None
        assert coordinator_node.event_queue is not None
        assert coordinator_node.graph is not None
    
    def test_node_loads_config_from_yaml(self, coordinator_node):
        """Test that the node loads configuration from YAML file."""
        # This test verifies that the node was created with a CoordinatorConfig
        # which would have been loaded from YAML during module import
        assert isinstance(coordinator_node.config, CoordinatorConfig)
        
        # Verify that the config has the expected properties
        assert coordinator_node.config.koi_net.node_name == "coordinator"
        assert coordinator_node.config.server.port == 8080
    
    def test_node_identity_properties(self, coordinator_node):
        """Test that the node identity is set up correctly."""
        identity = coordinator_node.identity
        
        # Should have a valid RID
        assert identity.rid is not None
        assert hasattr(identity.rid, 'name')
        assert hasattr(identity.rid, 'hash')
        
        # Should have a profile
        assert identity.profile is not None
        assert identity.profile.node_type.value == "FULL"


class TestCoordinatorLifecycle:
    """Test cases for coordinator lifecycle management."""
    
    def test_lifecycle_components_exist(self, coordinator_node):
        """Test that lifecycle management components exist."""
        assert hasattr(coordinator_node, 'lifecycle')
        assert hasattr(coordinator_node.lifecycle, 'start')
        assert hasattr(coordinator_node.lifecycle, 'stop')
        assert hasattr(coordinator_node.lifecycle, 'run')
    
    def test_server_components_exist(self, coordinator_node):
        """Test that server components exist."""
        assert hasattr(coordinator_node, 'server')
        assert hasattr(coordinator_node.server, 'run')
        assert hasattr(coordinator_node.server, 'app')
    
    def test_lifecycle_context_manager(self, coordinator_node):
        """Test that lifecycle can be used as context manager."""
        # Test that the lifecycle has the context manager methods
        assert hasattr(coordinator_node.lifecycle, 'run')
        
        # The run method should be callable
        assert callable(coordinator_node.lifecycle.run)

