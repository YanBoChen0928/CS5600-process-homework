"""
RAG Wrapper for Ollama Integration
Interfaces with Ollama + Llama models for medical query inference

Author: Yan-Bo Chen
Date: November 19, 2025
Purpose: CS5600 Final Project - Real RAG Integration
"""

import subprocess
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def check_ollama_running() -> bool:
    """
    Check if Ollama service is running
    
    Returns:
        True if Ollama is running, False otherwise
    """
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_model_available(model: str) -> bool:
    """
    Check if specified model is available in Ollama
    
    Args:
        model: Model name (e.g., "llama3.2-cpu")
        
    Returns:
        True if model is available
    """
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Check if model name appears in output
            return model in result.stdout
        return False
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def rag_query(query: str, model: str = "llama3.2-cpu", timeout: int = 300) -> str:
    """
    Execute RAG query using Ollama with specified model
    
    NOTE: Assumes Ollama and model availability already checked at startup.
          This avoids redundant checks for every query in batch experiments.
    
    Args:
        query: Medical query string
        model: Ollama model name (e.g., "llama3.2-cpu", "llama3.2:3b")
        timeout: Max seconds to wait for response (default: 300)
        
    Returns:
        Response string from RAG pipeline
        
    Raises:
        RuntimeError: If Ollama execution fails
        subprocess.TimeoutExpired: If query exceeds timeout
    """
    logger.debug(f"Executing RAG query with model '{model}': {query[:60]}...")
    
    try:
        # Execute Ollama command
        result = subprocess.run(
            ['ollama', 'run', model, query],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            raise RuntimeError(f"Ollama execution failed: {error_msg}")
        
        response = result.stdout.strip()
        
        if not response:
            raise RuntimeError("Ollama returned empty response")
        
        logger.debug(f"RAG query successful, response length: {len(response)} chars")
        
        return response
        
    except subprocess.TimeoutExpired:
        logger.error(f"RAG query timed out after {timeout}s")
        raise


def test_rag_wrapper():
    """
    Test function to verify RAG wrapper works
    Run this file directly to test: python rag_wrapper.py
    """
    print("=" * 70)
    print("RAG WRAPPER TEST")
    print("=" * 70)
    
    # Test 1: Check Ollama
    print("\n[TEST 1] Checking Ollama service...")
    if check_ollama_running():
        print("✓ Ollama is running")
    else:
        print("✗ Ollama is NOT running")
        print("  Please start Ollama first: ollama serve")
        return
    
    # Test 2: Check model
    test_model = "llama3.2-cpu"
    print(f"\n[TEST 2] Checking model '{test_model}'...")
    if check_model_available(test_model):
        print(f"✓ Model '{test_model}' is available")
    else:
        print(f"✗ Model '{test_model}' not found")
        print(f"  Available models:")
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        print(result.stdout)
    
    # Test 3: Simple query
    print(f"\n[TEST 3] Testing simple query...")
    test_query = "What is hypertension? Answer in one sentence."
    
    try:
        print(f"Query: {test_query}")
        start_time = time.time()
        
        response = rag_query(test_query, model=test_model, timeout=30)
        
        elapsed = time.time() - start_time
        
        print(f"✓ Query successful!")
        print(f"  Response: {response[:100]}...")
        print(f"  Length: {len(response)} chars")
        print(f"  Time: {elapsed:.2f}s")
        
    except Exception as e:
        print(f"✗ Query failed: {e}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    # Configure logging for standalone test
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s - %(message)s'
    )
    
    test_rag_wrapper()
