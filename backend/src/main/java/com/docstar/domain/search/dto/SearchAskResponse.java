package com.docstar.domain.search.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public record SearchAskResponse(
        String answer,
        List<SourceItem> sources,
        @JsonProperty("latency_ms") double latencyMs
) {
    public record SourceItem(
            @JsonProperty("document_id") int documentId,
            @JsonProperty("chunk_id") Integer chunkId,
            @JsonProperty("chunk_index") Integer chunkIndex,
            float score,
            String text
    ) {}
}
