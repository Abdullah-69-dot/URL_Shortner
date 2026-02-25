from django.test import TestCase
from core.consistent_hash import ConsistentHashRing
import collections

class ConsistentHashRingTest(TestCase):
    def setUp(self):
        # Create a fresh ring for each test to avoid singleton state interference
        self.ring = ConsistentHashRing(vnodes=100)
        self.ring.nodes = set()
        self.ring.ring = {}
        self.ring.sorted_keys = []
        
        self.ring.add_node('shard_1')
        self.ring.add_node('shard_2')
        self.ring.add_node('shard_3')

    def test_distribution_balance(self):
        """Tests if keys are distributed somewhat evenly across shards."""
        counts = collections.Counter()
        for i in range(1000):
            node = self.ring.get_node(f"test_key_{i}")
            counts[node] += 1
        
        # With 3 shards and 1000 keys, each should have roughly 333 +/- 100
        # This is a loose check to ensure no shard is empty or overloaded.
        for node in ['shard_1', 'shard_2', 'shard_3']:
            self.assertGreater(counts[node], 200)
            self.assertLess(counts[node], 450)

    def test_node_addition_remapping(self):
        """Tests that adding a node only remaps ~1/N keys."""
        initial_mapping = {}
        for i in range(1000):
            initial_mapping[i] = self.ring.get_node(str(i))
            
        self.ring.add_node('shard_4')
        
        remapped_count = 0
        for i in range(1000):
            new_node = self.ring.get_node(str(i))
            if new_node != initial_mapping[i]:
                remapped_count += 1
                # The remapped keys MUST go to the new node
                self.assertEqual(new_node, 'shard_4')
        
        # For 4 nodes, we expect ~25% (250) remapping. 
        # Range 150-350 is safe for 1000 keys.
        self.assertGreater(remapped_count, 150)
        self.assertLess(remapped_count, 350)

    def test_node_removal(self):
        """Tests that removing a node distributes its keys to remaining nodes."""
        # Ensure we have keys on shard_3
        keys_on_shard3 = [i for i in range(100) if self.ring.get_node(str(i)) == 'shard_3']
        self.assertGreater(len(keys_on_shard3), 0)
        
        self.ring.remove_node('shard_3')
        
        for i in keys_on_shard3:
            new_node = self.ring.get_node(str(i))
            self.assertIn(new_node, ['shard_1', 'shard_2'])

    def test_empty_ring(self):
        """Tests that get_node raises error on empty ring."""
        empty_ring = ConsistentHashRing(vnodes=10)
        empty_ring.nodes = set()
        empty_ring.ring = {}
        empty_ring.sorted_keys = []
        
        with self.assertRaises(ValueError):
            empty_ring.get_node("any_key")

    def test_singleton_behavior(self):
        """Tests that ConsistentHashRing behaves as a singleton."""
        from core.consistent_hash import hash_ring
        ring2 = ConsistentHashRing()
        self.assertIs(hash_ring, ring2)
