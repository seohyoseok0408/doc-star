package com.docstar.filter;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletInputStream;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.log4j.Log4j2;

import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.AuthenticationServiceException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.authentication.AbstractAuthenticationProcessingFilter;
import org.springframework.security.web.authentication.AuthenticationFailureHandler;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.security.web.servlet.util.matcher.PathPatternRequestMatcher;
import org.springframework.security.web.util.matcher.RequestMatcher;
import org.springframework.util.StreamUtils;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Map;

@Log4j2
public class LoginFilter extends AbstractAuthenticationProcessingFilter {

    public static final String SPRING_SECURITY_FORM_USERNAME_KEY = "username";

    public static final String SPRING_SECURITY_FORM_PASSWORD_KEY = "password";

    // 스프링 기본 경로 매핑 규칙을 가져와 사용
    // POST /login 요청을 가로챔
    private static final RequestMatcher DEFAULT_ANT_PATH_REQUEST_MATCHER = PathPatternRequestMatcher.withDefaults()
            .matcher(HttpMethod.POST, "/login");

    private String usernameParameter = SPRING_SECURITY_FORM_USERNAME_KEY;

    private String passwordParameter = SPRING_SECURITY_FORM_PASSWORD_KEY;

    // 인증 성공/실패 시, 후속 작업 처리 위한 핸들러 인스턴스 저장
    private final AuthenticationSuccessHandler authenticationSuccessHandler;
    private final AuthenticationFailureHandler authenticationFailureHandler; 

    // Spring Bean으로 주입받은 필수 의존성들을 필터에 전달
    // AuthenticationManager > 실제 사용자 자격 증명을 검증하는 작업을 위임받기 위한 중재자 객체
    // AuthenticationSuccessHandler > 인증 성공 시 실행될 로직을 담고 있는 핸들러 객체
    // AuthenticationFailureHandler > 인증 실패 시 실행될 로직을 담고 있는 핸들러 객체
    public LoginFilter(AuthenticationManager authenticationManager, AuthenticationSuccessHandler authenticationSuccessHandler, AuthenticationFailureHandler authenticationFailureHandler) {
        super(DEFAULT_ANT_PATH_REQUEST_MATCHER, authenticationManager);
        this.authenticationSuccessHandler = authenticationSuccessHandler;
        this.authenticationFailureHandler = authenticationFailureHandler;
    }

    // HTTP 요청에서 사용자 자격 증명을 추출 > 인증 관리자에게 위임하여 실제 인증을 시작하는 역할
    @Override
    public Authentication attemptAuthentication(HttpServletRequest request, HttpServletResponse response) throws AuthenticationException {
        // POST 요청인지 확인
        if (!request.getMethod().equals("POST")) {
            throw new AuthenticationServiceException("Authentication method not supported: " + request.getMethod());
        }

        Map<String, String> loginMap;

        // JSON 요청 바디 추출 및 파싱
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            // 원시 바디 데이터 추출
            ServletInputStream inputStream = request.getInputStream();
            // 바디 내용을 문자열로 변환
            String messageBody = StreamUtils.copyToString(inputStream, StandardCharsets.UTF_8);
            // JSON 문자열 역직렬화
            loginMap = objectMapper.readValue(messageBody, new TypeReference<>() {
            });

        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        String username = loginMap.get(usernameParameter);
        username = (username != null) ? username.trim() : "";
        String password = loginMap.get(passwordParameter);
        password = (password != null) ? password : "";

        // 인증 토큰 생성 및 위임
        // 인증 전 상태의 토큰 생성
        UsernamePasswordAuthenticationToken authRequest = UsernamePasswordAuthenticationToken.unauthenticated(username, password);
        // IP 주소 등과 같은 추가 인증 세부 정보 토큰에 첨부
        setDetails(request, authRequest);
        // AuthenticationManager에게 위임 (실제 사용자 인증 작업)
        return this.getAuthenticationManager().authenticate(authRequest);
    }

    protected void setDetails(HttpServletRequest request, UsernamePasswordAuthenticationToken authRequest) {
        authRequest.setDetails(this.authenticationDetailsSource.buildDetails(request));
    }

    // 인증 성공 시 자동 호출
    @Override
    protected void successfulAuthentication(HttpServletRequest request, HttpServletResponse response, FilterChain chain,
                                            Authentication authResult) throws IOException, ServletException {
        authenticationSuccessHandler.onAuthenticationSuccess(request, response, authResult);
    }

    // 인증 실패 시 자동 호출
    @Override
    protected void unsuccessfulAuthentication(HttpServletRequest request, HttpServletResponse response, 
                                            AuthenticationException failed) throws IOException, ServletException {

        authenticationFailureHandler.onAuthenticationFailure(request, response, failed);
    }
}