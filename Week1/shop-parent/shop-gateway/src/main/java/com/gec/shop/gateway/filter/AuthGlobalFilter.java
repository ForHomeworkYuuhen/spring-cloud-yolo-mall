package com.gec.shop.gateway.filter;

import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;
import com.gec.shop.gateway.util.JwtUtil;

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
        String path = exchange.getRequest().getURI().getPath();

        // 公开路径放行：登录/注册 + 商品目录浏览（未登录也能逛）
        if (path.startsWith("/user/") || path.startsWith("/product/") || path.startsWith("/admin/")) {
            return chain.filter(exchange);
        }

        // 其余（如下单 /order/**）必须携带有效 JWT
        String token = resolveToken(exchange);
        String username = (token == null) ? null : JwtUtil.verify(token);
        if (username == null) {
            log.warn("鉴权失败：JWT 缺失/无效/被篡改/已过期，path={}", path);
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        log.info("JWT 校验通过，用户={}，放行 {}", username, path);
        return chain.filter(exchange);
    }

    /** 从 Authorization: Bearer xxx 请求头，或 ?token=xxx 查询参数中取出令牌。 */
    private String resolveToken(ServerWebExchange exchange) {
        String auth = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (auth != null && auth.startsWith("Bearer ")) {
            return auth.substring(7);
        }
        return exchange.getRequest().getQueryParams().getFirst("token");
    }

    @Override
    public int getOrder() {
        return 0;
    }
}
