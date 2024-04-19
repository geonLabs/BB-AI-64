#!/bin/bash

# 현재 연월일 구하기 (YYYY-MM-DD 형식)
CURRENT_DATE=$(date +"%Y-%m-%d")

# 디렉토리 생성 및 경로 설정
WATCHED_DIR="$(pwd)/$CURRENT_DATE"
mkdir -p "$WATCHED_DIR"

# 인자로부터 값 받기
DESTINATION_USER="$1"            # 대상 컴퓨터의 사용자 이름
DESTINATION_HOST="$2"            # 대상 컴퓨터의 호스트
DESTINATION_PARENT_DIR="$3"      # 대상 컴퓨터의 부모 디렉토리
SSHPASS="$4"
PYTHON_SCRIPT_PATH="$5"          # 파이썬 스크립트 경로
PYTHON_SCRIPT_ARGS="${@:6}"      # 파이썬 스크립트에 전달할 인자들

# 필수 인자가 모두 제공되었는지 확인
if [ -z "$DESTINATION_USER" ] || [ -z "$DESTINATION_HOST" ] || [ -z "$DESTINATION_PARENT_DIR" ] || [ -z "$SSHPASS" ] || [ -z "$PYTHON_SCRIPT_PATH" ]; then
    echo "Usage: $0 DESTINATION_USER DESTINATION_HOST DESTINATION_PARENT_DIR SSHPASS PYTHON_SCRIPT_PATH [PYTHON_SCRIPT_ARGS...]"
    exit 1
fi

# 대상 컴퓨터에서 날짜별 폴더 생성
sshpass -p "$SSHPASS" ssh "$DESTINATION_USER@$DESTINATION_HOST" "mkdir -p \"$DESTINATION_PARENT_DIR/$CURRENT_DATE\""

# 파이썬 스크립트 시작 (인자 포함)
python3 "$PYTHON_SCRIPT_PATH" "$CURRENT_DATE" $PYTHON_SCRIPT_ARGS &
PYTHON_PID=$!

# 스크립트 종료 시 파이썬 프로세스 종료
trap "kill $PYTHON_PID; exit" SIGINT SIGTERM

# inotifywait를 사용하여 파일 추가 감지
inotifywait -m "$WATCHED_DIR" -e create |
    while read path action file; do
        echo "Detected new file: $file, action: $action"

        # sshpass와 SFTP를 사용하여 파일을 전송
        sshpass -p "$SSHPASS" sftp "$DESTINATION_USER@$DESTINATION_HOST" <<EOF
put "$path$file" "$DESTINATION_PARENT_DIR/$CURRENT_DATE/"
quit
EOF

        echo "File $file has been transferred via SFTP."

        # 전송된 파일 삭제
        rm "$path$file"
        echo "File $file has been deleted after transfer."
    done
