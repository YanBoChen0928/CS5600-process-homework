"""
Local Ollama LLM Client for CPU-only inference
Replaces cloud HuggingFace API with local Llama-3.2-3B

Author: Yan-Bo Chen  
Date: November 17, 2025
Purpose: CS5600 Project - ARM CPU Workload Characterization
"""

import subprocess
import logging
import time
import re
from typing import Optional, Dict, Union

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
        self.logger = logger
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
    
    def analyze_medical_query(self, query: str, max_tokens: int = 100, timeout: Optional[float] = None) -> Dict[str, Union[str, float]]:
        """
        Analyze medical query and extract condition (Level 2)
        
        Args:
            query: Medical query text
            max_tokens: Maximum tokens to generate
            timeout: Specific timeout (not used in subprocess version)
        
        Returns:
            Extracted medical condition information with latency
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Calling Ollama for medical query analysis: {query}")
            
            # System prompt for condition extraction
            system_prompt = """You are a medical assistant trained to extract medical conditions.

HANDLING MULTIPLE CONDITIONS:
1. If query contains multiple medical conditions, extract the PRIMARY/ACUTE condition
2. Priority order: Life-threatening emergencies > Acute conditions > Chronic diseases > Symptoms
3. For patient scenarios, focus on the condition requiring immediate medical attention

EXAMPLES:
- Single: "chest pain" → "Acute Coronary Syndrome"
- Multiple: "diabetic patient with chest pain" → "Acute Coronary Syndrome"
- Chronic+Acute: "hypertension patient having seizure" → "Seizure Disorder"

RESPONSE FORMAT:
- Medical queries: Return ONLY the primary condition name
- Non-medical queries: Return "NON_MEDICAL_QUERY"

DO NOT provide explanations or medical advice."""

            full_prompt = f"{system_prompt}\n\nUser query: {query}\n\nExtracted condition:"
            
            response_text = self.generate(full_prompt, max_tokens=max_tokens)
            
            # Calculate latency
            latency = time.time() - start_time
            
            self.logger.info(f"Raw LLM Response: {response_text}")
            self.logger.info(f"Query Latency: {latency:.4f} seconds")
            
            # Extract condition from response
            extracted_condition = self._extract_condition(response_text)
            confidence = '0.8'
            
            self.logger.info(f"Extracted condition: {extracted_condition}")
            
            return {
                'extracted_condition': extracted_condition,
                'confidence': confidence,
                'raw_response': response_text,
                'latency': latency
            }
            
        except Exception as e:
            latency = time.time() - start_time
            self.logger.error(f"Medical query analysis error: {str(e)}")
            
            return {
                'extracted_condition': '',
                'confidence': '0',
                'error': str(e),
                'latency': latency
            }
    
    def analyze_medical_query_dual_task(self, user_query: str, max_tokens: int = 100, timeout: Optional[float] = None) -> Dict[str, Union[str, float]]:
        """
        Analyze medical query with dual task (Level 2+4 Combined)
        Performs both condition extraction and medical validation
        
        Args:
            user_query: Original user medical query
            max_tokens: Maximum tokens to generate
            timeout: Timeout (not used in subprocess version)
        
        Returns:
            Dict with dual task results
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Calling Ollama (Dual Task) with query: {user_query}")
            
            system_prompt = """Medical Query Analysis - Dual Task Processing:

1. Extract primary medical condition (if specific condition identifiable)
2. Determine if this is a medical-related query

RESPONSE FORMAT:
MEDICAL: YES/NO
CONDITION: [specific condition name or "NONE"]
CONFIDENCE: [0.1-1.0]

EXAMPLES:
- "chest pain and shortness of breath" → MEDICAL: YES, CONDITION: Acute Coronary Syndrome, CONFIDENCE: 0.9
- "how to cook pasta safely" → MEDICAL: NO, CONDITION: NONE, CONFIDENCE: 0.95
- "persistent headache treatment" → MEDICAL: YES, CONDITION: Headache Disorder, CONFIDENCE: 0.8

Return ONLY the specified format."""

            full_prompt = f"{system_prompt}\n\nUser query: {user_query}\n\nAnalysis:"
            
            response_text = self.generate(full_prompt, max_tokens=max_tokens)
            
            # Calculate latency
            latency = time.time() - start_time
            
            self.logger.info(f"Raw LLM Dual Task Response: {response_text}")
            self.logger.info(f"Dual Task Latency: {latency:.4f} seconds")
            
            return {
                'extracted_condition': response_text,
                'confidence': '0.8',
                'raw_response': response_text,
                'latency': latency,
                'dual_task_mode': True
            }
            
        except Exception as e:
            latency = time.time() - start_time
            self.logger.error(f"Dual task query error: {str(e)}")
            
            return {
                'extracted_condition': '',
                'confidence': '0',
                'error': str(e),
                'latency': latency
            }
    
    def _extract_condition(self, response: str) -> str:
        """Extract condition name from LLM response"""
        # Clean up response
        response = response.strip()
        
        # Remove common prefixes
        response = re.sub(r'^(The |A |An )?condition is:?\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'^Extracted condition:?\s*', '', response, flags=re.IGNORECASE)
        
        # Take first line if multi-line
        response = response.split('\n')[0].strip()
        
        # Remove quotes
        response = response.strip('"\'')
        
        return response
    
    def generate_completion(self, prompt: str) -> Dict[str, Union[str, float]]:
        """
        Generate completion for medical advice (used by generation.py)
        
        Args:
            prompt: Complete prompt with guidelines and query
        
        Returns:
            Dict with response content and timing
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Generating medical advice ({len(prompt)} chars prompt)")
            
            response_text = self.generate(prompt, max_tokens=1600)
            
            latency = time.time() - start_time
            
            self.logger.info(f"✓ Medical advice generated ({len(response_text)} chars) in {latency:.2f}s")
            
            return {
                'raw_response': response_text,
                'content': response_text,
                'latency': latency,
                'error': None
            }
            
        except Exception as e:
            latency = time.time() - start_time
            self.logger.error(f"Generation failed: {str(e)}")
            
            return {
                'raw_response': '',
                'content': '',
                'latency': latency,
                'error': str(e)
            }
