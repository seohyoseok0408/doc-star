package com.docstar.domain.document.entity;

public enum DocumentStatus {
    UPLOADED, // Initial state after file upload
    PROCESSING,
    COMPLETED,
    FAILED
}
