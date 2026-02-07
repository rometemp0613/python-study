#!/bin/bash
# Phase 1 전체 테스트 실행 스크립트

set -e

BASE="/mnt/c/git/study/python-study/testing/phase1_foundation"

echo "============================================"
echo " Phase 1 Foundation - 테스트 실행"
echo "============================================"

run_test() {
    local dir="$1"
    local name="$2"
    echo ""
    echo "--- $name ---"
    cd "$BASE/$dir"
    pytest -v --tb=short 2>&1 || true
}

run_test "01_why_testing" "01. 왜 테스트가 필요한가"
run_test "02_unittest_doctest" "02. unittest & doctest"
run_test "03_pytest_basics" "03. pytest 기본기"
run_test "04_test_organization" "04. 테스트 구조와 프로젝트 조직"
run_test "05_testing_exceptions" "05. 예외와 에러 핸들링 테스트"
run_test "06_capturing_output" "06. 출력 캡처"

echo ""
echo "============================================"
echo " 전체 테스트 실행 완료"
echo "============================================"
