package com.docstar.domain.document.repository;

import com.docstar.domain.document.entity.DocumentTextEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface DocumentTextRepository extends JpaRepository<DocumentTextEntity, Long> {
}
