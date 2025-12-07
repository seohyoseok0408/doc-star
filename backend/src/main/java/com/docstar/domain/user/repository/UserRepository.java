package com.docstar.domain.user.repository;
import org.springframework.data.jpa.repository.JpaRepository;

import com.docstar.domain.user.entity.UserEntity;

public interface UserRepository extends JpaRepository<UserEntity, Long> {
}