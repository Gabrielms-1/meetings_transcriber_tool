    #!/bin/bash
    set -e 

    VENV_PATH="/home/ubuntu/meetings_transcriber_tool/venv"
    APP_DIR="/home/ubuntu/meetings_transcriber_tool/src/infra"
    LOG_FILE="/home/ubuntu/meetings_transcriber_tool/startup_access.log"
    ERROR_LOG="/home/ubuntu/meetings_transcriber_tool/api_error.log"
    
    WORKERS=1
    THREADS=4
    PORT=8000
    BIND="0.0.0.0:$PORT"
    MODULE="app:app"

    echo "🚀 Starting FastAPI via Gunicorn + UvicornWorker"
    echo "  virtualenv: $VENV_PATH"
    echo "  workdir: $APP_DIR"
    echo "  workers: $WORKERS, threads: $THREADS"
    echo "  binding: $BIND"
    echo ""

    source "$VENV_PATH/bin/activate"

    cd "$APP_DIR"

    exec gunicorn \
        -k uvicorn.workers.UvicornWorker \
        $MODULE \
        -w $WORKERS \
        --threads $THREADS \
        --bind $BIND \
        --access-logfile $LOG_FILE \
        --error-logfile $ERROR_LOG
        
    echo "--- Server setup script finished at $(date) ---" >> "${LOG_FILE}"

    exit 0 