#!/bin/bash
echo "========================================"
echo " Séance 👻 — Ghost Chat Setup (Linux)"
echo "========================================"
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: pip install failed. Make sure Python is installed."
    exit 1
fi
echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  python seance.py serve"
echo ""
echo "To send a message from terminal:"
echo '  python seance.py send "Hello!" --from desktop'
echo ""
echo "Then open http://localhost:5555 in your browser!"
