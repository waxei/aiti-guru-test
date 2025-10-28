#!/bin/bash
set -e

echo "[TESTS] Starting test suite..."

# Запускаем тесты
echo "[TESTS] Running pytest..."
cd /app
python -m pytest tests/ -v --tb=short --disable-warnings

if [ $? -eq 0 ]; then
    echo "[TESTS] ✓ All tests passed!"
    exit 0
else
    echo "[TESTS] ✗ Some tests failed!"
    exit 1
fi

