#!/usr/bin/env bash

# 현재 브랜치
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ ! -d .git ]; then
  echo "이 디렉토리는 git 저장소가 아닙니다."
  exit 1
fi

# 푸시
git push origin "$CURRENT_BRANCH"

echo "푸시 완료: 브랜치 '$CURRENT_BRANCH'"
