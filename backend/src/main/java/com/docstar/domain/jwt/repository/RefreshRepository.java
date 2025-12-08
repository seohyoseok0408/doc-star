package com.docstar.domain.jwt.repository;

import java.time.LocalDateTime;

import org.springframework.data.jpa.repository.JpaRepository;

import com.docstar.domain.jwt.entity.RefreshEntity;

public interface RefreshRepository extends JpaRepository<RefreshEntity, Long> {
    Boolean existsByRefresh(String refreshToken);

    void deleteByRefresh(String refresh);

    void deleteByUsername(String username);

    void deleteByCreatedDateBefore(LocalDateTime createdDate);
}