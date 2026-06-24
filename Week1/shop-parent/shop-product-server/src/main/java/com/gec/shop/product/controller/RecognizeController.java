package com.gec.shop.product.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

/**
 * 商品识别（应用层）。
 * <p>
 * 图片上传走微服务架构：前端 → 网关 → 本服务（应用层）→ 算法层 AI 服务。
 * 算法服务地址 {@code reco.service.url} 存放在 Nacos 配置中心；本类贴 {@link RefreshScope}，
 * 在 Nacos 控制台修改该地址后无需重启即动态刷新生效（数据处理的“刷新”方式）。
 */
@RestController
@RefreshScope
public class RecognizeController {

    /** 算法层 AI 服务地址，来自 Nacos 配置中心，可动态刷新。 */
    @Value("${reco.service.url:http://localhost:8123}")
    private String recoUrl;

    @Autowired
    private RestTemplate restTemplate;

    /** 接收前端上传的图片，转发给算法层做识别。 */
    @PostMapping("/recognize")
    public ResponseEntity<String> recognize(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "model", defaultValue = "11s_balanced") String model) throws IOException {

        final String filename = file.getOriginalFilename() == null ? "upload.jpg" : file.getOriginalFilename();
        MultiValueMap<String, Object> form = new LinkedMultiValueMap<>();
        form.add("file", new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return filename;
            }
        });
        form.add("model", model);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);
        HttpEntity<MultiValueMap<String, Object>> request = new HttpEntity<>(form, headers);

        // 转发到 Nacos 配置中指定的算法服务
        ResponseEntity<String> resp = restTemplate.postForEntity(recoUrl + "/recognize", request, String.class);
        return ResponseEntity.status(resp.getStatusCode())
                .contentType(MediaType.APPLICATION_JSON)
                .body(resp.getBody());
    }

    /** 透传算法层的模型列表（前端选择器用）。 */
    @GetMapping("/models")
    public ResponseEntity<String> models() {
        ResponseEntity<String> resp = restTemplate.getForEntity(recoUrl + "/models", String.class);
        return ResponseEntity.status(resp.getStatusCode())
                .contentType(MediaType.APPLICATION_JSON)
                .body(resp.getBody());
    }

    /** 查看当前生效的算法服务地址（演示 @RefreshScope：在 Nacos 改后这里会变）。 */
    @GetMapping("/recognize/config")
    public String currentRecoUrl() {
        return "当前算法服务地址(reco.service.url) = " + recoUrl;
    }
}
