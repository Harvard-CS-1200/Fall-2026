# Problem Set 4

## Overview

This problem set explores randomized algorithms and graphs. The programming portion of this problem set focuses on QuickSelect, a Las Vegas randomized algorithm.

*Make sure to pull from the course source often or check Ed for updates. We hope to release a perfect problem set but sometimes we add to the problem set to make things easier or fix obscure bugs.*

## Downloading Starter Code
Run the following command to download the necessary libraries for graphing:

```bash
pip install -r requirements.txt
```

## Instructions

**Problem 1a**: For this part of the problem, you must fill in the implementation of HashTable::search and HashTable::delete for the case when optimize is turned off, ensuring that it provides an always-correct Dictionary data structure. We have provided some local tests to help you check that your implementation returns the right answer. You can run the included tests with `python3 -m ps4_tests` (as explained below). **If you pass the local tests you should be in good shape to move on.** It also sets up for the next parts of the problem.

**Problem 1b**: For this part, we have provided the code for running experiments and generating graphs. You can run the included experiments with `python3 -m experiments`. Double check that the console output looks reasonable (you should see a table of results being printed out), then check to make sure that images `runtime_bar.png` and `incorrect_rate_bar.png` have been added to your ps4 folder. Take a look at these two graphs and write down your interpretation of these results in the problem set.

**Conclusion**: If your work passes the local tests, includes the figure for your generated graphs, and answers 1b, you should be in good shape to get full marks for this problem.

## Running the Code

The problem set includes some starter code in `ps4.py`. To run the code, type in your terminal:

```bash
python3 -m ps4
```

## Running the Included Tests

The problem set also includes some tests for you to test your code.

To run the tests, type in your terminal:

```bash
python3 -m ps4_tests
```
