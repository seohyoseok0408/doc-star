package com.docstar.domain.document.entity;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@EntityListeners(AuditingEntityListener.class)
@Table(name = "document_text")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DocumentTextEntity {

    @Id
    @Column(name = "doc_id")
    private Long docId; 

    @OneToOne
    @MapsId
    @JoinColumn(name = "doc_id")
    private DocumentEntity document;

    @Lob 
    @Column(name = "full_text", nullable = false)
    private String fullText;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}
