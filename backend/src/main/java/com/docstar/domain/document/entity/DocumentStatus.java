package com.docstar.domain.document.entity;

public enum DocumentStatus {
    UPLOADED,      // 파일 저장 완료
    PROCESSING,    // 텍스트 추출 / 정제 중
    COMPLETED,     // AI 사용 가능
    FAILED         // 처리 실패
}
