package com.gec.shop.gateway.config;

import com.alibaba.csp.sentinel.adapter.gateway.sc.callback.BlockRequestHandler;
import com.alibaba.csp.sentinel.adapter.gateway.sc.callback.GatewayCallbackManager;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.server.ServerResponse;

import javax.annotation.PostConstruct;
import java.util.HashMap;
import java.util.Map;

/**
 * Day04 7.9.3 自定义网关 Sentinel 限流后的返回格式（课后扩展）。
 * <p>
 * 默认情况下，请求被网关 Sentinel 限流时返回的是 Sentinel 内置的提示。
 * 这里通过 GatewayCallbackManager 注册自定义 BlockRequestHandler，
 * 让被限流的请求统一返回 JSON：{"code":0,"message":"接口被限流了"}。
 */
@Configuration
public class GatewayConfiguration {

    @PostConstruct
    public void initBlockHandlers() {
        BlockRequestHandler blockRequestHandler = (exchange, throwable) -> {
            Map<String, Object> map = new HashMap<>();
            map.put("code", 0);
            map.put("message", "接口被限流了");
            return ServerResponse.status(HttpStatus.OK)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(BodyInserters.fromValue(map));
        };
        GatewayCallbackManager.setBlockHandler(blockRequestHandler);
    }
}
