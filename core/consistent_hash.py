import hashlib
import bisect

class ConsistentHashRing:
    """
    Consistent Hashing implementation with virtual nodes (vnodes).
    Uses SHA-256 for high entropy and even distribution.
    Implemented as a singleton to maintain ring state across the application.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConsistentHashRing, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, vnodes=150):
        if self._initialized:
            return
        
        self.vnodes = vnodes
        self.ring = {}  # hash -> node_name
        self.sorted_keys = []  # sorted hashes for binary search
        self.nodes = set()
        self._initialized = True

    def _hash(self, key):
        """Returns a 32-bit integer hash for a given key string."""
        return int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node_name):
        """
        Adds a physical node to the ring by creating multiple virtual nodes.
        Vnodes help achieve a more balanced distribution of keys.
        """
        if node_name in self.nodes:
            return
        
        self.nodes.add(node_name)
        for i in range(self.vnodes):
            vnode_key = f"{node_name}:{i}"
            vnode_hash = self._hash(vnode_key)
            self.ring[vnode_hash] = node_name
            bisect.insort(self.sorted_keys, vnode_hash)

    def remove_node(self, node_name):
        """
        Removes a physical node and all its associated virtual nodes from the ring.
        """
        if node_name not in self.nodes:
            return
        
        self.nodes.remove(node_name)
        new_ring = {}
        new_sorted_keys = []
        
        for h, name in self.ring.items():
            if name != node_name:
                new_ring[h] = name
                new_sorted_keys.append(h)
        
        self.ring = new_ring
        self.sorted_keys = sorted(new_sorted_keys)

    def get_node(self, key):
        """
        Maps a given key (e.g., shortCode) to a node using consistent hashing.
        Returns the node_name of the responsible shard.
        """
        if not self.ring:
            raise ValueError("Consistent Hash Ring is empty. No nodes available.")
        
        key_hash = self._hash(key)
        # Find the first vnode hash >= key_hash
        idx = bisect.bisect_right(self.sorted_keys, key_hash)
        
        # If idx is outside range, wrap around to the first node (clockwise)
        if idx == len(self.sorted_keys):
            idx = 0
            
        return self.ring[self.sorted_keys[idx]]

    def get_ring_state(self):
        """Returns the current mapping of vnode hashes to physical nodes."""
        return {h: self.ring[h] for h in self.sorted_keys}

# Global singleton instance
hash_ring = ConsistentHashRing()
