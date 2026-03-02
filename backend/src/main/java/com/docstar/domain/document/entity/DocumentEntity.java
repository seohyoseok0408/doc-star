package com.docstar.domain.document.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Table(name = "document")
public class DocumentEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long docId;

    @Column(nullable = false)
    private Long userId;

    @Column
    private Long projectId;

    @Column(nullable = false)
    private String originalFileName;

    @Column(nullable = false, length = 500)
    private String filePath;

    @Column(nullable = false)
    private Long fileSize;

    @Column(nullable = false)
    private String mimeType;

    @Column(length = 30)
    private String documentType; // LECTURE, PAPER, CONTRACT ...

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private DocumentStatus status;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column
    private LocalDateTime updatedAt;

    public void markProcessing() {
        this.status = DocumentStatus.PROCESSING;
        this.updatedAt = LocalDateTime.now();
    }

    public void markCompleted() {
        this.status = DocumentStatus.COMPLETED;
        this.updatedAt = LocalDateTime.now();
    }

    public void markFailed() {
        this.status = DocumentStatus.FAILED;
        this.updatedAt = LocalDateTime.now();
    }    
}
