# SQLite to Drift ORM Conversion Tool

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Drift](https://img.shields.io/badge/Drift-ORM-green)

[简体中文](README-cn.md)
[English](README.md)

## Project Overview

This is a Python script that automatically converts SQLite database files into Dart files compatible with Flutter's [Drift ORM](https://drift.simonbinder.eu/). It simplifies the process of integrating SQLite databases into Flutter applications by generating complete database model code.

## Key Features

- 🔄 Automatically converts SQLite table structures to Drift Table classes
- 🧩 Supports common data types (INTEGER, TEXT, BLOB, REAL, NUMERIC)
- 🔑 Handles primary key constraints (single, composite, auto-increment)
- ⚙️ Converts field constraints (not null, unique, default values)
- ✨ Automatically generates database connection configuration code
- 🧹 Automatically formats generated Dart code

## Quick Start

```bash
# Basic usage (output file defaults to input filename + .dart)
python sqlite2drift.py my_database.sqlite

# Specify output file
python sqlite2drift.py my_database.sqlite -o lib/database/app_db.dart
```

## Future Plans

We plan to expand this tool to support more database types:

- ✅ Currently supported: SQLite
- 📅 Planned: PostgreSQL

Contributions and feature suggestions are welcome!
