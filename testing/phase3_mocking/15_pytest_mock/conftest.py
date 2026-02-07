"""
conftest.py - pytest 설정

이 디렉토리에서 pytest를 실행할 때
소스 모듈을 임포트할 수 있도록 경로를 설정합니다.
"""

import sys
import os

# 현재 디렉토리를 sys.path에 추가하여 src_* 모듈을 임포트 가능하게 함
sys.path.insert(0, os.path.dirname(__file__))
