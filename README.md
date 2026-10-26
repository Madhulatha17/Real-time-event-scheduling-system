# Real-Time Event Scheduling System

**Micro Project | Event Management and Scheduling Systems**

## Overview

EventFlow is an interactive web application for scheduling and managing events. It uses an AVL Tree for balanced event storage and compares its performance with an ordinary Binary Search Tree (BST).

## Objectives

- Efficiently insert, search, and delete events.
- Detect scheduling conflicts at the same venue.
- Reschedule existing events.
- Visualize the AVL Tree.
- Compare AVL Tree and BST height and search performance.
- Store events in JSON files without a database.

## Features

1. Add, edit, reschedule, and delete events.
2. Venue and time conflict detection.
3. AVL Tree insertion, deletion, searching, and rotations.
4. Interactive tree visualization.
5. AVL Tree versus BST comparison.
6. Event search and filters.
7. Dashboard statistics.
8. Dark mode.
9. Sample events.
10. Event history and undo.
11. Persistent JSON file storage.

## Technologies

- Python
- Flask
- HTML
- CSS
- JavaScript
- JSON
- AVL Tree and Binary Search Tree

## Installation

Install Python 3, then open a terminal in the project directory.

```bash
pip install -r requirements.txt
python app.py
```

Open this address in your browser:

http://127.0.0.1:5000

## Data Structures

The AVL Tree maintains its balance using rotations after insertion and deletion. The ordinary BST does not automatically rebalance, so it may become skewed.

Events are ordered by their start date and time, with the event ID used as a tie-breaker.

## Conflict Detection

Two events conflict if they use the same venue and their time intervals overlap. Back-to-back events are allowed.

## Storage

Events and undo snapshots are stored in JSON files. No database is required.

## Learning Outcomes

The project demonstrates tree-based data structures, file handling, web application development, event validation, and algorithm performance comparison.
