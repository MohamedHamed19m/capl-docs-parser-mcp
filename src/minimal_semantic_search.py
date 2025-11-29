"""
Minimal semantic search using only scikit-learn (TF-IDF).
Integrates with VectorDocParser for parsing CAPL documentation.
No TensorFlow, no PyTorch, no sentence-transformers needed.
Works on any Python version including 3.13.
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Import your existing parser
from .vector_doc_parser import VectorDocParser, parse_directory, FunctionInfo


class MinimalCAPLSearch:
    """Lightweight semantic search using TF-IDF vectors."""
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize the search engine.
        
        Args:
            cache_dir: Directory to cache the vectorizer and vectors
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.vectorizer_file = self.cache_dir / "tfidf_vectorizer.pkl"
        self.vectors_file = self.cache_dir / "tfidf_vectors.pkl"
        self.docs_file = self.cache_dir / "doc_chunks.json"
        
        # TF-IDF vectorizer with better parameters for code documentation
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),  # Unigrams and bigrams
            stop_words='english',
            min_df=1,
            max_df=0.8,
            sublinear_tf=True  # Better for short documents
        )
        
        self.doc_chunks: List[Dict[str, Any]] = []
        self.vectors = None
        
    def create_chunks(self, parsed_docs: List[Any]) -> List[Dict[str, Any]]:
        """
        Create searchable chunks from parsed CAPL documentation.
        
        Args:
            parsed_docs: List of FunctionInfo objects from VectorDocParser
            
        Returns:
            List of document chunks with metadata
        """
        chunks = []
        
        for doc in parsed_docs:
            function_name = doc.function_name
            
            # Main chunk: function with syntax and description
            main_text = f"{function_name}\n"
            
            # Add all syntax forms
            if doc.syntax_forms:
                main_text += "Syntax: " + " | ".join(doc.syntax_forms) + "\n"
            
            if doc.description:
                main_text += f"Description: {doc.description}\n"
            
            if doc.valid_for:
                main_text += f"Valid for: {doc.valid_for}\n"
            
            chunks.append({
                'text': main_text,
                'function_name': function_name,
                'type': 'main',
                'metadata': {
                    'syntax_forms': doc.syntax_forms,
                    'description': doc.description,
                    'valid_for': doc.valid_for
                }
            })
            
            # Parameters chunk
            if doc.parameters:
                param_text = f"{function_name} parameters:\n"
                for param in doc.parameters:
                    param_text += f"- {param.name}: {param.description}\n"
                
                chunks.append({
                    'text': param_text,
                    'function_name': function_name,
                    'type': 'parameters',
                    'metadata': {
                        'parameters': [(param.name, param.description) for param in doc.parameters]
                    }
                })
            
            # Return values chunk
            if doc.return_values:
                return_text = f"{function_name} returns:\n"
                for ret_val in doc.return_values:
                    return_text += f"- {ret_val}\n"
                
                chunks.append({
                    'text': return_text,
                    'function_name': function_name,
                    'type': 'return_values',
                    'metadata': {
                        'return_values': doc.return_values
                    }
                })
            
            # Example chunk
            if doc.example:
                example_text = f"{function_name} example:\n{doc.example}"
                
                chunks.append({
                    'text': example_text,
                    'function_name': function_name,
                    'type': 'example',
                    'metadata': {
                        'example': doc.example
                    }
                })
        
        return chunks
    
    def build_index(self, parsed_docs: List[Any], force_rebuild: bool = False):
        """
        Build or load the search index using TF-IDF.
        
        Args:
            parsed_docs: List of FunctionInfo objects from VectorDocParser
            force_rebuild: Force rebuilding even if cache exists
        """
        # Check if cache exists
        if not force_rebuild and all([
            self.vectorizer_file.exists(),
            self.vectors_file.exists(),
            self.docs_file.exists()
        ]):
            print("Loading cached index...")
            with open(self.vectorizer_file, 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open(self.vectors_file, 'rb') as f:
                self.vectors = pickle.load(f)
            with open(self.docs_file, 'r', encoding='utf-8') as f:
                self.doc_chunks = json.load(f)
            print(f" Loaded {len(self.doc_chunks)} document chunks from cache")
            return
        
        # Create chunks
        print(" Creating document chunks...")
        self.doc_chunks = self.create_chunks(parsed_docs)
        
        if not self.doc_chunks:
            print(" No chunks created. Check your parsed documents.")
            return
        
        # Generate TF-IDF vectors
        print(f" Generating TF-IDF vectors for {len(self.doc_chunks)} chunks...")
        texts = [chunk['text'] for chunk in self.doc_chunks]
        self.vectors = self.vectorizer.fit_transform(texts)
        
        # Save to cache
        print(" Saving to cache...")
        with open(self.vectorizer_file, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        with open(self.vectors_file, 'wb') as f:
            pickle.dump(self.vectors, f)
        with open(self.docs_file, 'w', encoding='utf-8') as f:
            json.dump(self.doc_chunks, f, indent=2)
        
        print(" Index built successfully!")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.1,
        filter_type: str = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search for relevant documentation chunks.
        
        Args:
            query: Search query
            top_k: Number of results to return
            min_score: Minimum similarity score (0-1)
            filter_type: Filter by chunk type ('main', 'parameters', 'examples', etc.)
            
        Returns:
            List of (chunk, score) tuples sorted by relevance
        """
        if self.vectors is None or len(self.doc_chunks) == 0:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_vector, self.vectors)[0]
        
        # Get top results
        results = []
        for idx, score in enumerate(similarities):
            chunk = self.doc_chunks[idx]
            
            # Apply filters
            if filter_type and chunk['type'] != filter_type:
                continue
            if score < min_score:
                continue
            
            results.append((chunk, float(score)))
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def search_functions(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Search for relevant CAPL functions.
        Returns a list of unique function names and their highest relevance score.
        """
        # Search a larger number of chunks to ensure we find enough unique functions
        results = self.search(query, top_k=top_k * 3, min_score=0.05)

        # Use a dictionary to store the highest score for each function
        function_scores = {}
        for chunk, score in results:
            func_name = chunk['function_name']
            if func_name not in function_scores or score > function_scores[func_name]:
                function_scores[func_name] = score

        # Sort the functions by score in descending order
        sorted_functions = sorted(function_scores.items(), key=lambda item: item[1], reverse=True)

        # Return the top k results
        return sorted_functions[:top_k]
    
    def get_function_context(self, function_name: str) -> Dict[str, Any]:
        """
        Get all chunks related to a specific function.
        
        Args:
            function_name: Name of the CAPL function
            
        Returns:
            Dictionary containing all information about the function
        """
        context = {
            'function_name': function_name,
            'syntax_forms': [],
            'description': None,
            'parameters': [],
            'return_values': [],
            'example': None,
            'valid_for': None
        }
        
        for chunk in self.doc_chunks:
            if chunk['function_name'] == function_name:
                chunk_type = chunk['type']
                if chunk_type == 'main':
                    context['syntax_forms'] = chunk['metadata'].get('syntax_forms', [])
                    context['description'] = chunk['metadata'].get('description')
                    context['valid_for'] = chunk['metadata'].get('valid_for')
                elif chunk_type == 'parameters':
                    context['parameters'] = chunk['metadata'].get('parameters', [])
                elif chunk_type == 'return_values':
                    context['return_values'] = chunk['metadata'].get('return_values', [])
                elif chunk_type == 'example':
                    context['example'] = chunk['metadata'].get('example')
        
        return context


# Example usage
if __name__ == "__main__":
    import sys
    
    # Get inputs directory from command line or use default
    inputs_dir = sys.argv[1] if len(sys.argv) > 1 else "inputs"
    
    print("CAPL Documentation Semantic Search")
    print("=" * 60)
    print(f"Loading documentation from: {inputs_dir}")
    print()
    
    # Use VectorDocParser to parse markdown files
    try:
        print(" Parsing markdown files with VectorDocParser...")
        parsed_docs = parse_directory(inputs_dir)
        
        if not parsed_docs:
            print("\n No documentation found. Please check:")
            print(f"   1. The '{inputs_dir}' folder exists")
            print("   2. It contains .md files")
            print("   3. The markdown files follow the expected format")
            sys.exit(1)
        
        # Show what we found
        print(f"\nLoaded {len(parsed_docs)} CAPL functions:")
        for i, doc in enumerate(parsed_docs[:5], 1):
            print(f"   {i}. {doc.function_name}")
        if len(parsed_docs) > 5:
            print(f"   ... and {len(parsed_docs) - 5} more")
        
    except Exception as e:
        import traceback
        print(f"\n Error parsing documentation: {e}")
        print("\nDebug info:")
        traceback.print_exc()
        print("\nMake sure vector_doc_parser.py is in the same directory!")
        sys.exit(1)
    
    # Initialize search engine
    print("\nBuilding search index...")
    search_engine = MinimalCAPLSearch()
    search_engine.build_index(parsed_docs)
    
    # Interactive search loop
    print("\n" + "=" * 60)
    print(" Search Ready! Try queries like:")
    print("=" * 60)
    print("  • 'how to read CAN messages'")
    print("  • 'send data on CAN bus'")
    print("  • 'debug output functions'")
    print("  • 'timer functions'")
    print("  • 'get message identifier'")
    print("\nType 'quit', 'exit', or 'q' to stop")
    print("Type 'list' to see all available functions")
    print()
    
    while True:
        try:
            query = input(" Search: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print(" Goodbye!")
                break
            
            if query.lower() == 'list':
                all_functions = sorted(set(chunk['function_name'] for chunk in search_engine.doc_chunks))
                print(f"\n All available functions ({len(all_functions)}):")
                for i, func in enumerate(all_functions, 1):
                    print(f"   {i}. {func}")
                print()
                continue
            
            if not query:
                continue
            
            # Perform search
            results = search_engine.search(query, top_k=5, min_score=0.1)
            
            if not results:
                print(" No results found. Try a different query.\n")
                continue
            
            print(f"\n Found {len(results)} results:\n")
            
            for i, (chunk, score) in enumerate(results, 1):
                print(f"{i}. {chunk['function_name']} (relevance: {score:.3f})")
                print(f"    Type: {chunk['type']}")
                if chunk['type'] == 'main' and chunk['metadata'].get('syntax_forms'):
                    syntax_forms = chunk['metadata']['syntax_forms']
                    if syntax_forms:
                        syntax = syntax_forms[0]  # Show first syntax form
                        # Truncate long syntax
                        if len(syntax) > 60:
                            syntax = syntax[:60] + "..."
                        print(f"    Syntax: {syntax}")
                        if len(syntax_forms) > 1:
                            print(f"    (+{len(syntax_forms)-1} more syntax forms)")
                print()
            
            # Ask if user wants details
            detail_input = input(" Enter number for full details (or press Enter to search again): ").strip()
            
            if detail_input.isdigit() and 1 <= int(detail_input) <= len(results):
                idx = int(detail_input) - 1
                func_name = results[idx][0]['function_name']
                context = search_engine.get_function_context(func_name)
                
                print(f"\n{'=' * 60}")
                print(f" {context['function_name']}")
                print('=' * 60)
                
                if context.get('valid_for'):
                    print(f"\n Valid for: {context['valid_for']}")
                
                if context.get('syntax_forms'):
                    print(f"\n Syntax:")
                    for i, syntax in enumerate(context['syntax_forms'], 1):
                        print(f"   Form {i}: {syntax}")
                
                if context.get('description'):
                    print(f"\n Description:")
                    print(f"   {context['description']}")
                
                if context.get('parameters'):
                    print(f"\n Parameters:")
                    for param_name, param_desc in context['parameters']:
                        print(f"   • {param_name}: {param_desc}")
                
                if context.get('return_values'):
                    print(f"\n  Return Values:")
                    for ret_val in context['return_values']:
                        print(f"   • {ret_val}")
                
                if context.get('example'):
                    print(f"\n Example:")
                    # Indent example code
                    example_lines = context['example'].split('\n')
                    for line in example_lines:
                        print(f"   {line}")
                
                print(f"\n{'=' * 60}\n")
        
        except KeyboardInterrupt:
            print("\n\n Goodbye!")
            break
        except Exception as e:
            print(f" Error: {e}\n")