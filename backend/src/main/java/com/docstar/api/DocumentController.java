package com.docstar.api;

import com.docstar.domain.document.service.DocumentService;
import com.docstar.global.ApiResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@Slf4j
@RestController
@RequestMapping("/api/document")
@RequiredArgsConstructor
public class DocumentController {

    private final DocumentService documentService;

    @PostMapping("/upload")
    public ResponseEntity<ApiResponse<String>> uploadDocument(@RequestParam("file") MultipartFile file) {

        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body(ApiResponse.failure("업로드할 파일을 선택해주세요."));
        }

        try {
            String username = SecurityContextHolder.getContext().getAuthentication().getName();
            String originalFileName = file.getOriginalFilename();

            documentService.processDocument(file, username);

            log.info("File upload by {}: {}", username, originalFileName);
            return ResponseEntity.ok(ApiResponse.success("파일이 성공적으로 업로드 및 처리 요청되었습니다: " + originalFileName, null));

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(ApiResponse.failure(e.getMessage()));
        } catch (IOException e) {
            log.error("Failed to process file upload", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(ApiResponse.failure("파일 업로드 및 처리에 실패했습니다."));
        }
    }
}
