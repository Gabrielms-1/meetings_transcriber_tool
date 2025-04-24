    #!/bin/bash
    set -e 

    VENV_PATH="/home/ubuntu/meetings_transcriber_tool/venv_new"
    APP_DIR="/home/ubuntu/meetings_transcriber_tool/src/infra"
    LOG_FILE="/home/ubuntu/meetings_transcriber_tool/logs/startup_access.log"
    ERROR_LOG="/home/ubuntu/meetings_transcriber_tool/logs/api_error.log"
    
    rm -f $LOG_FILE
    rm -f $ERROR_LOG

    WORKERS=1
    THREADS=4
    PORT=8000
    BIND="0.0.0.0:$PORT"
    MODULE="app:app"

    if lsof -i :$PORT -t > /dev/null; then
        echo "  Stopping FastAPI via Gunicorn + UvicornWorker $(date) " >> "${LOG_FILE}"
        lsof -ti :$PORT | xargs -r kill -9
    fi

    echo "  Starting FastAPI via Gunicorn + UvicornWorker $(date) " >> "${LOG_FILE}"
    echo "  virtualenv: $VENV_PATH" >> "${LOG_FILE}"
    echo "  workdir: $APP_DIR" >> "${LOG_FILE}"
    echo "  workers: $WORKERS, threads: $THREADS" >> "${LOG_FILE}"
    echo "  binding: $BIND" >> "${LOG_FILE}"
    echo "" >> "${LOG_FILE}"

    echo "Activating virtual environment... at $(date) " >> "${LOG_FILE}"
    source "$VENV_PATH/bin/activate"
    echo "Virtual environment activated at $(date) " >> "${LOG_FILE}"

    cd "$APP_DIR"

    gunicorn \
        -k uvicorn.workers.UvicornWorker \
        $MODULE \
        -w $WORKERS \
        --threads $THREADS \
        --bind $BIND \
        --access-logfile $LOG_FILE \
        --error-logfile $ERROR_LOG &

    GUNICORN_PID=$!
    echo "Gunicorn PID: $GUNICORN_PID" >> "${LOG_FILE}"
    wait $GUNICORN_PID

    echo "--- Server setup script finished at $(date) ---" >> "${LOG_FILE}"

    exit 0 