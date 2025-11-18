"""
Local Ollama LLM Client for CPU-only inference
Replaces cloud HuggingFace API with local Llama-3.2-3B

Author: Yan-Bo Chen  
Date: November 17, 2025
Purpose: CS5600 Project - ARM CPU Workload Characterization
"""

import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class OllamaLocalClient:
    """
    Local Ollama client for CPU-only LLM inference
    Replaces llm_Med42_70BClient with local llama3.2-cpu model
    """
    
    def __init__(self, model_name: str = "llama3.2-cpu"):
        """
        Initialize local Ollama client
        
        Args:
            model_name: Ollama model to use (default: llama3.2-cpu for CPU-only)
        """
        self.model_name = model_name
        logger.info(f"Initializing OllamaLocalClient with model: {model_name}")
        self._verify_model_exists()
    
    def _verify_model_exists(self):
        """Verify that the specified Ollama model is available"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if self.model_name not in result.stdout:
                raise ValueError(
                    f"Model '{self.model_name}' not found in Ollama.\n"
                    f"Available models:\n{result.stdout}\n"
                    f"Please run: ollama pull llama3.2:3b && ollama create {self.model_name} -f Modelfile-cpu"
                )
            
            logger.info(f"✓ Model {self.model_name} verified and ready")
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Ollama verification timed out. Is Ollama server running?")
        except FileNotFoundError:
            raise RuntimeError(
                "Ollama not found. Please install:\n"
                "macOS: brew install ollama\n"
                "Linux: curl -fsSL https://ollama.com/install.sh | sh"
            )
    
    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """
        Generate response using local Ollama model
        
        Args:
            prompt: Input prompt for generation
            max_tokens: Maximum tokens to generate (note: Ollama CLI ignores this)
        
        Returns:
            Generated text response
        """
        logger.info(f"Generating response with {self.model_name}...")
        
        try:
            result = subprocess.run(
                ['ollama', 'run', self.model_name, prompt],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Ollama generation failed: {error_msg}")
                raise RuntimeError(f"Ollama generation failed: {error_msg}")
            
            response = result.stdout.strip()
            logger.info(f"✓ Generated {len(response)} characters")
            
            return response
            
        except subprocess.TimeoutExpired:
            logger.error("Ollama generation timed out (>120s)")
            raise RuntimeError("Generation timed out. Query may be too complex.")
    
    def generate_with_context(self, query: str, context: str, max_tokens: int = 1024) -> str:
        """
        Generate response with RAG context (for medical queries)
        
        Args:
            query: User's medical query
            context: Retrieved medical guidelines
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated medical advice
        """
        # Build prompt with medical context
        prompt = f"""You are a medical assistant. Based on the following medical guidelines, answer the patient's question.

Medical Guidelines:
{context}

Patient Question: {query}

Provide clear, evidence-based medical guidance:"""
        
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        return self.generate(prompt, max_tokens)
