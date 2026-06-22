package com.gec.shop.gateway.filter;

import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

/**
 * Day04 7.8.2.3 自定义全局过滤器——网关统一鉴权。
 * <p>
 * 规则：所有经过网关的请求必须携带 ?token=123，否则返回 401。
 * （GlobalFilter 作用于所有路由，无需在路由上单独配置）
 * <p>
 * ServerWebExchange 是 Spring5 WebFlux 中 HTTP 请求/响应交互的契约，
 * 类似 Servlet 中的 Context，存放请求实例、响应实例等。
 */
@Slf4j
@Component
public class AuthGlobalFilter implements GlobalFilter, Ordered {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        log.info("--前置 pre 逻辑--");

        // 公开接口放行：登录/注册无需 token
        String path = exchange.getRequest().getURI().getPath();
        if (path.startsWith("/user/")) {
            return chain.filter(exchange);
        }

        String token = exchange.getRequest().getQueryParams().getFirst("token");
        if (token == null || !"123".equals(token)) {
            log.warn("鉴权失败：缺少有效 token");
            // 无权限：给出状态码并终止后续请求
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        log.info("认证有效，放行");
        return chain.filter(exchange).then(Mono.fromRunnable(() -> {
            // post 后置逻辑
            log.info("--后置 post 逻辑--");
        }));
    }

    @Override
    public int getOrder() {
        return 0;
    }
}
