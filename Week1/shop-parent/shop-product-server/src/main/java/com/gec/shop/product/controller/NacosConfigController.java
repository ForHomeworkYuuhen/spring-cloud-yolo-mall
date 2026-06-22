package com.gec.shop.product.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Day05 配置中心演示。
 * <p>
 * 必须贴 {@code @RefreshScope}，当 Nacos 中的配置发生更新时，该 Bean 会被重新创建，
 * 从而实现配置的动态刷新（无需重启服务）。
 * <p>
 * 这里给 {@code @Value} 都设置了默认值，使得在没有连接 Nacos 配置中心 / 未上传配置时，
 * 服务仍可正常启动。上传 nacos-config 目录下的配置文件后即可读到远程值。
 */
@RestController
@RefreshScope
public class NacosConfigController {

    @Value("${appConfig.name:本地默认appConfig.name}")
    private String appConfigName;

    @Value("${globalConfig:本地默认globalConfig}")
    private String globalConfig;

    @GetMapping("/appconfigname")
    public String appconfigname() {
        return "从nacos上动态获取到数据是:" + appConfigName + "---而且还是实时刷新的哦-";
    }

    @RequestMapping("/nacosConfig")
    public String nacosConfig() {
        return "远程信息:" + appConfigName;
    }

    @RequestMapping("/nacosConfig2")
    public String nacosConfig2() {
        return "全局配置:" + globalConfig;
    }
}
