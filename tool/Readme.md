# SQL Dependencies Analyzer

A comprehensive tool for analyzing dependencies in SQL statements using both syntactic and semantic approaches.

## Overview

This project implements algorithms for detecting and analyzing dependencies in SQL statements. It uses two main approaches:
- **Syntactic Analysis**: Analyzing the structure and grammar of SQL statements
- **Semantic Analysis**: Analyzing the meaning and behavior of SQL statements, further divided into:
  - Domain of Interval Analysis
  - Polyhedra Analysis

## Repository Structure

```
.
├── proformat/        # Code for preprocessing and formatting SQL statements
├── syntax/           # Implementation of syntactic dependency analysis
├── interval/         # Implementation of domain of interval analysis
├── polyhedra/        # Implementation of polyhedra analysis
├── tuning/           # Parameters and configurations for optimizing algorithms
└── images/           # Output visualizations and result examples
```

## Algorithms

### Syntactic Analysis

The syntactic analysis parses SQL statements to identify dependencies based on grammar rules and statement structure. It identifies relationships between tables, columns, and other SQL elements without considering the actual data or query execution.

### Semantic Analysis

Semantic analysis examines the meaning and behavior of SQL statements, considering how data is actually processed during query execution.

#### Domain of Interval Analysis

This algorithm analyzes numerical constraints and relationships in SQL statements by tracking intervals of possible values. It helps identify implicit dependencies that may not be apparent from syntax alone.

#### Polyhedra Analysis

A more sophisticated semantic approach that models query constraints as polyhedra (geometric objects with flat sides) in multi-dimensional space. This allows for precise dependency analysis even in complex query conditions.

## Getting Started

### Prerequisites

[List any prerequisites like Python version, database systems, etc.]

### Installation

```bash
git clone https://github.com/yourusername/sql-dependencies-analyzer.git
cd sql-dependencies-analyzer
# Add installation steps
```
-----------------------------------------------------------------------------
TOOL USAGE:
## Tool Usage

### Step 1: Upload Input & DB File & algorithm

![Upload Files](images/image1.png)

### Step 2: View Syntactic Analysis

![Select Algorithm](images/image2.png)

### Step 3: View Semantic(Domain Of Interval) Analysis

![Syntactic Result](images/image3.png)

### Step 4: View Semantic (Polyhedra) Analysis

![Polyhedra Result](images/image4.png)


## Configuration

The `tuning/` directory contains parameters for configuring and optimizing the algorithms for different SQL dialects and scenarios.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify license]

## Acknowledgements

[Any acknowledgements]
