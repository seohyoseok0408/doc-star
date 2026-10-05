package com.docstar.domain.document.repository;

import com.docstar.domain.document.entity.DocumentChunkEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface DocumentChunkRepository extends JpaRepository<DocumentChunkEntity, Integer> {
}
