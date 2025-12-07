package com.docstar.api;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.docstar.domain.user.dto.SignupRequest;
import com.docstar.domain.user.service.UserService;
import com.docstar.global.ApiResponse;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@Tag(name = "User", description = "사용자 관련 API")
public class UserController {

    private final UserService userService;

    @Operation(summary = "회원가입", description = "이메일, 비밀번호를 통해 회원가입을 수행합니다.")
    @PostMapping("/auth/signup")
    public ResponseEntity<ApiResponse<Void>> signup(@RequestBody @Valid SignupRequest request) throws Exception {
        
        userService.signup(request);
        return ResponseEntity.ok(ApiResponse.success("회원가입 성공", null));
    }
}