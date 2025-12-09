package com.docstar.api;

import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.docstar.domain.jwt.dto.JWTResponseDTO;
import com.docstar.domain.jwt.dto.RefreshRequestDTO;
import com.docstar.domain.jwt.service.JwtService;
import com.docstar.global.ApiResponse;

@RestController
public class JwtController {

    private final JwtService jwtService;

    public JwtController(JwtService jwtService) {
        this.jwtService = jwtService;
    }
    // Refresh 토큰으로 Access 토큰 재발급 (Rotate 포함)
    @PostMapping(value = "/jwt/refresh", consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<ApiResponse<JWTResponseDTO>> jwtRefreshApi(@Validated @RequestBody RefreshRequestDTO dto) {

        JWTResponseDTO responseDto = jwtService.refreshRotate(dto);
        return ResponseEntity.ok(ApiResponse.success("토큰 재발급 성공", responseDto));    }
}