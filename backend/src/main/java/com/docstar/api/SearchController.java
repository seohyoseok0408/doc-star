package com.docstar.api;

import com.docstar.domain.search.dto.SearchAskRequest;
import com.docstar.domain.search.dto.SearchAskResponse;
import com.docstar.global.ApiResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;

@Slf4j
@RestController
@RequestMapping("/api/search")
@RequiredArgsConstructor
public class SearchController {

    private final RestClient aiRestClient;

    @PostMapping("/ask")
    public ResponseEntity<ApiResponse<SearchAskResponse>> ask(@RequestBody SearchAskRequest request) {
        try {
            SearchAskResponse response = aiRestClient.post()
                    .uri("/internal/search/ask")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .body(SearchAskResponse.class);
            return ResponseEntity.ok(ApiResponse.success(response));
        } catch (Exception e) {
            log.error("검색 요청 실패", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.failure("검색 처리 중 오류가 발생했습니다."));
        }
    }
}
