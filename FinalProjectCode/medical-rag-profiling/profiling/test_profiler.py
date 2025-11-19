"""
Test script for WorkloadProfiler with real medical queries
Tests all 3 segments: initialization, profiling, timeline sampling

Author: Yan-Bo Chen
Date: November 18, 2025
Purpose: Validate profiler before full 100-query experiment
"""

import sys
import logging
import time
import random
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from profiling.workload_profiler import WorkloadProfiler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test queries - 3 real medical scenarios
TEST_QUERIES = [
    "A 45-year-old male presents with sudden chest pain radiating to the left arm. What emergency steps should I take?",
    
    "Patient has severe allergic reaction with difficulty breathing and facial swelling. Current vitals: BP 90/60, HR 120. Treatment protocol?",
    
    "Elderly patient fell and cannot move right leg. Suspected hip fracture. How to safely transport and what immediate care is needed?"
]


def mock_rag_function(query: str) -> str:
    """
    Mock RAG function for testing profiler
    Simulates CPU-intensive work with sleep
    
    In real experiment, this will be replaced by:
    response = rag_chain.invoke({"question": query})
    """
    # Simulate variable execution time (5-15 seconds)
    execution_time = random.uniform(5, 15)
    logger.info(f"  Mock RAG executing for {execution_time:.1f}s...")
    time.sleep(execution_time)
    
    # Return mock response
    return f"Mock response to: {query[:30]}... (length: {random.randint(100, 500)} chars)"


def test_profiler_initialization():
    """Test Segment 1: Profiler initialization and system info collection"""
    logger.info("=" * 70)
    logger.info("TEST 1: Profiler Initialization (Segment 1)")
    logger.info("=" * 70)
    
    # Initialize profiler
    profiler = WorkloadProfiler(output_dir="test_profiling_data")
    
    # Verify system info collected
    assert profiler.system_info is not None, "System info should be collected"
    assert "platform" in profiler.system_info, "Platform should be detected"
    assert "architecture" in profiler.system_info, "Architecture should be detected"
    
    logger.info(f"✓ Platform: {profiler.system_info['platform']}")
    logger.info(f"✓ Architecture: {profiler.system_info['architecture']}")
    logger.info(f"✓ CPU cores: {profiler.system_info['cpu_count_physical']} physical, "
               f"{profiler.system_info['cpu_count_logical']} logical")
    logger.info(f"✓ Memory: {profiler.system_info['total_memory_gb']}GB")
    
    if profiler.system_info.get('p_cores'):
        logger.info(f"✓ P-cores: {len(profiler.system_info['p_cores'])}, "
                   f"E-cores: {len(profiler.system_info['e_cores'])}")
        logger.info(f"✓ Note: {profiler.system_info['note']}")
    
    logger.info(f"✓ System info saved to: {profiler.output_dir / 'system_info.json'}")
    logger.info("✅ TEST 1 PASSED\n")
    
    return profiler



def test_single_query_profiling(profiler):
    """Test Segment 2: Single query profiling with CPU/memory metrics"""
    logger.info("=" * 70)
    logger.info("TEST 2: Single Query Profiling (Segment 2)")
    logger.info("=" * 70)
    
    query = TEST_QUERIES[0]
    logger.info(f"Query: {query[:60]}...")
    
    # Profile single query
    metrics = profiler.profile_query(
        query=query,
        query_id=0,
        run_id=0,
        rag_function=mock_rag_function
    )
    
    # Verify metrics structure
    assert "metadata" in metrics, "Should have metadata"
    assert "latency" in metrics, "Should have latency metrics"
    assert "cpu" in metrics, "Should have CPU metrics"
    assert "memory" in metrics, "Should have memory metrics"
    assert "timeline" in metrics, "Should have timeline data"
    assert "timeline_summary" in metrics, "Should have timeline summary"
    
    # Verify values are reasonable
    assert metrics["latency"]["total_ms"] > 0, "Latency should be positive"
    assert len(metrics["cpu"]["per_core"]) > 0, "Should have per-core CPU data"
    assert metrics["memory"]["used_gb"] > 0, "Memory usage should be positive"
    
    # Print results
    logger.info(f"✓ Latency: {metrics['latency']['total_ms']:.2f}ms")
    logger.info(f"✓ CPU peak: {metrics['cpu']['peak_percent']:.2f}%")
    logger.info(f"✓ CPU avg: {metrics['cpu']['average_percent']:.2f}%")
    
    if metrics['cpu']['p_cores_average']:
        logger.info(f"✓ P-cores avg: {metrics['cpu']['p_cores_average']:.2f}%")
        logger.info(f"✓ E-cores avg: {metrics['cpu']['e_cores_average']:.2f}%")
    
    logger.info(f"✓ Memory used: {metrics['memory']['used_gb']:.2f}GB")
    logger.info(f"✓ Memory %: {metrics['memory']['percent']:.2f}%")
    logger.info("✅ TEST 2 PASSED\n")
    
    return metrics



