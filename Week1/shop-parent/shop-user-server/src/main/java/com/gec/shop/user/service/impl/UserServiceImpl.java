package com.gec.shop.user.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.gec.shop.user.mapper.UserMapper;
import com.gec.shop.user.pojo.User;
import com.gec.shop.user.service.UserService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {

    /** 安全规范：密码 BCrypt 加盐哈希存储，不存明文 */
    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

    @Override
    public Map<String, Object> register(User u) {
        if (u.getUsername() == null || u.getPassword() == null) return r(-1, "参数不完整", null);
        if (count(new QueryWrapper<User>().eq("username", u.getUsername())) > 0) return r(-1, "用户名已存在", null);
        u.setPassword(encoder.encode(u.getPassword()));
        if (u.getNickname() == null) u.setNickname(u.getUsername());
        save(u);
        return r(0, "注册成功", token(u.getUsername()));
    }

    @Override
    public Map<String, Object> login(User u) {
        User db = getOne(new QueryWrapper<User>().eq("username", u.getUsername()));
        if (db == null) return r(-1, "用户不存在", null);
        if (!encoder.matches(u.getPassword(), db.getPassword())) return r(-1, "密码错误", null);
        return r(0, "登录成功", token(db.getUsername()));
    }

    @Override
    public Map<String, Object> info(String auth) {
        String token = (auth != null && auth.startsWith("Bearer ")) ? auth.substring(7) : null;
        String username = (token == null) ? null : com.gec.shop.user.util.JwtUtil.verify(token);
        if (username == null) return r(-1, "未登录或登录已过期", null);
        User db = getOne(new QueryWrapper<User>().eq("username", username));
        if (db == null) return r(-1, "用户不存在", null);
        Map<String, Object> m = r(0, "ok", null);
        m.put("username", db.getUsername());
        m.put("nickname", db.getNickname());
        m.put("phone", db.getPhone());
        m.put("id", db.getId());
        return m;
    }

    /** 签发 JWT（HS256 签名 + 2 小时过期），替代原先可伪造的 Base64 令牌。 */
    private String token(String username) {
        return com.gec.shop.user.util.JwtUtil.create(username);
    }

    private Map<String, Object> r(int code, String msg, String token) {
        Map<String, Object> m = new HashMap<>();
        m.put("code", code);
        m.put("message", msg);
        if (token != null) m.put("token", token);
        return m;
    }
}
