#!/usr/bin/env bash

# 인자: username, email, commit message
USERNAME="$1"
EMAIL="$2"
COMMIT_MESSAGE="$3"

if [[ -z "$USERNAME" || -z "$EMAIL" || -z "$COMMIT_MESSAGE" ]]; then
  echo "사용법: $0 <username> <email> <commit message>"
  exit 1
fi

if [ ! -d .git ]; then
  echo "이 디렉토리는 git 저장소가 아닙니다."
  exit 1
fi

# 커밋하기 전에 user 설정
git config user.name "$USERNAME"
git config user.email "$EMAIL"

# 스테이징
git add .

# 커밋
git commit -m "$COMMIT_MESSAGE"

echo "커밋 완료: '$COMMIT_MESSAGE' by $USERNAME <$EMAIL>"
