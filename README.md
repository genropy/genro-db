# Genro DB

Database abstraction layer for the Genro framework.

## Features

- **Database Adapters**: Support for SQLite, PostgreSQL (extensible)
- **ORM**: Type-safe table definitions with dataclass-based columns
- **Migrations**: Automatic schema migrations
- **Triggers**: Event-based triggers (onInserting, onInserted, onUpdating, etc.)
- **Query Compiler**: Genropy-style query syntax with `$field` and `:param`
- **Environment System**: Thread-local context for passing data through trigger chains
- **Trigger Stack**: Automatic prevention of infinite recursion

## Installation

```bash
pip install genro-db
```

## Quick Start

```python
from dataclasses import dataclass
from genro_db import GenroMicroDb, Table

# Define a table
class BookTable(Table):
    sql_name = "books"
    pkey = "id"

    @dataclass
    class Columns:
        id: int
        title: str
        author: str
        pages: int

# Create database
db = GenroMicroDb(name="mydb", implementation="sqlite", path="mydb.sqlite")
db.add_table(BookTable)
db.migrate()

# Use CRUD operations
book_id = db.tables.book.insert(record={
    'title': 'Clean Code',
    'author': 'Robert Martin',
    'pages': 464
})

book = db.tables.book.get(book_id)
```

## Dependencies

- `genro-core>=0.1.0` - Core utilities and decorators
- `pydantic>=2.0.0` - Data validation

## License

MIT License - see LICENSE file for details.
