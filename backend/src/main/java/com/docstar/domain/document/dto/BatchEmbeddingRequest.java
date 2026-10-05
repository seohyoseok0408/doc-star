package com.docstar.domain.document.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public record BatchEmbeddingRequest(
        @JsonProperty("document_id") int documentId,
        List<ChunkItem> chunks
) {
    public record ChunkItem(
            @JsonProperty("chunk_id") int chunkId,
            @JsonProperty("chunk_index") int chunkIndex,
            String text
    ) {}
}
