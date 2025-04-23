    #!/bin/bash
    set -e 

    LOG_FILE="./startup_script.log"
    UVICORN_LOG_FILE="./uvicorn.log"
    echo "--- Starting server setup at $(date) ---" > $LOG_FILE
    start_time=$(date +%s)

    echo "[$(($(date +%s) - start_time))s] Changing to project directory..." >> $LOG_FILE
    cd /home/ubuntu/meetings_transcriber_tool || { echo "Failed to cd into project dir" >> $LOG_FILE; exit 1; }
    echo "[$(($(date +%s) - start_time))s] Done. Current directory: $(pwd)" >> $LOG_FILE

    # deactivate &> /dev/null || true 
    
    # echo "[$(($(date +%s) - start_time))s] Activating venv..." >> $LOG_FILE
    # source venv/bin/activate || { echo "Failed to activate venv" >> $LOG_FILE; exit 1; }
    # echo "[$(($(date +%s) - start_time))s] Done." >> $LOG_FILE
    echo "[$(($(date +%s) - start_time))s] Changing to infra directory..." >> $LOG_FILE
    cd /home/ubuntu/meetings_transcriber_tool/src/infra 
    echo "[$(($(date +%s) - start_time))s] Done. Current directory: $(pwd)" >> $LOG_FILE

    UVICORN_CMD="/home/ubuntu/meetings_transcriber_tool/venv/bin/uvicorn"

    echo "[$(($(date +%s) - start_time))s] Starting Uvicorn in background... $(pwd)" >> $LOG_FILE
    nohup $UVICORN_CMD app:app --host 0.0.0.0 --port 8000 --workers 1 >> $UVICORN_LOG_FILE 2>&1 &
    UVICORN_PID=$!
    echo "[$(($(date +%s) - start_time))s] Uvicorn launched with PID $UVICORN_PID. App initialization might still be ongoing." >> $LOG_FILE

    end_time=$(date +%s)
    echo "--- Server setup script finished at $(date) (Total script execution time: $(($end_time - start_time))s) ---" >> $LOG_FILE

    exit 0 