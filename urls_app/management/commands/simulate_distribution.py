import random
import string
from django.core.management.base import BaseCommand
from core.consistent_hash import hash_ring
from collections import Counter

class Command(BaseCommand):
    help = 'Simulates distribution of 1000 random short codes across shards'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting distribution simulation for 1000 keys..."))
        
        characters = string.ascii_letters + string.digits
        distribution = Counter()
        total_keys = 1000
        
        for _ in range(total_keys):
            # Generate a random 6-char short code
            short_code = ''.join(random.choices(characters, k=6))
            # Determine which shard it maps to
            shard = hash_ring.get_node(short_code)
            distribution[shard] += 1
            
        self.stdout.write("\n" + "="*40)
        self.stdout.write(f"{'Shard Name':<20} | {'Count':<7} | {'Percentage':<10}")
        self.stdout.write("-" * 40)
        
        # Sort shards by name for consistent output
        for shard in sorted(hash_ring.nodes):
            count = distribution[shard]
            percentage = (count / total_keys) * 100
            self.stdout.write(f"{shard:<20} | {count:<7} | {percentage:>9.2f}%")
            
        self.stdout.write("="*40 + "\n")
        self.stdout.write(self.style.SUCCESS("Simulation complete."))
