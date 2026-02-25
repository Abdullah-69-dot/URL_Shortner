from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Initialize the Consistent Hashing Ring with the defined shards.
        Using AppConfig.ready ensures the ring is set up once at startup.
        """
        from .consistent_hash import hash_ring
        
        # Adding our initial 3 shards to the ring
        hash_ring.add_node('shard_1')
        hash_ring.add_node('shard_2')
        hash_ring.add_node('shard_3')
        
        print(f"Consistent Hash Ring initialized with nodes: {hash_ring.nodes}")
