package com.docstar.api;

import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.docstar.domain.user.dto.UserRequestDTO;
import com.docstar.domain.user.dto.UserResponseDTO;
import com.docstar.domain.user.service.UserService;
import com.docstar.global.ApiResponse;

import java.util.Collections;
import java.util.Map;

@RestController
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    // 자체 로그인 유저 존재 확인
    @PostMapping(value = "/user/exist", consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<ApiResponse<Boolean>> existUserApi(
            @Validated(UserRequestDTO.existGroup.class) @RequestBody UserRequestDTO dto) {

        Boolean exists = userService.existUser(dto);
        // 응답: 200 OK
        return ResponseEntity.ok(ApiResponse.success("유저 존재 확인 성공", exists));
    }

    // 회원가입
    @PostMapping(value = "/user", consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<ApiResponse<Map<String, Long>>> joinApi(
            @Validated(UserRequestDTO.addGroup.class) @RequestBody UserRequestDTO dto) {
                
        Long id = userService.addUser(dto);
        Map<String, Long> responseBody = Collections.singletonMap("userEntityId", id);

        return ResponseEntity.status(201).body(ApiResponse.success("회원가입 성공", responseBody));    
    }

    // 유저 정보
    @GetMapping(value = "/user")
    public ResponseEntity<ApiResponse<UserResponseDTO>> userMeApi() {

        UserResponseDTO userDto = userService.readUser();

        return ResponseEntity.ok(ApiResponse.success(userDto));   
     }

    // 유저 제거 (자체)
    @DeleteMapping(value = "/user", consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<ApiResponse<Boolean>> deleteUserApi(
            @Validated(UserRequestDTO.deleteGroup.class) @RequestBody UserRequestDTO dto) throws AccessDeniedException {

        userService.deleteUser(dto);
        return ResponseEntity.ok(ApiResponse.success("회원 탈퇴 성공", true));   
     }
}