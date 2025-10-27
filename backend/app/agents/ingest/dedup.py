import hashlib
import re
from typing import List, Set, Dict
from collections import defaultdict
from .base import IngestAgent
from .types import IngestContext, ProcessedChunk


class DedupAgent(IngestAgent):
    """
    DedupAgent - Deduplikacija chunk-ova pomoću MinHash i LSH.
    Pronalazi i označava duplicate/near-duplicate chunks.
    """
    
    def __init__(self, similarity_threshold: float = 0.85, shingle_size: int = 3):
        super().__init__("DedupAgent", dependencies=["StructureAgent"])
        self.similarity_threshold = similarity_threshold
        self.shingle_size = shingle_size
    
    async def process(self, context: IngestContext):
        """Deduplicira chunk-ove"""
        
        if not context.chunks:
            return
        
        # Step 1: Create MinHash signatures for all chunks
        signatures = []
        for chunk in context.chunks:
            signature = self._create_minhash(chunk.text)
            signatures.append(signature)
        
        # Step 2: Find duplicates using LSH
        duplicates_map = self._lsh_find_duplicates(signatures, context.chunks)
        
        # Step 3: Mark duplicates in chunks
        dedup_count = 0
        for idx, chunk in enumerate(context.chunks):
            if idx in duplicates_map:
                chunk.is_duplicate = True
                chunk.deduplicated_with = duplicates_map[idx]
                dedup_count += 1
        
        # Metrics
        context.set_metric("duplicate_chunks", dedup_count)
        context.set_metric("unique_chunks", len(context.chunks) - dedup_count)
    
    def _create_minhash(self, text: str, num_hashes: int = 128) -> List[float]:
        """
        Kreira MinHash signature za tekst.
        MinHash je probabilistički algoritam za procjenu Jaccard similarity.
        """
        # Normalize text
        normalized = self._normalize_text(text)
        
        # Create shingles (n-grams)
        shingles = self._create_shingles(normalized)
        
        if not shingles:
            return [0] * num_hashes
        
        # Initialize signature with infinity
        signature = [float('inf')] * num_hashes
        
        # For each shingle, compute hash with different seeds
        for shingle in shingles:
            for i in range(num_hashes):
                # Hash with seed i
                hash_val = self._hash_with_seed(shingle, i)
                
                # Keep minimum
                if hash_val < signature[i]:
                    signature[i] = hash_val
        
        return signature
    
    def _normalize_text(self, text: str) -> str:
        """Normalizuj tekst za comparison"""
        # Lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation (keep alphanumeric and spaces)
        text = re.sub(r'[^\w\s]', '', text)
        
        return text.strip()
    
    def _create_shingles(self, text: str) -> Set[str]:
        """Kreira word shingles (n-grams) iz teksta"""
        words = text.split()
        
        if len(words) < self.shingle_size:
            return {text}
        
        shingles = set()
        for i in range(len(words) - self.shingle_size + 1):
            shingle = ' '.join(words[i:i + self.shingle_size])
            shingles.add(shingle)
        
        return shingles
    
    def _hash_with_seed(self, text: str, seed: int) -> int:
        """Hash string sa seed-om"""
        hash_input = f"{seed}:{text}".encode('utf-8')
        hash_bytes = hashlib.sha256(hash_input).digest()
        
        # Convert first 8 bytes to int
        return int.from_bytes(hash_bytes[:8], byteorder='big')
    
    def _lsh_find_duplicates(
        self,
        signatures: List[List[int]],
        chunks: List[ProcessedChunk]
    ) -> Dict[int, str]:
        """
        LSH (Locality Sensitive Hashing) za pronalaženje duplicates.
        Vraća dict {duplicate_idx: original_hash}
        """
        # LSH parameters
        num_bands = 16
        rows_per_band = len(signatures[0]) // num_bands if signatures else 0
        
        if rows_per_band == 0:
            return {}
        
        # Hash tables for each band
        band_buckets: List[Dict[int, List[int]]] = [defaultdict(list) for _ in range(num_bands)]
        
        # Populate LSH buckets
        for idx, signature in enumerate(signatures):
            for band_idx in range(num_bands):
                # Extract band
                start = band_idx * rows_per_band
                end = start + rows_per_band
                band = tuple(signature[start:end])
                
                # Hash band
                band_hash = hash(band)
                
                # Add to bucket
                band_buckets[band_idx][band_hash].append(idx)
        
        # Find candidate pairs (chunks in same bucket)
        candidate_pairs = set()
        
        for band_bucket in band_buckets:
            for bucket_chunks in band_bucket.values():
                if len(bucket_chunks) > 1:
                    # All pairs in this bucket are candidates
                    for i in range(len(bucket_chunks)):
                        for j in range(i + 1, len(bucket_chunks)):
                            pair = tuple(sorted([bucket_chunks[i], bucket_chunks[j]]))
                            candidate_pairs.add(pair)
        
        # Verify candidates with exact similarity
        duplicates_map = {}
        chunk_hashes = {}  # Map idx to content hash
        
        for idx1, idx2 in candidate_pairs:
            similarity = self._jaccard_similarity(signatures[idx1], signatures[idx2])
            
            if similarity >= self.similarity_threshold:
                # idx2 is duplicate of idx1
                # Keep the first occurrence (idx1), mark idx2 as duplicate
                
                if idx1 not in chunk_hashes:
                    chunk_hashes[idx1] = self._hash_text(chunks[idx1].text)
                
                duplicates_map[idx2] = chunk_hashes[idx1]
        
        return duplicates_map
    
    def _jaccard_similarity(self, sig1: List[int], sig2: List[int]) -> float:
        """Procijeni Jaccard similarity iz MinHash signatures"""
        if len(sig1) != len(sig2):
            return 0.0
        
        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / len(sig1)
    
    def _hash_text(self, text: str) -> str:
        """Kreira hash ID za tekst"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:16]
