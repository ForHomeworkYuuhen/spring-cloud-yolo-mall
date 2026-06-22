package com.gec.shop.gateway.filter;

import lombok.Getter;
import lombok.Setter;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.factory.AbstractGatewayFilterFactory;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Mono;

import java.util.Arrays;
import java.util.List;

/**
 * Day04 7.8.3 自定义局部路由过滤器：统计请求耗时。
 * <p>
 * 命名必须满足固定格式 xxxGatewayFilterFactory，使用时在路由上配置 - Time=true。
 */
@Component
public class TimeGatewayFilterFactory extends AbstractGatewayFilterFactory<TimeGatewayFilterFactory.Config> {

    private static final String BEGIN_TIME = "beginTime";

    public TimeGatewayFilterFactory() {
        super(TimeGatewayFilterFactory.Config.class);
    }

    // 读取配置文件中的参数，赋值到配置类中
    @Override
    public List<String> shortcutFieldOrder() {
        return Arrays.asList("show");
    }

    @Override
    public GatewayFilter apply(Config config) {
        return (exchange, chain) -> {
            if (!config.isShow()) {
                return chain.filter(exchange);
            }
            exchange.getAttributes().put(BEGIN_TIME, System.currentTimeMillis());
            // pre 逻辑 -> chain.filter().then(post 逻辑)
            return chain.filter(exchange).then(Mono.fromRunnable(() -> {
                Long startTime = exchange.getAttribute(BEGIN_TIME);
                if (startTime != null) {
                    System.out.println(exchange.getRequest().getURI()
                            + " 请求耗时: " + (System.currentTimeMillis() - startTime) + "ms");
                }
            }));
        };
    }

    @Setter
    @Getter
    public static class Config {
        private boolean show;
    }
}
