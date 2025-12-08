package com.docstar.domain.user.repository;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.transaction.annotation.Transactional;

import com.docstar.domain.user.entity.UserEntity;

public interface UserRepository extends JpaRepository<UserEntity, Long> {
    Boolean existsByUsername(String username);
    Optional<UserEntity> findByUsernameAndIsLock(String username, boolean b);
    @Transactional
    void deleteByUsername(String username);
}