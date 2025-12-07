// package com.docstar.config;

// import lombok.RequiredArgsConstructor;

// import org.springframework.beans.factory.annotation.Value;
// import org.springframework.context.annotation.Bean;
// import org.springframework.context.annotation.Configuration;
// import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
// import org.springframework.security.config.annotation.web.builders.HttpSecurity;
// import org.springframework.security.config.http.SessionCreationPolicy;
// import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
// import org.springframework.security.crypto.password.PasswordEncoder;
// import org.springframework.security.web.SecurityFilterChain;
// import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
// import org.springframework.security.web.authentication.logout.LogoutFilter;

// @Configuration
// @RequiredArgsConstructor
// public class SecurityConfig {

//     private final AuthenticationConfiguration authenticationConfiguration;
//     private final JWTUtil jwtUtil;
//     private final CustomAuthenticationEntryPoint customAuthenticationEntryPoint; 
//     private final RedisTemplate<String, Object> redisTemplate;
//     private final CustomOAuth2UserService customOAuth2UserService;

//     @Value("${custom.frontend.base-url}")
//     private String frontendBaseUrl;

//     // 비밀번호 암호화를 위한 Bean 등록
//     @Bean
//     public PasswordEncoder passwordEncoder() {
//         return new BCryptPasswordEncoder();
//     }

//     // 보안 필터 체인 설정
//     @Bean
//     public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {

//         // 기본 설정 비활성화: CSRF, FormLogin, HttpBasic
//         http
//                 .csrf(csrf -> csrf.disable())
//                 .formLogin(form -> form.disable())
//                 .httpBasic(httpBasic -> httpBasic.disable());
        
//         // 경로별 인가 정책
//         http
//                 .authorizeHttpRequests(auth -> auth
//                         .requestMatchers("/api/auth/**", "/login/**", "oauth2/**", "/ws/**", "/swagger-ui/**", "/v3/api-docs/**").permitAll()
//                         .requestMatchers("/api/users/complete-info").hasRole("PREUSER")
//                         .requestMatchers("/api/**").hasRole("USER")
//                         .anyRequest().authenticated()
//                 );
        
//         // 인증 예외 처리 핸들러 설정 (401 에러 처리)
//         http
//                 .exceptionHandling(exception -> exception
//                 .authenticationEntryPoint(customAuthenticationEntryPoint) 
//                 );    
        
//         // OAuth2 로그인 설정
//         http
//                 .oauth2Login((oauth2) -> oauth2
//                         .successHandler(new CustomSuccessHandler(jwtUtil, redisTemplate, frontendBaseUrl))
//                         .userInfoEndpoint((userInfoEndpointConfig) -> userInfoEndpointConfig
//                                 .userService(customOAuth2UserService)));
        
//         // JWT 로그인 필터 등록 (아이디/비밀번호 기반 로그인)
//         http
//                 .addFilterAt(new LoginFilter(authenticationConfiguration.getAuthenticationManager(), jwtUtil, redisTemplate), UsernamePasswordAuthenticationFilter.class)
//                 // JWT 인증 필터 등록 (모든 요청마다 토큰 검증)
//                 .addFilterAfter(new JWTFilter(jwtUtil), LoginFilter.class);
        
//         // 커스텀 로그아웃 필터 등록 (JWT 기반 로그아웃 처리)
//         http
//                 .addFilterBefore(new CustomLogoutFilter(jwtUtil, redisTemplate), LogoutFilter.class);

//         // 세션 사용 안함
//         http
//                 .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS));

//         return http.build();
//     }
// }