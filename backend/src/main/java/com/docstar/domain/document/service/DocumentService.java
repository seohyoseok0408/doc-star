package com.docstar.domain.document.service;

import com.docstar.domain.document.entity.DocumentChunkEntity;
import com.docstar.domain.document.entity.DocumentEntity;
import com.docstar.domain.document.entity.DocumentStatus;
import com.docstar.domain.document.entity.DocumentTextEntity;
import com.docstar.domain.document.repository.DocumentChunkRepository;
import com.docstar.domain.document.repository.DocumentRepository;
import com.docstar.domain.document.repository.DocumentTextRepository;
import com.docstar.domain.user.entity.UserEntity;
import com.docstar.domain.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class DocumentService {

    private final DocumentRepository documentRepository;
    private final DocumentTextRepository documentTextRepository;
    private final DocumentChunkRepository documentChunkRepository;
    private final UserRepository userRepository;

    @Transactional
    public void processDocument(MultipartFile file, String username) throws IOException {
        UserEntity user = userRepository.findByUsernameAndIsLock(username, false)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 유저입니다. username=" + username));

        DocumentEntity documentEntity = DocumentEntity.builder()
                .user(user)
                .originalFileName(file.getOriginalFilename())
                .filePath("temp_path_for_now")
                .fileSize(file.getSize())
                .mimeType(file.getContentType() != null ? file.getContentType() : "application/octet-stream")
                .status(DocumentStatus.PROCESSING)
                .build();
        documentRepository.save(documentEntity);

        String fullText = extractText(file);

        DocumentTextEntity documentTextEntity = DocumentTextEntity.builder()
                .document(documentEntity)
                .fullText(fullText)
                .build();
        documentTextRepository.save(documentTextEntity);

        List<String> chunks = chunkText(fullText, 500);
        List<DocumentChunkEntity> chunkEntities = new ArrayList<>();

        for (int i = 0; i < chunks.size(); i++) {
            DocumentChunkEntity chunkEntity = DocumentChunkEntity.builder()
                    .document(documentEntity)
                    .chunkIndex(i)
                    .text(chunks.get(i))
                    .build();
            chunkEntities.add(chunkEntity);
        }
        documentChunkRepository.saveAll(chunkEntities);

        documentEntity.markCompleted();
        documentRepository.save(documentEntity);

        log.info("문서 처리 완료: docId={}, chunks={}", documentEntity.getDocId(), chunks.size());
    }

    private String extractText(MultipartFile file) throws IOException {
        String mimeType = file.getContentType();
        if ("application/pdf".equals(mimeType)) {
            try (PDDocument doc = Loader.loadPDF(file.getBytes())) {
                return new PDFTextStripper().getText(doc);
            }
        } else if (mimeType != null && mimeType.startsWith("text/")) {
            return new String(file.getBytes(), StandardCharsets.UTF_8);
        }
        throw new IllegalArgumentException("지원하지 않는 파일 형식입니다: " + mimeType);
    }

    private List<String> chunkText(String text, int chunkSize) {
        List<String> chunks = new ArrayList<>();
        for (int i = 0; i < text.length(); i += chunkSize) {
            chunks.add(text.substring(i, Math.min(text.length(), i + chunkSize)));
        }
        return chunks;
    }
}
