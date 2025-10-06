# MLFQ Homework - Quick Reference Guide

## Question 1: Random Problems
**Concept**: Priority Degradation
**Implementation**: 5 different seeds, 2 jobs, 2 queues, no I/O
**Key**: Jobs demote when quantum exhausted

## Question 2: Chapter Examples  
**Concept**: Classic MLFQ scenarios
**Implementation**: Use --jlist to define exact job characteristics
**Key**: Reproduces textbook figures

## Question 3: Round-Robin
**Concept**: MLFQ -> Round-Robin conversion
**Implementation**: -n 1 (single queue)
**Key**: No priority levels = round-robin

## Question 4: Gaming Scheduler
**Concept**: Rules 4a/4b exploit
**Implementation**: Job does I/O every 9ms (quantum=10ms) with -S flag
**Key**: Maintains high priority, gets 99% CPU

## Question 5: Boost Interval
**Concept**: Prevent starvation via priority boost
**Implementation**: Test different -B values
**Key**: For 5% CPU minimum, boost every 200ms (20 x quantum)

## Question 6: I/O Bump
**Concept**: Queue position after I/O
**Implementation**: Compare with/without -I flag
**Key**: -I puts I/O jobs at front = better responsiveness
