package com.docstar.domain.document.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record BatchEmbeddingResponse(
        @JsonProperty("document_id") int documentId,
        int total,
        int succeeded,
        int failed
) {}
