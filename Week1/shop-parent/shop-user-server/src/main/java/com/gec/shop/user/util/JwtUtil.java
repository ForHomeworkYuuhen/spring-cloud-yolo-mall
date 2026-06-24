package com.gec.shop.user.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import java.util.Date;

/**
 * JWT 工具：登录/注册成功后签发带 HS256 签名和过期时间的令牌。
 * <p>
 * 相比之前的 Base64(用户名:时间戳) —— JWT 有签名，无法伪造/篡改；带 exp，会过期。
 * 网关验签必须使用同一个 {@link #SECRET}。生产环境密钥应放配置中心/环境变量。
 */
public class JwtUtil {

    private static final byte[] SECRET =
            "gec-shop-2026-jwt-hs256-secret-please-change-in-prod".getBytes();
    private static final long EXPIRE_MS = 2 * 60 * 60 * 1000L; // 令牌有效期 2 小时

    /** 为指定用户签发 JWT。 */
    public static String create(String username) {
        long now = System.currentTimeMillis();
        return Jwts.builder()
                .setSubject(username)
                .setIssuedAt(new Date(now))
                .setExpiration(new Date(now + EXPIRE_MS))
                .signWith(SignatureAlgorithm.HS256, SECRET)
                .compact();
    }

    /** 校验 JWT，返回用户名（subject）；无效 / 过期 / 被篡改返回 null。 */
    public static String verify(String token) {
        try {
            Claims c = Jwts.parser().setSigningKey(SECRET).parseClaimsJws(token).getBody();
            return c.getSubject();
        } catch (Exception e) {
            return null;
        }
    }
}