def test_timeline_sampling(metrics):
    """Test Segment 3: Timeline sampling validation"""
    logger.info("=" * 70)
    logger.info("TEST 3: Timeline Sampling (Segment 3)")
    logger.info("=" * 70)
    
    timeline = metrics["timeline"]
    timeline_summary = metrics["timeline_summary"]
    
    # Verify timeline data exists
    assert len(timeline) > 0, "Timeline should have samples"
    assert timeline_summary["num_samples"] > 0, "Should have timeline samples"
    
    # Verify sampling interval (should be ~0.5s)
    if len(timeline) >= 2:
        intervals = [timeline[i+1]['t'] - timeline[i]['t'] for i in range(len(timeline)-1)]
        avg_interval = sum(intervals) / len(intervals)
        logger.info(f"✓ Timeline samples: {len(timeline)}")
        logger.info(f"✓ Average sampling interval: {avg_interval:.2f}s (target: 0.5s)")
        # Relaxed tolerance to 0.7s to account for:
        # - psutil.cpu_percent(interval=0.1) blocking time
        # - macOS process scheduling latency
        # - Python GIL thread switching overhead
        assert 0.4 <= avg_interval <= 0.7, f"Sampling interval should be ~0.5s, got {avg_interval:.2f}s"
    
    # Verify timeline metrics calculation
    assert timeline_summary["cpu_peak_from_timeline"] is not None, "Should have CPU peak"
    assert timeline_summary["cpu_avg_from_timeline"] is not None, "Should have CPU average"
    assert timeline_summary["memory_peak_from_timeline"] is not None, "Should have memory peak"
    
    logger.info(f"✓ CPU peak (timeline): {timeline_summary['cpu_peak_from_timeline']:.2f}%")
    logger.info(f"✓ CPU avg (timeline): {timeline_summary['cpu_avg_from_timeline']:.2f}%")
    logger.info(f"✓ Memory peak (timeline): {timeline_summary['memory_peak_from_timeline']:.2f}GB")
    
    # Show first and last sample
    logger.info(f"✓ First sample at t={timeline[0]['t']:.2f}s: "
               f"CPU={timeline[0]['cpu_total']:.2f}%, Mem={timeline[0]['memory_gb']:.2f}GB")
    logger.info(f"✓ Last sample at t={timeline[-1]['t']:.2f}s: "
               f"CPU={timeline[-1]['cpu_total']:.2f}%, Mem={timeline[-1]['memory_gb']:.2f}GB")
    
    logger.info("✅ TEST 3 PASSED\n")



def test_three_real_queries(profiler):
    """Test with 3 real medical queries, 2 runs each (total 6 profiles)"""
    logger.info("=" * 70)
    logger.info("TEST 4: Three Real Queries × 2 Runs Each")
    logger.info("=" * 70)
    
    all_results = []
    
    for query_id, query in enumerate(TEST_QUERIES):
        logger.info(f"\n📋 Query {query_id}: {query[:60]}...")
        
        for run_id in range(2):  # 2 runs per query
            logger.info(f"  🔄 Run {run_id}")
            
            # Profile query
            metrics = profiler.profile_query(
                query=query,
                query_id=query_id,
                run_id=run_id,
                rag_function=mock_rag_function
            )
            
            # Save result
            profiler.save_result(metrics)
            all_results.append(metrics)
            
            # Brief summary
            logger.info(f"    ✓ Latency: {metrics['latency']['total_ms']:.0f}ms, "
                       f"CPU: {metrics['cpu']['average_percent']:.1f}%, "
                       f"Memory: {metrics['memory']['used_gb']:.2f}GB, "
                       f"Samples: {metrics['timeline_summary']['num_samples']}")
    
    logger.info(f"\n✓ Total profiles generated: {len(all_results)}")
    logger.info(f"✓ Expected files: query_000_run_00.json to query_002_run_01.json")
    logger.info("✅ TEST 4 PASSED\n")
    
    return all_results


def main():
    """Run all tests"""
    logger.info("\n" + "=" * 70)
    logger.info("🧪 WORKLOAD PROFILER TEST SUITE")
    logger.info("=" * 70)
    logger.info("Testing 3 segments: Initialization, Profiling, Timeline Sampling")
    logger.info("=" * 70 + "\n")
    
    try:
        # Test 1: Initialization
        profiler = test_profiler_initialization()
        
        # Test 2: Single query profiling
        single_metrics = test_single_query_profiling(profiler)
        
        # Test 3: Timeline sampling validation
        test_timeline_sampling(single_metrics)
        
        # Test 4: Multiple queries
        all_results = test_three_real_queries(profiler)
        
        # Final summary
        logger.info("=" * 70)
        logger.info("🎉 ALL TESTS PASSED")
        logger.info("=" * 70)
        logger.info(f"✓ Total queries profiled: {len(all_results) + 1}")  # +1 for test 2
        logger.info(f"✓ Output directory: {profiler.output_dir}")
        logger.info(f"✓ JSON files generated: {len(all_results) + 1}")
        logger.info("=" * 70)
        
    except AssertionError as e:
        logger.error(f"❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ ERROR: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    main()
