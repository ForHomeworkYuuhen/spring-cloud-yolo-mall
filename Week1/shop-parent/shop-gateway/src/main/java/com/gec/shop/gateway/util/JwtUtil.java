package com.gec.shop.gateway.util;

import io.jsonwebtoken.Jwts;

/**
 * JWT 工具：网关侧验签解析。
 * <p>
 * 密钥必须与签发方（用户服务）完全一致，否则验签失败。
 */
public class JwtUtil {

    private static final byte[] SECRET =
            "gec-shop-2026-jwt-hs256-secret-please-change-in-prod".getBytes();

    /**
     * 验签 + 校验过期。
     *
     * @return 令牌有效则返回其中的用户名(subject)；缺失/签名不对/被篡改/已过期一律返回 null。
     */
    public static String verify(String token) {
        try {
            return Jwts.parser()
                    .setSigningKey(SECRET)
                    .parseClaimsJws(token)
                    .getBody()
                    .getSubject();
        } catch (Exception e) {
            return null;
        }
    }
}
