from core.consistent_hash import hash_ring

class ShardRouter:
    """
    A router to control all database operations on models in the
    url_shortener application. Routes URL-related queries to shards
    based on the consistent hashing of the short_code.
    """
    
    def _is_url_model(self, model):
        return model._meta.app_label == 'urls_app' and model._meta.model_name == 'url'

    def db_for_read(self, model, **hints):
        """
        Attempts to read URL models from the correct shard based on the short_code hint.
        """
        if self._is_url_model(model):
            short_code = hints.get('short_code')
            if short_code:
                try:
                    return hash_ring.get_node(short_code)
                except ValueError:
                    return 'default'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write URL models to the correct shard based on the short_code hint.
        """
        if self._is_url_model(model):
            short_code = hints.get('short_code')
            if short_code:
                try:
                    return hash_ring.get_node(short_code)
                except ValueError:
                    return 'default'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the same database or
        if neither is a URL model.
        """
        if self._is_url_model(obj1) or self._is_url_model(obj2):
            return obj1._state.db == obj2._state.db
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure the URL model is only migrated to the shards, and
        other models (admin, auth, etc.) go to the default DB.
        """
        if app_label == 'urls_app':
            # Run migrations for urls_app on all shards, but NOT on default
            # (In production, we might want to skip default entirely for sharded tables)
            return db in ['shard_1', 'shard_2', 'shard_3']
        
        # All other apps (admin, auth, sessions) go to default DB
        if db == 'default':
            return True
        
        return False
