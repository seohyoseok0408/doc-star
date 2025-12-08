package com.docstar.config;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import com.docstar.domain.jwt.service.JwtService;

@Component
public class ScheduleConfig {

    private final JwtService jwtService;
    
    public ScheduleConfig(JwtService jwtService) {
        this.jwtService = jwtService;
    }
    // Cron 표현식 (매일 새벽 3시 0분 0초))
    // Refresh 토큰 저장소 8일 지난 토큰 삭제
    @Scheduled(cron = "0 0 3 * * *")
    public void refreshEntityTtlSchedule() {
        jwtService.cleanupExpiredRefreshTokens();
    }
}