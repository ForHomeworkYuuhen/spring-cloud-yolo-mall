package com.gec.shop.order.config;

import com.alibaba.csp.sentinel.adapter.spring.webmvc.callback.RequestOriginParser;
import org.springframework.stereotype.Component;

import javax.servlet.http.HttpServletRequest;

/**
 * Day03 6.11 授权规则：定义请求来源（origin）如何获取。
 * 这里为方便演示，从 url 参数 serviceName 中取来源。
 */
@Component
public class RequestOriginParserDefinition implements RequestOriginParser {

    @Override
    public String parseOrigin(HttpServletRequest request) {
        return request.getParameter("serviceName");
    }
}
