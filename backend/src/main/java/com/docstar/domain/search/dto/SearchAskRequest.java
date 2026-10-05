package com.docstar.domain.search.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record SearchAskRequest(
        String question,
        @JsonProperty("top_k") int topK
) {}
